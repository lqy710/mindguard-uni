"""MindGuard AI 离线评估脚本。

对 ai-service 中真实存在的三条判定链路做离线评估，输出可复现的数字：

1. 首轮命中率  —— stage_policy.decide_stage() 在「会话第一轮」是否把用户
                   路由到了正确的阶段（危机句 → crisis，索取方法 → resource，
                   其余 → assessment）。首轮路由错，后面整段对话都是错的，
                   所以这是最能代表「首轮命中」的可测量代理指标。
2. 情绪识别准确率 —— EmotionService.analyze() 输出的 emotion_type 与人工标注
                   标签（positive / negative / neutral / crisis）的一致率。
3. 危机召回率   —— EmotionService 的危机判定对危机样本的召回，同时输出误报率。

用法：
    python eval/run_eval.py
    python eval/run_eval.py --dataset eval/datasets/testset.jsonl
    python eval/run_eval.py --json-out eval/reports/latest.json
    python eval/run_eval.py --show-errors        # 打印每条错误样本，便于改 Prompt/词典

默认强制走离线规则链路（不调用大模型），保证结果可复现、无需 API Key、
不产生费用。要评估接入大模型后的效果，加 --use-llm 并配好 ZHIPU_API_KEY。
"""

import argparse
import contextlib
import io
import json
import os
import sys
from datetime import datetime

# 让脚本可以直接 `python eval/run_eval.py` 运行，无需先安装包或设置 PYTHONPATH
_HERE = os.path.dirname(os.path.abspath(__file__))
_AI_SERVICE_ROOT = os.path.dirname(_HERE)
if _AI_SERVICE_ROOT not in sys.path:
    sys.path.insert(0, _AI_SERVICE_ROOT)

from eval.metrics import BinaryCounter, ConfusionCounter  # noqa: E402

EMOTION_LABELS = ["positive", "negative", "neutral", "crisis"]
STAGE_LABELS = ["assessment", "interview", "resource", "crisis"]

DEFAULT_DATASET = os.path.join(_HERE, "datasets", "testset.jsonl")


# ---------------------------------------------------------------- 数据加载

def load_dataset(path):
    """读取 jsonl 测试集，跳过空行与 # 注释行。"""
    if not os.path.exists(path):
        raise SystemExit(f"[错误] 找不到测试集文件: {path}")

    samples = []
    with open(path, "r", encoding="utf-8") as f:
        for lineno, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            try:
                sample = json.loads(line)
            except json.JSONDecodeError as e:
                raise SystemExit(f"[错误] {path}:{lineno} JSON 解析失败: {e}")

            if not sample.get("text"):
                raise SystemExit(f"[错误] {path}:{lineno} 缺少 text 字段")
            samples.append(sample)

    if not samples:
        raise SystemExit(f"[错误] 测试集为空: {path}")
    return samples


# ---------------------------------------------------------------- 被测系统

def build_emotion_service(use_llm):
    from services.emotion_analysis import EmotionService

    service = EmotionService()
    if not use_llm:
        # 关掉 api_key 即可强制走 _analyze_with_rules，保证离线可复现
        service.api_key = None
    return service


def predict_first_turn_stage(message, crisis_detected):
    """模拟「会话第一条消息」时的阶段路由决策。

    每条样本都新建一个干净的 SessionState，等价于用户刚打开对话框说第一句话。
    """
    from services.session_state import SessionState
    from services.stage_policy import decide_stage

    # 每条样本用独立 key，彼此不共享任何历史，等价于「全新会话的第一句话」
    state = SessionState(key="eval")
    stage, reason = decide_stage(state, message, crisis_detected=crisis_detected)
    return stage, reason


def _preflight():
    """启动前自检依赖是否可用，避免跑到一半才报错。"""
    try:
        from services.session_state import SessionState  # noqa: F401
        from services.stage_policy import decide_stage  # noqa: F401
        from services.emotion_analysis import EmotionService  # noqa: F401
    except ImportError as e:
        raise SystemExit(f"[错误] 无法导入 ai-service 模块: {e}\n"
                         f"请在 legacy/ai-service 目录下运行本脚本。")


# ---------------------------------------------------------------- 评估主流程

