"""
阶段策略：每个会话阶段的「提示词差异 + 可用工具集 + 流转条件」。

与 session_state.py 的分工：
  - session_state.py 负责「记状态」
  - stage_policy.py  负责「怎么表现」和「什么时候该走」

三块内容：
1. STAGE_PROMPTS   —— 追加在基础 system prompt 之后的阶段化指令
2. STAGE_TOOLS     —— 各阶段允许调用的工具白名单 + tool_choice 倾向
3. decide_stage()  —— 依据本轮输入信号与当前状态计算下一阶段
"""

import re

from services.session_state import (
    SessionStage,
    MIN_ASSESSMENT_TURNS,
    MAX_INTERVIEW_TURNS,
    CRISIS_COOLDOWN_TURNS,
)

# ---------------------------------------------------------------- 阶段提示词

STAGE_PROMPTS = {
    SessionStage.ASSESSMENT: """
【当前阶段：情况评估】
你正处在了解用户整体状态的阶段，目标是把「发生了什么」搞清楚，而不是急着给建议。

要做的：
- 用开放式问题引导用户描述处境，一次只问一个问题
- 关注三件事：主要困扰是什么、持续多久了、对生活造成了哪些影响
- 先共情再提问，让用户感到被接住而不是被问诊

不要做的：
- 不要在这个阶段大段输出方法论、技巧清单或科普知识
- 不要急于下结论或贴标签
- 不要一次抛出多个问题让用户不知从何答起""",

    SessionStage.INTERVIEW: """
【当前阶段：深度倾谈】
你已经大致了解用户的处境，现在要往下探一层，理解他的感受与应对方式。

要做的：
- 针对用户提到的具体事件继续深挖细节和感受
- 探索他此前尝试过什么方法、效果如何、身边有哪些支持
- 适度反映和总结你听到的内容，帮助用户理清自己的思路
- 如果用户提到需要具体方法，可以自然过渡到给建议

不要做的：
- 不要重复问已经问过的基础信息
- 不要在用户还在倾诉时打断去讲道理
- 不要堆砌专业术语""",

    SessionStage.RESOURCE: """
【当前阶段：资源建议】
用户需要可操作的帮助，现在把前面聊到的内容收敛成具体建议。

要做的：
- 优先调用 knowledge_query 获取权威资料再作答，保证建议有依据
- 给 2-3 条具体、当下就能开始做的建议，说明每条大概怎么做
- 建议要贴合用户前面描述的具体处境，不要给放之四海皆准的空话
- 如果情况超出自助范围，明确建议寻求线下专业帮助

不要做的：
- 不要一口气罗列七八条让用户无从下手
- 不要给出需要专业资质才能执行的操作
- 不要编造资料里没有的数据或结论""",

    SessionStage.CRISIS: """
【当前阶段：危机支持】⚠️ 最高优先级
用户可能正处于心理危机中。此刻唯一目标是稳住他的情绪并连接到专业资源。

必须做的：
- 第一时间表达关心，肯定他愿意说出来的勇气
- 明确、完整地给出求助热线：400-161-9995（24小时）
- 鼓励他联系身边可信任的人，或前往最近医院急诊
- 语气温和、简短、具体，让他感到有人在

绝对不要做的：
- 不要说教、不要讲大道理、不要罗列条目式建议
- 不要评判他的想法，不要说"你不应该这样想"
- 不要转移话题，不要在这时候科普心理学知识
- 不要长篇大论，此刻简短而坚定比全面更重要""",
}


# ---------------------------------------------------------------- 阶段工具集

#: 各阶段允许调用的工具白名单。
#: trigger_warning 在所有阶段都保留——危机可能在任何时候出现。
STAGE_TOOLS = {
    # 评估阶段优先做情绪分析，不做知识检索（此时还不知道该查什么）
    SessionStage.ASSESSMENT: ["analyze_emotion", "trigger_warning"],
    # 访谈阶段两者都可用，情绪分析仍是主力
    SessionStage.INTERVIEW: ["analyze_emotion", "knowledge_query", "trigger_warning"],
    # 资源阶段以知识库检索为主，情绪分析让位
    SessionStage.RESOURCE: ["knowledge_query", "trigger_warning"],
    # 危机阶段只允许预警，禁止模型跑去查知识库耽误干预
    SessionStage.CRISIS: ["trigger_warning"],
}

