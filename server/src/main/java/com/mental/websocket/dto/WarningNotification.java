package com.mental.websocket.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class WarningNotification {
    
    private Long warningId;
    
    private String riskLevel;
    
    private String triggerSource;
    
    private String summary;
    
    private Long createdAt;
}
