package com.mental.service.impl;

import cn.hutool.core.util.StrUtil;
import cn.hutool.http.HttpRequest;
import cn.hutool.http.HttpResponse;
import cn.hutool.json.JSONArray;
import cn.hutool.json.JSONObject;
import cn.hutool.json.JSONUtil;
import com.mental.service.ZhipuAiService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Slf4j
@Service
public class ZhipuAiServiceImpl implements ZhipuAiService {

    @Value("${ai.zhipu.api-key}")
    private String apiKey;

    @Value("${ai.zhipu.model:glm-4-flash}")
    private String model;

    @Value("${ai.zhipu.base-url:https://open.bigmodel.cn/api/paas/v4}")
    private String baseUrl;

    private static final String MENTAL_HEALTH_SYSTEM_PROMPT = "你是一位专业、温暖的心理健康助手。你的职责是：\n" +
            "1. 以同理心和理解的态度倾听用户的问题\n" +
            "2. 提供科学、专业的心理健康建议\n" +
            "3. 在必要时建议用户寻求专业心理医生的帮助\n" +
            "4. 保持积极、支持性的对话风格\n" +
            "5. 不要诊断或治疗任何心理疾病\n" +
            "请用简洁、温暖的语气回应用户。";

    @Override
    public String chat(String message) {
        return chatWithContext(MENTAL_HEALTH_SYSTEM_PROMPT, message);
    }

    @Override
    public String chatWithContext(String systemPrompt, String userMessage) {
        try {
            String url = baseUrl + "/chat/completions";
            
            List<JSONObject> messages = new ArrayList<>();
            
            if (StrUtil.isNotBlank(systemPrompt)) {
                JSONObject systemMsg = new JSONObject();
                systemMsg.set("role", "system");
                systemMsg.set("content", systemPrompt);
                messages.add(systemMsg);
            }
            
            JSONObject userMsg = new JSONObject();
            userMsg.set("role", "user");
            userMsg.set("content", userMessage);
            messages.add(userMsg);
            
            JSONObject requestBody = new JSONObject();
            requestBody.set("model", model);
            requestBody.set("messages", messages);
            requestBody.set("temperature", 0.7);
            requestBody.set("max_tokens", 2000);
            
            log.debug("Calling Zhipu AI with request: {}", requestBody.toString());
            
            HttpResponse response = HttpRequest.post(url)
                    .header("Content-Type", "application/json")
                    .header("Authorization", "Bearer " + apiKey)
                    .body(requestBody.toString())
                    .timeout(60000)
                    .execute();
            
            if (!response.isOk()) {
                log.error("Zhipu AI API error: status={}, body={}", response.getStatus(), response.body());
                return "抱歉，AI服务暂时不可用，请稍后再试。";
            }
            
            String body = response.body();
            log.debug("Zhipu AI response: {}", body);
            
            JSONObject jsonResponse = JSONUtil.parseObj(body);
            JSONArray choices = jsonResponse.getJSONArray("choices");
            
            if (choices == null || choices.isEmpty()) {
                log.error("No choices in Zhipu AI response: {}", body);
                return "抱歉，AI没有返回有效回复。";
            }
            
            JSONObject firstChoice = choices.getJSONObject(0);
            JSONObject messageObj = firstChoice.getJSONObject("message");
            
            if (messageObj == null) {
                log.error("No message in Zhipu AI response: {}", body);
                return "抱歉，AI回复格式异常。";
            }
            
            return messageObj.getStr("content", "抱歉，我暂时无法回应。");
            
        } catch (Exception e) {
            log.error("Error calling Zhipu AI", e);
            return "抱歉，服务暂时不可用，请稍后再试。";
        }
    }
}
