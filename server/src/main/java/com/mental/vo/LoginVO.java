package com.mental.vo;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class LoginVO {
    
    private String token;
    
    private UserVO user;
    
    private LocalDateTime expiresAt;
}