#: 各阶段对模型的调用倾向提示，拼在阶段提示词后面
STAGE_TOOL_HINTS = {
    SessionStage.ASSESSMENT: (
        "\n\n【本阶段工具倾向】\n"
        "用户描述感受时优先调用 analyze_emotion 判断情绪强度。"
        "本阶段不要查知识库，先把情况了解清楚。"
    ),
    SessionStage.INTERVIEW: (
        "\n\n【本阶段工具倾向】\n"
        "以 analyze_emotion 跟踪情绪变化为主；"
        "只有用户明确问到某个概念或方法时才调用 knowledge_query。"
    ),
    SessionStage.RESOURCE: (
        "\n\n【本阶段工具倾向】\n"
        "给建议前应先调用 knowledge_query 检索权威资料，让建议有据可依。"
    ),
    SessionStage.CRISIS: (
        "\n\n【本阶段工具倾向】\n"
        "若尚未推送过预警，必须调用 trigger_warning。不要调用其他工具。"
    ),
}


def get_stage_prompt(stage, state=None, with_tools=False):
    """取阶段提示词，可附带阶段内进度信息与工具倾向。"""
    prompt = STAGE_PROMPTS.get(stage, STAGE_PROMPTS[SessionStage.ASSESSMENT])

    if state is not None:
        progress = _build_progress_hint(stage, state)
        if progress:
            prompt += progress

    if with_tools:
        prompt += STAGE_TOOL_HINTS.get(stage, "")

    return prompt


def _build_progress_hint(stage, state):
    """把阶段内进度翻译成模型能理解的提示，避免它重复提问或重复推荐。"""
    parts = []

    if state.topics:
        parts.append(f"用户已提到的议题：{'、'.join(state.topics[-5:])}")

    if state.last_emotion_type:
        parts.append(f"最近一次情绪判断：{state.last_emotion_type}")

    if stage == SessionStage.ASSESSMENT:
        remaining = MIN_ASSESSMENT_TURNS - state.stage_turns
        if remaining > 0:
            parts.append(f"评估还需约 {remaining} 轮，请继续了解情况，先不要给方案")
        else:
            parts.append("基础情况已了解得差不多，可以开始往深处聊了")

    elif stage == SessionStage.INTERVIEW:
        if state.stage_turns >= MAX_INTERVIEW_TURNS - 1:
            parts.append("已经聊得比较深入，可以适时收敛到具体建议了")

    elif stage == SessionStage.RESOURCE:
        if state.recommended_article_ids:
            parts.append("已经推荐过一些资料，这次请给出不重复的新角度")

    elif stage == SessionStage.CRISIS:
        if state.warning_pushed:
            parts.append("本会话已推送过预警给心理老师，不要重复触发，专注于陪伴与稳定情绪")

    if not parts:
        return ""

    return "\n\n【本阶段进度】\n" + "\n".join(f"- {p}" for p in parts)


def get_allowed_tools(stage):
    """取当前阶段允许的工具名列表。"""
    return STAGE_TOOLS.get(stage, STAGE_TOOLS[SessionStage.ASSESSMENT])


def get_tool_choice(stage, state=None):
    """危机阶段且尚未预警时强制调用 trigger_warning，其余交给模型自行判断。"""
    if stage == SessionStage.CRISIS:
        if state is None or not state.warning_pushed:
            return {"type": "function", "function": {"name": "trigger_warning"}}
    return "auto"


# ---------------------------------------------------------------- 意图识别

#: 用户主动索取方法/资源的表达
_RESOURCE_PATTERNS = [
    r"怎么办", r"怎么(样)?(才能|可以)?(缓解|改善|调节|应对|克服|解决)",
    r"有(没有|什么)(方法|办法|建议|技巧|资料|课程|书)",
    r"该(怎么|如何)", r"如何(缓解|改善|调节|应对|克服|解决|面对)",
    r"求(推荐|建议|方法)", r"给我(点|一些|些)?(建议|方法|办法)",
    r"想(学|了解|知道).{0,6}(方法|技巧|怎么)",
    r"需要(帮助|建议|资源)", r"能帮我", r"教教我", r"有什么可以做",
    r"what (can|should) i do", r"how (can|do) i",
    r"any (advice|suggestions|tips|resources)", r"help me",
]

#: 用户抛出新议题、想继续倾诉的表达（用于从 resource 回退到 interview）
_NEW_TOPIC_PATTERNS = [
    r"还有(一件事|个问题|件事)", r"另外", r"其实我", r"我还(想说|有)",
    r"除此之外", r"不只(是)?这些", r"我想说说", r"再说说",
    r"actually", r"another (thing|issue|problem)", r"one more thing",
]

