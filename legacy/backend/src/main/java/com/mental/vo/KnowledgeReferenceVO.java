package com.mental.vo;

import lombok.Data;

/**
 * RAG 检索命中的知识片段，用于前端「参考来源」展示。
 */
@Data
public class KnowledgeReferenceVO {

    /** 命中的文章 ID；负数表示来自 AI 服务内置兜底语料 */
    private Long articleId;

    private String title;

    private String category;

    /** 命中的正文片段 */
    private String snippet;

    /** 余弦相似度，0~1，越大越相关 */
    private Double score;
}
