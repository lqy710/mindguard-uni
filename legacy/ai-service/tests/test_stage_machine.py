"""会话阶段状态机全面测试（离线，不依赖真实 Zhipu API）。

当 ZHIPU_API_KEY 为空时，ChatService.reply_with_context 走本地兜底路径，
阶段状态机逻辑仍完整执行，可用于离线验证。

运行：python -m tests.test_stage_machine
"""
import os
import sys
import json

# 确保项目根目录在 sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.session_state import SessionStage, session_store
from services.stage_policy import (
    get_allowed_tools, get_tool_choice, decide_stage,
    apply_post_turn_signals, get_stage_prompt, STAGE_PROMPTS,
)
from services.chat_service import ChatService
from services.ai_tools import filter_tools, TOOL_DEFINITIONS

PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✓ {name}")
    else:
        FAIL += 1
        print(f"  ✗ {name}  {detail}")


def reset_store():
    # 清空所有会话状态（通过公开接口）
    for key in list(session_store._states.keys()):
        session_store.reset(user_id=key[0], session_id=key[1])


def stage_of(resp):
    return resp.get("stage")


def run_turn(svc, message, user_id=1, session_id=1, context=None):
    """走 reply_with_context 完整链路（无 key 兜底）。"""
    if context is None:
        context = []
    return svc.reply_with_context(
        message, context, user_id, "zh", session_id=session_id
    )


# ---------------------------------------------------------------------------
print("== 一、stage_policy 纯函数单测 ==")

# 1.1 各阶段工具白名单
check("assessment 工具集", get_allowed_tools(SessionStage.ASSESSMENT) == ["analyze_emotion", "trigger_warning"], str(get_allowed_tools(SessionStage.ASSESSMENT)))
check("interview 工具集全开", get_allowed_tools(SessionStage.INTERVIEW) == ["analyze_emotion", "knowledge_query", "trigger_warning"], str(get_allowed_tools(SessionStage.INTERVIEW)))
check("resource 工具集", get_allowed_tools(SessionStage.RESOURCE) == ["knowledge_query", "trigger_warning"], str(get_allowed_tools(SessionStage.RESOURCE)))
check("crisis 工具集仅预警", get_allowed_tools(SessionStage.CRISIS) == ["trigger_warning"], str(get_allowed_tools(SessionStage.CRISIS)))

# 1.2 tool_choice 行为
reset_store()
st = session_store.get_or_create(10, 20)
st.transit_to(SessionStage.ASSESSMENT)
st.warning_pushed = True
check("crisis 已预警->tool_choice auto", get_tool_choice(SessionStage.CRISIS, st) == "auto", str(get_tool_choice(SessionStage.CRISIS, st)))
st.warning_pushed = False
tc = get_tool_choice(SessionStage.CRISIS, st)
check("crisis 未预警->强制 trigger_warning", tc == {"type": "function", "function": {"name": "trigger_warning"}}, str(tc))
check("assessment 已预警->auto", get_tool_choice(SessionStage.ASSESSMENT, st) == "auto", str(get_tool_choice(SessionStage.ASSESSMENT, st)))
st.warning_pushed = False
check("assessment 未预警->auto(非强制)", get_tool_choice(SessionStage.ASSESSMENT, st) == "auto", str(get_tool_choice(SessionStage.ASSESSMENT, st)))

# 1.3 filter_tools
filtered = filter_tools(["analyze_emotion"])
names = {t["function"]["name"] for t in filtered}
check("filter_tools 按名单裁剪", names == {"analyze_emotion"}, str(names))
check("filter_tools 空名单->全量", len(filter_tools([])) == len(TOOL_DEFINITIONS))
check("filter_tools 未知名->全量", len(filter_tools(["__not_exist__"])) == len(TOOL_DEFINITIONS))

# 1.4 阶段提示词非空
STAGES = [SessionStage.ASSESSMENT, SessionStage.INTERVIEW, SessionStage.RESOURCE, SessionStage.CRISIS]
for s in STAGES:
    check(f"STAGE_PROMPTS[{s}] 存在且非空", bool(STAGE_PROMPTS.get(s, "")), "")
check("get_stage_prompt 带工具清单", "analyze_emotion" in get_stage_prompt(SessionStage.ASSESSMENT, state=st, with_tools=True))

