package com.mental.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("warning")
public class Warning {
    
    @TableId(type = IdType.AUTO)
    private Long id;
    
    private Long userId;
    
    private String riskLevel;
    
    private String triggerSource;
    
    private String triggerContent;
    
    private String status;
    
    private Long handlerId;
    
    private String handleNote;
    
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;
    
    private LocalDateTime handledAt;
}
