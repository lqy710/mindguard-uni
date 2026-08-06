package com.mental.vo;

import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

@Data
public class ChatMessageVO {
    
    private Long id;
    
    /**
     * 所属会话 id。发送消息时返回（可能是本次新建的会话），供前端延续多轮对话。
     */
    private Long sessionId;
    
    private String role;
    
    private String content;
    
    private BigDecimal sentimentScore;
    
    private LocalDateTime createdAt;
    
    /**
     * RAG 参考来源。仅 AI 实时回复时返回，历史消息为 null。
     */
    private List<KnowledgeReferenceVO> references;
    
    /**
     * 本次回复触发的工具调用链路。仅 AI 实时回复时返回，历史消息为 null。
     */
    private List<ToolCallVO> toolCalls;
    
    /**
     * 当前会话阶段：assessment / interview / resource / crisis。
     * 仅 AI 实时回复时返回，历史消息为 null。
     */
    private String stage;
    
    /**
     * 阶段中文名，供前端直接展示，避免前端硬编码映射表。
     */
    private String stageLabel;
    
    /**
     * 阶段说明文案。
     */
    private String stageDescription;
    
    /**
     * 本轮是否发生了阶段切换，前端据此决定是否提示用户。
     */
    private Boolean stageChanged;
}
