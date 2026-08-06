package com.mental.vo;

import lombok.Data;

import java.util.Map;

/**
 * AI 一次 function calling 的调用记录，用于前端展示「AI 做了什么」。
 */
@Data
public class ToolCallVO {

    /**
     * 工具名：analyze_emotion / knowledge_query / trigger_warning
     */
    private String name;

    /**
     * 模型生成的调用入参
     */
    private Map<String, Object> arguments;

    /**
     * 工具执行结果。不同工具结构不同，前端按 name 分支渲染。
     */
    private Map<String, Object> result;

    /**
     * success / error
     */
    private String status;

    /**
     * 工具执行耗时（毫秒）
     */
    private Integer durationMs;
}
