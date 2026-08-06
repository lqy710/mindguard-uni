package com.mental.service.impl;

import cn.hutool.core.bean.BeanUtil;
import com.mental.common.enums.ResultCode;
import com.mental.common.exception.BusinessException;
import com.mental.dto.LoginDTO;
import com.mental.dto.RegisterDTO;
import com.mental.entity.User;
import com.mental.mapper.UserMapper;
import com.mental.security.JwtUtils;
import com.mental.service.AuthService;
import com.mental.vo.LoginVO;
import com.mental.vo.UserVO;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
public class AuthServiceImpl implements AuthService {
    
    private final UserMapper userMapper;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtils jwtUtils;
    private final AuthenticationManager authenticationManager;
    
    @Override
    public LoginVO login(LoginDTO dto) {
        Authentication authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(dto.getUsername(), dto.getPassword())
        );
        
        SecurityContextHolder.getContext().setAuthentication(authentication);
        
        User user = userMapper.selectByUsername(dto.getUsername());
        if (user.getStatus() == 0) {
            throw new BusinessException(ResultCode.USER_DISABLED);
        }
        
        String token = jwtUtils.generateToken(dto.getUsername(), user.getId());
        
        LoginVO vo = new LoginVO();
        vo.setToken(token);
        vo.setUser(BeanUtil.copyProperties(user, UserVO.class));
        vo.setExpiresAt(LocalDateTime.now().plusSeconds(604800L));
        
        return vo;
    }
    
    @Override
    public UserVO register(RegisterDTO dto) {
        User existUser = userMapper.selectByUsername(dto.getUsername());
        if (existUser != null) {
            throw new BusinessException(ResultCode.USERNAME_EXISTS);
        }
        
        User user = new User();
        user.setUsername(dto.getUsername());
        user.setPassword(passwordEncoder.encode(dto.getPassword()));
        user.setNickname(dto.getNickname() != null && !dto.getNickname().isEmpty() 
            ? dto.getNickname() : dto.getUsername());
        user.setGender(dto.getGender() != null ? dto.getGender() : 0);
        user.setAge(dto.getAge());
        user.setRole("user");
        user.setStatus(1);
        
        userMapper.insert(user);
        
        return BeanUtil.copyProperties(user, UserVO.class);
    }
    
    @Override
    public UserVO getCurrentUser() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String username = authentication.getName();
        User user = userMapper.selectByUsername(username);
        if (user == null) {
            throw new BusinessException(ResultCode.USER_NOT_FOUND);
        }
        return BeanUtil.copyProperties(user, UserVO.class);
    }
}
