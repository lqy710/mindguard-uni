package com.mental.service;

public interface ZhipuAiService {
    String chat(String message);
    String chatWithContext(String systemPrompt, String userMessage);
}
