# MindGuard AI 效果闭环：负反馈回流 → 离线评估 → Prompt 迭代

> 目标：让 AI 对话效果**有数据来源、有评估手段、有迭代依据**，
> 而不是拍脑袋写一个好看的百分比。

---

## 0. 为什么要做这件事

在此之前项目的真实状态是：

- 前端没有任何埋点，用户觉得回答不好，这个信号**直接丢失**；
- 后端没有反馈表，无法沉淀「哪些回答是坏的、坏在哪」；
- 没有评估脚本，改完 Prompt 只能靠人工聊几句「感觉变好了」；
- 因此任何「命中率 XX%」的说法都**没有可验证来源**。

本次改造补齐的正是这条链路上缺失的三环：**采集 → 度量 → 迭代**。

```
                 ┌──────────────────────────────────────────┐
                 │                                          │
                 ▼                                          │
  用户对话 ─→ 👍/👎 负反馈 ─→ chat_feedback 表 ─→ 人工标注 ─→ 扩充测试集
                                                              │
                                                              ▼
                          Prompt / 规则词典修改 ←─ 定位缺陷 ←─ 离线评估脚本
                                    │                          ▲
                                    └──────── 重新评估 ─────────┘
```

---

## 1. 第一环：负反馈采集

### 1.1 前端

`src/pages/chat/chat.vue` 中每条 **AI 回复**下方渲染 👍 / 👎：

- 👍 直接提交（`rating = 1`）；
- 👎 展开原因面板，四选一后提交（`rating = -1` + `category`）；
- 采用**乐观更新**，请求失败自动回滚并 toast，避免用户点了没反应；
- 仅当消息带有后端真实 `recordId` 时才展示反馈入口。

> ⚠️ 实现要点：消息流里的 `msg.id` 是前端自增序号，**不是**数据库主键。
> 为此在 `MessageItem` 上新增了 `recordId` 字段承接后端 `ChatMessageVO.id`，
> 否则反馈会关联到错误的记录上。

### 1.2 接口

与现有 `assessment` / `diary` 接口保持完全一致的 `Result<T>` 响应体：

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/chat/feedback` | 提交反馈，同一条回复重复提交视为**修改** |
| GET | `/api/chat/session/{sessionId}/feedback` | 拉取本会话反馈，用于回显选中态 |

```json
{ "code": 200, "message": "success", "data": { "id": 1, "recordId": 42, "rating": -1, "category": "irrelevant", "categoryLabel": "答非所问" } }
```

服务端校验（`ChatFeedbackServiceImpl`）：

1. `rating` 只允许 `1 / -1`；
2. 记录必须存在，且 `user_id` 属于当前登录用户，否则 403；
3. 只能对 `role = 'assistant'` 的消息评价；
4. `category` 走白名单，点踩未选原因时兜底为 `other`。

### 1.3 标注分类

`chat_feedback.category` 的四个取值即标注体系，前后端共用一套：

| 枚举值 | 中文 | 对应的典型缺陷 | 通常要改哪里 |
| --- | --- | --- | --- |
| `irrelevant` | 答非所问 | 阶段路由错、意图识别错 | `stage_policy` 正则 / 阶段 Prompt |
| `unsafe` | 不安全 | 危机漏判、回复带风险引导 | 危机词典 / 危机阶段 Prompt（最高优先级） |
| `unprofessional` | 不专业 | 说教、空泛、共情缺失 | 各阶段 Prompt 的语气与话术约束 |
| `other` | 其他 | 兜底 | 人工归因后再拆分 |

配套字段让这张表**自身就能变成评估集**，无需回表拼接：

- `user_content` / `reply_content`：冗余存下当轮问答；
- `stage`：当时所处会话阶段；
- `label_status`：`0` 未标注 → `1` 已标注 → `2` 已转为评估样本。

---

## 2. 第二环：离线评估

### 2.1 评估什么

关键取舍：**只评估当前代码里真实存在、且能被确定性复现的判定链路**，
不去编造无法测量的指标。

| 指标 | 被测对象 | 判定方式 |
| --- | --- | --- |
| 首轮命中率 | `stage_policy.decide_stage()` | 全新会话第一句话，路由到的阶段是否等于人工标注阶段 |
| 情绪识别准确率 | `EmotionService.analyze()` | `emotion_type` 与标注标签一致率（4 分类） |
| 危机召回率 | `EmotionService._detect_crisis()` | 危机样本中被正确识别的比例 |

> **关于「首轮命中率」的定义**：一个开放域回复「答得好不好」无法自动判定，
> 强行用大模型打分会引入不可复现的噪声。因此这里选择**阶段路由正确率**作为代理指标——
> 首轮就把用户路由错（例如求助方法却进了评估问答），后面整段对话必然是错的。
> 这是一个**定义清晰、可复现、且与体验强相关**的代理指标，文档中必须如实这样表述。

同时输出**危机误报率**：只看召回容易走捷径（把所有输入都判为危机即可拿到 100%），
必须用误报率约束住。

### 2.2 怎么跑

```bash
cd legacy/ai-service

