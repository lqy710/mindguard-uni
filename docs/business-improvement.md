> **历史文档（已迁移）**：本文档属于 MindGuard 旧版 Web 项目（`legacy/`，Vue3 Web + Spring Boot + Flask），**不再维护**。当前用户端已重构为 uni-app（微信小程序 + H5），实际实现见仓库 `src/` 目录；开发规则与当前设计系统见 `.trae/rules/mindguard-migration.md`。本文件仅作历史回溯参考。

# MindGuard 业务逻辑改进待办清单

> 本文档列出了 MindGuard 项目需要改进的业务逻辑问题，建议每个问题在新会话中单独解决。
> 
> 创建时间：2026-03-24
> 分析依据：代码审查 + 竞品分析（心境奇旅、简单心理、Woebot、平安科技专利）

---

## 📋 待办事项概览

| 序号 | 问题 | 优先级 | 预计耗时 | 状态 |
|------|------|--------|----------|------|
| 1 | AI 对话缺乏上下文记忆 | 🔴 P0 | 30分钟 | ⬜ 待处理 |
| 2 | 预警触发机制不完善 | 🔴 P0 | 45分钟 | ⬜ 待处理 |
| 3 | 测评报告内容单薄 | 🟡 P1 | 40分钟 | ⬜ 待处理 |
| 4 | 用户画像数据未充分利用 | 🟡 P1 | 35分钟 | ⬜ 待处理 |
| 5 | 测评缺乏个性化推荐 | 🟡 P1 | 30分钟 | ⬜ 待处理 |
| 6 | 缺乏专业心理干预方法 | 🟢 P2 | 60分钟 | ⬜ 待处理 |
| 7 | 情绪日记分析不够深入 | 🟢 P2 | 25分钟 | ⬜ 待处理 |
| 8 | 缺乏定期追踪和提醒机制 | 🟢 P2 | 30分钟 | ⬜ 待处理 |

---

## 🔴 P0 级别问题（必须立即修复）

---

### 问题 1：AI 对话缺乏上下文记忆

#### 问题描述

**当前状态**：

查看 `backend/src/main/java/com/mental/service/impl/ChatServiceImpl.java` 第 124-126 行：

```java
private String callAiService(String message) {
    return pythonAiService.chat(message);  // 只传了当前消息，没有历史上下文
}
```

**问题影响**：
- 每次对话都是独立的，AI 无法记住之前的交流内容
- 用户说"我之前提到的那个问题"，AI 无法理解
- 用户体验差，对话不连贯，缺乏个性化

**竞品对比**：
| 产品 | 上下文记忆 | 个性化 |
|------|-----------|--------|
| 心境奇旅 | ✅ 完整对话记忆 | ✅ 记住用户姓名、偏好 |
| Woebot | ✅ 多轮对话上下文 | ✅ CBT 引导式对话 |
| MindGuard | ❌ 无上下文 | ❌ 每次独立对话 |

#### 解决方案

**步骤1：修改 Python AI 服务，支持上下文**

修改 `ai-service/services/chat_service.py`，添加带上下文的回复方法：

```python
def reply_with_context(self, message, context=None, user_id=None, language='auto'):
    """
    带上下文的对话回复
    
    Args:
        message: 当前用户消息
        context: 历史对话列表，格式 [{"role": "user/assistant", "content": "..."}]
        user_id: 用户ID，用于个性化
        language: 语言
    """
    detected_language = self._detect_language(message) if language == 'auto' else language
    
    # 危机检测
    if self._detect_crisis(message, detected_language):
        return {
            'reply': self.crisis_response.get(detected_language, self.crisis_response['zh']),
            'confidence': 1.0,
            'crisis_detected': True,
            'need_human_support': True,
            'language': detected_language
        }
    
    # 更新用户画像
    if user_id:
        self._update_user_profile(user_id, message, detected_language)
    
    # 调用智谱AI，传入上下文
    if self.api_key:
        try:
            return self._call_zhipu_api_with_context(message, context, detected_language, user_id)
        except Exception as e:
            if DEBUG:
                print(f"智谱AI调用失败: {e}")
    
    # 降级到本地响应
    return self._generate_local_response(message, detected_language, user_id)

def _call_zhipu_api_with_context(self, message, context, language='zh', user_id=None):
    """调用智谱AI，传入完整上下文"""
    url = f"{self.base_url}/chat/completions"
    
    messages = []
    
    # 构建个性化系统提示
    personalized_prompt = self.system_prompt
    if user_id and user_id in self.user_profiles:
        profile = self.user_profiles[user_id]
        if profile['name']:
            personalized_prompt += f"\n\n【用户信息】\n- 姓名：{profile['name']}\n- 历史问题：{', '.join(profile['issues'][-3:])}\n- 互动次数：{profile['interaction_count']}"
    
    messages.append({"role": "system", "content": personalized_prompt})
    
    # 添加历史上下文（最多保留10轮）
    if context:
        for msg in context[-20:]:  # 最多20条消息（10轮对话）
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
    
    # 添加当前消息
    messages.append({"role": "user", "content": message})
    
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
    
    response = requests.post(url, headers=headers, json=data, timeout=60)
    
    if response.status_code == 200:
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            return {
                "reply": content,
                "confidence": 0.95,
                "crisis_detected": False,
                "language": language
            }
    
    return self._generate_local_response(message, language, user_id)
```

**步骤2：修改 `ai-service/app.py`，添加新接口**

```python
@app.route('/api/chat/reply_with_context', methods=['POST'])
def chat_reply_with_context():
    """带上下文的对话接口"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        context = data.get('context', [])
        user_id = data.get('user_id')
        language = data.get('language', 'auto')
        
        if not message:
            return jsonify({'error': '消息不能为空'}), 400
        
        result = chat_service.reply_with_context(message, context, user_id, language)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e), 'reply': '抱歉，服务暂时不可用'}), 500
```

**步骤3：修改后端 `PythonAiService` 接口**

修改 `backend/src/main/java/com/mental/service/PythonAiService.java`：

```java
public interface PythonAiService {
    
    String chat(String message);
    
    /**
     * 带上下文的对话
     * @param message 当前消息
     * @param context 历史对话上下文
     * @param userId 用户ID
     * @return AI回复
     */
    String chatWithContext(String message, List<Map<String, String>> context, Long userId);
}
```

修改实现类 `backend/src/main/java/com/mental/service/impl/PythonAiServiceImpl.java`：

```java
@Override
public String chatWithContext(String message, List<Map<String, String>> context, Long userId) {
    try {
        String url = pythonUrl + "/api/chat/reply_with_context";
        
        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("message", message);
        requestBody.put("context", context);
        requestBody.put("user_id", userId);
        requestBody.put("language", "auto");
        
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        
        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);
        
        ResponseEntity<Map> response = restTemplate.postForEntity(url, entity, Map.class);
        
        if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
            Map<String, Object> body = response.getBody();
            return (String) body.get("reply");
        }
    } catch (Exception e) {
        log.error("调用AI服务失败: {}", e.getMessage());
    }
    
    return "抱歉，我现在无法回应，请稍后再试。";
}
```

**步骤4：修改 `ChatServiceImpl`，传入上下文**

修改 `backend/src/main/java/com/mental/service/impl/ChatServiceImpl.java`：

```java
@Override
public ChatMessageVO sendMessage(ChatDTO dto) {
    Long userId = getCurrentUserId();
    
    Long sessionId = dto.getSessionId();
    if (sessionId == null) {
        ChatSession session = new ChatSession();
        session.setUserId(userId);
        session.setTitle(dto.getMessage().length() > 20 ? dto.getMessage().substring(0, 20) + "..." : dto.getMessage());
        sessionMapper.insert(session);
        sessionId = session.getId();
    }
    
    // 保存用户消息
    ChatRecord userRecord = new ChatRecord();
    userRecord.setSessionId(sessionId);
    userRecord.setUserId(userId);
    userRecord.setRole("user");
    userRecord.setContent(dto.getMessage());
    recordMapper.insert(userRecord);
    
    // 获取历史对话作为上下文
    List<Map<String, String>> context = getConversationContext(sessionId, 10);
    
    // 调用AI服务，传入上下文
    String aiReply = pythonAiService.chatWithContext(dto.getMessage(), context, userId);
    
    // 保存AI回复
    ChatRecord aiRecord = new ChatRecord();
    aiRecord.setSessionId(sessionId);
    aiRecord.setUserId(userId);
    aiRecord.setRole("assistant");
    aiRecord.setContent(aiReply);
    recordMapper.insert(aiRecord);
    
    ChatMessageVO vo = new ChatMessageVO();
    vo.setId(aiRecord.getId());
    vo.setRole("assistant");
    vo.setContent(aiReply);
    vo.setCreatedAt(aiRecord.getCreatedAt());
    
    // WebSocket通知
    ChatNotification chatNotification = ChatNotification.builder()
            .sessionId(sessionId)
            .content(aiReply)
            .createdAt(System.currentTimeMillis())
            .build();
    notificationService.sendChatMessage(userId, chatNotification);
    
    return vo;
}

/**
 * 获取对话上下文
 * @param sessionId 会话ID
 * @param rounds 对话轮数（一轮=用户+AI两条消息）
 * @return 上下文列表
 */
private List<Map<String, String>> getConversationContext(Long sessionId, int rounds) {
    LambdaQueryWrapper<ChatRecord> wrapper = new LambdaQueryWrapper<>();
    wrapper.eq(ChatRecord::getSessionId, sessionId)
           .orderByDesc(ChatRecord::getCreatedAt)
           .last("LIMIT " + (rounds * 2));
    
    List<ChatRecord> records = recordMapper.selectList(wrapper);
    
    // 按时间正序排列
    List<Map<String, String>> context = new ArrayList<>();
    for (int i = records.size() - 1; i >= 0; i--) {
        ChatRecord record = records.get(i);
        Map<String, String> msg = new HashMap<>();
        msg.put("role", record.getRole());
        msg.put("content", record.getContent());
        context.add(msg);
    }
    
    return context;
}
```

