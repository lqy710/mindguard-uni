package com.mental.websocket.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChatNotification {
    
    private Long sessionId;
    
    private String content;
    
    private String sentimentScore;
    
    private Long createdAt;
}
