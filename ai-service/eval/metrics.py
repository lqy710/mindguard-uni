"""评估指标计算。

只做纯函数式的指标计算，不涉及模型调用与 IO，便于单独验证正确性。
"""


def _safe_div(numerator, denominator):
    return numerator / denominator if denominator else 0.0


class ConfusionCounter:
    """多分类混淆统计，用于按类别输出 P/R/F1。"""

    def __init__(self, labels):
        self.labels = list(labels)
        self.tp = {label: 0 for label in self.labels}
        self.fp = {label: 0 for label in self.labels}
        self.fn = {label: 0 for label in self.labels}
        self.total = 0
        self.correct = 0

    def add(self, expected, predicted):
        self.total += 1
        if expected == predicted:
            self.correct += 1
            if expected in self.tp:
                self.tp[expected] += 1
        else:
            if predicted in self.fp:
                self.fp[predicted] += 1
            if expected in self.fn:
                self.fn[expected] += 1

    @property
    def accuracy(self):
        return _safe_div(self.correct, self.total)

    def per_label(self):
        rows = []
        for label in self.labels:
            tp, fp, fn = self.tp[label], self.fp[label], self.fn[label]
            precision = _safe_div(tp, tp + fp)
            recall = _safe_div(tp, tp + fn)
            f1 = _safe_div(2 * precision * recall, precision + recall)
            rows.append({
                "label": label,
                "support": tp + fn,
                "precision": precision,
                "recall": recall,
                "f1": f1,
            })
        return rows

    def macro_f1(self):
        rows = self.per_label()
        scored = [r for r in rows if r["support"] > 0]
        return _safe_div(sum(r["f1"] for r in scored), len(scored))


class BinaryCounter:
    """二分类统计，用于危机召回率这类以「漏报代价极高」为核心的指标。"""

    def __init__(self):
        self.tp = 0
        self.fp = 0
        self.tn = 0
        self.fn = 0

    def add(self, expected, predicted):
        if expected and predicted:
            self.tp += 1
        elif expected and not predicted:
            self.fn += 1
        elif not expected and predicted:
            self.fp += 1
        else:
            self.tn += 1

    @property
    def total(self):
        return self.tp + self.fp + self.tn + self.fn

    @property
    def positives(self):
        return self.tp + self.fn

    @property
    def recall(self):
        """危机召回率：真实危机中被识别出来的比例。漏一个都是事故。"""
        return _safe_div(self.tp, self.tp + self.fn)

    @property
    def precision(self):
        return _safe_div(self.tp, self.tp + self.fp)

    @property
    def f1(self):
        return _safe_div(2 * self.precision * self.recall, self.precision + self.recall)

    @property
    def false_alarm_rate(self):
        """误报率：非危机样本被误判为危机的比例。过高会让用户被反复打断。"""
        return _safe_div(self.fp, self.fp + self.tn)

    @property
    def accuracy(self):
        return _safe_div(self.tp + self.tn, self.total)