python eval/run_eval.py                                   # 跑默认测试集
python eval/run_eval.py --show-errors                     # 打印逐条错误，定位缺陷
python eval/run_eval.py --json-out eval/reports/x.json    # 输出结构化报告
python eval/run_eval.py --fail-under-crisis-recall 0.95   # CI 红线，低于阈值非 0 退出
```

默认**强制走规则链路**（脚本内把 `service.api_key` 置空），因此：
无需 API Key、不产生费用、结果完全可复现。
要评估接入大模型后的效果，加 `--use-llm` 并配置 `ZHIPU_API_KEY`。

### 2.3 当前真实基线

数据集 `eval/datasets/testset.jsonl`，31 条样本（危机 8 / 情绪 13 / 知识问答 10），
纯规则模式，2026-08-06 实测：

| 指标 | 数值 | 明细 |
| --- | --- | --- |
| 首轮命中率 | **93.5%** | 29/31 |
| 情绪识别准确率 | **74.2%** | 23/31，macro-F1 72.0% |
| 危机召回率 | **100.0%** | 8/8，漏报 0 |
| 危机误报率 | **0.0%** | 0/23 |

情绪识别分类别：

| label | support | precision | recall | f1 |
| --- | --- | --- | --- | --- |
| positive | 4 | 100.0% | 50.0% | 66.7% |
| negative | 9 | 100.0% | 33.3% | 50.0% |
| neutral | 10 | 55.6% | 100.0% | 71.4% |
| crisis | 8 | 100.0% | 100.0% | 100.0% |

> 这些数字**由脚本真实打印**，可在本地一条命令复现。
> 样本量仅 31 条，属于冒烟级测试集，**置信区间很宽**，
> 对外表述时应说明「31 条样本的离线评估」，不要包装成线上大盘指标。

### 2.4 基线暴露出的真实缺陷

`--show-errors` 直接指出了 10 处不一致，全部是**规则词典的真实盲区**：

1. **negative 召回仅 33.3%**（6 条漏判为 neutral）：
   `emotion_analysis.negative_keywords` 缺少「焦虑、孤独、委屈、疲惫、提不起兴趣」等高频词；
2. **positive 召回 50%**：缺少「轻松、不错、愉快」等表达；
3. **neutral 精确率仅 55.6%**：上面两类漏判全部堆积到 neutral，属连带效应；
4. **2 条阶段路由错**：`stage_policy._RESOURCE_PATTERNS` 未覆盖
   「能给我一些…建议吗」「我想了解一下…的方法」这两种索取句式。

这正是评估脚本的价值——**把「感觉不太准」变成「这 4 类词典要补，具体是这 10 条」**。

---

## 3. 第三环：Prompt 优化 → 验证 → 迭代

### 标准作业流程

**Step 1 · 归因**
每周导出 `chat_feedback` 中 `rating = -1 AND label_status = 0` 的记录，
按 `category` 聚类，找出占比最高的那一类。

```sql
SELECT category, COUNT(*) AS cnt
FROM chat_feedback
WHERE rating = -1 AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY category
ORDER BY cnt DESC;
```

**Step 2 · 沉淀样本（关键一步）**
把踩过的 case 转成测试样本追加进 `testset.jsonl`，并置 `label_status = 2`。
**这是闭环真正闭合的地方**：线上每一次踩，都变成一条永久的回归用例，
保证同一个问题不会被修好之后再退化。

```json
{"id": "fb-20260806-001", "text": "<user_content>", "type": "emotion", "expect_crisis": false, "expect_emotion": "negative", "expect_stage": "assessment", "note": "来源: feedback#123 答非所问"}
```

**Step 3 · 先记录基线**
```bash
python eval/run_eval.py --json-out eval/reports/before.json
```

**Step 4 · 只改一处**
每轮迭代**只动一个变量**（一个阶段的 Prompt，或一类关键词），
否则指标变化无法归因。改动位置对照：

| 问题类别 | 改动位置 |
| --- | --- |
| 答非所问 | `services/stage_policy.py` 的 `_RESOURCE_PATTERNS` / `get_stage_prompt()` |
| 不安全 | `services/emotion_analysis.py` 的 `crisis_keywords`、危机阶段 Prompt |
| 不专业 | `get_stage_prompt()` 中对应阶段的语气与话术约束 |
| 情绪识别不准 | `negative_keywords` / `positive_keywords` 词典 |

**Step 5 · 复评并对比**
```bash
python eval/run_eval.py --json-out eval/reports/after.json --show-errors
```

**Step 6 · 按准入门槛决定合入**

| 条件 | 结论 |
| --- | --- |
| 危机召回率 < 100% | **一票否决**，无论其他指标涨多少 |
| 危机误报率 > 15% | 打回，会频繁误打断正常对话 |
| 目标指标上升，其余不降 | 合入 |
| 目标指标上升但其他下降 | 记录 trade-off，人工判断 |

**Step 7 · 回归红线**
`eval/test_eval_regression.py` 把上述门槛固化为 pytest 用例：

```bash
pytest eval/test_eval_regression.py -v
# 4 passed
```

其中危机召回率阈值设为 `1.0`——**漏掉一条自杀意念就是产品事故，零容忍**。

---

## 4. 文件清单

| 文件 | 作用 |
| --- | --- |
| `legacy/database/init.sql` | 新增 `chat_feedback` 建表语句 |
| `backend/.../entity/ChatFeedback.java` | 反馈实体，风格对齐 `EmotionDiary` |
| `backend/.../mapper/ChatFeedbackMapper.java` | MyBatis-Plus Mapper |
| `backend/.../dto/ChatFeedbackDTO.java` | 请求参数 + 校验 |
| `backend/.../vo/ChatFeedbackVO.java` | 响应体 |
| `backend/.../service/ChatFeedbackService.java` | 服务接口 |
| `backend/.../service/impl/ChatFeedbackServiceImpl.java` | 落库、鉴权、去重 |
| `backend/.../controller/ChatController.java` | 新增 2 个反馈接口 |
| `src/api/chat.ts` | 反馈 API 与分类常量 |
| `src/pages/chat/chat.vue` | 👍/👎 UI 与原因面板 |
| `ai-service/eval/run_eval.py` | 评估主脚本 |
| `ai-service/eval/metrics.py` | 指标计算（混淆矩阵 / P-R-F1） |
| `ai-service/eval/datasets/testset.jsonl` | 31 条标注测试集 |
| `ai-service/eval/test_eval_regression.py` | pytest 回归红线 |
| `ai-service/eval/reports/baseline.json` | 基线报告快照 |

---

## 5. 简历表述建议

改造前的写法（**不可验证，建议不要再用**）：

> ~~首轮命中率 54%→82%，情绪识别 60%→85%，危机召回 95%+，对话完成率 85%+~~

改造后可以**如实**这样写：

> 搭建 AI 对话效果闭环：前端埋点采集用户负反馈（👍/👎 + 四类原因标注）落库，
> 编写离线评估脚本对阶段路由、情绪识别、危机检测三条链路做可复现度量。
> 当前 31 条标注样本上：**危机召回率 100%（0 漏报）、误报率 0%，
> 首轮阶段路由准确率 93.5%，情绪识别准确率 74.2%**；
> 并将危机召回率零漏报固化为 pytest 回归红线，防止 Prompt 迭代引入效果退化。

差别在于：每个数字都能用一条命令当场复现，且能说清楚定义、样本量与局限。
面试时若被追问「怎么测的」「样本多少」「为什么这么定义」，都有明确答案——
这比一个漂亮但站不住的数字更有说服力。