#### 验证方法

1. 启动 AI 服务和后端服务
2. 发送多轮对话测试：
   ```
   用户: 我叫小明
   AI: 你好小明！很高兴认识你...
   用户: 我刚才说我叫什么？
   AI: 你刚才说你叫小明。（能正确回答说明上下文生效）
   ```
3. 检查数据库 `chat_record` 表，确认消息正确保存

---

### 问题 2：预警触发机制不完善

#### 问题描述

**当前状态**：

查看 `backend/src/main/java/com/mental/service/impl/AssessmentServiceImpl.java` 第 78-107 行：

```java
@Transactional
public ReportVO submitAssessment(AssessmentSubmitDTO dto) {
    // ... 计算分数和风险等级
    
    assessmentMapper.insert(assessment);
    // ❌ 没有触发预警！
    
    return buildReport(assessment, scale, totalScore);
}
```

**问题影响**：
- 测评提交后没有自动创建预警记录
- 情绪日记和 AI 对话中的危机词检测后没有触发预警
- 高风险用户可能被遗漏，存在安全隐患

**竞品对比**：
| 产品 | 预警机制 | 触发场景 |
|------|---------|---------|
| 心境奇旅 | ✅ 完整预警 | 测评、对话、日记 |
| 平安科技 | ✅ AI智能预警 | 多维度综合评估 |
| MindGuard | ❌ 无自动触发 | 仅管理员手动查看 |

#### 解决方案

**步骤1：创建预警服务类**

创建 `backend/src/main/java/com/mental/service/WarningTriggerService.java`：

```java
package com.mental.service;

import com.mental.entity.Warning;
import com.mental.websocket.dto.WarningNotification;
import com.mental.websocket.service.NotificationService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

@Slf4j
@Service
@RequiredArgsConstructor
public class WarningTriggerService {
    
    private final WarningMapper warningMapper;
    private final NotificationService notificationService;
    private final UserMapper userMapper;
    
    /**
     * 触发预警
     * @param userId 用户ID
     * @param riskLevel 风险等级 (low/medium/high)
     * @param triggerSource 触发来源 (assessment/diary/chat)
     * @param triggerContent 触发内容
     */
    public void triggerWarning(Long userId, String riskLevel, String triggerSource, String triggerContent) {
        // 检查是否已存在未处理的预警
        LambdaQueryWrapper<Warning> existingWrapper = new LambdaQueryWrapper<>();
        existingWrapper.eq(Warning::getUserId, userId)
                       .eq(Warning::getStatus, "pending")
                       .orderByDesc(Warning::getCreatedAt)
                       .last("LIMIT 1");
        Warning existingWarning = warningMapper.selectOne(existingWrapper);
        
        // 如果已存在同级别或更高级别的未处理预警，不重复创建
        if (existingWarning != null && isSameOrHigherRisk(existingWarning.getRiskLevel(), riskLevel)) {
            log.info("用户{}已存在未处理的{}预警，跳过创建", userId, existingWarning.getRiskLevel());
            return;
        }
        
        // 创建新预警
        Warning warning = new Warning();
        warning.setUserId(userId);
        warning.setRiskLevel(riskLevel);
        warning.setTriggerSource(triggerSource);
        warning.setTriggerContent(triggerContent);
        warning.setStatus("pending");
        warning.setCreatedAt(LocalDateTime.now());
        
        warningMapper.insert(warning);
        log.warn("创建预警: userId={}, riskLevel={}, source={}", userId, riskLevel, triggerSource);
        
        // 实时通知管理员
        notifyAdmins(warning);
        
        // 如果是高风险，同时通知用户
        if ("high".equals(riskLevel)) {
            notifyUser(userId, triggerSource);
        }
    }
    
    private boolean isSameOrHigherRisk(String existingLevel, String newLevel) {
        int existingScore = getRiskScore(existingLevel);
        int newScore = getRiskScore(newLevel);
        return existingScore >= newScore;
    }
    
    private int getRiskScore(String level) {
        return switch (level) {
            case "high" -> 3;
            case "medium" -> 2;
            default -> 1;
        };
    }
    
    private void notifyAdmins(Warning warning) {
        // 获取用户信息
        User user = userMapper.selectById(warning.getUserId());
        String username = user != null ? user.getUsername() : "未知用户";
        
        // 构建通知内容
        WarningNotification notification = WarningNotification.builder()
                .warningId(warning.getId())
                .userId(warning.getUserId())
                .username(username)
                .riskLevel(warning.getRiskLevel())
                .triggerSource(warning.getTriggerSource())
                .triggerContent(warning.getTriggerContent())
                .createdAt(System.currentTimeMillis())
                .message(String.format("【%s预警】用户 %s 触发预警，来源：%s", 
                    getRiskLevelText(warning.getRiskLevel()), 
                    username, 
                    getTriggerSourceText(warning.getTriggerSource())))
                .build();
        
        // 发送给所有管理员
        notificationService.sendWarningToAdmins(notification);
    }
    
    private void notifyUser(Long userId, String triggerSource) {
        // 发送关怀通知给用户
        String message = switch (triggerSource) {
            case "assessment" -> "您的测评结果显示需要关注，建议您联系专业心理咨询师或拨打心理援助热线：400-161-9995";
            case "diary" -> "我们注意到您最近的情绪状态需要关注，如果需要帮助，请随时联系我们或拨打心理援助热线：400-161-9995";
            case "chat" -> "如果您正在经历困难时刻，请知道您并不孤单。24小时心理援助热线：400-161-9995";
            default -> "如果您需要帮助，请拨打24小时心理援助热线：400-161-9995";
        };
        
        notificationService.sendUserNotification(userId, "心理健康关怀", message);
    }
    
    private String getRiskLevelText(String level) {
        return switch (level) {
            case "high" -> "高风险";
            case "medium" -> "中风险";
            default -> "低风险";
        };
    }
    
    private String getTriggerSourceText(String source) {
        return switch (source) {
            case "assessment" -> "心理测评";
            case "diary" -> "情绪日记";
            case "chat" -> "AI对话";
            default -> "其他";
        };
    }
}
```

**步骤2：在测评提交时触发预警**

修改 `backend/src/main/java/com/mental/service/impl/AssessmentServiceImpl.java`：

```java
@Service
@RequiredArgsConstructor
public class AssessmentServiceImpl implements AssessmentService {
    
    // 添加依赖
    private final WarningTriggerService warningTriggerService;
    
    @Override
    @Transactional
    public ReportVO submitAssessment(AssessmentSubmitDTO dto) {
        Scale scale = scaleMapper.selectById(dto.getScaleId());
        if (scale == null) {
            throw new BusinessException(ResultCode.SCALE_NOT_FOUND);
        }
        
        int totalScore = 0;
        for (AssessmentSubmitDTO.AnswerItem item : dto.getAnswers()) {
            totalScore += item.getAnswer();
        }
        
        String riskLevel = calculateRiskLevel(scale, totalScore);
        
        Assessment assessment = new Assessment();
        assessment.setUserId(getCurrentUserId());
        assessment.setScaleId(dto.getScaleId());
        assessment.setTotalScore(BigDecimal.valueOf(totalScore));
        assessment.setRiskLevel(riskLevel);
        assessmentMapper.insert(assessment);
        
        for (AssessmentSubmitDTO.AnswerItem item : dto.getAnswers()) {
            AssessmentAnswer answer = new AssessmentAnswer();
            answer.setAssessmentId(assessment.getId());
            answer.setQuestionId(item.getQuestionId());
            answer.setAnswer(item.getAnswer());
            answerMapper.insert(answer);
        }
        
        // ✅ 新增：根据风险等级触发预警
        Long userId = getCurrentUserId();
        if ("high".equals(riskLevel)) {
            warningTriggerService.triggerWarning(
                userId, 
                "high", 
                "assessment", 
                String.format("测评得分: %d, 量表: %s, 风险等级: 高", totalScore, scale.getName())
            );
        } else if ("medium".equals(riskLevel)) {
            warningTriggerService.triggerWarning(
                userId, 
                "medium", 
                "assessment", 
                String.format("测评得分: %d, 量表: %s, 风险等级: 中", totalScore, scale.getName())
            );
        }
        
        return buildReport(assessment, scale, totalScore);
    }
    
    // ... 其他方法保持不变
}
```

**步骤3：在情绪日记创建时触发预警**

修改 `backend/src/main/java/com/mental/service/impl/DiaryServiceImpl.java`：

