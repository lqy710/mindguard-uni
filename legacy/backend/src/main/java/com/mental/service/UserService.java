package com.mental.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mental.dto.UserUpdateDTO;
import com.mental.vo.UserStatsVO;
import com.mental.vo.UserVO;

public interface UserService {
    
    UserVO getById(Long id);
    
    UserVO updateProfile(UserUpdateDTO dto);
    
    Page<UserVO> getPage(Integer current, Integer size, String keyword, Integer status);
    
    void updateStatus(Long id, Integer status);
    
    UserStatsVO getUserStats();
}
