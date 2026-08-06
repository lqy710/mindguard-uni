"""
会话阶段状态机。

把原先「线性多轮对话 + 危机关键词短路」升级为显式的阶段管理：

    评估(assessment) → 深度访谈(interview) → 资源推荐(resource)
                    ↘ 危机干预(crisis) ↙   （任意阶段可随时短路进入）

设计要点：
1. 状态与业务解耦：本模块只负责「记住我在哪个阶段、进度如何」以及
   「根据本轮信号判断该去哪个阶段」，不关心 prompt 怎么写、工具怎么调，
   那部分在 stage_policy.py。
2. 状态键控：优先用 session_id（一个会话一条状态线），没有 session_id
   时退化到 user_id，两者都没有时使用匿名键，保证永远能拿到一个 state。
3. 内存存储 + TTL：与既有 user_profiles 保持一致的进程内实现，
   附带惰性过期清理，避免长期运行内存无界增长。
4. 危机优先级最高：任何阶段命中危机信号都立即跳转 crisis，
   且危机解除后只降级回 interview，绝不退回 assessment
   （用户已经倾诉过，再从头评估是二次伤害）。
"""

import threading
import time


class SessionStage:
    """会话阶段常量。用字符串而非 Enum，便于直接 JSON 序列化给前端。"""

    ASSESSMENT = "assessment"
    INTERVIEW = "interview"
    RESOURCE = "resource"
    CRISIS = "crisis"

    ALL = (ASSESSMENT, INTERVIEW, RESOURCE, CRISIS)

    #: 展示给前端的中文名，随 stage 字段一起下发，避免前端硬编码映射表
    LABELS = {
        ASSESSMENT: "情况评估",
        INTERVIEW: "深度倾谈",
        RESOURCE: "资源建议",
        CRISIS: "危机支持",
    }

    #: 每个阶段给用户看的一句话说明
    DESCRIPTIONS = {
        ASSESSMENT: "正在了解你的整体状态",
        INTERVIEW: "正在和你深入聊聊具体情况",
        RESOURCE: "正在为你整理可行的建议与资料",
        CRISIS: "已进入紧急支持模式，你的安全最重要",
    }

    @classmethod
    def is_valid(cls, stage):
        return stage in cls.ALL

    @classmethod
    def label(cls, stage):
        return cls.LABELS.get(stage, cls.LABELS[cls.ASSESSMENT])

    @classmethod
    def description(cls, stage):
        return cls.DESCRIPTIONS.get(stage, cls.DESCRIPTIONS[cls.ASSESSMENT])


# ---------------------------------------------------------------- 流转阈值

#: 评估阶段至少要经过多少轮才允许进入深度访谈
MIN_ASSESSMENT_TURNS = 3

#: 深度访谈到多少轮后，即便用户没明说也主动给资源建议
MAX_INTERVIEW_TURNS = 5

#: 危机阶段连续多少轮没有危机信号才允许降级
CRISIS_COOLDOWN_TURNS = 2

#: 状态过期时间（秒）。超过这个时间没有新消息，视为新会话重新开始评估
SESSION_TTL = 2 * 60 * 60


