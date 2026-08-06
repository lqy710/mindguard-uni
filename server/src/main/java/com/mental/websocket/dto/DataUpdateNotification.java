package com.mental.websocket.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DataUpdateNotification {
    
    private String module;
    
    private String action;
    
    private Long recordId;
    
    private String message;
}
