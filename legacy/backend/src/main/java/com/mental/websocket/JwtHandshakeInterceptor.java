package com.mental.websocket;

import com.mental.security.JwtUtils;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.server.ServerHttpRequest;
import org.springframework.http.server.ServerHttpResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.WebSocketHandler;
import org.springframework.web.socket.server.HandshakeInterceptor;

import java.util.Map;

@Slf4j
@Component
@RequiredArgsConstructor
public class JwtHandshakeInterceptor implements HandshakeInterceptor {
    
    private final JwtUtils jwtUtils;
    
    @Override
    public boolean beforeHandshake(ServerHttpRequest request, ServerHttpResponse response, 
                                   WebSocketHandler wsHandler, Map<String, Object> attributes) {
        try {
            String query = request.getURI().getQuery();
            if (query != null && query.contains("token=")) {
                String token = query.split("token=")[1].split("&")[0];
                if (jwtUtils.validateToken(token)) {
                    Long userId = jwtUtils.getUserIdFromToken(token);
                    String username = jwtUtils.extractUsername(token);
                    attributes.put("userId", userId);
                    attributes.put("username", username);
                    log.info("WebSocket握手成功, userId: {}, username: {}", userId, username);
                    return true;
                }
            }
            log.warn("WebSocket握手失败: 无效的token");
            return false;
        } catch (Exception e) {
            log.error("WebSocket握手异常: {}", e.getMessage());
            return false;
        }
    }
    
    @Override
    public void afterHandshake(ServerHttpRequest request, ServerHttpResponse response, 
                               WebSocketHandler wsHandler, Exception exception) {
    }
}
