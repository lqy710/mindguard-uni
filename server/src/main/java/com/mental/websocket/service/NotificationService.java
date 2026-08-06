package com.mental.websocket.service;

import com.mental.websocket.WebSocketHandler;
import com.mental.websocket.dto.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class NotificationService {
    
    private final WebSocketHandler webSocketHandler;
    
    public static final String TYPE_WARNING = "WARNING";
    public static final String TYPE_CHAT = "CHAT";
    public static final String TYPE_DATA_UPDATE = "DATA_UPDATE";
    public static final String TYPE_SYSTEM = "SYSTEM";
    
    public void sendWarningToAdmins(WarningNotification notification) {
        WebSocketMessage<WarningNotification> message = WebSocketMessage.of(TYPE_WARNING, notification);
        webSocketHandler.sendMessageToAll(message);
        log.info("发送预警通知: {}", notification);
    }
    
    public void sendWarningToUser(Long userId, WarningNotification notification) {
        WebSocketMessage<WarningNotification> message = WebSocketMessage.of(TYPE_WARNING, notification);
        webSocketHandler.sendMessageToUser(userId, message);
        log.info("向用户 {} 发送预警通知: {}", userId);
    }
    
    public void sendChatMessage(Long userId, ChatNotification notification) {
        WebSocketMessage<ChatNotification> message = WebSocketMessage.of(TYPE_CHAT, notification);
        webSocketHandler.sendMessageToUser(userId, message);
        log.info("向用户 {} 发送聊天消息: {}", userId);
    }
    
    public void sendDataUpdateNotification(Long userId, DataUpdateNotification notification) {
        WebSocketMessage<DataUpdateNotification> message = WebSocketMessage.of(TYPE_DATA_UPDATE, notification);
        webSocketHandler.sendMessageToUser(userId, message);
        log.info("向用户 {} 发送数据更新通知: {}", userId);
    }
    
    public void sendDataUpdateToAll(DataUpdateNotification notification) {
        WebSocketMessage<DataUpdateNotification> message = WebSocketMessage.of(TYPE_DATA_UPDATE, notification);
        webSocketHandler.sendMessageToAll(message);
        log.info("广播数据更新通知: {}", notification);
    }
    
    public void sendSystemNotification(Long userId, String message) {
        WebSocketMessage<String> wsMessage = WebSocketMessage.of(TYPE_SYSTEM, message);
        webSocketHandler.sendMessageToUser(userId, wsMessage);
        log.info("向用户 {} 发送系统通知: {}", userId);
    }
    
    public void sendSystemNotificationToAll(String message) {
        WebSocketMessage<String> wsMessage = WebSocketMessage.of(TYPE_SYSTEM, message);
        webSocketHandler.sendMessageToAll(wsMessage);
        log.info("广播系统通知: {}", message);
    }
    
    public boolean isUserOnline(Long userId) {
        return webSocketHandler.isUserOnline(userId);
    }
}