```java
@Service
@RequiredArgsConstructor
public class DiaryServiceImpl implements DiaryService {
    
    // 添加依赖
    private final WarningTriggerService warningTriggerService;
    
    @Override
    public DiaryVO create(DiaryDTO dto) {
        EmotionDiary diary = new EmotionDiary();
        diary.setUserId(getCurrentUserId());
        diary.setEmotionType(dto.getEmotionType());
        diary.setEmotionScore(dto.getEmotionScore());
        diary.setContent(dto.getContent());
        
        BigDecimal sentimentScore = null;
        try {
            Map<String, Object> emotionResult = pythonAiService.analyzeEmotion(dto.getContent());
            Object sentimentScoreObj = emotionResult.get("sentiment_score");
            
            if (sentimentScoreObj != null) {
                sentimentScore = new BigDecimal(sentimentScoreObj.toString());
                diary.setSentimentScore(sentimentScore);
            }
            
            // ✅ 新增：检测危机关键词
            Boolean crisisDetected = (Boolean) emotionResult.get("crisis_detected");
            if (Boolean.TRUE.equals(crisisDetected)) {
                warningTriggerService.triggerWarning(
                    getCurrentUserId(),
                    "high",
                    "diary",
                    "日记内容检测到危机信号: " + dto.getContent().substring(0, Math.min(100, dto.getContent().length()))
                );
            }
        } catch (Exception e) {
            log.warn("情感分析失败，使用默认值: {}", e.getMessage());
        }
        
        diaryMapper.insert(diary);
        
        // ✅ 新增：情感分数持续偏低触发预警
        if (sentimentScore != null && sentimentScore.compareTo(new BigDecimal("0.3")) < 0) {
            // 检查最近3天的平均情感分数
            BigDecimal avgScore = getRecentAvgSentimentScore(getCurrentUserId(), 3);
            if (avgScore.compareTo(new BigDecimal("0.35")) < 0) {
                warningTriggerService.triggerWarning(
                    getCurrentUserId(),
                    "medium",
                    "diary",
                    String.format("近期情绪持续低落，平均情感分数: %.2f", avgScore.doubleValue())
                );
            }
        }
        
        return BeanUtil.copyProperties(diary, DiaryVO.class);
    }
    
    /**
     * 获取最近N天的平均情感分数
     */
    private BigDecimal getRecentAvgSentimentScore(Long userId, int days) {
        LocalDateTime startTime = LocalDate.now().minusDays(days).atStartOfDay();
        
        LambdaQueryWrapper<EmotionDiary> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(EmotionDiary::getUserId, userId)
               .ge(EmotionDiary::getCreatedAt, startTime)
               .isNotNull(EmotionDiary::getSentimentScore);
        
        List<EmotionDiary> diaries = diaryMapper.selectList(wrapper);
        
        if (diaries.isEmpty()) {
            return new BigDecimal("0.5");
        }
        
        double avg = diaries.stream()
            .filter(d -> d.getSentimentScore() != null)
            .mapToDouble(d -> d.getSentimentScore().doubleValue())
            .average()
            .orElse(0.5);
        
        return BigDecimal.valueOf(avg);
    }
    
    // ... 其他方法保持不变
}
```

**步骤4：在 AI 对话时触发预警**

修改 `backend/src/main/java/com/mental/service/impl/ChatServiceImpl.java`：

```java
@Service
@RequiredArgsConstructor
public class ChatServiceImpl implements ChatService {
    
    // 添加依赖
    private final WarningTriggerService warningTriggerService;
    
    @Override
    public ChatMessageVO sendMessage(ChatDTO dto) {
        Long userId = getCurrentUserId();
        
        // ... 现有的会话创建逻辑
        
        // ✅ 新增：检测危机关键词
        if (containsCrisisKeywords(dto.getMessage())) {
            warningTriggerService.triggerWarning(
                userId,
                "high",
                "chat",
                "对话内容检测到危机信号: " + dto.getMessage().substring(0, Math.min(100, dto.getMessage().length()))
            );
        }
        
        // ... 现有的消息保存和AI调用逻辑
        
        return vo;
    }
    
    /**
     * 检测危机关键词
     */
    private boolean containsCrisisKeywords(String message) {
        if (message == null) return false;
        
        String[] crisisKeywords = {
            "自杀", "想死", "不想活", "活着没意思", "结束生命",
            "自残", "伤害自己", "跳楼", "割腕", "服药自杀",
            "活不下去", "没有希望", "绝望", "解脱"
        };
        
        String lowerMessage = message.toLowerCase();
        for (String keyword : crisisKeywords) {
            if (lowerMessage.contains(keyword)) {
                return true;
            }
        }
        return false;
    }
    
    // ... 其他方法保持不变
}
```

**步骤5：修改 AI 服务返回危机检测结果**

修改 `ai-service/services/chat_service.py`，确保返回危机检测标志：

```python
def reply_with_context(self, message, context=None, user_id=None, language='auto'):
    detected_language = self._detect_language(message) if language == 'auto' else language
    
    # 危机检测
    crisis_detected = self._detect_crisis(message, detected_language)
    
    if crisis_detected:
        return {
            'reply': self.crisis_response.get(detected_language, self.crisis_response['zh']),
            'confidence': 1.0,
            'crisis_detected': True,  # 明确返回危机标志
            'need_human_support': True,
            'language': detected_language
        }
    
    # ... 其他逻辑
    
    return {
        "reply": content,
        "confidence": 0.95,
        "crisis_detected": False,  # 明确返回无危机
        "language": language
    }
```

**步骤6：修改后端 PythonAiService 解析危机标志**

修改 `backend/src/main/java/com/mental/service/impl/PythonAiServiceImpl.java`：

```java
@Override
public Map<String, Object> chatWithContextAndMeta(String message, List<Map<String, String>> context, Long userId) {
    try {
        String url = pythonUrl + "/api/chat/reply_with_context";
        
        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("message", message);
        requestBody.put("context", context);
        requestBody.put("user_id", userId);
        requestBody.put("language", "auto");
        
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        
        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);
        
        ResponseEntity<Map> response = restTemplate.postForEntity(url, entity, Map.class);
        
        if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
            return response.getBody();  // 返回完整结果，包含 crisis_detected
        }
    } catch (Exception e) {
        log.error("调用AI服务失败: {}", e.getMessage());
    }
    
    return Map.of("reply", "抱歉，我现在无法回应，请稍后再试。", "crisis_detected", false);
}
```

#### 验证方法

1. **测试测评预警**：
   - 完成 PHQ-9 测评，得分 > 20
   - 检查 `warning` 表是否有新记录
   - 检查管理员是否收到 WebSocket 通知

2. **测试日记预警**：
   - 创建包含"自杀"关键词的日记
   - 检查预警是否触发
   - 连续3天创建低情感分数日记，检查预警

3. **测试对话预警**：
   - 发送包含危机关键词的消息
   - 检查预警是否触发
   - 检查 AI 是否返回危机响应

---

## 🟡 P1 级别问题（尽快优化）

---

### 问题 3：测评报告内容单薄

#### 问题描述

**当前状态**：

查看 `backend/src/main/java/com/mental/service/impl/AssessmentServiceImpl.java` 第 160-184 行：

```java
private ReportVO buildReport(Assessment assessment, Scale scale, int totalScore) {
    ReportVO vo = new ReportVO();
    vo.setAssessmentId(assessment.getId());
    vo.setScaleName(scale.getName());
    vo.setTotalScore(BigDecimal.valueOf(totalScore));
    vo.setRiskLevel(assessment.getRiskLevel());
    // ❌ 只有基本信息，缺乏深度分析
    return vo;
}
```

**问题影响**：
- 用户获得的信息有限，价值感低
- 无法了解各维度表现
- 缺乏历史对比和趋势分析
- 缺乏个性化建议

**竞品对比**：
| 产品 | 报告内容 |
|------|---------|
| 心境奇旅 | 多维度分析 + 趋势对比 + AI建议 + 资源推荐 |
| 平安科技 | AI智能解读 + 个性化干预方案 |
| MindGuard | 仅基础分数和风险等级 |

#### 解决方案

**步骤1：扩展 ReportVO 类**

修改 `backend/src/main/java/com/mental/vo/ReportVO.java`：

```java
package com.mental.vo;

import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Data
public class ReportVO {
    // 现有字段
    private Long assessmentId;
    private Long scaleId;
    private String scaleName;
    private BigDecimal totalScore;
    private String riskLevel;
    private String riskText;
    private LocalDateTime createdAt;
    
    // 新增字段
    private Map<String, Integer> dimensions;           // 各维度得分
    private List<DimensionAnalysis> dimensionAnalysis;  // 维度分析
    private TrendComparison trendComparison;            // 历史趋势对比
    private String aiSuggestion;                        // AI个性化建议
    private List<ResourceRecommendation> resources;     // 推荐资源
    private String interpretation;                      // 专业解读
    
    @Data
    public static class DimensionAnalysis {
        private String name;           // 维度名称
        private Integer score;         // 得分
        private Integer maxScore;      // 满分
        private String level;          // 等级
        private String description;    // 描述
        private String suggestion;     // 建议
    }
    
    @Data
    public static class TrendComparison {
        private BigDecimal previousScore;    // 上次得分
        private BigDecimal scoreChange;      // 分数变化
        private String trend;                // 趋势 (improved/declined/stable)
        private List<ScorePoint> history;    // 历史记录
    }
    
    @Data
    public static class ScorePoint {
        private LocalDateTime date;
        private BigDecimal score;
        private String riskLevel;
    }
    
    @Data
    public static class ResourceRecommendation {
        private Long id;
        private String type;        // article/exercise/hotline
        private String title;
        private String description;
        private String url;
    }
}
```

**步骤2：修改 buildReport 方法**

修改 `backend/src/main/java/com/mental/service/impl/AssessmentServiceImpl.java`：

