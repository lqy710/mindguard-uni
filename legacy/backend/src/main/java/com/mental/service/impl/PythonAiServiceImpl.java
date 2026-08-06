package com.mental.service.impl;

import cn.hutool.http.HttpRequest;
import cn.hutool.http.HttpResponse;
import cn.hutool.json.JSONObject;
import cn.hutool.json.JSONUtil;
import com.mental.service.PythonAiService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Slf4j
@Service
public class PythonAiServiceImpl implements PythonAiService {

    @Value("${ai.python.url:http://localhost:5000}")
    private String pythonServiceUrl;

    @Override
    public String chat(String message) {
        return chatWithContext(message, null);
    }

    @Override
    public String chatWithContext(String message, List<Map<String, String>> context) {
        try {
            String url = pythonServiceUrl + "/api/chat/reply_with_context";
            
            JSONObject requestBody = new JSONObject();
            requestBody.set("message", message);
            
            if (context != null && !context.isEmpty()) {
                requestBody.set("context", context);
            } else {
                requestBody.set("context", new cn.hutool.json.JSONArray());
            }
            
            log.debug("Calling Python AI service with context: {}", url);
            
            HttpResponse response = HttpRequest.post(url)
                    .header("Content-Type", "application/json")
                    .body(requestBody.toString())
                    .timeout(60000)
                    .execute();
            
            if (!response.isOk()) {
                log.error("Python AI service error: status={}, body={}", response.getStatus(), response.body());
                return "抱歉，AI服务暂时不可用，请稍后再试。";
            }
            
            String body = response.body();
            log.debug("Python AI service response: {}", body);
            
            JSONObject jsonResponse = JSONUtil.parseObj(body);
            Integer code = jsonResponse.getInt("code");
            
            if (code == null || code != 200) {
                log.error("Python AI service returned error: {}", body);
                return "抱歉，AI服务返回错误，请稍后再试。";
            }
            
            JSONObject data = jsonResponse.getJSONObject("data");
            if (data == null) {
                log.error("No data in Python AI service response: {}", body);
                return "抱歉，AI回复格式异常。";
            }
            
            return data.getStr("reply", "抱歉，我暂时无法回应。");
            
        } catch (Exception e) {
            log.error("Error calling Python AI service", e);
            return "抱歉，服务暂时不可用，请稍后再试。";
        }
    }

    @Override
    public Map<String, Object> chatWithRag(String message, List<Map<String, String>> context) {
        return chatWithRag(message, context, null, null);
    }

    @Override
    public Map<String, Object> chatWithRag(String message, List<Map<String, String>> context,
                                           Long userId, Long sessionId) {
        Map<String, Object> fallback = new HashMap<>();
        fallback.put("references", List.of());
        fallback.put("toolCalls", List.of());
        // AI 服务不可用时阶段退回评估，保证前端始终能拿到合法 stage
        fallback.put("stage", "assessment");
        fallback.put("stageLabel", "情况评估");
        fallback.put("stageDescription", "正在了解你的整体状态");
        fallback.put("stageChanged", false);

        try {
            String url = pythonServiceUrl + "/api/chat/reply_with_context";

            JSONObject requestBody = new JSONObject();
            requestBody.set("message", message);
            requestBody.set("context", context != null && !context.isEmpty()
                    ? context : new cn.hutool.json.JSONArray());
            // trigger_warning 工具需要 userId 才能把预警落库
            if (userId != null) {
                requestBody.set("user_id", userId);
            }
            if (sessionId != null) {
                requestBody.set("session_id", sessionId);
            }

            HttpResponse response = HttpRequest.post(url)
                    .header("Content-Type", "application/json")
                    .body(requestBody.toString())
                    .timeout(60000)
                    .execute();

            if (!response.isOk()) {
                log.error("Python AI service error: status={}", response.getStatus());
                fallback.put("reply", "抱歉，AI服务暂时不可用，请稍后再试。");
                return fallback;
            }

            JSONObject jsonResponse = JSONUtil.parseObj(response.body());
            Integer code = jsonResponse.getInt("code");
            JSONObject data = jsonResponse.getJSONObject("data");

            if (code == null || code != 200 || data == null) {
                log.error("Python AI service returned error: {}", response.body());
                fallback.put("reply", "抱歉，AI服务返回错误，请稍后再试。");
                return fallback;
            }

            Map<String, Object> result = new HashMap<>();
            result.put("reply", data.getStr("reply", "抱歉，我暂时无法回应。"));
            result.put("references", parseReferences(data.getJSONArray("references")));
            result.put("crisisDetected", data.getBool("crisis_detected", false));
            result.put("needHumanSupport", data.getBool("need_human_support", false));
            result.put("toolCalls", parseToolCalls(data.getJSONArray("tool_calls")));
            // 会话阶段状态机字段，透传给前端展示「当前阶段」
            result.put("stage", data.getStr("stage", "assessment"));
            result.put("stageLabel", data.getStr("stageLabel", ""));
            result.put("stageDescription", data.getStr("stageDescription", ""));
            result.put("stageChanged", data.getBool("stageChanged", false));
            return result;

        } catch (Exception e) {
            log.error("Error calling Python AI service with RAG", e);
            fallback.put("reply", "抱歉，服务暂时不可用，请稍后再试。");
            return fallback;
        }
    }

