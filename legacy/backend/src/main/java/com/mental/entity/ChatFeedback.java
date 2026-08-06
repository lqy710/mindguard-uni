package com.mental.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * AI 对话负反馈记录。
 * 用于回流用户对单条 AI 回复的评价（点赞/点踩 + 原因分类），
 * 作为 Prompt 迭代与离线评估集的数据来源。
 */
@Data
@TableName("chat_feedback")
public class ChatFeedback {
    
    @TableId(type = IdType.AUTO)
    private Long id;
    
    private Long userId;
    
    private Long sessionId;
    
    /**
     * 被评价的 chat_record.id（AI 回复那条）。
     */
    private Long recordId;
    
    /**
     * 评价：1=点赞，-1=点踩。
     */
    private Integer rating;
    
    /**
     * 负反馈原因分类：irrelevant(答非所问) / unsafe(不安全) /
     * unprofessional(不专业) / other(其他)。点赞时为 null。
     */
    private String category;
    
    /**
     * 用户补充的文字说明，可选。
     */
    private String comment;
    
    /**
     * 冗余存一份被评价的回复内容，便于后续离线标注时无需回表。
     */
    private String replyContent;
    
    /**
     * 触发该回复的用户提问，便于构造评估样本。
     */
    private String userContent;
    
    /**
     * 该回复所处的会话阶段：assessment / interview / resource / crisis。
     */
    private String stage;
    
    /**
     * 人工标注状态：0=未标注，1=已标注，2=已转为评估样本。
     */
    private Integer labelStatus;
    
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;
}
