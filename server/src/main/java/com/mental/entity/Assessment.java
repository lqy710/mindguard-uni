package com.mental.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("assessment")
public class Assessment {
    
    @TableId(type = IdType.AUTO)
    private Long id;
    
    private Long userId;
    
    private Long scaleId;
    
    private BigDecimal totalScore;
    
    private String riskLevel;
    
    private String report;
    
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;
}
