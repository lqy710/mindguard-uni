package com.mental.vo;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class UserVO {
    
    private Long id;
    
    private String username;
    
    private String nickname;
    
    private String avatar;
    
    private Integer gender;
    
    private Integer age;
    
    private String role;
    
    private Integer status;
    
    private LocalDateTime createdAt;
}