```java
@RequiredArgsConstructor
public class AssessmentServiceImpl implements AssessmentService {
    
    private final ScaleMapper scaleMapper;
    private final QuestionMapper questionMapper;
    private final AssessmentMapper assessmentMapper;
    private final AssessmentAnswerMapper answerMapper;
    private final UserMapper userMapper;
    private final PythonAiService pythonAiService;  // 新增
    private final ArticleMapper articleMapper;      // 新增
    
    private ReportVO buildReport(Assessment assessment, Scale scale, int totalScore) {
        ReportVO vo = new ReportVO();
        
        // 基础信息
        vo.setAssessmentId(assessment.getId());
        vo.setScaleId(scale.getId());
        vo.setScaleName(scale.getName());
        vo.setTotalScore(BigDecimal.valueOf(totalScore));
        vo.setRiskLevel(assessment.getRiskLevel());
        vo.setCreatedAt(assessment.getCreatedAt());
        
        // 1. 解析基础解读
        String interpretation = scale.getInterpretation();
        if (StrUtil.isNotBlank(interpretation)) {
            JSONArray rules = JSONUtil.parseArray(interpretation);
            for (int i = 0; i < rules.size(); i++) {
                cn.hutool.json.JSONObject rule = rules.getJSONObject(i);
                int min = rule.getInt("min", 0);
                int max = rule.getInt("max", Integer.MAX_VALUE);
                if (totalScore >= min && totalScore <= max) {
                    vo.setRiskText(rule.getStr("text", ""));
                    break;
                }
            }
        }
        
        // 2. 维度分析（针对 PHQ-9 等量表）
        if (scale.getId() == 1) { // PHQ-9
            vo.setDimensions(analyzePHQ9Dimensions(assessment.getId()));
            vo.setDimensionAnalysis(getPHQ9DimensionAnalysis(vo.getDimensions(), totalScore));
        } else if (scale.getId() == 2) { // GAD-7
            vo.setDimensions(analyzeGAD7Dimensions(assessment.getId()));
        }
        
        // 3. 历史趋势对比
        vo.setTrendComparison(getTrendComparison(assessment.getUserId(), scale.getId(), totalScore));
        
        // 4. AI 个性化建议
        vo.setAiSuggestion(generateAiSuggestion(scale, totalScore, assessment.getRiskLevel(), vo.getDimensions()));
        
        // 5. 推荐资源
        vo.setResources(getRecommendedResources(assessment.getRiskLevel()));
        
        return vo;
    }
    
    /**
     * 分析 PHQ-9 各维度得分
     * PHQ-9 可分为：情绪症状(1-2)、躯体症状(3-5)、认知症状(6-9)
     */
    private Map<String, Integer> analyzePHQ9Dimensions(Long assessmentId) {
        LambdaQueryWrapper<AssessmentAnswer> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(AssessmentAnswer::getAssessmentId, assessmentId)
               .orderByAsc(AssessmentAnswer::getQuestionId);
        
        List<AssessmentAnswer> answers = answerMapper.selectList(wrapper);
        
        Map<String, Integer> dimensions = new LinkedHashMap<>();
        
        // 情绪症状（题目1-2）
        int emotionalScore = answers.stream()
            .filter(a -> a.getQuestionId() >= 1 && a.getQuestionId() <= 2)
            .mapToInt(AssessmentAnswer::getAnswer)
            .sum();
        dimensions.put("emotional", emotionalScore);
        
        // 躯体症状（题目3-5）
        int somaticScore = answers.stream()
            .filter(a -> a.getQuestionId() >= 3 && a.getQuestionId() <= 5)
            .mapToInt(AssessmentAnswer::getAnswer)
            .sum();
        dimensions.put("somatic", somaticScore);
        
        // 认知症状（题目6-9）
        int cognitiveScore = answers.stream()
            .filter(a -> a.getQuestionId() >= 6 && a.getQuestionId() <= 9)
            .mapToInt(AssessmentAnswer::getAnswer)
            .sum();
        dimensions.put("cognitive", cognitiveScore);
        
        return dimensions;
    }
    
    /**
     * 分析 GAD-7 各维度得分
     * GAD-7 可分为：认知焦虑(1-3)、躯体焦虑(4-7)
     */
    private Map<String, Integer> analyzeGAD7Dimensions(Long assessmentId) {
        LambdaQueryWrapper<AssessmentAnswer> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(AssessmentAnswer::getAssessmentId, assessmentId)
               .orderByAsc(AssessmentAnswer::getQuestionId);
        
        List<AssessmentAnswer> answers = answerMapper.selectList(wrapper);
        
        Map<String, Integer> dimensions = new LinkedHashMap<>();
        
        // 认知焦虑（题目1-3）
        int cognitiveAnxiety = answers.stream()
            .filter(a -> a.getQuestionId() >= 1 && a.getQuestionId() <= 3)
            .mapToInt(AssessmentAnswer::getAnswer)
            .sum();
        dimensions.put("cognitive_anxiety", cognitiveAnxiety);
        
        // 躯体焦虑（题目4-7）
        int somaticAnxiety = answers.stream()
            .filter(a -> a.getQuestionId() >= 4 && a.getQuestionId() <= 7)
            .mapToInt(AssessmentAnswer::getAnswer)
            .sum();
        dimensions.put("somatic_anxiety", somaticAnxiety);
        
        return dimensions;
    }
    
    /**
     * 获取 PHQ-9 维度分析
     */
    private List<ReportVO.DimensionAnalysis> getPHQ9DimensionAnalysis(Map<String, Integer> dimensions, int totalScore) {
        List<ReportVO.DimensionAnalysis> analysis = new ArrayList<>();
        
        // 情绪症状分析
        ReportVO.DimensionAnalysis emotional = new ReportVO.DimensionAnalysis();
        emotional.setName("情绪症状");
        emotional.setScore(dimensions.get("emotional"));
        emotional.setMaxScore(6);
        emotional.setLevel(getDimensionLevel(dimensions.get("emotional"), 6));
        emotional.setDescription("包括情绪低落、兴趣减退等");
        emotional.setSuggestion(getEmotionalSuggestion(dimensions.get("emotional")));
        analysis.add(emotional);
        
        // 躯体症状分析
        ReportVO.DimensionAnalysis somatic = new ReportVO.DimensionAnalysis();
        somatic.setName("躯体症状");
        somatic.setScore(dimensions.get("somatic"));
        somatic.setMaxScore(9);
        somatic.setLevel(getDimensionLevel(dimensions.get("somatic"), 9));
        somatic.setDescription("包括睡眠问题、疲劳、食欲变化等");
        somatic.setSuggestion(getSomaticSuggestion(dimensions.get("somatic")));
        analysis.add(somatic);
        
        // 认知症状分析
        ReportVO.DimensionAnalysis cognitive = new ReportVO.DimensionAnalysis();
        cognitive.setName("认知症状");
        cognitive.setScore(dimensions.get("cognitive"));
        cognitive.setMaxScore(12);
        cognitive.setLevel(getDimensionLevel(dimensions.get("cognitive"), 12));
        cognitive.setDescription("包括自我评价低、注意力问题、消极想法等");
        cognitive.setSuggestion(getCognitiveSuggestion(dimensions.get("cognitive")));
        analysis.add(cognitive);
        
        return analysis;
    }
    
    private String getDimensionLevel(Integer score, Integer maxScore) {
        double ratio = (double) score / maxScore;
        if (ratio >= 0.7) return "严重";
        if (ratio >= 0.4) return "中度";
        if (ratio >= 0.2) return "轻度";
        return "正常";
    }
    
    private String getEmotionalSuggestion(Integer score) {
        if (score >= 4) {
            return "情绪症状较明显，建议增加愉快的活动，与亲友保持联系，必要时寻求专业帮助";
        } else if (score >= 2) {
            return "情绪有些低落，建议多参与感兴趣的活动，保持社交";
        }
        return "情绪状态良好，继续保持积极的生活态度";
    }
    
    private String getSomaticSuggestion(Integer score) {
        if (score >= 6) {
            return "躯体症状较明显，建议关注睡眠卫生，规律作息，必要时咨询医生";
        } else if (score >= 3) {
            return "有些躯体不适，建议保持规律作息，适度运动";
        }
        return "躯体状态良好，继续保持健康的生活方式";
    }
    
    private String getCognitiveSuggestion(Integer score) {
        if (score >= 8) {
            return "认知症状较明显，建议尝试认知行为疗法(CBT)技巧，寻求专业心理咨询";
        } else if (score >= 4) {
            return "有些消极想法，建议练习正念冥想，关注当下";
        }
        return "认知状态良好，保持积极的思维方式";
    }
    
    /**
     * 获取历史趋势对比
     */
    private ReportVO.TrendComparison getTrendComparison(Long userId, Long scaleId, int currentScore) {
        ReportVO.TrendComparison comparison = new ReportVO.TrendComparison();
        
        // 获取该量表的最近测评记录
        LambdaQueryWrapper<Assessment> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Assessment::getUserId, userId)
               .eq(Assessment::getScaleId, scaleId)
               .ne(Assessment::getId, getCurrentAssessmentId())  // 排除当前测评
               .orderByDesc(Assessment::getCreatedAt)
               .last("LIMIT 10");
        
        List<Assessment> history = assessmentMapper.selectList(wrapper);
        
        if (history.isEmpty()) {
            comparison.setPreviousScore(null);
            comparison.setScoreChange(null);
            comparison.setTrend("first");
            comparison.setHistory(new ArrayList<>());
            return comparison;
        }
        
        // 上次得分
        Assessment lastAssessment = history.get(0);
        comparison.setPreviousScore(lastAssessment.getTotalScore());
        
        // 分数变化
        BigDecimal change = BigDecimal.valueOf(currentScore).subtract(lastAssessment.getTotalScore());
        comparison.setScoreChange(change);
        
        // 趋势判断
        if (change.compareTo(BigDecimal.ZERO) > 0) {
            comparison.setTrend("declined");  // 分数上升，症状加重
        } else if (change.compareTo(BigDecimal.ZERO) < 0) {
            comparison.setTrend("improved");  // 分数下降，症状改善
        } else {
            comparison.setTrend("stable");
        }
        
        // 历史记录
        List<ReportVO.ScorePoint> scorePoints = new ArrayList<>();
        for (int i = Math.min(4, history.size() - 1); i >= 0; i--) {
            Assessment a = history.get(i);
            ReportVO.ScorePoint point = new ReportVO.ScorePoint();
            point.setDate(a.getCreatedAt());
            point.setScore(a.getTotalScore());
            point.setRiskLevel(a.getRiskLevel());
            scorePoints.add(point);
        }
        // 添加当前测评
        ReportVO.ScorePoint current = new ReportVO.ScorePoint();
        current.setDate(LocalDateTime.now());
        current.setScore(BigDecimal.valueOf(currentScore));
        current.setRiskLevel(getCurrentRiskLevel());
        scorePoints.add(current);
        
        comparison.setHistory(scorePoints);
        
        return comparison;
    }
    
    /**
     * 生成 AI 个性化建议
     */
    private String generateAiSuggestion(Scale scale, int totalScore, String riskLevel, Map<String, Integer> dimensions) {
        try {
            Map<String, Object> userData = new HashMap<>();
            userData.put("scale_name", scale.getName());
            userData.put("total_score", totalScore);
            userData.put("risk_level", riskLevel);
            userData.put("dimensions", dimensions);
            
            return pythonAiService.generateAssessmentSuggestion(userData);
        } catch (Exception e) {
            log.warn("AI建议生成失败: {}", e.getMessage());
            return getDefaultSuggestion(riskLevel);
        }
    }
    
    private String getDefaultSuggestion(String riskLevel) {
        return switch (riskLevel) {
            case "high" -> "您的测评结果显示需要关注心理健康。建议您尽快寻求专业心理咨询师的帮助，或拨打心理援助热线：400-161-9995";
            case "medium" -> "您的测评结果显示存在一些心理困扰。建议您关注自身情绪变化，适当进行放松活动，必要时寻求专业帮助";
            default -> "您的心理状态良好。建议继续保持健康的生活方式，定期关注心理健康";
        };
    }
    
    /**
     * 获取推荐资源
     */
    private List<ReportVO.ResourceRecommendation> getRecommendedResources(String riskLevel) {
        List<ReportVO.ResourceRecommendation> resources = new ArrayList<>();
        
        // 根据风险等级推荐文章
        LambdaQueryWrapper<Article> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Article::getStatus, 1);
        
        if ("high".equals(riskLevel)) {
            wrapper.eq(Article::getCategoryId, 1L);  // 抑郁相关
        } else if ("medium".equals(riskLevel)) {
            wrapper.eq(Article::getCategoryId, 2L);  // 焦虑相关
        } else {
            wrapper.eq(Article::getCategoryId, 5L);  // 自我成长
        }
        
        wrapper.orderByDesc(Article::getViewCount)
               .last("LIMIT 3");
        
        List<Article> articles = articleMapper.selectList(wrapper);
        
        for (Article article : articles) {
            ReportVO.ResourceRecommendation resource = new ReportVO.ResourceRecommendation();
            resource.setId(article.getId());
            resource.setType("article");
            resource.setTitle(article.getTitle());
            resource.setDescription(article.getSummary());
            resource.setUrl("/knowledge/article/" + article.getId());
            resources.add(resource);
        }
        
        // 高风险用户添加热线资源
        if ("high".equals(riskLevel)) {
            ReportVO.ResourceRecommendation hotline = new ReportVO.ResourceRecommendation();
            hotline.setType("hotline");
            hotline.setTitle("24小时心理援助热线");
            hotline.setDescription("如果您正在经历困难时刻，请拨打心理援助热线");
            hotline.setUrl("tel:400-161-9995");
            resources.add(0, hotline);  // 放在最前面
        }
        
        return resources;
    }
}
```

