package com.mental.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class ChatDTO {
    
    private Long sessionId;
    
    @NotBlank(message = "消息内容不能为空")
    private String message;
}
