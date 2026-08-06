package com.mental.service.impl;

import com.mental.mapper.*;
import com.mental.service.StatisticsService;
import com.mental.vo.HomeStatsVO;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class StatisticsServiceImpl implements StatisticsService {
    
    private final UserMapper userMapper;
    private final AssessmentMapper assessmentMapper;
    private final EmotionDiaryMapper diaryMapper;
    private final ArticleMapper articleMapper;
    private final ScaleMapper scaleMapper;
    
    @Override
    public HomeStatsVO getHomeStats() {
        Long userCount = userMapper.selectCount(null);
        Long assessmentCount = assessmentMapper.selectCount(null);
        Long diaryCount = diaryMapper.selectCount(null);
        Long articleCount = articleMapper.selectCount(null);
        Long scaleCount = scaleMapper.selectCount(null);
        
        return HomeStatsVO.builder()
                .userCount(userCount)
                .assessmentCount(assessmentCount)
                .diaryCount(diaryCount)
                .articleCount(articleCount)
                .scaleCount(scaleCount)
                .build();
    }
}
