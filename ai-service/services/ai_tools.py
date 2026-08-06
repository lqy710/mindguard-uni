"""
GLM Function Calling 工具集。

把已有的领域能力包装成智谱开放平台 tool 协议可用的函数：
  - analyze_emotion  -> EmotionService.analyze
  - knowledge_query  -> knowledge_service.retrieve（会话1 的 RAG 检索）
  - trigger_warning  -> RiskService.quick_assess + 回调 Java 后端写入 warning

设计要点：
1. TOOL_DEFINITIONS 是喂给模型的 schema，只描述「做什么」和「什么时候用」，
   不暴露内部实现细节。
2. execute_tool() 是统一分发入口，保证任何工具异常都不会把整条对话打挂，
   而是返回结构化的错误给模型，让模型自己决定怎么兜底。
3. 每个工具都返回两份数据：
   - llm_content：喂回模型的精简文本/JSON，控制 token
   - raw：完整结果，透传给前端展示
"""

import json
import time

import requests

import config
from services.emotion_analysis import EmotionService
from services.risk_assessment import RiskService
from services.knowledge_service import knowledge_service

emotion_service = EmotionService()
risk_service = RiskService()


# ---------------------------------------------------------------- 工具 schema

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "analyze_emotion",
            "description": (
                "分析一段中文或英文文本的情绪状态，返回情绪极性分值、情绪类型、"
                "情绪关键词以及是否存在心理危机信号。"
                "当用户在倾诉心情、描述自身感受，或你需要判断用户当前情绪强度时调用。"
                "不要用它来回答知识性问题。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "需要做情绪分析的原始文本，通常是用户最近一条消息的完整内容。",
                    }
                },
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "knowledge_query",
            "description": (
                "在心理健康知识库中做语义检索，返回最相关的科普文章片段。"
                "当用户询问某个心理学概念、症状表现、调节方法、疾病知识，"
                "或你需要基于权威资料给出建议时调用。"
                "纯情绪陪伴、闲聊、问候不需要调用。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "检索用的查询语句。应当是提炼后的核心问题，而不是照抄用户原句。",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "返回的文章片段数量，默认 3，最大 5。",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_warning",
            "description": (
                "对用户当前状态做风险评估，并在命中危机/高风险时向平台心理老师推送预警。"
                "当用户表达自杀、自伤念头，提到具体轻生计划，表现出强烈绝望感，"
                "或流露出伤害他人的意图时，必须调用此工具。"
                "这是一个会产生真实干预动作的工具，普通的情绪低落、压力大不要调用。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "触发预警判断的用户原始文本，用于风险研判和留档。",
                    },
                    "reason": {
                        "type": "string",
                        "description": "你判断需要预警的简要理由，例如「用户明确表达自杀意图并提到具体方式」。",
                    },
                },
                "required": ["text"],
            },
        },
    },
]

# ---------------------------------------------------------------- 工具实现


def _tool_analyze_emotion(args, ctx):
    text = (args.get("text") or "").strip()
    if not text:
        return {"error": "text 不能为空"}, {"error": "text 不能为空"}

    result = emotion_service.analyze(text)

    raw = {
        "sentimentScore": result.get("sentiment_score"),
        "emotionType": result.get("emotion_type"),
        "emotions": result.get("emotions", []),
        "keywords": result.get("keywords", []),
        "crisisDetected": bool(result.get("crisis_detected")),
        "recommendation": result.get("recommendation"),
    }

    # 喂回模型的内容去掉冗余字段，只保留决策所需信息
    llm_content = {
        "sentiment_score": raw["sentimentScore"],
        "emotion_type": raw["emotionType"],
        "emotions": raw["emotions"][:5],
        "keywords": raw["keywords"][:5],
        "crisis_detected": raw["crisisDetected"],
    }
    return llm_content, raw


def _tool_knowledge_query(args, ctx):
    query = (args.get("query") or "").strip()
    if not query:
        return {"error": "query 不能为空"}, {"error": "query 不能为空"}

    try:
        top_k = int(args.get("top_k") or 3)
    except (TypeError, ValueError):
        top_k = 3
    top_k = max(1, min(top_k, 5))

    # 会话1 已实现：返回 [{articleId,title,category,snippet,score}]
    items = knowledge_service.retrieve(query, top_k=top_k) or []

    if not items:
        return (
            {"found": 0, "message": "知识库中没有检索到相关内容，请基于你自己的专业知识回答。"},
            {"query": query, "items": []},
        )

    llm_content = {
        "found": len(items),
        "passages": [
            {
                "title": it.get("title"),
                "category": it.get("category"),
                "content": it.get("snippet"),
            }
            for it in items
        ],
    }
    raw = {"query": query, "items": items}
    return llm_content, raw


