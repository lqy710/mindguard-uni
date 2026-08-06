package com.mental.dto;

import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.util.List;

@Data
public class AssessmentSubmitDTO {
    
    @NotNull(message = "量表ID不能为空")
    private Long scaleId;
    
    @NotNull(message = "答案不能为空")
    private List<AnswerItem> answers;
    
    @Data
    public static class AnswerItem {
        private Long questionId;
        private Integer answer;
    }
}