class SessionState:
    """单个会话的阶段状态与阶段内进度。"""

    def __init__(self, key):
        self.key = key
        self.stage = SessionStage.ASSESSMENT

        #: 整个会话的总轮次
        self.total_turns = 0
        #: 当前阶段内已进行的轮次，每次切换阶段清零
        self.stage_turns = 0

        #: 阶段流转历史 [{from, to, reason, at}]，便于排查与回溯
        self.history = []
        #: 本轮是否发生了阶段切换，供前端决定是否提示「已进入 XX 阶段」
        self.stage_changed_this_turn = False

        #: --- 评估阶段进度信号 ---
        #: 是否已经拿到过情绪分析结果
        self.emotion_profiled = False
        #: 最近一次情绪分值与类型
        self.last_sentiment = None
        self.last_emotion_type = None
        #: 评估阶段累计收集到的议题关键词
        self.topics = []

        #: --- 危机阶段进度信号 ---
        #: 连续多少轮没有再出现危机信号
        self.calm_turns = 0
        #: 本会话是否曾经触发过危机（用于后续全程保持更谨慎的语气）
        self.crisis_history = False
        #: 是否已经推送过预警，避免同一会话反复刷预警
        self.warning_pushed = False

        #: --- 资源阶段进度信号 ---
        #: 已经推荐过的资料 articleId，避免重复推荐
        self.recommended_article_ids = []

        self.created_at = time.time()
        self.updated_at = time.time()

    # ------------------------------------------------------------ 阶段切换

    def transit_to(self, stage, reason=""):
        """切换阶段。相同阶段则只累加阶段内轮次。"""
        if stage == self.stage:
            return False

        self.history.append({
            "from": self.stage,
            "to": stage,
            "reason": reason,
            "at": int(time.time() * 1000),
        })
        # 只保留最近 20 条，防止长会话无限增长
        if len(self.history) > 20:
            self.history = self.history[-20:]

        self.stage = stage
        self.stage_turns = 0
        self.stage_changed_this_turn = True

        if stage == SessionStage.CRISIS:
            self.crisis_history = True
            self.calm_turns = 0

        return True

    def mark_turn(self):
        """记一轮对话。需在本轮阶段判定之前调用，它会清掉上一轮的切换标记。"""
        self.total_turns += 1
        self.stage_turns += 1
        self.stage_changed_this_turn = False
        self.updated_at = time.time()

    # ------------------------------------------------------------ 信号写入

    def record_emotion(self, sentiment_score=None, emotion_type=None):
        self.emotion_profiled = True
        if sentiment_score is not None:
            self.last_sentiment = sentiment_score
        if emotion_type:
            self.last_emotion_type = emotion_type

    def record_topic(self, topic):
        if topic and topic not in self.topics:
            self.topics.append(topic)
            if len(self.topics) > 10:
                self.topics = self.topics[-10:]

    def record_references(self, references):
        for ref in references or []:
            article_id = ref.get("articleId")
            if article_id and article_id not in self.recommended_article_ids:
                self.recommended_article_ids.append(article_id)
        if len(self.recommended_article_ids) > 30:
            self.recommended_article_ids = self.recommended_article_ids[-30:]

    def is_expired(self, ttl=SESSION_TTL):
        return (time.time() - self.updated_at) > ttl

    # ------------------------------------------------------------ 对外快照

    def snapshot(self):
        """给前端 / 接口用的精简快照。"""
        return {
            "stage": self.stage,
            "stageLabel": SessionStage.label(self.stage),
            "stageDescription": SessionStage.description(self.stage),
            "stageTurns": self.stage_turns,
            "totalTurns": self.total_turns,
            "crisisHistory": self.crisis_history,
        }

    def debug_snapshot(self):
        """调试接口用的完整快照。"""
        data = self.snapshot()
        data.update({
            "key": self.key,
            "emotionProfiled": self.emotion_profiled,
            "lastSentiment": self.last_sentiment,
            "lastEmotionType": self.last_emotion_type,
            "topics": list(self.topics),
            "calmTurns": self.calm_turns,
            "warningPushed": self.warning_pushed,
            "recommendedArticleIds": list(self.recommended_article_ids),
            "history": list(self.history),
            "createdAt": int(self.created_at * 1000),
            "updatedAt": int(self.updated_at * 1000),
        })
        return data


class SessionStateStore:
    """进程内的会话状态仓库，按 user_id / session_id 键控。

    多线程下 Flask 可能并发处理同一用户的请求，这里用一把粗粒度锁
    保证 get_or_create 不会产生重复实例。单条会话内部的读写在
    ChatService 中是串行的，不再额外加锁。
    """

    def __init__(self, ttl=SESSION_TTL):
        self._states = {}
        self._lock = threading.Lock()
        self._ttl = ttl

    @staticmethod
    def build_key(user_id=None, session_id=None):
        """会话优先，其次用户，最后匿名。

        注意：user_id 与 session_id 必须组合进 key，否则不同用户的
        session_id 本地都从 1 开始计数会互相覆盖（例如用户 A 的
        session_id=1 与用户 B 的 session_id=1 撞成同一个 key）。
        单独只有 user_id（无 session_id）时仍按用户隔离，保证多端
        未传 session_id 的场景也不串号。
        """
        if session_id is not None and user_id is not None:
            return f"u:{user_id}:s:{session_id}"
        if session_id is not None:
            return f"s:{session_id}"
        if user_id is not None:
            return f"u:{user_id}"
        return "anonymous"

    def get_or_create(self, user_id=None, session_id=None):
        key = self.build_key(user_id, session_id)
        with self._lock:
            state = self._states.get(key)
            # 过期视为新会话：重新从评估阶段开始
            if state is None or state.is_expired(self._ttl):
                state = SessionState(key)
                self._states[key] = state
            return state

    def get(self, user_id=None, session_id=None):
        key = self.build_key(user_id, session_id)
        with self._lock:
            state = self._states.get(key)
            if state and state.is_expired(self._ttl):
                self._states.pop(key, None)
                return None
            return state

    def reset(self, user_id=None, session_id=None):
        key = self.build_key(user_id, session_id)
        with self._lock:
            return self._states.pop(key, None) is not None

    def purge_expired(self):
        """惰性清理过期状态，由调用方在合适时机触发。"""
        with self._lock:
            expired = [k for k, v in self._states.items() if v.is_expired(self._ttl)]
            for k in expired:
                self._states.pop(k, None)
            return len(expired)


#: 全局单例，与 chat_service 中的 user_profiles 生命周期一致
session_store = SessionStateStore()
