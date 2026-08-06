package com.mental.service.impl;

import cn.hutool.core.bean.BeanUtil;
import cn.hutool.core.util.StrUtil;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mental.entity.*;
import com.mental.mapper.*;
import com.mental.service.PythonAiService;
import com.mental.service.WarningService;
import com.mental.vo.StatisticsVO;
import com.mental.vo.WarningVO;
import com.mental.websocket.dto.DataUpdateNotification;
import com.mental.websocket.dto.WarningNotification;
import com.mental.websocket.service.NotificationService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class WarningServiceImpl implements WarningService {
    
    private final WarningMapper warningMapper;
    private final UserMapper userMapper;
    private final AssessmentMapper assessmentMapper;
    private final EmotionDiaryMapper diaryMapper;
    private final NotificationService notificationService;
    private final PythonAiService pythonAiService;
    
    @Override
    public Page<WarningVO> getPage(Integer current, Integer size, String status, String riskLevel) {
        Page<Warning> page = new Page<>(current, size);
        LambdaQueryWrapper<Warning> wrapper = new LambdaQueryWrapper<>();
        
        if (StrUtil.isNotBlank(status)) {
            wrapper.eq(Warning::getStatus, status);
        }
        if (StrUtil.isNotBlank(riskLevel)) {
            wrapper.eq(Warning::getRiskLevel, riskLevel);
        }
        wrapper.orderByDesc(Warning::getCreatedAt);
        
        Page<Warning> warningPage = warningMapper.selectPage(page, wrapper);
        
        Page<WarningVO> voPage = new Page<>(warningPage.getCurrent(), warningPage.getSize(), warningPage.getTotal());
        voPage.setRecords(warningPage.getRecords().stream()
                .map(this::convertToVO)
                .collect(Collectors.toList()));
        
        return voPage;
    }
    
    @Override
    public WarningVO getById(Long id) {
        Warning warning = warningMapper.selectById(id);
        if (warning == null) {
            return null;
        }
        return convertToVO(warning);
    }
    
    @Override
    public void handle(Long id, String handleNote) {
        Warning warning = warningMapper.selectById(id);
        if (warning == null) {
            return;
        }
        
        warning.setStatus("resolved");
        warning.setHandleNote(handleNote);
        warning.setHandlerId(getCurrentUserId());
        warning.setHandledAt(LocalDateTime.now());
        
        warningMapper.updateById(warning);
        
        DataUpdateNotification notification = DataUpdateNotification.builder()
                .module("warning")
                .action("handled")
                .recordId(id)
                .message("预警已处理")
                .build();
        notificationService.sendDataUpdateNotification(warning.getUserId(), notification);
    }
    
    @Override
    public StatisticsVO getDashboardStatistics() {
        StatisticsVO vo = new StatisticsVO();
        
        vo.setTotalUsers(userMapper.selectCount(null));
        
        LocalDateTime todayStart = LocalDate.now().atStartOfDay();
        LambdaQueryWrapper<User> todayUserWrapper = new LambdaQueryWrapper<>();
        todayUserWrapper.ge(User::getCreatedAt, todayStart);
        vo.setTodayNewUsers(userMapper.selectCount(todayUserWrapper));
        
        vo.setTotalAssessments(assessmentMapper.selectCount(null));
        
        LambdaQueryWrapper<Assessment> todayAssessmentWrapper = new LambdaQueryWrapper<>();
        todayAssessmentWrapper.ge(Assessment::getCreatedAt, todayStart);
        vo.setTodayAssessments(assessmentMapper.selectCount(todayAssessmentWrapper));
        
        vo.setTotalDiaries(diaryMapper.selectCount(null));
        
        LambdaQueryWrapper<EmotionDiary> todayDiaryWrapper = new LambdaQueryWrapper<>();
        todayDiaryWrapper.ge(EmotionDiary::getCreatedAt, todayStart);
        vo.setTodayDiaries(diaryMapper.selectCount(todayDiaryWrapper));
        
        LambdaQueryWrapper<Warning> pendingWrapper = new LambdaQueryWrapper<>();
        pendingWrapper.eq(Warning::getStatus, "pending");
        vo.setPendingWarnings(warningMapper.selectCount(pendingWrapper));
        
        LambdaQueryWrapper<Assessment> highRiskWrapper = new LambdaQueryWrapper<>();
        highRiskWrapper.eq(Assessment::getRiskLevel, "high");
        vo.setHighRiskUsers(assessmentMapper.selectCount(highRiskWrapper));
        
        vo.setAssessmentTrend(getAssessmentTrend());
        vo.setEmotionDistribution(getEmotionDistribution());
        
        return vo;
    }
    
    private List<StatisticsVO.ChartData> getAssessmentTrend() {
        List<StatisticsVO.ChartData> trend = new ArrayList<>();
        
        for (int i = 6; i >= 0; i--) {
            LocalDate date = LocalDate.now().minusDays(i);
            LocalDateTime dayStart = date.atStartOfDay();
            LocalDateTime dayEnd = date.atTime(LocalTime.MAX);
            
            LambdaQueryWrapper<Assessment> wrapper = new LambdaQueryWrapper<>();
            wrapper.ge(Assessment::getCreatedAt, dayStart)
                    .le(Assessment::getCreatedAt, dayEnd);
            
            StatisticsVO.ChartData data = new StatisticsVO.ChartData();
            data.setLabel(date.toString());
            data.setValue(assessmentMapper.selectCount(wrapper));
            trend.add(data);
        }
        
        return trend;
    }
    
    private List<StatisticsVO.ChartData> getEmotionDistribution() {
        List<StatisticsVO.ChartData> distribution = new ArrayList<>();
        
        List<Map<String, Object>> result = diaryMapper.selectMaps(
                new LambdaQueryWrapper<EmotionDiary>()
                        .select(EmotionDiary::getEmotionType)
                        .groupBy(EmotionDiary::getEmotionType)
        );
        
        for (Map<String, Object> item : result) {
            String emotionType = (String) item.get("emotion_type");
            
            LambdaQueryWrapper<EmotionDiary> wrapper = new LambdaQueryWrapper<>();
            wrapper.eq(EmotionDiary::getEmotionType, emotionType);
            
            StatisticsVO.ChartData data = new StatisticsVO.ChartData();
            data.setLabel(emotionType);
            data.setValue(diaryMapper.selectCount(wrapper));
            distribution.add(data);
        }
        
        return distribution;
    }
    
    private WarningVO convertToVO(Warning warning) {
        WarningVO vo = BeanUtil.copyProperties(warning, WarningVO.class);
        
        User user = userMapper.selectById(warning.getUserId());
        if (user != null) {
            vo.setUsername(user.getUsername());
        }
        
        if (warning.getHandlerId() != null) {
            User handler = userMapper.selectById(warning.getHandlerId());
            if (handler != null) {
                vo.setHandlerName(handler.getNickname());
            }
        }
        
        return vo;
    }
    
    private Long getCurrentUserId() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String username = authentication.getName();
        User user = userMapper.selectByUsername(username);
        return user.getId();
    }
    
    @Override
    public Long createWarning(Long userId, String riskLevel, String triggerSource, String triggerContent) {
        if (userId == null) {
            log.warn("创建预警失败：userId 为空");
            return null;
        }
        
        User user = userMapper.selectById(userId);
        if (user == null) {
            log.warn("创建预警失败：用户不存在, userId={}", userId);
            return null;
        }
        
        // 去重：同一用户同一来源存在未处理预警时不再新建，避免连续对话刷屏工作台
        LambdaQueryWrapper<Warning> dedupWrapper = new LambdaQueryWrapper<>();
        dedupWrapper.eq(Warning::getUserId, userId)
                .eq(Warning::getTriggerSource, triggerSource)
                .eq(Warning::getStatus, "pending")
                .ge(Warning::getCreatedAt, LocalDateTime.now().minusHours(1));
        Long existing = warningMapper.selectCount(dedupWrapper);
        if (existing != null && existing > 0) {
            log.info("1小时内已存在未处理预警，跳过创建: userId={}, source={}", userId, triggerSource);
            return null;
        }
        
        Warning warning = new Warning();
        warning.setUserId(userId);
        warning.setRiskLevel(riskLevel);
        warning.setTriggerSource(triggerSource);
        warning.setTriggerContent(triggerContent);
        warning.setStatus("pending");
        // createdAt 由 MyBatis-Plus 自动填充（FieldFill.INSERT）
        
        warningMapper.insert(warning);
        log.warn("AI 对话触发预警: warningId={}, userId={}, riskLevel={}",
                warning.getId(), userId, riskLevel);
        
        // 实时推送给管理端/心理老师
        try {
            WarningNotification notification = WarningNotification.builder()
                    .warningId(warning.getId())
                    .riskLevel(riskLevel)
                    .triggerSource(triggerSource)
                    .summary(StrUtil.maxLength(triggerContent, 50))
                    .createdAt(System.currentTimeMillis())
                    .build();
            notificationService.sendWarningToAdmins(notification);
        } catch (Exception e) {
            // 推送失败不影响预警落库
            log.error("预警推送失败: warningId={}, {}", warning.getId(), e.getMessage());
        }
        
        return warning.getId();
    }
    
    @Override
    public Map<String, Object> assessUserRisk(Long userId) {
        Map<String, Object> userData = new HashMap<>();
        
        LambdaQueryWrapper<Assessment> assessmentWrapper = new LambdaQueryWrapper<>();
        assessmentWrapper.eq(Assessment::getUserId, userId)
                .orderByDesc(Assessment::getCreatedAt)
                .last("LIMIT 1");
        Assessment latestAssessment = assessmentMapper.selectOne(assessmentWrapper);
        
        if (latestAssessment != null) {
            userData.put("score", latestAssessment.getTotalScore());
        } else {
            userData.put("score", 0);
        }
        
        LambdaQueryWrapper<Assessment> historyWrapper = new LambdaQueryWrapper<>();
        historyWrapper.eq(Assessment::getUserId, userId)
                .orderByDesc(Assessment::getCreatedAt)
                .last("LIMIT 10");
        List<Assessment> assessments = assessmentMapper.selectList(historyWrapper);
        
        List<Map<String, Object>> history = new ArrayList<>();
        for (Assessment a : assessments) {
            Map<String, Object> record = new HashMap<>();
            record.put("risk_level", a.getRiskLevel());
            record.put("score", a.getTotalScore());
            history.add(record);
        }
        userData.put("history", history);
        
        try {
            Map<String, Object> riskResult = pythonAiService.assessRisk(userData);
            log.info("AI风险评估结果: userId={}, riskLevel={}", userId, riskResult.get("risk_level"));
            return riskResult;
        } catch (Exception e) {
            log.error("风险评估失败: {}", e.getMessage());
            return Map.of(
                "risk_level", "low",
                "risk_factors", List.of("评估服务暂时不可用"),
                "recommendation", "请稍后重试"
            );
        }
    }
}