**步骤3：添加 AI 服务方法**

修改 `ai-service/services/chat_service.py`：

```python
def generate_assessment_suggestion(self, user_data):
    """生成测评报告的个性化建议"""
    scale_name = user_data.get('scale_name', '')
    total_score = user_data.get('total_score', 0)
    risk_level = user_data.get('risk_level', 'low')
    dimensions = user_data.get('dimensions', {})
    
    prompt = f"""作为心理健康助手，请根据以下测评结果生成个性化建议（200字以内）：

量表：{scale_name}
总分：{total_score}
风险等级：{risk_level}
各维度得分：{dimensions}

要求：
1. 用温暖、专业的语气
2. 给出具体、可操作的建议
3. 不要重复量表解读内容
4. 如有需要，提醒寻求专业帮助"""

    if not self.api_key:
        return self._get_default_suggestion(risk_level)
    
    try:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一位专业的心理健康助手，擅长根据测评结果给出个性化建议。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 300
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
    except Exception as e:
        if DEBUG:
            print(f"AI建议生成失败: {e}")
    
    return self._get_default_suggestion(risk_level)

def _get_default_suggestion(self, risk_level):
    suggestions = {
        'high': '您的测评结果显示需要关注心理健康。建议您尽快寻求专业心理咨询师的帮助，或拨打心理援助热线：400-161-9995。您不必独自面对，专业的帮助可以让您度过难关。',
        'medium': '您的测评结果显示存在一些心理困扰。建议您关注自身情绪变化，适当进行放松活动，如运动、冥想等。如果困扰持续，建议寻求专业帮助。',
        'low': '您的心理状态良好。建议继续保持健康的生活方式，保持规律作息，适度运动，与亲友保持联系，定期关注心理健康。'
    }
    return suggestions.get(risk_level, suggestions['low'])
```

**步骤4：添加后端 AI 服务接口**

修改 `backend/src/main/java/com/mental/service/PythonAiService.java`：

```java
public interface PythonAiService {
    String chat(String message);
    String chatWithContext(String message, List<Map<String, String>> context, Long userId);
    Map<String, Object> analyzeEmotion(String text);
    Map<String, Object> assessRisk(Map<String, Object> userData);
    
    // 新增
    String generateAssessmentSuggestion(Map<String, Object> userData);
}
```

修改实现类：

```java
@Override
public String generateAssessmentSuggestion(Map<String, Object> userData) {
    try {
        String url = pythonUrl + "/api/chat/assessment_suggestion";
        
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        
        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(userData, headers);
        
        ResponseEntity<Map> response = restTemplate.postForEntity(url, entity, Map.class);
        
        if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
            return (String) response.getBody().get("suggestion");
        }
    } catch (Exception e) {
        log.error("生成AI建议失败: {}", e.getMessage());
    }
    
    return "建议关注自身心理健康，必要时寻求专业帮助。";
}
```

#### 验证方法

1. 完成 PHQ-9 测评
2. 检查返回的报告是否包含：
   - 各维度得分和分析
   - 历史趋势对比
   - AI 个性化建议
   - 推荐资源列表
3. 对比多次测评的趋势变化

---

### 问题 4：用户画像数据未充分利用

#### 问题描述

**当前状态**：

数据库中 `user_profile` 表存在但未被充分使用：

```sql
CREATE TABLE `user_profile` (
  `total_assessment` INT NOT NULL DEFAULT 0,  -- 有字段但未更新
  `avg_score` DECIMAL(5,2) DEFAULT NULL,      -- 有字段但未更新
  `risk_trend` TEXT DEFAULT NULL,             -- 有字段但未更新
  `emotion_trend` TEXT DEFAULT NULL           -- 有字段但未更新
);
```

**问题影响**：
- 无法追踪用户心理状态变化
- 缺乏个性化服务基础
- 无法进行精准的风险预警

#### 解决方案

**步骤1：创建 UserProfileService**

创建 `backend/src/main/java/com/mental/service/UserProfileService.java`：

```java
package com.mental.service;

import com.mental.vo.UserProfileVO;
import java.util.Map;

public interface UserProfileService {
    
    /**
     * 获取用户完整画像
     */
    UserProfileVO getFullProfile(Long userId);
    
    /**
     * 测评后更新画像
     */
    void updateAfterAssessment(Long userId, Long assessmentId);
    
    /**
     * 日记后更新画像
     */
    void updateAfterDiary(Long userId, Long diaryId);
    
    /**
     * 获取综合风险评估
     */
    Map<String, Object> getOverallRiskAssessment(Long userId);
    
    /**
     * 获取个性化建议
     */
    String getPersonalizedSuggestions(Long userId);
}
```

**步骤2：实现 UserProfileService**

创建 `backend/src/main/java/com/mental/service/impl/UserProfileServiceImpl.java`：

