package com.mental.websocket.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class WebSocketMessage<T> {
    
    private String type;
    
    private T data;
    
    private Long timestamp;
    
    public static <T> WebSocketMessage<T> of(String type, T data) {
        return WebSocketMessage.<T>builder()
                .type(type)
                .data(data)
                .timestamp(System.currentTimeMillis())
                .build();
    }
}
