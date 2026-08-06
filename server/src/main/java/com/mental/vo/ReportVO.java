package com.mental.vo;

import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
public class ReportVO {
    
    private Long assessmentId;
    
    private Long scaleId;
    
    private String scaleName;
    
    private BigDecimal totalScore;
    
    private String riskLevel;
    
    private String riskText;
    
    private String interpretation;
    
    private String suggestion;
    
    private LocalDateTime createdAt;
}
