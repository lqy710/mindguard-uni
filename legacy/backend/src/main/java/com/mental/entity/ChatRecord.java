package com.mental.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("chat_record")
public class ChatRecord {
    
    @TableId(type = IdType.AUTO)
    private Long id;
    
    private Long sessionId;
    
    private Long userId;
    
    private String role;
    
    private String content;
    
    private BigDecimal sentimentScore;
    
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;
}