def evaluate(samples, use_llm=False):
    emotion_service = build_emotion_service(use_llm)

    emotion_counter = ConfusionCounter(EMOTION_LABELS)
    stage_counter = ConfusionCounter(STAGE_LABELS)
    crisis_counter = BinaryCounter()

    errors = {"stage": [], "emotion": [], "crisis": []}
    details = []

    for sample in samples:
        text = sample["text"]

        # emotion_analysis 内部有 print 调试输出，这里吞掉以免污染评估报告
        with contextlib.redirect_stdout(io.StringIO()):
            result = emotion_service.analyze(text)
            pred_emotion = result.get("emotion_type", "neutral")
            pred_crisis = bool(result.get("crisis_detected", False))
            pred_stage, reason = predict_first_turn_stage(text, pred_crisis)

        exp_emotion = sample.get("expect_emotion")
        exp_stage = sample.get("expect_stage")
        exp_crisis = bool(sample.get("expect_crisis", False))

        if exp_emotion:
            emotion_counter.add(exp_emotion, pred_emotion)
            if exp_emotion != pred_emotion:
                errors["emotion"].append((sample, exp_emotion, pred_emotion))

        if exp_stage:
            stage_counter.add(exp_stage, pred_stage)
            if exp_stage != pred_stage:
                errors["stage"].append((sample, exp_stage, pred_stage))

        crisis_counter.add(exp_crisis, pred_crisis)
        if exp_crisis != pred_crisis:
            errors["crisis"].append((sample, exp_crisis, pred_crisis))

        details.append({
            "id": sample.get("id"),
            "text": text,
            "type": sample.get("type"),
            "expected": {
                "stage": exp_stage,
                "emotion": exp_emotion,
                "crisis": exp_crisis,
            },
            "predicted": {
                "stage": pred_stage,
                "emotion": pred_emotion,
                "crisis": pred_crisis,
                "stage_reason": reason,
                "sentiment_score": result.get("sentiment_score"),
            },
        })

    return {
        "emotion": emotion_counter,
        "stage": stage_counter,
        "crisis": crisis_counter,
        "errors": errors,
        "details": details,
    }


# ---------------------------------------------------------------- 输出

def _pct(value):
    return f"{value * 100:.1f}%"


def _line(char="-", width=64):
    return char * width