    @Override
    public List<Map<String, Object>> retrieveKnowledge(String query, Integer topK) {
        try {
            String url = pythonServiceUrl + "/api/knowledge/retrieve";

            JSONObject requestBody = new JSONObject();
            requestBody.set("query", query);
            requestBody.set("top_k", topK == null ? 3 : topK);

            HttpResponse response = HttpRequest.post(url)
                    .header("Content-Type", "application/json")
                    .body(requestBody.toString())
                    .timeout(30000)
                    .execute();

            if (!response.isOk()) {
                log.error("Knowledge retrieve error: status={}", response.getStatus());
                return List.of();
            }

            JSONObject jsonResponse = JSONUtil.parseObj(response.body());
            Integer code = jsonResponse.getInt("code");
            JSONObject data = jsonResponse.getJSONObject("data");

            if (code == null || code != 200 || data == null) {
                log.error("Knowledge retrieve returned error: {}", response.body());
                return List.of();
            }

            return parseReferences(data.getJSONArray("references"));

        } catch (Exception e) {
            // 检索失败降级为空引用，不影响主流程
            log.error("Error calling knowledge retrieve", e);
            return List.of();
        }
    }

    @Override
    public int reindexKnowledge(List<Map<String, Object>> articles) {
        try {
            String url = pythonServiceUrl + "/api/knowledge/reindex";

            JSONObject requestBody = new JSONObject();
            requestBody.set("articles", articles == null ? List.of() : articles);

            HttpResponse response = HttpRequest.post(url)
                    .header("Content-Type", "application/json")
                    .body(requestBody.toString())
                    // 语料量大时向量化较慢，超时放宽
                    .timeout(180000)
                    .execute();

            if (!response.isOk()) {
                log.error("Knowledge reindex error: status={}", response.getStatus());
                return 0;
            }

            JSONObject jsonResponse = JSONUtil.parseObj(response.body());
            JSONObject data = jsonResponse.getJSONObject("data");
            if (data == null) {
                return 0;
            }
            return data.getInt("chunkCount", 0);

        } catch (Exception e) {
            log.error("Error calling knowledge reindex", e);
            return 0;
        }
    }

    /**
     * 把 Python 返回的 tool_calls 数组转成 Java Map 列表。
     * 结构透传即可，具体渲染逻辑交给前端按 name 分支处理。
     */
    private List<Map<String, Object>> parseToolCalls(cn.hutool.json.JSONArray array) {
        List<Map<String, Object>> calls = new ArrayList<>();
        if (array == null) {
            return calls;
        }
        for (Object item : array) {
            JSONObject obj = JSONUtil.parseObj(item);
            Map<String, Object> call = new HashMap<>();
            call.put("name", obj.getStr("name", ""));
            call.put("arguments", obj.getJSONObject("arguments"));
            call.put("result", obj.getJSONObject("result"));
            call.put("status", obj.getStr("status", "success"));
            call.put("durationMs", obj.getInt("durationMs", 0));
            calls.add(call);
        }
        return calls;
    }

