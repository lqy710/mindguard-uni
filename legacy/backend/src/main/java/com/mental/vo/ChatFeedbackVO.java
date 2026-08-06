package com.mental.vo;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class ChatFeedbackVO {
    
    private Long id;
    
    private Long recordId;
    
    private Long sessionId;
    
    private Integer rating;
    
    private String category;
    
    /**
     * 原因分类的中文名，供前端直接展示。
     */
    private String categoryLabel;
    
    private String comment;
    
    private String stage;
    
    private LocalDateTime createdAt;
}
