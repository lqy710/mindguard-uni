package com.mental.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("emotion_diary")
public class EmotionDiary {
    
    @TableId(type = IdType.AUTO)
    private Long id;
    
    private Long userId;
    
    private String emotionType;
    
    private Integer emotionScore;
    
    private String content;
    
    private BigDecimal sentimentScore;
    
    private String aiAnalysis;
    
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;
}
