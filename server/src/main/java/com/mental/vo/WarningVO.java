package com.mental.vo;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class WarningVO {
    
    private Long id;
    
    private Long userId;
    
    private String username;
    
    private String riskLevel;
    
    private String triggerSource;
    
    private String triggerContent;
    
    private String status;
    
    private String handlerName;
    
    private String handleNote;
    
    private LocalDateTime createdAt;
    
    private LocalDateTime handledAt;
}
