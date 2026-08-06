package com.mental.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.mental.entity.Assessment;
import com.mental.mapper.AssessmentMapper;
import com.mental.mapper.EmotionDiaryMapper;
import com.mental.mapper.UserMapper;
import com.mental.mapper.WarningMapper;
import com.mental.service.impl.WarningServiceImpl;
import com.mental.websocket.service.NotificationService;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.util.*;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class WarningServiceTest {

    @Mock
    private WarningMapper warningMapper;

    @Mock
    private UserMapper userMapper;

    @Mock
    private AssessmentMapper assessmentMapper;

    @Mock
    private EmotionDiaryMapper diaryMapper;

    @Mock
    private NotificationService notificationService;

    @Mock
    private PythonAiService pythonAiService;

    @InjectMocks
    private WarningServiceImpl warningService;

    @Test
    @DisplayName("测试风险评估 - 高风险用户")
    @SuppressWarnings("unchecked")
    void testAssessUserRisk_HighRisk() {
        Long userId = 1L;
        Assessment assessment = new Assessment();
        assessment.setUserId(userId);
        assessment.setTotalScore(new BigDecimal("25.0"));
        assessment.setRiskLevel("high");

        when(assessmentMapper.selectOne(any(LambdaQueryWrapper.class))).thenReturn(assessment);
        when(assessmentMapper.selectList(any(LambdaQueryWrapper.class))).thenReturn(Arrays.asList(assessment));
        
        Map<String, Object> riskResult = new HashMap<>();
        riskResult.put("risk_level", "high");
        riskResult.put("risk_factors", Arrays.asList("测评得分较高"));
        riskResult.put("recommendation", "建议寻求专业帮助");
        when(pythonAiService.assessRisk(any())).thenReturn(riskResult);

        Map<String, Object> result = warningService.assessUserRisk(userId);

        assertEquals("high", result.get("risk_level"));
        verify(pythonAiService, times(1)).assessRisk(any());
    }

    @Test
    @DisplayName("测试风险评估 - 低风险用户")
    @SuppressWarnings("unchecked")
    void testAssessUserRisk_LowRisk() {
        Long userId = 2L;
        Assessment assessment = new Assessment();
        assessment.setUserId(userId);
        assessment.setTotalScore(new BigDecimal("5.0"));
        assessment.setRiskLevel("low");

        when(assessmentMapper.selectOne(any(LambdaQueryWrapper.class))).thenReturn(assessment);
        when(assessmentMapper.selectList(any(LambdaQueryWrapper.class))).thenReturn(Arrays.asList(assessment));
        
        Map<String, Object> riskResult = new HashMap<>();
        riskResult.put("risk_level", "low");
        riskResult.put("risk_factors", new ArrayList<>());
        riskResult.put("recommendation", "继续保持良好状态");
        when(pythonAiService.assessRisk(any())).thenReturn(riskResult);

        Map<String, Object> result = warningService.assessUserRisk(userId);

        assertEquals("low", result.get("risk_level"));
    }

    @Test
    @DisplayName("测试风险评估 - 无测评记录")
    @SuppressWarnings("unchecked")
    void testAssessUserRisk_NoAssessment() {
        Long userId = 3L;

        when(assessmentMapper.selectOne(any(LambdaQueryWrapper.class))).thenReturn(null);
        when(assessmentMapper.selectList(any(LambdaQueryWrapper.class))).thenReturn(new ArrayList<>());
        
        Map<String, Object> riskResult = new HashMap<>();
        riskResult.put("risk_level", "low");
        riskResult.put("risk_factors", new ArrayList<>());
        when(pythonAiService.assessRisk(any())).thenReturn(riskResult);

        Map<String, Object> result = warningService.assessUserRisk(userId);

        assertNotNull(result);
        verify(pythonAiService, times(1)).assessRisk(any());
    }

    @Test
    @DisplayName("测试风险评估 - AI服务异常时返回默认结果")
    @SuppressWarnings("unchecked")
    void testAssessUserRisk_ServiceException() {
        Long userId = 4L;
        Assessment assessment = new Assessment();
        assessment.setUserId(userId);
        assessment.setTotalScore(new BigDecimal("15.0"));
        assessment.setRiskLevel("medium");

        when(assessmentMapper.selectOne(any(LambdaQueryWrapper.class))).thenReturn(assessment);
        when(assessmentMapper.selectList(any(LambdaQueryWrapper.class))).thenReturn(Arrays.asList(assessment));
        when(pythonAiService.assessRisk(any())).thenThrow(new RuntimeException("AI服务不可用"));

        Map<String, Object> result = warningService.assessUserRisk(userId);

        assertEquals("low", result.get("risk_level"));
        assertTrue(((List<?>) result.get("risk_factors")).contains("评估服务暂时不可用"));
    }
}
