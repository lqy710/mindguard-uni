package com.mental.service.impl;

import cn.hutool.core.bean.BeanUtil;
import cn.hutool.core.util.StrUtil;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mental.common.enums.ResultCode;
import com.mental.common.exception.BusinessException;
import com.mental.dto.UserUpdateDTO;
import com.mental.entity.Assessment;
import com.mental.entity.EmotionDiary;
import com.mental.entity.User;
import com.mental.mapper.AssessmentMapper;
import com.mental.mapper.EmotionDiaryMapper;
import com.mental.mapper.UserMapper;
import com.mental.service.UserService;
import com.mental.vo.UserStatsVO;
import com.mental.vo.UserVO;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;

import java.time.LocalDate;

@Service
@RequiredArgsConstructor
public class UserServiceImpl implements UserService {
    
    private final UserMapper userMapper;
    private final AssessmentMapper assessmentMapper;
    private final EmotionDiaryMapper emotionDiaryMapper;
    
    @Override
    public UserVO getById(Long id) {
        User user = userMapper.selectById(id);
        if (user == null) {
            throw new BusinessException(ResultCode.USER_NOT_FOUND);
        }
        return BeanUtil.copyProperties(user, UserVO.class);
    }
    
    @Override
    public UserVO updateProfile(UserUpdateDTO dto) {
        Long userId = getCurrentUserId();
        User user = userMapper.selectById(userId);
        if (user == null) {
            throw new BusinessException(ResultCode.USER_NOT_FOUND);
        }
        
        if (dto.getNickname() != null) {
            user.setNickname(dto.getNickname());
        }
        if (dto.getAvatar() != null) {
            user.setAvatar(dto.getAvatar());
        }
        if (dto.getGender() != null) {
            user.setGender(dto.getGender());
        }
        if (dto.getAge() != null) {
            user.setAge(dto.getAge());
        }
        
        userMapper.updateById(user);
        return BeanUtil.copyProperties(user, UserVO.class);
    }
    
    @Override
    public Page<UserVO> getPage(Integer current, Integer size, String keyword, Integer status) {
        Page<User> page = new Page<>(current, size);
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        
        if (StrUtil.isNotBlank(keyword)) {
            wrapper.like(User::getUsername, keyword)
                    .or()
                    .like(User::getNickname, keyword);
        }
        if (status != null) {
            wrapper.eq(User::getStatus, status);
        }
        wrapper.orderByDesc(User::getCreatedAt);
        
        Page<User> userPage = userMapper.selectPage(page, wrapper);
        
        Page<UserVO> voPage = new Page<>(userPage.getCurrent(), userPage.getSize(), userPage.getTotal());
        voPage.setRecords(BeanUtil.copyToList(userPage.getRecords(), UserVO.class));
        
        return voPage;
    }
    
    @Override
    public void updateStatus(Long id, Integer status) {
        User user = userMapper.selectById(id);
        if (user == null) {
            throw new BusinessException(ResultCode.USER_NOT_FOUND);
        }
        user.setStatus(status);
        userMapper.updateById(user);
    }
    
    @Override
    public UserStatsVO getUserStats() {
        Long userId = getCurrentUserId();
        
        UserStatsVO stats = new UserStatsVO();
        
        LambdaQueryWrapper<Assessment> assessmentWrapper = new LambdaQueryWrapper<>();
        assessmentWrapper.eq(Assessment::getUserId, userId);
        Long assessmentCount = assessmentMapper.selectCount(assessmentWrapper);
        stats.setAssessmentCount(assessmentCount);
        
        LambdaQueryWrapper<EmotionDiary> diaryWrapper = new LambdaQueryWrapper<>();
        diaryWrapper.eq(EmotionDiary::getUserId, userId);
        Long diaryCount = emotionDiaryMapper.selectCount(diaryWrapper);
        stats.setDiaryCount(diaryCount);
        
        long streakDays = calculateStreakDays(userId);
        stats.setStreakDays(streakDays);
        
        return stats;
    }
    
    private long calculateStreakDays(Long userId) {
        LambdaQueryWrapper<EmotionDiary> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(EmotionDiary::getUserId, userId)
               .orderByDesc(EmotionDiary::getCreatedAt)
               .last("LIMIT 30");
        
        var diaries = emotionDiaryMapper.selectList(wrapper);
        
        if (diaries.isEmpty()) {
            return 0L;
        }
        
        long streak = 0;
        LocalDate today = LocalDate.now();
        LocalDate lastDate = null;
        
        for (var diary : diaries) {
            LocalDate diaryDate = diary.getCreatedAt().toLocalDate();
            
            if (lastDate == null) {
                if (diaryDate.equals(today) || diaryDate.equals(today.minusDays(1))) {
                    streak = 1;
                    lastDate = diaryDate;
                }
            } else {
                if (diaryDate.equals(lastDate.minusDays(1))) {
                    streak++;
                    lastDate = diaryDate;
                } else if (diaryDate.equals(lastDate)) {
                    continue;
                } else {
                    break;
                }
            }
        }
        
        return streak;
    }
    
    private Long getCurrentUserId() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String username = authentication.getName();
        User user = userMapper.selectByUsername(username);
        return user.getId();
    }
}