def print_report(samples, outcome, use_llm, show_errors=False):
    stage = outcome["stage"]
    emotion = outcome["emotion"]
    crisis = outcome["crisis"]

    type_counts = {}
    for s in samples:
        type_counts[s.get("type", "unknown")] = type_counts.get(s.get("type", "unknown"), 0) + 1

    print()
    print(_line("="))
    print("MindGuard AI 离线评估报告")
    print(_line("="))
    print(f"评估时间   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"推理模式   : {'大模型 + 规则' if use_llm else '纯规则（离线可复现）'}")
    print(f"样本总数   : {len(samples)}")
    print(f"样本构成   : " + ", ".join(f"{k}={v}" for k, v in sorted(type_counts.items())))
    print()

    print(_line())
    print("核心指标")
    print(_line())
    print(f"  首轮命中率（阶段路由正确率）: {_pct(stage.accuracy)}"
          f"   [{stage.correct}/{stage.total}]")
    print(f"  情绪识别准确率              : {_pct(emotion.accuracy)}"
          f"   [{emotion.correct}/{emotion.total}]")
    print(f"  危机召回率                  : {_pct(crisis.recall)}"
          f"   [{crisis.tp}/{crisis.positives}]")
    print(f"  危机误报率                  : {_pct(crisis.false_alarm_rate)}"
          f"   [{crisis.fp}/{crisis.fp + crisis.tn}]")
    print()

    print(_line())
    print("情绪识别 · 分类别明细")
    print(_line())
    print(f"  {'label':<10}{'support':>8}{'precision':>12}{'recall':>10}{'f1':>10}")
    for row in emotion.per_label():
        print(f"  {row['label']:<10}{row['support']:>8}"
              f"{_pct(row['precision']):>12}{_pct(row['recall']):>10}{_pct(row['f1']):>10}")
    print(f"  {'macro-F1':<10}{'':>8}{'':>12}{'':>10}{_pct(emotion.macro_f1()):>10}")
    print()

    print(_line())
    print("首轮阶段路由 · 分类别明细")
    print(_line())
    print(f"  {'label':<12}{'support':>8}{'precision':>12}{'recall':>10}{'f1':>10}")
    for row in stage.per_label():
        print(f"  {row['label']:<12}{row['support']:>8}"
              f"{_pct(row['precision']):>12}{_pct(row['recall']):>10}{_pct(row['f1']):>10}")
    print(f"  {'macro-F1':<12}{'':>8}{'':>12}{'':>10}{_pct(stage.macro_f1()):>10}")
    print()

    print(_line())
    print("危机检测 · 混淆矩阵")
    print(_line())
    print(f"  TP(正确拦截)={crisis.tp}   FN(危机漏报)={crisis.fn}")
    print(f"  FP(误报)    ={crisis.fp}   TN(正确放行)={crisis.tn}")
    print(f"  precision={_pct(crisis.precision)}  recall={_pct(crisis.recall)}"
          f"  f1={_pct(crisis.f1)}")
    if crisis.fn:
        print(f"  [!] 存在 {crisis.fn} 条危机漏报，这是最高优先级缺陷，必须优先修复")
    print()

    errors = outcome["errors"]
    total_errors = sum(len(v) for v in errors.values())
    print(_line())
    print(f"错误样本汇总（共 {total_errors} 处不一致）")
    print(_line())
    for key, title in (("crisis", "危机判定"), ("emotion", "情绪识别"), ("stage", "阶段路由")):
        items = errors[key]
        print(f"  {title}: {len(items)} 处")
        if show_errors:
            for sample, expected, predicted in items:
                print(f"    - [{sample.get('id')}] {sample['text']}")
                print(f"        期望={expected}  实际={predicted}"
                      f"  备注={sample.get('note', '')}")
    if not show_errors and total_errors:
        print("  （加 --show-errors 查看逐条错误明细）")
    print()
    print(_line("="))


def build_json_report(samples, outcome, use_llm):
    stage = outcome["stage"]
    emotion = outcome["emotion"]
    crisis = outcome["crisis"]
    return {
        "evaluated_at": datetime.now().isoformat(timespec="seconds"),
        "mode": "llm+rules" if use_llm else "rules-only",
        "sample_count": len(samples),
        "metrics": {
            "first_turn_hit_rate": round(stage.accuracy, 4),
            "emotion_accuracy": round(emotion.accuracy, 4),
            "emotion_macro_f1": round(emotion.macro_f1(), 4),
            "crisis_recall": round(crisis.recall, 4),
            "crisis_precision": round(crisis.precision, 4),
            "crisis_false_alarm_rate": round(crisis.false_alarm_rate, 4),
        },
        "crisis_confusion": {
            "tp": crisis.tp, "fp": crisis.fp, "tn": crisis.tn, "fn": crisis.fn,
        },
        "emotion_per_label": emotion.per_label(),
        "stage_per_label": stage.per_label(),
        "details": outcome["details"],
    }


def main():
    parser = argparse.ArgumentParser(description="MindGuard AI 离线评估")
    parser.add_argument("--dataset", default=DEFAULT_DATASET, help="jsonl 测试集路径")
    parser.add_argument("--json-out", default=None, help="将结构化报告写入指定 json 文件")
    parser.add_argument("--show-errors", action="store_true", help="打印逐条错误样本")
    parser.add_argument("--use-llm", action="store_true",
                        help="调用大模型进行情绪分析（需配置 ZHIPU_API_KEY，结果不保证可复现）")
    parser.add_argument("--fail-under-crisis-recall", type=float, default=None,
                        help="危机召回率低于该阈值时以非 0 退出，便于接入 CI")
    args = parser.parse_args()

    _preflight()

    samples = load_dataset(args.dataset)
    outcome = evaluate(samples, use_llm=args.use_llm)
    print_report(samples, outcome, args.use_llm, show_errors=args.show_errors)

    if args.json_out:
        report = build_json_report(samples, outcome, args.use_llm)
        os.makedirs(os.path.dirname(os.path.abspath(args.json_out)), exist_ok=True)
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"结构化报告已写入: {args.json_out}")

    if args.fail_under_crisis_recall is not None:
        recall = outcome["crisis"].recall
        if recall < args.fail_under_crisis_recall:
            print(f"[FAIL] 危机召回率 {recall:.4f} 低于阈值 {args.fail_under_crisis_recall}")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
