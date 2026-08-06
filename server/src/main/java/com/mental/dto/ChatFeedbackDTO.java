package com.mental.dto;

import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
public class ChatFeedbackDTO {
    
    /**
     * 被评价的 AI 回复对应的 chat_record.id。
     */
    @NotNull(message = "消息ID不能为空")
    private Long recordId;
    
    /**
     * 1=点赞，-1=点踩。
     */
    @NotNull(message = "评价不能为空")
    private Integer rating;
    
    /**
     * 负反馈原因：irrelevant / unsafe / unprofessional / other。
     */
    private String category;
    
    private String comment;
}
