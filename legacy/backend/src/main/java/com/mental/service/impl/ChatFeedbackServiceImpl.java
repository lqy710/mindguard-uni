package com.mental.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.mental.common.exception.BusinessException;
import com.mental.dto.ChatFeedbackDTO;
import com.mental.entity.ChatFeedback;
import com.mental.entity.ChatRecord;
import com.mental.entity.User;
import com.mental.mapper.ChatFeedbackMapper;
import com.mental.mapper.ChatRecordMapper;
import com.mental.mapper.UserMapper;
import com.mental.service.ChatFeedbackService;
import com.mental.vo.ChatFeedbackVO;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class ChatFeedbackServiceImpl implements ChatFeedbackService {
    
    private final ChatFeedbackMapper feedbackMapper;
    private final ChatRecordMapper chatRecordMapper;
    private final UserMapper userMapper;
    
    /**
     * 负反馈原因分类白名单，与前端选项保持一致。
     */
    private static final Map<String, String> CATEGORY_LABELS = new LinkedHashMap<>();
    
    static {
        CATEGORY_LABELS.put("irrelevant", "答非所问");
        CATEGORY_LABELS.put("unsafe", "不安全");
        CATEGORY_LABELS.put("unprofessional", "不专业");
        CATEGORY_LABELS.put("other", "其他");
    }
    
    @Override
    public ChatFeedbackVO submit(ChatFeedbackDTO dto) {
        Integer rating = dto.getRating();
        if (rating == null || (rating != 1 && rating != -1)) {
            throw new BusinessException("评价值只能为 1 或 -1");
        }
        
        Long userId = getCurrentUserId();
        
        ChatRecord record = chatRecordMapper.selectById(dto.getRecordId());
        if (record == null) {
            throw new BusinessException("消息不存在");
        }
        if (!userId.equals(record.getUserId())) {
            throw new BusinessException(403, "无权评价该消息");
        }
        if (!"assistant".equals(record.getRole())) {
            throw new BusinessException("只能对 AI 回复进行评价");
        }
        
        String category = null;
        if (rating == -1) {
            category = dto.getCategory();
            if (category == null || category.isBlank()) {
                category = "other";
            }
            if (!CATEGORY_LABELS.containsKey(category)) {
                throw new BusinessException("不支持的反馈原因分类: " + category);
            }
        }
        
        // 同一用户对同一条回复只保留一条反馈，重复提交视为修改
        ChatFeedback feedback = feedbackMapper.selectOne(new LambdaQueryWrapper<ChatFeedback>()
                .eq(ChatFeedback::getUserId, userId)
                .eq(ChatFeedback::getRecordId, dto.getRecordId())
                .last("limit 1"));
        
        boolean isNew = feedback == null;
        if (isNew) {
            feedback = new ChatFeedback();
            feedback.setUserId(userId);
            feedback.setRecordId(record.getId());
            feedback.setSessionId(record.getSessionId());
            feedback.setReplyContent(record.getContent());
            feedback.setUserContent(findPrecedingUserContent(record));
            feedback.setLabelStatus(0);
        }
        feedback.setRating(rating);
        feedback.setCategory(category);
        feedback.setComment(dto.getComment());
        
        if (isNew) {
            feedbackMapper.insert(feedback);
        } else {
            feedbackMapper.updateById(feedback);
        }
        
        log.info("收到对话反馈: userId={}, recordId={}, rating={}, category={}",
                userId, feedback.getRecordId(), rating, category);
        
        return toVO(feedback);
    }
    
    @Override
    public List<ChatFeedbackVO> listBySession(Long sessionId) {
        List<ChatFeedback> list = feedbackMapper.selectList(new LambdaQueryWrapper<ChatFeedback>()
                .eq(ChatFeedback::getUserId, getCurrentUserId())
                .eq(ChatFeedback::getSessionId, sessionId)
                .orderByAsc(ChatFeedback::getId));
        return list.stream().map(this::toVO).collect(Collectors.toList());
    }
    
    /**
     * 找到该 AI 回复之前最近的一条用户提问，用于构造评估样本。
     */
    private String findPrecedingUserContent(ChatRecord record) {
        ChatRecord prev = chatRecordMapper.selectOne(new LambdaQueryWrapper<ChatRecord>()
                .eq(ChatRecord::getSessionId, record.getSessionId())
                .eq(ChatRecord::getRole, "user")
                .lt(ChatRecord::getId, record.getId())
                .orderByDesc(ChatRecord::getId)
                .last("limit 1"));
        return prev == null ? null : prev.getContent();
    }
    
    private ChatFeedbackVO toVO(ChatFeedback feedback) {
        ChatFeedbackVO vo = new ChatFeedbackVO();
        vo.setId(feedback.getId());
        vo.setRecordId(feedback.getRecordId());
        vo.setSessionId(feedback.getSessionId());
        vo.setRating(feedback.getRating());
        vo.setCategory(feedback.getCategory());
        vo.setCategoryLabel(CATEGORY_LABELS.get(feedback.getCategory()));
        vo.setComment(feedback.getComment());
        vo.setStage(feedback.getStage());
        vo.setCreatedAt(feedback.getCreatedAt());
        return vo;
    }
    
    private Long getCurrentUserId() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String username = authentication.getName();
        User user = userMapper.selectByUsername(username);
        return user.getId();
    }
}