_RESOURCE_RE = re.compile("|".join(_RESOURCE_PATTERNS), re.IGNORECASE)
_NEW_TOPIC_RE = re.compile("|".join(_NEW_TOPIC_PATTERNS), re.IGNORECASE)


def detect_resource_intent(message):
    """判断用户是否在索取具体方法或资源。"""
    return bool(_RESOURCE_RE.search(message or ""))


def detect_new_topic_intent(message):
    """判断用户是否抛出了新议题。"""
    return bool(_NEW_TOPIC_RE.search(message or ""))


# ---------------------------------------------------------------- 流转决策

def decide_stage(state, message, crisis_detected=False):
    """计算本轮应处的阶段。

    在「调用模型之前」执行，依据是用户输入与既有状态。
    模型执行完拿到工具结果后，再由 apply_post_turn_signals 做一次修正。

    :param state:  SessionState
    :param message: 用户本轮原始输入
    :param crisis_detected: 关键词硬匹配等前置手段判定的危机
    :return: (stage, reason)
    """
    current = state.stage

    # ① 危机最高优先级，任何阶段随时短路进入
    if crisis_detected:
        return SessionStage.CRISIS, "检测到危机信号"

    # ② 危机阶段的降级：需要连续若干轮平稳才允许退出
    if current == SessionStage.CRISIS:
        if state.calm_turns >= CRISIS_COOLDOWN_TURNS:
            # 危机后不回评估，直接回访谈继续陪伴
            return SessionStage.INTERVIEW, "危机信号已连续多轮未出现，降级为深度倾谈"
        return SessionStage.CRISIS, "危机干预中，继续观察"

    # ③ 用户主动索取方法/资源 —— 评估与访谈阶段都可直接跳转
    if detect_resource_intent(message):
        if current != SessionStage.RESOURCE:
            return SessionStage.RESOURCE, "识别到用户索取具体方法或资源"
        return SessionStage.RESOURCE, "继续提供资源建议"

    # ④ 资源阶段用户抛出新议题 → 回到深度访谈
    if current == SessionStage.RESOURCE and detect_new_topic_intent(message):
        return SessionStage.INTERVIEW, "用户提出新议题，回到深度倾谈"

    # ⑤ 评估 → 访谈：轮次达标且已建立情绪画像
    if current == SessionStage.ASSESSMENT:
        if state.stage_turns >= MIN_ASSESSMENT_TURNS and state.emotion_profiled:
            return SessionStage.INTERVIEW, "基础情况评估完成"
        return SessionStage.ASSESSMENT, "继续评估"

    # ⑥ 访谈 → 资源：聊得足够深了主动收敛到建议
    if current == SessionStage.INTERVIEW:
        if state.stage_turns >= MAX_INTERVIEW_TURNS:
            return SessionStage.RESOURCE, "深度倾谈轮次达标，主动给出建议"
        return SessionStage.INTERVIEW, "继续深度倾谈"

    return current, "保持当前阶段"


def apply_post_turn_signals(state, tool_trace, crisis_detected):
    """模型执行完后，用工具结果修正状态。

    典型场景：进入本轮时还在评估阶段，但 analyze_emotion 返回
    crisisDetected=True，此时必须立刻把阶段纠正为 crisis。

    :return: (final_stage, changed_reason or None)
    """
    emotion_crisis = False
    warning_high = False

    for call in tool_trace or []:
        name = call.get("name")
        result = call.get("result") or {}
        if call.get("status") != "success":
            continue

        if name == "analyze_emotion":
            state.record_emotion(
                sentiment_score=result.get("sentimentScore"),
                emotion_type=result.get("emotionType"),
            )
            if result.get("crisisDetected"):
                emotion_crisis = True

        elif name == "trigger_warning":
            if result.get("warningPushed"):
                state.warning_pushed = True
            if result.get("riskLevel") == "high":
                warning_high = True

        elif name == "knowledge_query":
            state.record_references(result.get("items"))

    # 工具结果暴露出危机 → 立即纠正阶段
    if (emotion_crisis or warning_high or crisis_detected) and state.stage != SessionStage.CRISIS:
        reason = "工具结果检测到危机信号"
        state.transit_to(SessionStage.CRISIS, reason)
        return state.stage, reason

    # 危机阶段：本轮工具结果仍暴露危机则重置平稳计数。
    # 平稳轮次的累加由 ChatService 在调用前统一完成，此处只负责「归零」，
    # 保证本函数可重复调用而不会把计数推快。
    if state.stage == SessionStage.CRISIS:
        if emotion_crisis or warning_high or crisis_detected:
            state.calm_turns = 0

    return state.stage, None
