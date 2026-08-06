package com.mental.common.enums;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public enum ResultCode {
    SUCCESS(200, "操作成功"),
    PARAM_ERROR(400, "参数错误"),
    UNAUTHORIZED(401, "未授权"),
    FORBIDDEN(403, "禁止访问"),
    NOT_FOUND(404, "资源不存在"),
    METHOD_NOT_ALLOWED(405, "方法不允许"),
    INTERNAL_ERROR(500, "服务器内部错误"),
    
    USER_NOT_FOUND(1001, "用户不存在"),
    PASSWORD_ERROR(1002, "密码错误"),
    USER_DISABLED(1003, "用户已被禁用"),
    USERNAME_EXISTS(1004, "用户名已存在"),
    TOKEN_EXPIRED(1005, "Token已过期"),
    TOKEN_INVALID(1006, "Token无效"),
    
    SCALE_NOT_FOUND(2001, "量表不存在"),
    ASSESSMENT_NOT_FOUND(2002, "测评记录不存在"),
    ASSESSMENT_IN_PROGRESS(2003, "测评正在进行中"),
    
    DIARY_NOT_FOUND(3001, "日记不存在"),
    
    CHAT_SESSION_NOT_FOUND(4001, "对话会话不存在"),
    
    ARTICLE_NOT_FOUND(5001, "文章不存在"),
    
    WARNING_NOT_FOUND(6001, "预警记录不存在");
    
    private final Integer code;
    private final String message;
}
