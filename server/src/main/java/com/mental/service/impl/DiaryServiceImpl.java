package com.mental.service.impl;

import cn.hutool.core.bean.BeanUtil;
import cn.hutool.core.util.StrUtil;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mental.common.exception.BusinessException;
import com.mental.dto.DiaryDTO;
import com.mental.entity.EmotionDiary;
import com.mental.entity.User;
import com.mental.mapper.EmotionDiaryMapper;
import com.mental.mapper.UserMapper;
import com.mental.service.DiaryService;
import com.mental.service.PythonAiService;
import com.mental.vo.DiaryVO;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class DiaryServiceImpl implements DiaryService {
    
    private final EmotionDiaryMapper diaryMapper;
    private final UserMapper userMapper;
    private final PythonAiService pythonAiService;
    
    @Override
    public DiaryVO create(DiaryDTO dto) {
        EmotionDiary diary = new EmotionDiary();
        diary.setUserId(getCurrentUserId());
        diary.setEmotionType(dto.getEmotionType());
        diary.setEmotionScore(dto.getEmotionScore());
        diary.setContent(dto.getContent());
        
        try {
            Map<String, Object> emotionResult = pythonAiService.analyzeEmotion(dto.getContent());
            Object sentimentScoreObj = emotionResult.get("sentiment_score");
            String emotionType = (String) emotionResult.get("emotion_type");
            
            if (sentimentScoreObj != null) {
                BigDecimal sentimentScore = new BigDecimal(sentimentScoreObj.toString());
                diary.setSentimentScore(sentimentScore);
            }
            if (emotionType != null && !"error".equals(emotionType)) {
                log.info("AI情感分析结果: sentiment={}, emotionType={}", sentimentScoreObj, emotionType);
            }
        } catch (Exception e) {
            log.warn("情感分析失败，使用默认值: {}", e.getMessage());
        }
        
        diaryMapper.insert(diary);
        
        return BeanUtil.copyProperties(diary, DiaryVO.class);
    }
    
    @Override
    public DiaryVO getById(Long id) {
        EmotionDiary diary = diaryMapper.selectById(id);
        if (diary == null) {
            throw new BusinessException("日记不存在");
        }
        return BeanUtil.copyProperties(diary, DiaryVO.class);
    }
    
    @Override
    public Page<DiaryVO> getPage(Integer current, Integer size, String emotionType) {
        Long userId = getCurrentUserId();
        
        Page<EmotionDiary> page = new Page<>(current, size);
        LambdaQueryWrapper<EmotionDiary> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(EmotionDiary::getUserId, userId);
        if (StrUtil.isNotBlank(emotionType)) {
            wrapper.eq(EmotionDiary::getEmotionType, emotionType);
        }
        wrapper.orderByDesc(EmotionDiary::getCreatedAt);
        
        Page<EmotionDiary> diaryPage = diaryMapper.selectPage(page, wrapper);
        
        Page<DiaryVO> voPage = new Page<>(diaryPage.getCurrent(), diaryPage.getSize(), diaryPage.getTotal());
        voPage.setRecords(BeanUtil.copyToList(diaryPage.getRecords(), DiaryVO.class));
        
        return voPage;
    }
    
    @Override
    public void delete(Long id) {
        EmotionDiary diary = diaryMapper.selectById(id);
        if (diary == null) {
            throw new BusinessException("日记不存在");
        }
        diaryMapper.deleteById(id);
    }
    
    @Override
    public Map<String, Object> getStatistics() {
        Long userId = getCurrentUserId();
        
        Map<String, Object> result = new HashMap<>();
        
        LocalDateTime startOfMonth = LocalDate.now().withDayOfMonth(1).atStartOfDay();
        LambdaQueryWrapper<EmotionDiary> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(EmotionDiary::getUserId, userId)
                .ge(EmotionDiary::getCreatedAt, startOfMonth);
        
        List<EmotionDiary> diaries = diaryMapper.selectList(wrapper);
        
        result.put("total", diaries.size());
        
        Map<String, Long> emotionCount = diaries.stream()
                .collect(Collectors.groupingBy(EmotionDiary::getEmotionType, Collectors.counting()));
        result.put("emotionDistribution", emotionCount);
        
        double avgScore = diaries.stream()
                .mapToInt(EmotionDiary::getEmotionScore)
                .average()
                .orElse(5.0);
        result.put("avgScore", avgScore);
        
        return result;
    }
    
    @Override
    public List<Map<String, Object>> getEmotionTrend(Integer days) {
        Long userId = getCurrentUserId();
        
        LocalDateTime startTime = LocalDate.now().minusDays(days).atStartOfDay();
        
        LambdaQueryWrapper<EmotionDiary> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(EmotionDiary::getUserId, userId)
                .ge(EmotionDiary::getCreatedAt, startTime)
                .orderByAsc(EmotionDiary::getCreatedAt);
        
        List<EmotionDiary> diaries = diaryMapper.selectList(wrapper);
        
        return diaries.stream()
                .map(d -> {
                    Map<String, Object> item = new HashMap<>();
                    item.put("date", d.getCreatedAt().toLocalDate().toString());
                    item.put("emotionType", d.getEmotionType());
                    item.put("emotionScore", d.getEmotionScore());
                    return item;
                })
                .collect(Collectors.toList());
    }
    
    private Long getCurrentUserId() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String username = authentication.getName();
        User user = userMapper.selectByUsername(username);
        return user.getId();
    }
}
