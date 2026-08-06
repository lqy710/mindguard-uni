package com.mental.vo;

import lombok.Data;

import java.util.List;

@Data
public class ScaleDetailVO {
    
    private Long id;
    
    private String name;
    
    private String description;
    
    private String category;
    
    private Integer questionNum;
    
    private Integer estimatedTime;
    
    private List<QuestionVO> questions;
    
    @Data
    public static class QuestionVO {
        private Long id;
        private Integer orderNum;
        private String content;
        private String options;
    }
}
