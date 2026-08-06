package com.mental.vo;

import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
public class DiaryVO {
    
    private Long id;
    
    private String emotionType;
    
    private Integer emotionScore;
    
    private String content;
    
    private BigDecimal sentimentScore;
    
    private String aiAnalysis;
    
    private LocalDateTime createdAt;
}