    /** 把 Python 返回的 references 数组转成 Java Map 列表 */
    private List<Map<String, Object>> parseReferences(cn.hutool.json.JSONArray array) {
        List<Map<String, Object>> refs = new ArrayList<>();
        if (array == null) {
            return refs;
        }
        for (Object item : array) {
            JSONObject obj = JSONUtil.parseObj(item);
            Map<String, Object> ref = new HashMap<>();
            ref.put("articleId", obj.get("articleId"));
            ref.put("title", obj.getStr("title", ""));
            ref.put("category", obj.getStr("category", ""));
            ref.put("snippet", obj.getStr("snippet", ""));
            ref.put("score", obj.getDouble("score", 0.0));
            refs.add(ref);
        }
        return refs;
    }

    @Override
    public Map<String, Object> analyzeEmotion(String text) {
        try {
            String url = pythonServiceUrl + "/api/emotion/analyze";
            
            JSONObject requestBody = new JSONObject();
            requestBody.set("text", text);
            
            log.debug("Calling Python emotion analysis: {}", url);
            
            HttpResponse response = HttpRequest.post(url)
                    .header("Content-Type", "application/json")
                    .body(requestBody.toString())
                    .timeout(30000)
                    .execute();
            
            if (!response.isOk()) {
                log.error("Emotion analysis error: status={}", response.getStatus());
                return Map.of(
                    "sentiment_score", 0.5,
                    "emotion_type", "neutral",
                    "keywords", List.of()
                );
            }
            
            String body = response.body();
            JSONObject jsonResponse = JSONUtil.parseObj(body);
            Integer code = jsonResponse.getInt("code");
            
            if (code == null || code != 200) {
                log.error("Emotion analysis returned error: {}", body);
                return Map.of(
                    "sentiment_score", 0.5,
                    "emotion_type", "neutral",
                    "keywords", List.of()
                );
            }
            
            JSONObject data = jsonResponse.getJSONObject("data");
            if (data == null) {
                return Map.of(
                    "sentiment_score", 0.5,
                    "emotion_type", "neutral",
                    "keywords", List.of()
                );
            }
            
            return data;
            
        } catch (Exception e) {
            log.error("Error calling emotion analysis", e);
            return Map.of(
                "sentiment_score", 0.5,
                "emotion_type", "error",
                "keywords", List.of()
            );
        }
    }

    @Override
    public Map<String, Object> assessRisk(Map<String, Object> userData) {
        try {
            String url = pythonServiceUrl + "/api/risk/assess";
            
            JSONObject requestBody = new JSONObject();
            requestBody.set("userData", userData);
            
            log.debug("Calling Python risk assessment: {}", url);
            
            HttpResponse response = HttpRequest.post(url)
                    .header("Content-Type", "application/json")
                    .body(requestBody.toString())
                    .timeout(30000)
                    .execute();
            
            if (!response.isOk()) {
                log.error("Risk assessment error: status={}", response.getStatus());
                return Map.of(
                    "risk_level", "low",
                    "risk_factors", List.of(),
                    "recommendation", "风险评估服务暂时不可用"
                );
            }
            
            String body = response.body();
            JSONObject jsonResponse = JSONUtil.parseObj(body);
            Integer code = jsonResponse.getInt("code");
            
            if (code == null || code != 200) {
                log.error("Risk assessment returned error: {}", body);
                return Map.of(
                    "risk_level", "low",
                    "risk_factors", List.of(),
                    "recommendation", "风险评估失败"
                );
            }
            
            JSONObject data = jsonResponse.getJSONObject("data");
            if (data == null) {
                return Map.of(
                    "risk_level", "low",
                    "risk_factors", List.of(),
                    "recommendation", "无评估结果"
                );
            }
            
            return data;
            
        } catch (Exception e) {
            log.error("Error calling risk assessment", e);
            return Map.of(
                "risk_level", "low",
                "risk_factors", List.of("评估服务异常"),
                "recommendation", "风险评估服务暂时不可用"
            );
        }
    }
}
