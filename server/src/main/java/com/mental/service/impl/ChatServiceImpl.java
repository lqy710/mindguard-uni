package com.mental.service.impl;

import cn.hutool.core.bean.BeanUtil;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.mental.dto.ChatDTO;
import com.mental.entity.ChatRecord;
import com.mental.entity.ChatSession;
import com.mental.entity.User;
import com.mental.mapper.ChatRecordMapper;
import com.mental.mapper.ChatSessionMapper;
import com.mental.mapper.UserMapper;
import com.mental.service.ChatService;
import com.mental.service.PythonAiService;
import com.mental.vo.ChatMessageVO;
import com.mental.vo.KnowledgeReferenceVO;
import com.mental.vo.ToolCallVO;
import com.mental.websocket.dto.ChatNotification;
import com.mental.websocket.service.NotificationService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ChatServiceImpl implements ChatService {
    
    private final ChatSessionMapper sessionMapper;
    private final ChatRecordMapper recordMapper;
    private final UserMapper userMapper;
    private final NotificationService notificationService;
    private final PythonAiService pythonAiService;
    
    @Override
    public Long createSession() {
        ChatSession session = new ChatSession();
        session.setUserId(getCurrentUserId());
        session.setTitle("新对话");
        sessionMapper.insert(session);
        return session.getId();
    }
    
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
        
        List<Map<String, String>> context = getRecentContext(sessionId, 20);
        
        ChatRecord userRecord = new ChatRecord();
        userRecord.setSessionId(sessionId);
        userRecord.setUserId(userId);
        userRecord.setRole("user");
        userRecord.setContent(dto.getMessage());
        recordMapper.insert(userRecord);
        
        // 传入 userId / sessionId，供 Python 侧 trigger_warning 工具落库预警
        Map<String, Object> aiResult = pythonAiService.chatWithRag(
                dto.getMessage(), context, userId, sessionId);
        String aiReply = String.valueOf(aiResult.getOrDefault("reply", "抱歉，我暂时无法回应。"));
        
        ChatRecord aiRecord = new ChatRecord();
        aiRecord.setSessionId(sessionId);
        aiRecord.setUserId(userId);
        aiRecord.setRole("assistant");
        aiRecord.setContent(aiReply);
        recordMapper.insert(aiRecord);
        
        ChatMessageVO vo = new ChatMessageVO();
        vo.setId(aiRecord.getId());
        vo.setSessionId(sessionId);
        vo.setRole("assistant");
        vo.setContent(aiReply);
        vo.setCreatedAt(aiRecord.getCreatedAt());
        vo.setReferences(toReferenceVOs(aiResult.get("references")));
        vo.setToolCalls(toToolCallVOs(aiResult.get("toolCalls")));
        // 会话阶段：供前端展示「当前阶段」提示
        vo.setStage(asString(aiResult.get("stage"), "assessment"));
        vo.setStageLabel(asString(aiResult.get("stageLabel"), ""));
        vo.setStageDescription(asString(aiResult.get("stageDescription"), ""));
        vo.setStageChanged(Boolean.TRUE.equals(aiResult.get("stageChanged")));
        
        ChatNotification chatNotification = ChatNotification.builder()
                .sessionId(sessionId)
                .content(aiReply)
                .createdAt(System.currentTimeMillis())
                .build();
        notificationService.sendChatMessage(userId, chatNotification);
        
        return vo;
    }
    
    @Override
    public List<ChatMessageVO> getSessionMessages(Long sessionId) {
        LambdaQueryWrapper<ChatRecord> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ChatRecord::getSessionId, sessionId)
                .orderByAsc(ChatRecord::getCreatedAt);
        
        List<ChatRecord> records = recordMapper.selectList(wrapper);
        return records.stream()
                .map(r -> BeanUtil.copyProperties(r, ChatMessageVO.class))
                .collect(Collectors.toList());
    }
    
    @Override
    public List<Long> getUserSessions() {
        Long userId = getCurrentUserId();
        
        LambdaQueryWrapper<ChatSession> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ChatSession::getUserId, userId)
                .orderByDesc(ChatSession::getUpdatedAt);
        
        List<ChatSession> sessions = sessionMapper.selectList(wrapper);
        return sessions.stream()
                .map(ChatSession::getId)
                .collect(Collectors.toList());
    }
    
    @Override
    public void deleteSession(Long sessionId) {
        sessionMapper.deleteById(sessionId);
        
        LambdaQueryWrapper<ChatRecord> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ChatRecord::getSessionId, sessionId);
        recordMapper.delete(wrapper);
    }
    
    /** 安全取字符串，null 时回落到默认值 */
    private String asString(Object raw, String defaultValue) {
        if (raw == null) {
            return defaultValue;
        }
        String value = String.valueOf(raw);
        return value.isEmpty() ? defaultValue : value;
    }
    
    /** 把 AI 服务返回的 references 原始结构转成 VO */
    @SuppressWarnings("unchecked")
    private List<KnowledgeReferenceVO> toReferenceVOs(Object raw) {
        if (!(raw instanceof List<?> list) || list.isEmpty()) {
            return Collections.emptyList();
        }
        
        List<KnowledgeReferenceVO> result = new ArrayList<>();
        for (Object item : list) {
            if (!(item instanceof Map)) {
                continue;
            }
            Map<String, Object> map = (Map<String, Object>) item;
            KnowledgeReferenceVO vo = new KnowledgeReferenceVO();
            Object articleId = map.get("articleId");
            if (articleId instanceof Number n) {
                vo.setArticleId(n.longValue());
            }
            vo.setTitle(map.get("title") == null ? null : String.valueOf(map.get("title")));
            vo.setCategory(map.get("category") == null ? null : String.valueOf(map.get("category")));
            vo.setSnippet(map.get("snippet") == null ? null : String.valueOf(map.get("snippet")));
            if (map.get("score") instanceof Number s) {
                vo.setScore(s.doubleValue());
            }
            result.add(vo);
        }
        return result;
    }
    
    /** 把 AI 服务返回的 toolCalls 原始结构转成 VO */
    @SuppressWarnings("unchecked")
    private List<ToolCallVO> toToolCallVOs(Object raw) {
        if (!(raw instanceof List<?> list) || list.isEmpty()) {
            return Collections.emptyList();
        }
        
        List<ToolCallVO> result = new ArrayList<>();
        for (Object item : list) {
            if (!(item instanceof Map)) {
                continue;
            }
            Map<String, Object> map = (Map<String, Object>) item;
            ToolCallVO vo = new ToolCallVO();
            vo.setName(map.get("name") == null ? null : String.valueOf(map.get("name")));
            vo.setStatus(map.get("status") == null ? "success" : String.valueOf(map.get("status")));
            if (map.get("arguments") instanceof Map) {
                vo.setArguments((Map<String, Object>) map.get("arguments"));
            }
            if (map.get("result") instanceof Map) {
                vo.setResult((Map<String, Object>) map.get("result"));
            }
            if (map.get("durationMs") instanceof Number d) {
                vo.setDurationMs(d.intValue());
            }
            result.add(vo);
        }
        return result;
    }
    
    private List<Map<String, String>> getRecentContext(Long sessionId, int limit) {
        LambdaQueryWrapper<ChatRecord> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ChatRecord::getSessionId, sessionId)
                .orderByDesc(ChatRecord::getCreatedAt)
                .last("LIMIT " + limit);
        
        List<ChatRecord> records = recordMapper.selectList(wrapper);
        
        List<Map<String, String>> context = new ArrayList<>();
        
        List<ChatRecord> orderedRecords = new ArrayList<>();
        for (int i = records.size() - 1; i >= 0; i--) {
            orderedRecords.add(records.get(i));
        }
        
        for (ChatRecord record : orderedRecords) {
            Map<String, String> msg = new LinkedHashMap<>();
            msg.put("role", record.getRole());
            msg.put("content", record.getContent());
            context.add(msg);
        }
        
        return context;
    }
    
    private Long getCurrentUserId() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String username = authentication.getName();
        User user = userMapper.selectByUsername(username);
        return user.getId();
    }
}