```java
package com.mental.service.impl;

import cn.hutool.json.JSONUtil;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.mental.entity.*;
import com.mental.mapper.*;
import com.mental.service.UserProfileService;
import com.mental.service.PythonAiService;
import com.mental.vo.UserProfileVO;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.time.LocalDate;
import java.util.*;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class UserProfileServiceImpl implements UserProfileService {
    
    private final UserProfileMapper profileMapper;
    private final AssessmentMapper assessmentMapper;
    private final EmotionDiaryMapper diaryMapper;
    private final ChatRecordMapper chatRecordMapper;
    private final WarningMapper warningMapper;
    private final PythonAiService pythonAiService;
    
    @Override
    public UserProfileVO getFullProfile(Long userId) {
        UserProfile profile = profileMapper.selectByUserId(userId);
        
        if (profile == null) {
            profile = initProfile(userId);
        }
        
        UserProfileVO vo = new UserProfileVO();
        
        // 基本信息
        vo.setUserId(userId);
        vo.setTotalAssessment(profile.getTotalAssessment());
        vo.setAvgScore(profile.getAvgScore());
        vo.setLastAssessmentAt(profile.getLastAssessmentAt());
        
        // 风险趋势分析
        vo.setRiskTrendAnalysis(analyzeRiskTrend(profile.getRiskTrend()));
        
        // 情绪趋势分析
        vo.setEmotionTrendAnalysis(analyzeEmotionTrend(userId));
        
        // 综合风险评估
        vo.setOverallRiskLevel(calculateOverallRisk(userId));
        
        // 活跃度分析
        vo.setActivityAnalysis(analyzeActivity(userId));
        
        // 个性化建议
        vo.setPersonalizedSuggestions(generatePersonalizedSuggestions(userId, vo));
        
        return vo;
    }
    
    @Override
    @Transactional
    public void updateAfterAssessment(Long userId, Long assessmentId) {
        UserProfile profile = getOrCreateProfile(userId);
        Assessment assessment = assessmentMapper.selectById(assessmentId);
        
        if (assessment == null) return;
        
        // 更新测评次数
        profile.setTotalAssessment(profile.getTotalAssessment() + 1);
        
        // 更新平均分
        BigDecimal avgScore = calculateAvgAssessmentScore(userId);
        profile.setAvgScore(avgScore);
        
        // 更新风险趋势
        List<Assessment> recent = getRecentAssessments(userId, 10);
        List<Map<String, Object>> trend = recent.stream()
            .map(a -> {
                Map<String, Object> item = new HashMap<>();
                item.put("date", a.getCreatedAt().toString());
                item.put("risk_level", a.getRiskLevel());
                item.put("score", a.getTotalScore());
                return item;
            })
            .collect(Collectors.toList());
        profile.setRiskTrend(JSONUtil.toJsonStr(trend));
        
        // 更新最后测评时间
        profile.setLastAssessmentAt(LocalDateTime.now());
        
        profileMapper.updateById(profile);
        log.info("更新用户画像: userId={}, totalAssessment={}", userId, profile.getTotalAssessment());
    }
    
    @Override
    @Transactional
    public void updateAfterDiary(Long userId, Long diaryId) {
        UserProfile profile = getOrCreateProfile(userId);
        EmotionDiary diary = diaryMapper.selectById(diaryId);
        
        if (diary == null) return;
        
        // 更新情绪趋势
        List<EmotionDiary> recent = getRecentDiaries(userId, 30);
        List<Map<String, Object>> trend = recent.stream()
            .map(d -> {
                Map<String, Object> item = new HashMap<>();
                item.put("date", d.getCreatedAt().toLocalDate().toString());
                item.put("emotion_type", d.getEmotionType());
                item.put("emotion_score", d.getEmotionScore());
                item.put("sentiment_score", d.getSentimentScore());
                return item;
            })
            .collect(Collectors.toList());
        profile.setEmotionTrend(JSONUtil.toJsonStr(trend));
        
        profileMapper.updateById(profile);
    }
    
    @Override
    public Map<String, Object> getOverallRiskAssessment(Long userId) {
        Map<String, Object> result = new HashMap<>();
        
        // 1. 测评风险
        Assessment latestAssessment = getLatestAssessment(userId);
        String assessmentRisk = latestAssessment != null ? latestAssessment.getRiskLevel() : "unknown";
        
        // 2. 情绪风险
        BigDecimal avgSentiment = getAvgSentimentScore(userId, 7);
        String emotionRisk = getEmotionRisk(avgSentiment);
        
        // 3. 对话风险（检测危机词频率）
        int crisisCount = getCrisisKeywordCount(userId, 30);
        String chatRisk = crisisCount > 0 ? "high" : "low";
        
        // 4. 综合风险
        String overallRisk = calculateOverallRiskLevel(assessmentRisk, emotionRisk, chatRisk);
        
        result.put("assessment_risk", assessmentRisk);
        result.put("emotion_risk", emotionRisk);
        result.put("chat_risk", chatRisk);
        result.put("overall_risk", overallRisk);
        result.put("crisis_count_30d", crisisCount);
        
        // 风险因素
        List<String> riskFactors = new ArrayList<>();
        if ("high".equals(assessmentRisk)) {
            riskFactors.add("测评结果显示高风险");
        }
        if ("high".equals(emotionRisk)) {
            riskFactors.add("近期情绪持续低落");
        }
        if (crisisCount > 0) {
            riskFactors.add("对话中检测到危机信号");
        }
        result.put("risk_factors", riskFactors);
        
        return result;
    }
    
    @Override
    public String getPersonalizedSuggestions(Long userId) {
        UserProfileVO profile = getFullProfile(userId);
        return generatePersonalizedSuggestions(userId, profile);
    }
    
    // ==================== 私有方法 ====================
    
    private UserProfile initProfile(Long userId) {
        UserProfile profile = new UserProfile();
        profile.setUserId(userId);
        profile.setTotalAssessment(0);
        profile.setAvgScore(null);
        profile.setRiskTrend("[]");
        profile.setEmotionTrend("[]");
        profileMapper.insert(profile);
        return profile;
    }
    
    private UserProfile getOrCreateProfile(Long userId) {
        UserProfile profile = profileMapper.selectByUserId(userId);
        if (profile == null) {
            profile = initProfile(userId);
        }
        return profile;
    }
    
    private BigDecimal calculateAvgAssessmentScore(Long userId) {
        LambdaQueryWrapper<Assessment> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Assessment::getUserId, userId);
        
        List<Assessment> assessments = assessmentMapper.selectList(wrapper);
        
        if (assessments.isEmpty()) {
            return null;
        }
        
        double avg = assessments.stream()
            .mapToDouble(a -> a.getTotalScore().doubleValue())
            .average()
            .orElse(0);
        
        return BigDecimal.valueOf(avg).setScale(2, RoundingMode.HALF_UP);
    }
    
    private List<Assessment> getRecentAssessments(Long userId, int limit) {
        LambdaQueryWrapper<Assessment> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Assessment::getUserId, userId)
               .orderByDesc(Assessment::getCreatedAt)
               .last("LIMIT " + limit);
        return assessmentMapper.selectList(wrapper);
    }
    
    private List<EmotionDiary> getRecentDiaries(Long userId, int limit) {
        LambdaQueryWrapper<EmotionDiary> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(EmotionDiary::getUserId, userId)
               .orderByDesc(EmotionDiary::getCreatedAt)
               .last("LIMIT " + limit);
        return diaryMapper.selectList(wrapper);
    }
    
    private Assessment getLatestAssessment(Long userId) {
        LambdaQueryWrapper<Assessment> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Assessment::getUserId, userId)
               .orderByDesc(Assessment::getCreatedAt)
               .last("LIMIT 1");
        return assessmentMapper.selectOne(wrapper);
    }
    
    private BigDecimal getAvgSentimentScore(Long userId, int days) {
        LocalDateTime startTime = LocalDate.now().minusDays(days).atStartOfDay();
        
        LambdaQueryWrapper<EmotionDiary> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(EmotionDiary::getUserId, userId)
               .ge(EmotionDiary::getCreatedAt, startTime)
               .isNotNull(EmotionDiary::getSentimentScore);
        
        List<EmotionDiary> diaries = diaryMapper.selectList(wrapper);
        
        if (diaries.isEmpty()) {
            return new BigDecimal("0.5");
        }
        
        double avg = diaries.stream()
            .filter(d -> d.getSentimentScore() != null)
            .mapToDouble(d -> d.getSentimentScore().doubleValue())
            .average()
            .orElse(0.5);
        
        return BigDecimal.valueOf(avg).setScale(2, RoundingMode.HALF_UP);
    }
    
    private String getEmotionRisk(BigDecimal avgSentiment) {
        if (avgSentiment == null) return "unknown";
        if (avgSentiment.compareTo(new BigDecimal("0.3")) < 0) return "high";
        if (avgSentiment.compareTo(new BigDecimal("0.45")) < 0) return "medium";
        return "low";
    }
    
    private int getCrisisKeywordCount(Long userId, int days) {
        // 查询预警记录中该用户的危机预警数量
        LocalDateTime startTime = LocalDate.now().minusDays(days).atStartOfDay();
        
        LambdaQueryWrapper<Warning> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Warning::getUserId, userId)
               .eq(Warning::getRiskLevel, "high")
               .ge(Warning::getCreatedAt, startTime);
        
        return Math.toIntExact(warningMapper.selectCount(wrapper));
    }
    
    private String calculateOverallRiskLevel(String assessmentRisk, String emotionRisk, String chatRisk) {
        int maxRisk = Math.max(
            getRiskScore(assessmentRisk),
            Math.max(getRiskScore(emotionRisk), getRiskScore(chatRisk))
        );
        
        return switch (maxRisk) {
            case 3 -> "high";
            case 2 -> "medium";
            default -> "low";
        };
    }
    
    private int getRiskScore(String level) {
        return switch (level) {
            case "high" -> 3;
            case "medium" -> 2;
            default -> 1;
        };
    }
    
    private String calculateOverallRisk(Long userId) {
        Map<String, Object> assessment = getOverallRiskAssessment(userId);
        return (String) assessment.get("overall_risk");
    }
    
    private Map<String, Object> analyzeRiskTrend(String riskTrendJson) {
        Map<String, Object> result = new HashMap<>();
        
        if (riskTrendJson == null || riskTrendJson.isEmpty()) {
            result.put("trend", "unknown");
            result.put("data", new ArrayList<>());
            return result;
        }
        
        try {
            List<Map> trend = JSONUtil.toList(riskTrendJson, Map.class);
            result.put("data", trend);
            
            if (trend.size() < 2) {
                result.put("trend", "insufficient_data");
                return result;
            }
            
            // 分析趋势
            String firstLevel = (String) trend.get(0).get("risk_level");
            String lastLevel = (String) trend.get(trend.size() - 1).get("risk_level");
            
            int firstScore = getRiskScore(firstLevel);
            int lastScore = getRiskScore(lastLevel);
            
            if (lastScore > firstScore) {
                result.put("trend", "worsening");
            } else if (lastScore < firstScore) {
                result.put("trend", "improving");
            } else {
                result.put("trend", "stable");
            }
            
        } catch (Exception e) {
            result.put("trend", "error");
        }
        
        return result;
    }
    
    private Map<String, Object> analyzeEmotionTrend(Long userId) {
        Map<String, Object> result = new HashMap<>();
        
        List<EmotionDiary> diaries = getRecentDiaries(userId, 30);
        
        if (diaries.isEmpty()) {
            result.put("trend", "no_data");
            return result;
        }
        
        // 计算平均情绪分数
        double avgEmotionScore = diaries.stream()
            .mapToInt(EmotionDiary::getEmotionScore)
            .average()
            .orElse(5.0);
        
        // 计算平均情感分数
        double avgSentiment = diaries.stream()
            .filter(d -> d.getSentimentScore() != null)
            .mapToDouble(d -> d.getSentimentScore().doubleValue())
            .average()
            .orElse(0.5);
        
        // 情绪分布
        Map<String, Long> distribution = diaries.stream()
            .collect(Collectors.groupingBy(EmotionDiary::getEmotionType, Collectors.counting()));
        
        // 主导情绪
        String dominantEmotion = distribution.entrySet().stream()
            .max(Map.Entry.comparingByValue())
            .map(Map.Entry::getKey)
            .orElse("unknown");
        
        result.put("avg_emotion_score", avgEmotionScore);
        result.put("avg_sentiment_score", avgSentiment);
        result.put("emotion_distribution", distribution);
        result.put("dominant_emotion", dominantEmotion);
        result.put("diary_count", diaries.size());
        
        return result;
    }
    
    private Map<String, Object> analyzeActivity(Long userId) {
        Map<String, Object> result = new HashMap<>();
        
        LocalDateTime weekAgo = LocalDate.now().minusDays(7).atStartOfDay();
        
        // 本周测评次数
        LambdaQueryWrapper<Assessment> assessmentWrapper = new LambdaQueryWrapper<>();
        assessmentWrapper.eq(Assessment::getUserId, userId)
                        .ge(Assessment::getCreatedAt, weekAgo);
        long assessmentCount = assessmentMapper.selectCount(assessmentWrapper);
        
        // 本周日记次数
        LambdaQueryWrapper<EmotionDiary> diaryWrapper = new LambdaQueryWrapper<>();
        diaryWrapper.eq(EmotionDiary::getUserId, userId)
                   .ge(EmotionDiary::getCreatedAt, weekAgo);
        long diaryCount = diaryMapper.selectCount(diaryWrapper);
        
        // 本周对话次数
        LambdaQueryWrapper<ChatRecord> chatWrapper = new LambdaQueryWrapper<>();
        chatWrapper.eq(ChatRecord::getUserId, userId)
                  .eq(ChatRecord::getRole, "user")
                  .ge(ChatRecord::getCreatedAt, weekAgo);
        long chatCount = chatRecordMapper.selectCount(chatWrapper);
        
        result.put("weekly_assessments", assessmentCount);
        result.put("weekly_diaries", diaryCount);
        result.put("weekly_chats", chatCount);
        result.put("total_activity", assessmentCount + diaryCount + chatCount);
        
        // 活跃度评级
        int totalActivity = (int) (assessmentCount + diaryCount + chatCount);
        String activityLevel = totalActivity >= 10 ? "high" : 
                              totalActivity >= 5 ? "medium" : 
                              totalActivity >= 1 ? "low" : "inactive";
        result.put("activity_level", activityLevel);
        
        return result;
    }
    
    private String generatePersonalizedSuggestions(Long userId, UserProfileVO profile) {
        List<String> suggestions = new ArrayList<>();
        
        // 基于活跃度
        String activityLevel = (String) profile.getActivityAnalysis().get("activity_level");
        if ("inactive".equals(activityLevel)) {
            suggestions.add("您有一段时间没有使用系统了，建议定期记录情绪，关注心理健康");
        }
        
        // 基于风险等级
        String overallRisk = profile.getOverallRiskLevel();
        if ("high".equals(overallRisk)) {
            suggestions.add("建议您尽快寻求专业心理咨询师的帮助，或拨打心理援助热线：400-161-9995");
        } else if ("medium".equals(overallRisk)) {
            suggestions.add("建议增加情绪记录频率，尝试放松练习，必要时寻求专业帮助");
        }
        
        // 基于情绪趋势
        String emotionTrend = (String) profile.getEmotionTrendAnalysis().get("trend");
        if ("worsening".equals(emotionTrend)) {
            suggestions.add("近期情绪有所波动，建议多参与愉快的活动，与亲友保持联系");
        }
        
        // 基于测评情况
        if (profile.getTotalAssessment() == 0) {
            suggestions.add("建议完成心理测评，了解自己的心理状态");
        } else if (profile.getLastAssessmentAt() != null && 
                   profile.getLastAssessmentAt().isBefore(LocalDateTime.now().minusDays(30))) {
            suggestions.add("距离上次测评已超过30天，建议重新测评追踪心理状态变化");
        }
        
        if (suggestions.isEmpty()) {
            suggestions.add("继续保持良好的心理健康习惯，定期关注自己的心理状态");
        }
        
        return String.join("\n", suggestions);
    }
}
```

