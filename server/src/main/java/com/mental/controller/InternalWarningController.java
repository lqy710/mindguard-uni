package com.mental.controller;

import com.mental.common.result.Result;
import com.mental.service.WarningService;
import io.swagger.v3.oas.annotations.Hidden;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/**
 * 服务间内部接口：供 Python ai-service 的 trigger_warning 工具回调写入预警。
 * <p>
 * 该接口不走 JWT（调用方是后台服务而非登录用户），改用 X-Internal-Token header 鉴权。
 * 生产环境必须同时在网关/安全组层面限制为内网可访问。
 */
@Slf4j
@Hidden
@RestController
@RequestMapping("/api/internal")
@RequiredArgsConstructor
public class InternalWarningController {

    private final WarningService warningService;

    @Value("${internal.api-token:mindguard-internal-token}")
    private String internalApiToken;

    @PostMapping("/warning")
    public Result<Map<String, Object>> createWarning(
            @RequestHeader(value = "X-Internal-Token", required = false) String token,
            @RequestBody InternalWarningRequest request) {

        if (internalApiToken == null || !internalApiToken.equals(token)) {
            log.warn("内部预警接口鉴权失败, userId={}", request.getUserId());
            return Result.error(403, "无效的内部调用令牌");
        }

        if (request.getUserId() == null) {
            return Result.error(400, "userId 不能为空");
        }

        try {
            Long warningId = warningService.createWarning(
                    request.getUserId(),
                    request.getRiskLevel() != null ? request.getRiskLevel() : "medium",
                    request.getTriggerSource() != null ? request.getTriggerSource() : "ai_chat",
                    request.getTriggerContent()
            );

            Map<String, Object> data = new HashMap<>();
            data.put("warningId", warningId);
            // warningId 为 null 表示命中去重规则，对调用方来说仍算处理成功
            data.put("deduplicated", warningId == null);
            return Result.success(data);
        } catch (Exception e) {
            log.error("创建预警失败: userId={}, {}", request.getUserId(), e.getMessage(), e);
            return Result.error(500, "创建预警失败");
        }
    }

    @Data
    public static class InternalWarningRequest {
        private Long userId;
        private String riskLevel;
        private String triggerSource;
        private String triggerContent;
        private String reason;
        private Long sessionId;
    }
}
