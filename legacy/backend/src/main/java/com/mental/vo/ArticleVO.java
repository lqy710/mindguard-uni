package com.mental.vo;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class ArticleVO {
    
    private Long id;
    
    private Long categoryId;
    
    private String categoryName;
    
    private String title;
    
    private String summary;
    
    private String coverImage;
    
    private String author;
    
    private Integer viewCount;
    
    private LocalDateTime createdAt;
}
