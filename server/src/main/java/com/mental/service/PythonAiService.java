package com.mental.service;

import java.util.List;
import java.util.Map;

public interface PythonAiService {
    
    String chat(String message);
    
    String chatWithContext(String message, List<Map<String, String>> context);
    
    /**
     * 带 RAG 的对话，返回 reply 与 references 两部分。
     *
     * @return {"reply": String, "references": List&lt;Map&lt;String,Object&gt;&gt;}
     */
    Map<String, Object> chatWithRag(String message, List<Map<String, String>> context);
    
    /**
     * 带 RAG + Function Calling 的对话。
     * <p>
     * userId / sessionId 会透传给 Python 侧，trigger_warning 工具依赖 userId 落库预警。
     *
     * @return {"reply": String, "references": List, "toolCalls": List,
     *          "crisisDetected": Boolean, "needHumanSupport": Boolean}
     */
    Map<String, Object> chatWithRag(String message, List<Map<String, String>> context,
                                    Long userId, Long sessionId);
    
    /**
     * 知识库向量检索
     *
     * @return 每项含 articleId / title / category / snippet / score
     */
    List<Map<String, Object>> retrieveKnowledge(String query, Integer topK);
    
    /**
     * 推送全量语料重建向量索引，返回生成的片段数
     */
    int reindexKnowledge(List<Map<String, Object>> articles);
    
    Map<String, Object> analyzeEmotion(String text);
    
    Map<String, Object> assessRisk(Map<String, Object> userData);
}
