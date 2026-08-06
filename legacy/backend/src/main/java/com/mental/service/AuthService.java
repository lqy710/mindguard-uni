package com.mental.service;

import com.mental.dto.LoginDTO;
import com.mental.dto.RegisterDTO;
import com.mental.vo.LoginVO;
import com.mental.vo.UserVO;

public interface AuthService {
    
    LoginVO login(LoginDTO dto);
    
    UserVO register(RegisterDTO dto);
    
    UserVO getCurrentUser();
}