**步骤3：在测评和日记服务中调用画像更新**

修改 `AssessmentServiceImpl.java`：

```java
@Service
@RequiredArgsConstructor
public class AssessmentServiceImpl implements AssessmentService {
    
    private final UserProfileService userProfileService;  // 新增
    
    @Override
    @Transactional
    public ReportVO submitAssessment(AssessmentSubmitDTO dto) {
        // ... 现有逻辑
        
        assessmentMapper.insert(assessment);
        
        // 新增：更新用户画像
        userProfileService.updateAfterAssessment(getCurrentUserId(), assessment.getId());
        
        // ... 其余逻辑
    }
}
```

修改 `DiaryServiceImpl.java`：

```java
@Service
@RequiredArgsConstructor
public class DiaryServiceImpl implements DiaryService {
    
    private final UserProfileService userProfileService;  // 新增
    
    @Override
    public DiaryVO create(DiaryDTO dto) {
        // ... 现有逻辑
        
        diaryMapper.insert(diary);
        
        // 新增：更新用户画像
        userProfileService.updateAfterDiary(getCurrentUserId(), diary.getId());
        
        return BeanUtil.copyProperties(diary, DiaryVO.class);
    }
}
```

**步骤4：创建用户画像 VO**

创建 `backend/src/main/java/com/mental/vo/UserProfileVO.java`：

```java
package com.mental.vo;

import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Data
public class UserProfileVO {
    private Long userId;
    private Integer totalAssessment;
    private BigDecimal avgScore;
    private LocalDateTime lastAssessmentAt;
    
    private Map<String, Object> riskTrendAnalysis;
    private Map<String, Object> emotionTrendAnalysis;
    private Map<String, Object> activityAnalysis;
    
    private String overallRiskLevel;
    private String personalizedSuggestions;
    
    // 详细数据
    private List<AssessmentRecord> recentAssessments;
    private List<DiaryRecord> recentDiaries;
    
    @Data
    public static class AssessmentRecord {
        private LocalDateTime date;
        private String scaleName;
        private BigDecimal score;
        private String riskLevel;
    }
    
    @Data
    public static class DiaryRecord {
        private LocalDateTime date;
        private String emotionType;
        private Integer emotionScore;
        private BigDecimal sentimentScore;
    }
}
```

#### 验证方法

1. 完成测评后检查 `user_profile` 表是否更新
2. 创建日记后检查 `emotion_trend` 字段
3. 调用 `/api/user/profile` 接口查看完整画像
4. 验证综合风险评估是否正确计算

---

### 问题 5：测评缺乏个性化推荐

#### 问题描述

**当前状态**：

用户需要自己从量表列表中选择，没有智能推荐机制。

**竞品做法**：
- 平安科技专利：基于 AI 分析用户状态，推荐最适合的量表
- 心境奇旅：根据情绪记录推荐相关测评

#### 解决方案

**步骤1：添加推荐服务方法**

修改 `backend/src/main/java/com/mental/service/AssessmentService.java`：

```java
public interface AssessmentService {
    // 现有方法...
    
    /**
     * 获取个性化推荐的量表
     */
    List<ScaleVO> getRecommendedScales(Long userId);
    
    /**
     * 获取推荐理由
     */
    Map<Long, String> getRecommendationReasons(Long userId);
}
```

**步骤2：实现推荐逻辑**

修改 `backend/src/main/java/com/mental/service/impl/AssessmentServiceImpl.java`：

