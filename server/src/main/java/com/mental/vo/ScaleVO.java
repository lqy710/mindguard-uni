package com.mental.vo;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class ScaleVO {
    
    private Long id;
    
    private String name;
    
    private String description;
    
    private String category;
    
    private Integer questionNum;
    
    private Integer estimatedTime;
    
    private Integer status;
    
    private LocalDateTime createdAt;
}