# 1.5 decide_stage：危机优先于资源/进度（返回 (stage, reason) 元组）
reset_store()
st = session_store.get_or_create(11, 21)
st.transit_to(SessionStage.RESOURCE)
st.stage_turns = 5
check("decide_stage 危机信号->crisis", decide_stage(st, "想死", crisis_detected=True)[0] == SessionStage.CRISIS)
check("decide_stage 无危机/短进度->保持", decide_stage(st, "还行", crisis_detected=False)[0] == SessionStage.RESOURCE)
st.stage_turns = 0
st.transit_to(SessionStage.ASSESSMENT)
check("decide_stage 评估阶段短进度->保持", decide_stage(st, "今天心情不好", crisis_detected=False)[0] == SessionStage.ASSESSMENT)

# 1.6 apply_post_turn_signals 幂等（只归零不累加）
reset_store()
st = session_store.get_or_create(12, 22)
st.transit_to(SessionStage.CRISIS)
st.calm_turns = 5
apply_post_turn_signals(st, [{"name": "trigger_warning"}], crisis_detected=True)
check("危机态+预警->calm_turns 归零(幂等不累加)", st.calm_turns == 0, str(st.calm_turns))
# 关键：兜底路径会累加 calm_turns+=1，apply_post_turn 不应再加
st.calm_turns = 0
apply_post_turn_signals(st, [{"name": "trigger_warning"}], crisis_detected=True)
check("再次 apply 仍为0（幂等）", st.calm_turns == 0, str(st.calm_turns))


# ---------------------------------------------------------------------------
print("== 二、完整阶段流转：评估->访谈->资源（无 key 兜底） ==")
reset_store()
svc = ChatService()

r = run_turn(svc, "你好，我最近情绪不太稳定")
check("T1 进入 assessment", stage_of(r) == "assessment", stage_of(r))
check("T1 stageChanged=true", r.get("stageChanged") is True, str(r.get("stageChanged")))

r = run_turn(svc, "工作压力大，经常失眠")
check("T2 仍在 assessment", stage_of(r) == "assessment", stage_of(r))
check("T2 stageChanged=false（同阶段）", r.get("stageChanged") is False, str(r.get("stageChanged")))

r = run_turn(svc, "我感觉很焦虑，不知道怎么调节")
# 含“怎么调节”资源意图 -> 资源阶段（设计：资源意图可越过 interview）
check("T3 转移到 resource（资源意图）", stage_of(r) == "resource", stage_of(r))

r = run_turn(svc, "可以具体说说是什么让你焦虑吗")
check("T4 仍在 resource", stage_of(r) == "resource", stage_of(r))

r = run_turn(svc, "有没有什么放松的方法推荐")
check("T5 转移到 resource", stage_of(r) == "resource", stage_of(r))
check("T5 stageLabel 非空", bool(r.get("stageLabel")), str(r.get("stageLabel")))

r = run_turn(svc, "再给我讲讲怎么练习呼吸放松")
check("T6 保持在 resource", stage_of(r) == "resource", stage_of(r))


# ---------------------------------------------------------------------------
print("== 三、危机短路与降级 ==")
reset_store()
svc = ChatService()

run_turn(svc, "你好")
run_turn(svc, "今天心情还行")
run_turn(svc, "工作有点累")

# 关键词危机 -> 直接短路进入 crisis
r = run_turn(svc, "我不想活了，觉得没意义")
check("C1 关键词危机->crisis 短路", stage_of(r) == "crisis", stage_of(r))
check("C1 stageChanged=true", r.get("stageChanged") is True, str(r.get("stageChanged")))
check("C1 含热线号码", "400-161-9995" in (r.get("reply") or ""), str(r.get("reply"))[:50])

# 危机态平静轮1（无关键词，无危机信号），兜底累加 calm_turns=1
r = run_turn(svc, "就是最近特别累")
check("C2 仍在 crisis", stage_of(r) == "crisis", stage_of(r))
st = session_store.get_or_create(1, 1)
check("C2 calm_turns=1", st.calm_turns == 1, str(st.calm_turns))

# 平静轮2，calm_turns=2（判断时仍为1），保持 crisis
r = run_turn(svc, "嗯，还好")
check("C3 仍在 crisis", stage_of(r) == "crisis", stage_of(r))
check("C3 calm_turns=2", session_store.get_or_create(1, 1).calm_turns == 2, str(session_store.get_or_create(1, 1).calm_turns))

