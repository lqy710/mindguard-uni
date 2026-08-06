import requests
import json
import time
from config import (
    ZHIPU_API_KEY, ZHIPU_MODEL, ZHIPU_BASE_URL, DEBUG,
    ENABLE_FUNCTION_CALLING, MAX_TOOL_ROUNDS, REQUEST_TIMEOUT,
)
from services.knowledge_service import knowledge_service
from services import ai_tools
from services import stage_policy
from services.session_state import SessionStage, session_store

class ChatService:
    MAX_TOKENS = 4096
    MAX_RETRY = 3
    RETRY_DELAY = 1

    # RAG 检索片段数量，以及注入 prompt 的最大字符数
    RAG_TOP_K = 3
    RAG_MAX_CONTEXT_CHARS = 1500
    
    def __init__(self):
        self.api_key = ZHIPU_API_KEY
        self.model = ZHIPU_MODEL
        self.base_url = ZHIPU_BASE_URL
        
        self.crisis_keywords = {
            'zh': ['自杀', '想死', '不想活', '活着没意思', '结束生命', '结束一切', '结束这一切',
                   '自残', '伤害自己', '跳楼', '割腕', '服药自杀', '活不下去', '活得太累',
                   '没有希望', '绝望', '解脱', '撑不下去', '撑不住了', '不想活了'],
            'en': ['suicide', 'kill myself', 'want to die', 'end my life', 'end it all',
                   'self-harm', 'harm myself', 'jump off', 'cut wrist', 'overdose',
                   "can't go on", "can't go on living", 'no hope', 'desperate', 'relief', 'want out']
        }
        
        self.user_profiles = {}

        # 会话阶段状态机仓库：按 user_id / session_id 维护当前阶段与阶段内进度
        self.session_store = session_store
        
        self.system_prompt = """你是一位专业、温暖的心理健康助手"小安"。请遵循以下原则：

【核心原则】
1. 用自然、亲切的语气交流，像朋友一样倾听
2. 根据用户的具体情况回应，不要每次都用相同的开场白
3. 提供科学、专业的心理健康建议，但不要诊断疾病
4. 必要时建议用户寻求专业心理医生的帮助
5. 记住用户的历史交互，提供个性化的回应

【回复风格】
- 简洁温暖，避免过长
- 直接回应用户的问题或情绪
- 使用"我"而不是"我是一位..."这种自我介绍
- 适当使用共情语句，如"我理解你的感受"

【禁止事项】
- 不要每次都用"您好！"开头
- 不要每次都说"看起来您可能..."
- 不要使用过于书面化的语言
- 不要忽视用户表达的具体内容

【个性化】
- 记住用户的姓名、偏好和历史问题
- 根据用户的语言类型进行回应
- 适应用户的沟通风格"""

        # 只在开启 function calling 时追加，避免降级模式下模型提到不存在的能力
        self.tool_prompt = """

【工具使用规则】
你可以调用工具来获取信息，请严格按需调用：
- analyze_emotion：用户在倾诉心情、描述感受时调用，用于判断情绪强度
- knowledge_query：用户询问心理学概念、症状、调节方法等知识性问题时调用
- trigger_warning：用户表达自杀、自伤、伤害他人意图或极端绝望时必须调用

注意事项：
1. 打招呼、闲聊、简单致谢不要调用任何工具，直接回复
2. 一轮对话里通常最多调用 1-2 个工具，不要为了调用而调用
3. 拿到工具结果后，用自然、口语化的方式融入回答，不要罗列原始数据
4. 不要向用户提及"我调用了xx工具"、"根据检索结果"这类系统实现细节
5. 若工具返回错误或为空，就基于你自己的专业知识正常回答，不要把错误暴露给用户"""

        self.crisis_response = {
            'zh': """我注意到你现在可能正在经历非常困难的时刻。你的生命很重要，我非常关心你的安全。

请立即联系专业帮助：
🆘 24小时心理援助热线：400-161-9995
🆘 北京心理危机研究与干预中心：010-82951332
🆘 生命热线：400-821-1215

如果你现在有伤害自己的想法，请：
1. 立即拨打上面的热线电话
2. 联系你信任的家人或朋友
3. 前往最近的医院急诊科

你不需要独自面对这些，专业的帮助可以让你度过难关。""",
            'en': """I notice you may be going through a very difficult time right now. Your life is important, and I am deeply concerned about your safety.

Please contact professional help immediately:
🆘 24-hour psychological assistance hotline: +86 400-161-9995
🆘 Beijing Psychological Crisis Research and Intervention Center: +86 010-82951332
🆘 Life hotline: +86 400-821-1215

If you are having thoughts of harming yourself, please:
1. Call the hotline number above immediately
2. Contact a trusted family member or friend
3. Go to the nearest hospital emergency department

You don't have to face this alone. Professional help can help you get through this difficult time."""
        }
    
    def _retrieve_references(self, message, top_k=None):
        """
        检索与用户提问相关的知识片段。
        检索失败不应影响正常对话，因此异常一律吞掉并返回空列表。
        """
        try:
            return knowledge_service.retrieve(
                message, top_k=top_k or self.RAG_TOP_K
            )
        except Exception as e:
            if DEBUG:
                print(f"知识库检索失败: {e}")
            return []

    def _build_rag_prompt(self, base_prompt, references):
        """把检索到的知识拼进 system prompt。无引用时原样返回。"""
        if not references:
            return base_prompt

        context_text = knowledge_service.build_context(
            references, max_chars=self.RAG_MAX_CONTEXT_CHARS
        )
        if not context_text:
            return base_prompt

        return (
            f"{base_prompt}\n\n"
            "【参考资料】\n"
            "以下是从心理健康知识库中检索到的资料，请优先基于这些资料作答：\n\n"
            f"{context_text}\n\n"
            "【资料使用要求】\n"
            "1. 若资料与用户问题相关，请自然地融入回答，不要生硬罗列或直接复制原文\n"
            "2. 不要在回复正文中出现\"[资料1]\"这类标记，来源会单独展示给用户\n"
            "3. 若资料与用户问题无关，请忽略资料，按你自己的专业判断回答\n"
            "4. 不要编造资料中不存在的数据、结论或出处"
        )

    # ------------------------------------------------------------------
    # Function Calling
    # ------------------------------------------------------------------

    def _build_system_prompt(self, user_id=None, references=None, with_tools=False,
                             state=None):
        """组装 system prompt。

        启用 function calling 时不再预注入 RAG 资料（改由模型自己调
        knowledge_query），只追加工具使用规则。

        :param state: SessionState。传入时会追加当前阶段的角色指令与阶段进度，
                      这是不同阶段表现差异的主要来源。
        """
        prompt = self.system_prompt

        if user_id and user_id in self.user_profiles:
            profile = self.user_profiles[user_id]
            if profile['name']:
                prompt += (
                    f"\n\n【用户信息】\n- 姓名：{profile['name']}"
                    f"\n- 历史问题：{', '.join(profile['issues'][-3:])}"
                    f"\n- 互动次数：{profile['interaction_count']}"
                )

        if with_tools:
            prompt += self.tool_prompt

        # 阶段指令放在最后，优先级最高，可覆盖前面的通用风格约束
        if state is not None:
            prompt += "\n" + stage_policy.get_stage_prompt(
                state.stage, state=state, with_tools=with_tools
            )

        if with_tools:
            return prompt

        return self._build_rag_prompt(prompt, references)

    def _post_zhipu(self, payload):
        """带重试的智谱 API 调用，返回 response json；失败返回 None。"""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        for attempt in range(self.MAX_RETRY):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)

                if response.status_code == 200:
                    return response.json()
                if response.status_code == 429 or response.status_code >= 500:
                    if DEBUG:
                        print(f"[chat] status {response.status_code}, retry {attempt + 1}/{self.MAX_RETRY}")
                    time.sleep(self.RETRY_DELAY * (attempt + 1))
                    continue

                if DEBUG:
                    print(f"[chat] API error: {response.status_code} - {response.text}")
                return None

            except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
                if DEBUG:
                    print(f"[chat] request failed: {e}, retry {attempt + 1}/{self.MAX_RETRY}")
                time.sleep(self.RETRY_DELAY * (attempt + 1))
                continue

        return None

    def _normalize_history(self, context, limit=20):
        """把外部传入的历史消息规整成 API 需要的格式。"""
        messages = []
        if not context:
            return messages
        for msg in context[-limit:]:
            if isinstance(msg, dict) and msg.get('role') and msg.get('content'):
                messages.append({"role": msg['role'], "content": msg['content']})
        return messages

    def _run_with_tools(self, message, context, language, user_id, ctx=None, state=None):
        """
        function calling 主循环：
          请求模型 -> 若返回 tool_calls 则本地执行 -> 结果以 role=tool 回填 -> 再请求
        直到模型给出自然语言回复，或达到 MAX_TOOL_ROUNDS 上限。

        与阶段状态机协同：传入 state 时，system prompt 带上阶段指令，
        且 tools 只暴露该阶段白名单内的工具（如评估阶段不给 knowledge_query）。

        返回 (result_dict, ok)。ok=False 表示需要上层走兜底逻辑。
        """
        ctx = ctx or {}
        ctx.setdefault('user_id', user_id)

        messages = [{
            "role": "system",
            "content": self._build_system_prompt(user_id, with_tools=True, state=state),
        }]
        messages.extend(self._normalize_history(context))
        messages.append({"role": "user", "content": message})
        messages = self._truncate_context(messages, self.MAX_TOKENS - 800)

        # 按阶段裁剪工具集：不同阶段允许调用的工具不同
        stage = state.stage if state is not None else None
        if stage is not None:
            stage_tools = ai_tools.filter_tools(stage_policy.get_allowed_tools(stage))
            tool_choice = stage_policy.get_tool_choice(stage, state)
        else:
            stage_tools = ai_tools.TOOL_DEFINITIONS
            tool_choice = "auto"

        tool_trace = []      # 给前端看的工具调用轨迹
        references = []      # knowledge_query 命中的资料，单独透出
        crisis_flag = False
        need_human = False

        for round_index in range(MAX_TOOL_ROUNDS):
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.8,
                "max_tokens": 800,
                "tools": stage_tools,
                # 强制指定的 tool_choice 只在第一轮生效，
                # 否则模型会陷入反复调用同一工具的死循环
                "tool_choice": tool_choice if round_index == 0 else "auto",
            }

            result = self._post_zhipu(payload)
            if not result or not result.get("choices"):
                return None, False

            choice = result["choices"][0]
            assistant_msg = choice.get("message", {}) or {}
            tool_calls = assistant_msg.get("tool_calls") or []

            # 模型不再需要工具，产出最终回复
            if not tool_calls:
                content = (assistant_msg.get("content") or "").strip()
                if not content:
                    return None, False
                return {
                    "reply": content,
                    "confidence": 0.95,
                    "crisis_detected": crisis_flag,
                    "need_human_support": need_human,
                    "language": language,
                    "references": references,
                    "tool_calls": tool_trace,
                    "stage": stage,
                }, True

            # 把带 tool_calls 的 assistant 消息原样放回上下文，协议要求
            messages.append({
                "role": "assistant",
                "content": assistant_msg.get("content") or "",
                "tool_calls": tool_calls,
            })

            for call in tool_calls:
                fn = call.get("function", {}) or {}
                name = fn.get("name")
                raw_args = fn.get("arguments", "{}")

                executed = ai_tools.execute_tool(name, raw_args, ctx)

                # 收集副作用信息
                if name == "knowledge_query" and executed["status"] == "success":
                    items = (executed["result"] or {}).get("items") or []
                    for it in items:
                        if it not in references:
                            references.append(it)
                elif name == "analyze_emotion" and executed["status"] == "success":
                    if (executed["result"] or {}).get("crisisDetected"):
                        crisis_flag = True
                elif name == "trigger_warning" and executed["status"] == "success":
                    res = executed["result"] or {}
                    if res.get("riskLevel") == "high":
                        crisis_flag = True
                        need_human = True
                    elif res.get("needImmediateAttention"):
                        need_human = True

                tool_trace.append({
                    "name": executed["name"],
                    "arguments": executed["arguments"],
                    "result": executed["result"],
                    "status": executed["status"],
                    "durationMs": executed["durationMs"],
                })

                messages.append({
                    "role": "tool",
                    "tool_call_id": call.get("id"),
                    "content": json.dumps(executed["llm_content"], ensure_ascii=False),
                })

            if DEBUG:
                print(f"[chat] tool round {round_index + 1} done, calls={[t['name'] for t in tool_trace]}")

        # 轮数用尽仍未收敛：再要一次纯文本回复，禁用工具
        final = self._post_zhipu({
            "model": self.model,
            "messages": messages,
            "temperature": 0.8,
            "max_tokens": 800,
        })
        if final and final.get("choices"):
            content = (final["choices"][0].get("message", {}) or {}).get("content", "").strip()
            if content:
                return {
                    "reply": content,
                    "confidence": 0.9,
                    "crisis_detected": crisis_flag,
                    "need_human_support": need_human,
                    "language": language,
                    "references": references,
                    "tool_calls": tool_trace,
                    "stage": stage,
                }, True

        return None, False

    def _estimate_tokens(self, text):
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        other_chars = len(text) - chinese_chars
        return int(chinese_chars * 1.5 + other_chars * 0.5)
    
    def _truncate_context(self, messages, max_tokens):
        total_tokens = sum(self._estimate_tokens(msg.get('content', '')) for msg in messages)
        
        while total_tokens > max_tokens and len(messages) > 1:
            removed = messages.pop(1)
            total_tokens -= self._estimate_tokens(removed.get('content', ''))
        
        return messages
    
    def _handle_crisis(self, message, language, user_id, session_id=None, state=None):
        """
        关键词硬匹配命中的危机分支。

        这是不依赖模型判断的安全兜底：直接给干预话术，同时强制走一次
        trigger_warning 把预警落库，保证「模型没识别出来」时预警也不会漏。
        """
        executed = ai_tools.execute_tool(
            'trigger_warning',
            {'text': message, 'reason': '危机关键词硬匹配命中'},
            {'user_id': user_id, 'session_id': session_id},
        )

        # 同步状态机：标记预警已推送，重置平稳轮次
        if state is not None:
            result = executed.get('result') or {}
            if result.get('warningPushed'):
                state.warning_pushed = True
            state.calm_turns = 0

        return {
            'reply': self.crisis_response.get(language, self.crisis_response['zh']),
            'confidence': 1.0,
            'crisis_detected': True,
            'need_human_support': True,
            'language': language,
            'references': [],
            'tool_calls': [{
                'name': executed['name'],
                'arguments': executed['arguments'],
                'result': executed['result'],
                'status': executed['status'],
                'durationMs': executed['durationMs'],
            }],
            'stage': SessionStage.CRISIS,
        }

    def reply(self, message, context=None, user_id=None, language='auto',
              use_rag=True, session_id=None):
        return self.reply_with_context(
            message, context, user_id=user_id, language=language,
            use_rag=use_rag, session_id=session_id,
        )

    # ------------------------------------------------------------------
    # 会话阶段：对外查询与重置
    # ------------------------------------------------------------------

    def get_stage(self, user_id=None, session_id=None):
        """查询当前会话阶段。会话不存在时返回初始阶段快照。"""
        state = self.session_store.get(user_id=user_id, session_id=session_id)
        if state is None:
            return {
                'stage': SessionStage.ASSESSMENT,
                'stageLabel': SessionStage.label(SessionStage.ASSESSMENT),
                'stageDescription': SessionStage.description(SessionStage.ASSESSMENT),
                'stageTurns': 0,
                'totalTurns': 0,
                'crisisHistory': False,
                'exists': False,
            }
        data = state.debug_snapshot()
        data['exists'] = True
        return data

    def reset_stage(self, user_id=None, session_id=None):
        """重置会话阶段，回到评估阶段。用于「开启新对话」。"""
        self.session_store.purge_expired()
        return self.session_store.reset(user_id=user_id, session_id=session_id)

    def reply_with_context(self, message, context=None, user_id=None, language='auto',
                           use_rag=True, session_id=None):
        detected_language = self._detect_language(message) if language == 'auto' else language

        # ---- 1. 取出本会话的阶段状态，并按本轮输入决定进入哪个阶段 ----
        state = self.session_store.get_or_create(user_id=user_id, session_id=session_id)
        state.mark_turn()
        state.record_topic(self._extract_topic(message))

        keyword_crisis = self._detect_crisis(message, detected_language)
        target_stage, reason = stage_policy.decide_stage(
            state, message, crisis_detected=keyword_crisis
        )
        state.transit_to(target_stage, reason)

        if DEBUG:
            print(f"[chat] stage={state.stage} turns={state.stage_turns} reason={reason}")

        # ---- 2. 危机关键词硬匹配：最高优先级，不经过模型 ----
        if keyword_crisis:
            result = self._handle_crisis(
                message, detected_language, user_id, session_id, state=state
            )
            return self._finalize(result, state)

        if user_id:
            self._update_user_profile(user_id, message, detected_language)

        # 未命中危机的轮次要累计平稳计数，否则危机阶段永远无法降级
        if state.stage == SessionStage.CRISIS:
            state.calm_turns += 1

        # ---- 3. 无 key 时直接本地兜底 ----
        if not self.api_key:
            references = self._retrieve_references(message) if use_rag else []
            result = self._generate_local_response(
                message, detected_language, user_id, references
            )
            return self._finalize(result, state)

        # ---- 4. 主路径：带阶段约束的 function calling ----
        if ENABLE_FUNCTION_CALLING:
            try:
                result, ok = self._run_with_tools(
                    message, context, detected_language, user_id,
                    ctx={'user_id': user_id, 'session_id': session_id},
                    state=state,
                )
                if ok:
                    # 用工具结果回写状态，必要时纠正阶段（如情绪分析暴露危机）
                    final_stage, corrected = stage_policy.apply_post_turn_signals(
                        state, result.get('tool_calls'), result.get('crisis_detected')
                    )
                    if corrected:
                        # 阶段被纠正为危机：追加标准干预话术，保证热线一定出现
                        result = self._escalate_to_crisis(result, detected_language)
                        if DEBUG:
                            print(f"[chat] 阶段纠正 -> {final_stage}: {corrected}")
                    return self._finalize(result, state)
                if DEBUG:
                    print("[chat] function calling 未产出有效回复，降级到普通模式")
            except Exception as e:
                if DEBUG:
                    print(f"[chat] function calling 异常，降级: {e}")

        # ---- 5. 降级路径：旧的「预检索 RAG + 普通对话」 ----
        references = self._retrieve_references(message) if use_rag else []
        try:
            result = self._call_zhipu_api_with_context(
                message, context, detected_language, user_id, references, state=state
            )
        except Exception as e:
            if DEBUG:
                print(f"智谱AI调用失败: {e}")
            result = self._generate_local_response(
                message, detected_language, user_id, references
            )
        return self._finalize(result, state)

    def _extract_topic(self, message):
        """从用户输入里粗提一个议题词，用于阶段进度提示，避免模型重复提问。

        只做关键词命中，不引入额外依赖；提不出来就返回 None。
        """
        topic_keywords = {
            '学业': ['学习', '考试', '成绩', '论文', '作业', '毕业', '升学'],
            '工作': ['工作', '上班', '职场', '同事', '领导', '加班', '裁员', '面试'],
            '人际': ['朋友', '同学', '室友', '社交', '孤独', '被孤立', '人际'],
            '家庭': ['父母', '家人', '家庭', '爸妈', '亲戚'],
            '情感': ['恋爱', '分手', '女友', '男友', '感情', '暗恋', '失恋'],
            '睡眠': ['失眠', '睡不着', '睡眠', '噩梦', '早醒'],
            '情绪': ['焦虑', '抑郁', '难过', '低落', '烦躁', '恐慌', '压力'],
            '身体': ['头痛', '胃疼', '心慌', '没胃口', '身体'],
        }
        for topic, words in topic_keywords.items():
            if any(w in message for w in words):
                return topic
        return None

    def _escalate_to_crisis(self, result, language):
        """模型回复完成后才发现是危机：在其回复后追加标准干预信息。

        不直接丢弃模型回复（它通常已有共情内容），而是补上热线与求助路径，
        保证危机场景下用户一定能拿到可操作的求助方式。
        """
        crisis_text = self.crisis_response.get(language, self.crisis_response['zh'])
        original = (result.get('reply') or '').strip()

        # 模型回复里已经带了热线号码就不重复追加
        if '400-161-9995' not in original:
            result['reply'] = f"{original}\n\n{crisis_text}" if original else crisis_text

        result['crisis_detected'] = True
        result['need_human_support'] = True
        result['confidence'] = 1.0
        return result

    def _finalize(self, result, state):
        """统一出口：把阶段快照写进返回结构，供前端展示「当前阶段」。"""
        if not isinstance(result, dict):
            return result

        result['stage'] = state.stage
        result['stageLabel'] = SessionStage.label(state.stage)
        result['stageDescription'] = SessionStage.description(state.stage)
        result['stageTurns'] = state.stage_turns
        result['totalTurns'] = state.total_turns

        # 本轮是否发生了阶段切换，前端据此决定要不要弹提示。
        # 首轮（新建会话）也视为一次「进入评估阶段」的变化，让前端能弹出阶段提示。
        is_first_turn = (state.total_turns <= 1) and (not state.history)
        result['stageChanged'] = state.stage_changed_this_turn or is_first_turn
        if (state.stage_changed_this_turn or is_first_turn) and state.history:
            result['stageChangeReason'] = state.history[-1].get('reason', '')

        return result
    
    def _detect_language(self, text):
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        return 'zh' if chinese_chars > len(text) * 0.3 else 'en'
    
    def _detect_crisis(self, message, language):
        lang = 'zh' if language not in ['zh', 'en'] else language
        message_lower = message.lower()
        for keyword in self.crisis_keywords.get(lang, []):
            if keyword in message_lower:
                return True
        return False
    
    def _update_user_profile(self, user_id, message, language):
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                'language': language,
                'name': None,
                'issues': [],
                'preferences': {},
                'interaction_count': 0,
                'last_interaction': None
            }
        
        profile = self.user_profiles[user_id]
        profile['interaction_count'] += 1
        profile['last_interaction'] = message
        
        if '我叫' in message or '我的名字是' in message:
            import re
            match = re.search(r'(我叫|我的名字是)(.*)', message)
            if match:
                profile['name'] = match.group(2).strip()
        
        profile['issues'].append(message[:100])
        if len(profile['issues']) > 10:
            profile['issues'] = profile['issues'][-10:]
    
    def _call_zhipu_api_with_context(self, message, context, language='zh', user_id=None,
                                     references=None, state=None):
        url = f"{self.base_url}/chat/completions"
        
        messages = []
        
        personalized_prompt = self.system_prompt
        if user_id and user_id in self.user_profiles:
            profile = self.user_profiles[user_id]
            if profile['name']:
                personalized_prompt += f"\n\n【用户信息】\n- 姓名：{profile['name']}\n- 历史问题：{', '.join(profile['issues'][-3:])}\n- 互动次数：{profile['interaction_count']}"
        
        personalized_prompt = self._build_rag_prompt(personalized_prompt, references)

        # 降级路径同样带上阶段指令，保证阶段体验一致
        if state is not None:
            personalized_prompt += "\n" + stage_policy.get_stage_prompt(
                state.stage, state=state, with_tools=False
            )
        
        messages.append({"role": "system", "content": personalized_prompt})
        
        if context:
            for msg in context[-20:]:
                if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                    messages.append({"role": msg['role'], "content": msg['content']})
        
        messages.append({"role": "user", "content": message})
        
        messages = self._truncate_context(messages, self.MAX_TOKENS - 500)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.8,
            "max_tokens": 500
        }
        
        for attempt in range(self.MAX_RETRY):
            try:
                response = requests.post(url, headers=headers, json=data, timeout=60)
                
                if response.status_code == 200:
                    result = response.json()
                    if "choices" in result and len(result["choices"]) > 0:
                        content = result["choices"][0]["message"]["content"]
                        return {
                            "reply": content,
                            "confidence": 0.95,
                            "crisis_detected": False,
                            "language": language,
                            "references": references or [],
                            "tool_calls": []
                        }
                elif response.status_code == 429:
                    if DEBUG:
                        print(f"Rate limited, retrying... (attempt {attempt + 1}/{self.MAX_RETRY})")
                    time.sleep(self.RETRY_DELAY * (attempt + 1))
                    continue
                elif response.status_code >= 500:
                    if DEBUG:
                        print(f"Server error {response.status_code}, retrying... (attempt {attempt + 1}/{self.MAX_RETRY})")
                    time.sleep(self.RETRY_DELAY * (attempt + 1))
                    continue
                else:
                    if DEBUG:
                        print(f"API error: {response.status_code} - {response.text}")
                    break
                    
            except requests.exceptions.Timeout:
                if DEBUG:
                    print(f"Request timeout, retrying... (attempt {attempt + 1}/{self.MAX_RETRY})")
                time.sleep(self.RETRY_DELAY * (attempt + 1))
                continue
            except requests.exceptions.RequestException as e:
                if DEBUG:
                    print(f"Request error: {e}, retrying... (attempt {attempt + 1}/{self.MAX_RETRY})")
                time.sleep(self.RETRY_DELAY * (attempt + 1))
                continue
        
        return self._generate_local_response(message, language, user_id, references)
    
    def _generate_local_response(self, message, language='zh', user_id=None, references=None):
        """本地兜底回复。统一在出口处补上 references，避免逐个分支修改。"""
        result = self._local_response_body(message, language, user_id)
        result.setdefault('crisis_detected', False)
        result['references'] = references or []
        result.setdefault('tool_calls', [])
        return result

    def _local_response_body(self, message, language='zh', user_id=None):
        message_lower = message.lower()
        lang = 'zh' if language not in ['zh', 'en'] else language
        
        # 个性化问候
        if any(word in message_lower for word in ['你好', 'hi', 'hello', '嗨', '在吗']):
            if user_id and user_id in self.user_profiles and self.user_profiles[user_id]['name']:
                name = self.user_profiles[user_id]['name']
                if lang == 'zh':
                    return {
                        'reply': f"你好呀，{name}！我是小安，很高兴见到你。今天想聊点什么？",
                        'confidence': 0.9,
                        'language': lang
                    }
                else:
                    return {
                        'reply': f"Hello, {name}! I'm Xiao An, nice to meet you. What would you like to talk about today?",
                        'confidence': 0.9,
                        'language': lang
                    }
            else:
                if lang == 'zh':
                    return {
                        'reply': "你好呀！我是小安，很高兴见到你。今天想聊点什么？",
                        'confidence': 0.9,
                        'language': lang
                    }
                else:
                    return {
                        'reply': "Hello! I'm Xiao An, nice to meet you. What would you like to talk about today?",
                        'confidence': 0.9,
                        'language': lang
                    }
        
        if any(word in message_lower for word in ['谢谢', '感谢', 'thank']):
            if lang == 'zh':
                return {
                    'reply': "不客气，能帮到你我很开心。有需要随时找我。",
                    'confidence': 0.9,
                    'language': lang
                }
            else:
                return {
                    'reply': "You're welcome! I'm glad I could help. Feel free to reach out anytime.",
                    'confidence': 0.9,
                    'language': lang
                }
        
        if any(word in message_lower for word in ['难过', '悲伤', '伤心', '不开心', '郁闷', '哭', 'sad', 'grief', 'heartbroken']):
            if lang == 'zh':
                return {
                    'reply': "听起来你现在心里很难受。愿意和我说说发生了什么吗？有时候把事情说出来会好受一些。",
                    'confidence': 0.85,
                    'language': lang
                }
            else:
                return {
                    'reply': "It sounds like you're feeling really upset right now. Would you like to talk about what happened? Sometimes sharing your feelings can help you feel better.",
                    'confidence': 0.85,
                    'language': lang
                }
        
        if any(word in message_lower for word in ['焦虑', '紧张', '担心', '害怕', '恐惧', '不安', 'anxious', 'nervous', 'worried', 'afraid']):
            if lang == 'zh':
                return {
                    'reply': "焦虑的感觉确实不好受。你可以试试深呼吸：慢慢吸气4秒，屏住呼吸4秒，再慢慢呼气4秒。这样做几次，看看会不会好一点？",
                    'confidence': 0.85,
                    'language': lang
                }
            else:
                return {
                    'reply': "Anxiety can be really uncomfortable. You can try deep breathing: slowly inhale for 4 seconds, hold for 4 seconds, then slowly exhale for 4 seconds. Do this a few times and see if you feel better?",
                    'confidence': 0.85,
                    'language': lang
                }
        
        if any(word in message_lower for word in ['压力', '累', '疲惫', '倦怠', '撑不住', 'stress', 'tired', 'exhausted', 'burnout']):
            if lang == 'zh':
                return {
                    'reply': "你承担了很多，辛苦了。记得给自己留点休息的时间，这不是偷懒，是为了更好地前行。有什么具体让你感到压力的事吗？",
                    'confidence': 0.8,
                    'language': lang
                }
            else:
                return {
                    'reply': "You're carrying a lot, and that's hard. Remember to give yourself time to rest—it's not laziness, it's necessary for your well-being. Is there something specific that's causing you stress?",
                    'confidence': 0.8,
                    'language': lang
                }
        
        if any(word in message_lower for word in ['孤独', '寂寞', '没人理解', '一个人', 'lonely', 'alone', 'no one understands']):
            if lang == 'zh':
                return {
                    'reply': "孤独的感觉真的很沉重。虽然我只是一个AI，但我在这里陪着你。你愿意和我分享更多吗？",
                    'confidence': 0.8,
                    'language': lang
                }
            else:
                return {
                    'reply': "Loneliness can feel really heavy. Even though I'm just an AI, I'm here with you. Would you like to share more?",
                    'confidence': 0.8,
                    'language': lang
                }
        
        if any(word in message_lower for word in ['失眠', '睡不着', '睡眠', '做噩梦', 'insomnia', 'can\'t sleep', 'sleep', 'nightmares']):
            if lang == 'zh':
                return {
                    'reply': "睡眠问题确实会影响心情。睡前可以试试：放下手机、喝杯温牛奶、听些轻音乐。如果长期失眠，建议咨询一下专业医生。",
                    'confidence': 0.8,
                    'language': lang
                }
            else:
                return {
                    'reply': "Sleep problems can really affect your mood. Before bed, you can try: putting away your phone, drinking a warm glass of milk, or listening to soft music. If you have chronic insomnia, it's a good idea to consult a professional doctor.",
                    'confidence': 0.8,
                    'language': lang
                }
        
        if lang == 'zh':
            return {
                'reply': "我在听，你愿意多说一些吗？",
                'confidence': 0.7,
                'language': lang
            }
        else:
            return {
                'reply': "I'm listening. Would you like to share more?",
                'confidence': 0.7,
                'language': lang
            }
