package com.mental.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
public class DiaryDTO {
    
    @NotBlank(message = "情绪类型不能为空")
    private String emotionType;
    
    @NotNull(message = "情绪分数不能为空")
    private Integer emotionScore;
    
    @NotBlank(message = "日记内容不能为空")
    private String content;
}
