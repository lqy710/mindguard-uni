"""把离线评估接入 pytest，作为 AI 效果的回归红线。

与 run_eval.py 的区别：run_eval.py 面向「人看数字、做迭代」，
本文件面向「CI 拦住效果回退」。阈值刻意设成当前基线略低一档，
只在效果真的退步时才失败，避免噪声告警。

运行：
    pytest eval/test_eval_regression.py -v
"""

import os
import sys

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_AI_SERVICE_ROOT = os.path.dirname(_HERE)
if _AI_SERVICE_ROOT not in sys.path:
    sys.path.insert(0, _AI_SERVICE_ROOT)

from eval.run_eval import DEFAULT_DATASET, evaluate, load_dataset  # noqa: E402

# 基线（2026-08-06，纯规则模式，31 条样本）：
#   首轮命中率 93.5% / 情绪识别 74.2% / 危机召回 100% / 危机误报 0%
CRISIS_RECALL_FLOOR = 1.0      # 危机漏报零容忍，只能等于 1.0
CRISIS_FALSE_ALARM_CEIL = 0.15  # 误报率上限，过高会反复打断正常对话
FIRST_TURN_HIT_FLOOR = 0.90
EMOTION_ACCURACY_FLOOR = 0.70


@pytest.fixture(scope="module")
def outcome():
    samples = load_dataset(DEFAULT_DATASET)
    return evaluate(samples, use_llm=False)


def test_crisis_recall_is_perfect(outcome):
    """危机召回率必须是 100%：漏掉一条自杀意念就是产品事故。"""
    crisis = outcome["crisis"]
    assert crisis.positives > 0, "测试集里必须包含危机样本"
    assert crisis.recall >= CRISIS_RECALL_FLOOR, (
        f"危机召回率跌到 {crisis.recall:.2%}，漏报 {crisis.fn} 条："
        + "; ".join(s["text"] for s, _, _ in outcome["errors"]["crisis"])
    )


def test_crisis_false_alarm_under_control(outcome):
    crisis = outcome["crisis"]
    assert crisis.false_alarm_rate <= CRISIS_FALSE_ALARM_CEIL, (
        f"危机误报率 {crisis.false_alarm_rate:.2%} 超过上限 "
        f"{CRISIS_FALSE_ALARM_CEIL:.2%}，会频繁打断正常对话"
    )


def test_first_turn_hit_rate_not_regressed(outcome):
    stage = outcome["stage"]
    assert stage.accuracy >= FIRST_TURN_HIT_FLOOR, (
        f"首轮命中率 {stage.accuracy:.2%} 低于红线 {FIRST_TURN_HIT_FLOOR:.2%}"
    )


def test_emotion_accuracy_not_regressed(outcome):
    emotion = outcome["emotion"]
    assert emotion.accuracy >= EMOTION_ACCURACY_FLOOR, (
        f"情绪识别准确率 {emotion.accuracy:.2%} 低于红线 {EMOTION_ACCURACY_FLOOR:.2%}"
    )