```java
@Override
public List<ScaleVO> getRecommendedScales(Long userId) {
    List<ScaleVO> recommendations = new ArrayList<>();
    
    // 1. 获取用户画像信息
    Map<String, Object> emotionAnalysis = userProfileService.getEmotionTrendAnalysis(userId);
    String dominantEmotion = (String) emotionAnalysis.get("dominant_emotion");
    Double avgSentiment = (Double) emotionAnalysis.get("avg_sentiment_score");
    
    // 2. 获取用户历史测评
    List<Assessment> history = getRecentAssessments(userId, 10);
    Set<Long> assessedScaleIds = history.stream()
        .map(Assessment::getScaleId)
        .collect(Collectors.toSet());
    
    // 3. 获取最近测评的风险等级
    String lastRiskLevel = history.isEmpty() ? null : history.get(0).getRiskLevel();
    
    // 4. 基于规则推荐
    List<Scale> candidates = new ArrayList<>();
    
    // 规则1：基于主导情绪
    if ("sad".equals(dominantEmotion) || "depressed".equals(dominantEmotion)) {
        candidates.addAll(getScalesByCategory("depression"));
    }
    if ("anxious".equals(dominantEmotion) || "fear".equals(dominantEmotion)) {
        candidates.addAll(getScalesByCategory("anxiety"));
    }
    if ("stressed".equals(dominantEmotion)) {
        candidates.addAll(getScalesByCategory("stress"));
    }
    
    // 规则2：基于情感分数
    if (avgSentiment != null && avgSentiment < 0.4) {
        // 情感分数低，推荐抑郁和焦虑量表
        candidates.addAll(getScalesByCategory("depression"));
        candidates.addAll(getScalesByCategory("anxiety"));
    }
    
    // 规则3：基于上次测评风险
    if ("high".equals(lastRiskLevel) || "medium".equals(lastRiskLevel)) {
        // 高风险用户推荐更全面的量表
        candidates.addAll(getScalesByCategory("depression"));
        candidates.addAll(getScalesByCategory("anxiety"));
    }
    
    // 规则4：如果用户从未测评，推荐基础量表
    if (history.isEmpty()) {
        candidates.add(scaleMapper.selectById(1L)); // PHQ-9
        candidates.add(scaleMapper.selectById(2L)); // GAD-7
    }
    
    // 规则5：定期复测提醒（超过30天未测评的量表）
    for (Assessment a : history) {
        if (a.getCreatedAt().isBefore(LocalDateTime.now().minusDays(30))) {
            Scale scale = scaleMapper.selectById(a.getScaleId());
            if (scale != null) {
                candidates.add(scale);
            }
        }
    }
    
    // 5. 去重并排序
    recommendations = candidates.stream()
        .distinct()
        .filter(s -> s != null && s.getStatus() == 1)
        .map(s -> {
            ScaleVO vo = BeanUtil.copyProperties(s, ScaleVO.class);
            vo.setRecommendationReason(getRecommendationReason(s.getId(), dominantEmotion, avgSentiment, history));
            return vo;
        })
        .sorted((a, b) -> {
            // 优先推荐未测评过的
            boolean aAssessed = assessedScaleIds.contains(a.getId());
            boolean bAssessed = assessedScaleIds.contains(b.getId());
            if (aAssessed != bAssessed) {
                return aAssessed ? 1 : -1;
            }
            return 0;
        })
        .limit(5)
        .collect(Collectors.toList());
    
    return recommendations;
}

private List<Scale> getScalesByCategory(String category) {
    LambdaQueryWrapper<Scale> wrapper = new LambdaQueryWrapper<>();
    wrapper.eq(Scale::getCategory, category)
           .eq(Scale::getStatus, 1);
    return scaleMapper.selectList(wrapper);
}

private String getRecommendationReason(Long scaleId, String dominantEmotion, Double avgSentiment, List<Assessment> history) {
    Scale scale = scaleMapper.selectById(scaleId);
    if (scale == null) return "";
    
    // 检查是否需要复测
    for (Assessment a : history) {
        if (a.getScaleId().equals(scaleId) && 
            a.getCreatedAt().isBefore(LocalDateTime.now().minusDays(30))) {
            return "距离上次测评已超过30天，建议复测追踪变化";
        }
    }
    
    // 基于情绪推荐
    if ("depression".equals(scale.getCategory())) {
        if ("sad".equals(dominantEmotion) || "depressed".equals(dominantEmotion)) {
            return "根据您近期的情绪状态，建议了解抑郁相关指标";
        }
        if (avgSentiment != null && avgSentiment < 0.4) {
            return "您的情感分数偏低，建议评估抑郁症状";
        }
    }
    
    if ("anxiety".equals(scale.getCategory())) {
        if ("anxious".equals(dominantEmotion) || "fear".equals(dominantEmotion)) {
            return "根据您近期的情绪状态，建议了解焦虑相关指标";
        }
    }
    
    if ("stress".equals(scale.getCategory())) {
        if ("stressed".equals(dominantEmotion)) {
            return "根据您近期的情绪状态，建议评估压力水平";
        }
    }
    
    return "推荐您进行此项测评，了解心理健康状况";
}

@Override
public Map<Long, String> getRecommendationReasons(Long userId) {
    List<ScaleVO> recommendations = getRecommendedScales(userId);
    return recommendations.stream()
        .collect(Collectors.toMap(ScaleVO::getId, ScaleVO::getRecommendationReason));
}
```

**步骤3：添加推荐接口**

修改 `backend/src/main/java/com/mental/controller/AssessmentController.java`：

```java
@GetMapping("/recommendations")
@Operation(summary = "获取个性化推荐的量表")
public Result<List<ScaleVO>> getRecommendations() {
    Long userId = getCurrentUserId();
    List<ScaleVO> recommendations = assessmentService.getRecommendedScales(userId);
    return Result.success(recommendations);
}
```

**步骤4：前端展示推荐**

修改前端量表列表页面，优先展示推荐量表：

```vue
<template>
  <div class="scale-list">
    <!-- 推荐区域 -->
    <div v-if="recommendedScales.length > 0" class="recommend-section">
      <h3>为您推荐</h3>
      <div class="scale-cards">
        <div v-for="scale in recommendedScales" :key="scale.id" class="scale-card recommended">
          <div class="recommend-badge">推荐</div>
          <h4>{{ scale.name }}</h4>
          <p class="recommend-reason">{{ scale.recommendationReason }}</p>
          <p class="description">{{ scale.description }}</p>
          <el-button type="primary" @click="startAssessment(scale.id)">开始测评</el-button>
        </div>
      </div>
    </div>
    
    <!-- 全部量表 -->
    <div class="all-scales">
      <h3>全部量表</h3>
      <!-- ... -->
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getRecommendedScales, getScaleList } from '@/api/assessment'

const recommendedScales = ref([])
const allScales = ref([])

onMounted(async () => {
  const [recRes, listRes] = await Promise.all([
    getRecommendedScales(),
    getScaleList()
  ])
  recommendedScales.value = recRes.data || []
  allScales.value = listRes.data || []
})
</script>
```

#### 验证方法

1. 新用户访问，检查是否推荐 PHQ-9 和 GAD-7
2. 创建低情感分数日记后，检查是否推荐抑郁量表
3. 30天后检查是否提示复测
4. 验证推荐理由是否合理

---

## 🟢 P2 级别问题（后续迭代）

---

### 问题 6：缺乏专业心理干预方法

#### 问题描述

**当前状态**：

只有 AI 对话和量表测评，缺乏专业的心理干预工具。

**竞品做法**：
- 心境奇旅：CBT 认知行为疗法练习、正念冥想、情绪急救 SOS
- Woebot：基于 CBT 的对话引导
- Wysa：正念练习、呼吸训练

#### 解决方案概要

需要新增心理练习模块，包括：

1. **数据库设计**：
```sql
CREATE TABLE `psychological_exercise` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL COMMENT '练习名称',
  `category` VARCHAR(50) NOT NULL COMMENT '分类：CBT/正念/呼吸/放松',
  `description` TEXT COMMENT '描述',
  `duration` INT COMMENT '时长（分钟）',
  `steps` TEXT COMMENT '步骤（JSON）',
  `target_symptoms` VARCHAR(255) COMMENT '适用症状',
  `difficulty` INT DEFAULT 1 COMMENT '难度等级1-5',
  `status` TINYINT DEFAULT 1,
  PRIMARY KEY (`id`)
);

CREATE TABLE `exercise_record` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT NOT NULL,
  `exercise_id` BIGINT NOT NULL,
  `completed_at` DATETIME NOT NULL,
  `duration` INT COMMENT '实际完成时长',
  `feedback` INT COMMENT '用户反馈1-5',
  PRIMARY KEY (`id`)
);
```

2. **核心练习类型**：
   - CBT 认知重构练习
   - 正念冥想（5分钟、10分钟、15分钟）
   - 呼吸训练（4-7-8呼吸法、腹式呼吸）
   - 渐进式肌肉放松
   - 情绪急救 SOS

3. **个性化推荐**：根据用户情绪状态推荐适合的练习

#### 详细实现

由于篇幅限制，详细实现请参考问题 1-5 的格式，在新会话中单独处理。

---

### 问题 7：情绪日记分析不够深入

#### 问题描述

**当前状态**：

情绪日记统计只有基础数据，缺乏深度分析。

#### 解决方案概要

需要增强的分析功能：

1. **情绪波动分析**：计算情绪波动指数
2. **触发因素分析**：提取关键词，分析情绪触发因素
3. **周/月对比**：与上周、上月对比
4. **情绪改善建议**：基于分析结果给出建议

#### 详细实现

在新会话中单独处理。

---

### 问题 8：缺乏定期追踪和提醒机制

#### 问题描述

**当前状态**：

用户需要主动使用系统，缺乏定期追踪和提醒。

#### 解决方案概要

需要添加的提醒功能：

1. **每日情绪记录提醒**：晚上8点推送
2. **每周测评提醒**：周一上午推送
3. **高风险用户追踪**：管理员每日提醒
4. **长期未活跃用户召回**：7天未登录提醒

#### 详细实现

在新会话中单独处理。

---

## 📝 使用说明

### 如何使用本文档

1. **每个问题单独处理**：建议在新会话中一次只处理一个问题
2. **复制问题描述**：将问题描述和解决方案复制到新会话
3. **逐步验证**：完成一个问题后，验证通过再处理下一个

### 会话提示词模板

```
请帮我完善 MindGuard 项目的【问题X】。

问题描述：
【粘贴问题描述】

解决方案：
【粘贴解决方案】

请按照上述方案帮我实现。
```

---

## ✅ 完成记录

| 序号 | 问题 | 完成日期 | 备注 |
|------|------|----------|------|
| 1 | AI 对话缺乏上下文记忆 | | |
| 2 | 预警触发机制不完善 | | |
| 3 | 测评报告内容单薄 | | |
| 4 | 用户画像数据未充分利用 | | |
| 5 | 测评缺乏个性化推荐 | | |
| 6 | 缺乏专业心理干预方法 | | |
| 7 | 情绪日记分析不够深入 | | |
| 8 | 缺乏定期追踪和提醒机制 | | |

---

## 📊 竞品参考

| 产品 | 核心特点 | 值得借鉴 |
|------|---------|---------|
| 心境奇旅 | CBT理论、AI旅伴、情绪急救 | 专业干预方法、隐私保护 |
| 简单心理 | 专业咨询师、线上轻咨询 | 咨询转介机制 |
| Woebot | CBT对话机器人 | 对话引导技巧 |
| 平安科技 | AI智能量表推荐 | 个性化推荐算法 |

---

*文档创建时间：2026-03-24*
*最后更新时间：2026-03-24*
