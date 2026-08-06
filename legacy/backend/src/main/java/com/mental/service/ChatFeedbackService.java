package com.mental.service;

import com.mental.dto.ChatFeedbackDTO;
import com.mental.vo.ChatFeedbackVO;

import java.util.List;

public interface ChatFeedbackService {
    
    /**
     * 提交对某条 AI 回复的反馈。同一用户对同一条回复重复提交时覆盖旧记录。
     */
    ChatFeedbackVO submit(ChatFeedbackDTO dto);
    
    /**
     * 查询当前用户在某会话下已提交的反馈，供前端回显按钮选中态。
     */
    List<ChatFeedbackVO> listBySession(Long sessionId);
}