def _push_warning_to_backend(payload):
    """回调 Java 后端写入 warning 表并推送给心理老师。

    失败不抛异常：预警推送失败不应该让用户拿不到 AI 回复，
    但必须把失败状态透传出去，方便前端与日志排查。
    """
    url = f"{config.BACKEND_BASE_URL.rstrip('/')}/api/internal/warning"
    try:
        resp = requests.post(
            url,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "X-Internal-Token": config.INTERNAL_API_TOKEN,
            },
            timeout=config.TOOL_TIMEOUT,
        )
        if resp.status_code != 200:
            return {"pushed": False, "error": f"backend status {resp.status_code}"}
        body = resp.json()
        if body.get("code") != 200:
            return {"pushed": False, "error": body.get("message", "backend rejected")}
        data = body.get("data") or {}
        return {"pushed": True, "warningId": data.get("warningId")}
    except Exception as exc:  # noqa: BLE001 - 网络异常统一降级
        return {"pushed": False, "error": str(exc)}


def _tool_trigger_warning(args, ctx):
    text = (args.get("text") or "").strip()
    reason = (args.get("reason") or "").strip()
    if not text:
        return {"error": "text 不能为空"}, {"error": "text 不能为空"}

    # 复用既有规则引擎做风险定级，不让模型自己拍板等级
    assessment = risk_service.quick_assess(text)
    risk_level = assessment.get("risk_level", "low")
    need_attention = bool(assessment.get("need_immediate_attention"))

    user_id = ctx.get("user_id")
    push_result = {"pushed": False, "error": None}

    # 只有 medium 及以上才真正落库，避免误报刷屏心理老师工作台
    should_push = risk_level in ("high", "medium")
    if should_push and user_id:
        push_result = _push_warning_to_backend(
            {
                "userId": user_id,
                "riskLevel": risk_level,
                "triggerSource": "ai_chat",
                "triggerContent": text[:500],
                "reason": reason or assessment.get("recommendation", ""),
                "sessionId": ctx.get("session_id"),
            }
        )
    elif should_push and not user_id:
        push_result = {"pushed": False, "error": "missing userId, warning not persisted"}

    raw = {
        "riskLevel": risk_level,
        "needImmediateAttention": need_attention,
        "recommendation": assessment.get("recommendation"),
        "reason": reason,
        "warningPushed": push_result.get("pushed", False),
        "warningId": push_result.get("warningId"),
        "pushError": push_result.get("error"),
    }

    # 明确告诉模型「已经做了什么」，避免它再编造一遍干预动作
    llm_content = {
        "risk_level": risk_level,
        "need_immediate_attention": need_attention,
        "warning_pushed": raw["warningPushed"],
        "hotline": "400-161-9995",
        "guidance": (
            "已通知平台心理老师介入。请用温和、不评判的语气回应用户，"
            "肯定他愿意说出来的勇气，明确告知求助热线 400-161-9995，"
            "并鼓励他联系身边可信任的人。不要说教，不要罗列条目。"
            if raw["warningPushed"]
            else "请用温和、共情的语气回应，并主动提供求助热线 400-161-9995。"
        ),
    }
    return llm_content, raw


_TOOL_IMPL = {
    "analyze_emotion": _tool_analyze_emotion,
    "knowledge_query": _tool_knowledge_query,
    "trigger_warning": _tool_trigger_warning,
}


# ---------------------------------------------------------------- 阶段裁剪


def filter_tools(allowed_names):
    """按名单裁剪 TOOL_DEFINITIONS，供会话阶段状态机按阶段限定工具集。

    传空或 None 表示不裁剪，返回全量定义。名单中的未知工具名会被忽略，
    裁剪后为空时同样回退到全量，避免把 tools 字段传成空数组导致请求异常。
    """
    if not allowed_names:
        return TOOL_DEFINITIONS

    allowed = set(allowed_names)
    subset = [
        t for t in TOOL_DEFINITIONS
        if (t.get("function") or {}).get("name") in allowed
    ]
    return subset or TOOL_DEFINITIONS


# ---------------------------------------------------------------- 分发入口


def execute_tool(name, arguments, ctx=None):
    """执行单个工具调用。

    :param name: 工具名
    :param arguments: 模型给出的参数，可能是 dict 或 JSON 字符串
    :param ctx: 运行时上下文，含 user_id / session_id 等模型不该感知的信息
    :return: dict —— name / arguments / llm_content / result / status / durationMs
    """
    ctx = ctx or {}
    started = time.time()

    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments) if arguments.strip() else {}
        except json.JSONDecodeError:
            arguments = {}
    if not isinstance(arguments, dict):
        arguments = {}

    impl = _TOOL_IMPL.get(name)
    if impl is None:
        err = {"error": f"未知工具: {name}"}
        return {
            "name": name,
            "arguments": arguments,
            "llm_content": err,
            "result": err,
            "status": "error",
            "durationMs": 0,
        }

    try:
        llm_content, raw = impl(arguments, ctx)
        status = "error" if isinstance(raw, dict) and raw.get("error") else "success"
    except Exception as exc:  # noqa: BLE001 - 任何工具异常都降级，不影响主流程
        print(f"[ai_tools] tool {name} failed: {exc}")
        llm_content = {"error": f"工具执行失败: {exc}"}
        raw = {"error": str(exc)}
        status = "error"

    return {
        "name": name,
        "arguments": arguments,
        "llm_content": llm_content,
        "result": raw,
        "status": status,
        "durationMs": int((time.time() - started) * 1000),
    }
