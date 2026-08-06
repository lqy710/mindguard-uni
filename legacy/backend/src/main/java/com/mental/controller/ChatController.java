package com.mental.controller;

import com.mental.common.result.Result;
import com.mental.dto.ChatDTO;
import com.mental.dto.ChatFeedbackDTO;
import com.mental.service.ChatFeedbackService;
import com.mental.service.ChatService;
import com.mental.vo.ChatFeedbackVO;
import com.mental.vo.ChatMessageVO;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Tag(name = "对话接口")
@RestController
@RequestMapping("/api/chat")
@RequiredArgsConstructor
public class ChatController {
    
    private final ChatService chatService;
    private final ChatFeedbackService chatFeedbackService;
    
    @Operation(summary = "创建新会话")
    @PostMapping("/session")
    public Result<Long> createSession() {
        return Result.success(chatService.createSession());
    }
    
    @Operation(summary = "发送消息")
    @PostMapping("/send")
    public Result<ChatMessageVO> sendMessage(@Valid @RequestBody ChatDTO dto) {
        return Result.success(chatService.sendMessage(dto));
    }
    
    @Operation(summary = "获取会话消息列表")
    @GetMapping("/session/{sessionId}/messages")
    public Result<List<ChatMessageVO>> getSessionMessages(@PathVariable Long sessionId) {
        return Result.success(chatService.getSessionMessages(sessionId));
    }
    
    @Operation(summary = "获取用户会话列表")
    @GetMapping("/sessions")
    public Result<List<Long>> getUserSessions() {
        return Result.success(chatService.getUserSessions());
    }
    
    @Operation(summary = "删除会话")
    @DeleteMapping("/session/{sessionId}")
    public Result<Void> deleteSession(@PathVariable Long sessionId) {
        chatService.deleteSession(sessionId);
        return Result.success();
    }
    
    @Operation(summary = "提交对话反馈（点赞/点踩）")
    @PostMapping("/feedback")
    public Result<ChatFeedbackVO> submitFeedback(@Valid @RequestBody ChatFeedbackDTO dto) {
        return Result.success(chatFeedbackService.submit(dto));
    }
    
    @Operation(summary = "获取会话的反馈记录")
    @GetMapping("/session/{sessionId}/feedback")
    public Result<List<ChatFeedbackVO>> getSessionFeedback(@PathVariable Long sessionId) {
        return Result.success(chatFeedbackService.listBySession(sessionId));
    }
}