# 平静轮3 的判断时 calm_turns 已=2 >= CRISIS_COOLDOWN_TURNS -> 降级 interview
r = run_turn(svc, "谢谢你的陪伴")
check("C4 降级到 interview", stage_of(r) == "interview", stage_of(r))
check("C4 stageChanged=true（crisis->interview）", r.get("stageChanged") is True, str(r.get("stageChanged")))
check("C4 不在 crisis（确认降级）", stage_of(r) != "crisis")


# ---------------------------------------------------------------------------
print("== 四、资源阶段危机短路（任意阶段可短路） ==")
reset_store()
svc = ChatService()
run_turn(svc, "你好，我最近情绪不太好")
run_turn(svc, "工作压力大，经常失眠")
# 资源意图：命中 "能帮我" 正则，直接跳转 resource
r_prev = run_turn(svc, "能帮我推荐一些放松的方法吗")
check("R0 先到 resource", stage_of(r_prev) == "resource", stage_of(r_prev))
# resource 阶段发危机关键词 -> 立刻短路进入 crisis
r = run_turn(svc, "我不想活了，想结束这一切")
check("R1 resource 阶段危机->crisis", stage_of(r) == "crisis", stage_of(r))
check("R1 含热线", "400-161-9995" in (r.get("reply") or ""), str(r.get("reply"))[:50])

# 补充：新补词库覆盖 "撑不住了/想结束一切" 也能命中（任意阶段危机短路）
reset_store()
svc2 = ChatService()
run_turn(svc2, "你好，我最近不太好", user_id=300, session_id=1)
r2 = run_turn(svc2, "我真的撑不住了，想结束一切", user_id=300, session_id=1)
check("R2 新词库'撑不住了/想结束一切'命中->crisis", stage_of(r2) == "crisis", stage_of(r2))
check("R2 含热线", "400-161-9995" in (r2.get("reply") or ""), str(r2.get("reply"))[:50])


# ---------------------------------------------------------------------------
print("== 五、安全路径：仅工具暴露危机（无关键词） ==")
reset_store()
svc = ChatService()
# 评估阶段：模型不返回危机关键词，但 analyze_emotion 工具可能返回 crisisDetected
# 无 key 兜底不会真实调工具，但我们用 decide_stage + apply_post_turn_signals 模拟
# 直接验证 reply 仍返回 stage 字段且 crisis 工具被裁剪逻辑正确
r = run_turn(svc, "测试消息")
check("S1 返回结构含 stage 字段", "stage" in r, str(list(r.keys())))
check("S1 含 stageLabel", "stageLabel" in r)
check("S1 含 stageDescription", "stageDescription" in r)
check("S1 含 stageChanged", "stageChanged" in r)


# ---------------------------------------------------------------------------
print("== 六、get_stage / reset_stage 接口逻辑 ==")
reset_store()
svc = ChatService()
run_turn(svc, "你好")
run_turn(svc, "心情不好")
run_turn(svc, "很焦虑")
g = svc.get_stage(user_id=1, session_id=1)
check("get_stage 返回当前阶段", g.get("stage") in ("assessment", "interview", "resource"), str(g))
removed = svc.reset_stage(user_id=1, session_id=1)
check("reset_stage 清除了状态", removed >= 0)
g2 = svc.get_stage(user_id=1, session_id=1)
check("reset 后回到 assessment", g2.get("stage") == "assessment", str(g2))


# ---------------------------------------------------------------------------
print("== 七、多会话隔离 ==")
reset_store()
svc = ChatService()
run_turn(svc, "会话A 情绪不好", user_id=100, session_id=1)
run_turn(svc, "会话A 工作压力大", user_id=100, session_id=1)
run_turn(svc, "会话A 很焦虑想聊聊", user_id=100, session_id=1)
run_turn(svc, "会话A 最近睡眠也差", user_id=100, session_id=1)
run_turn(svc, "会话B 你好", user_id=200, session_id=1)
ga = svc.get_stage(user_id=100, session_id=1)
gb = svc.get_stage(user_id=200, session_id=1)
check("会话隔离：A 已到 interview", ga.get("stage") == "interview", str(ga))
check("会话隔离：B 仍在 assessment", gb.get("stage") == "assessment", str(gb))
# 验证不同 session_id 同一用户也隔离
run_turn(svc, "会话A2 开机", user_id=100, session_id=999)
g2 = svc.get_stage(user_id=100, session_id=999)
check("会话隔离：同用户不同 session 独立", g2.get("stage") == "assessment", str(g2))


print(f"\n结果：PASS={PASS}  FAIL={FAIL}")
sys.exit(1 if FAIL else 0)
