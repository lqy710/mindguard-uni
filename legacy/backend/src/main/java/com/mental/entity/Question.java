package com.mental.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("question")
public class Question {
    
    @TableId(type = IdType.AUTO)
    private Long id;
    
    private Long scaleId;
    
    private Integer orderNum;
    
    private String content;
    
    private String options;
    
    private String scoreRule;
    
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;
}
