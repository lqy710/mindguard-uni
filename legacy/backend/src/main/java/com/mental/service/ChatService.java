package com.mental.service;

import com.mental.dto.ChatDTO;
import com.mental.vo.ChatMessageVO;

import java.util.List;

public interface ChatService {
    
    Long createSession();
    
    ChatMessageVO sendMessage(ChatDTO dto);
    
    List<ChatMessageVO> getSessionMessages(Long sessionId);
    
    List<Long> getUserSessions();
    
    void deleteSession(Long sessionId);
}
