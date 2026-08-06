package com.mental.service.impl;

import cn.hutool.core.bean.BeanUtil;
import cn.hutool.core.util.StrUtil;
import cn.hutool.json.JSONArray;
import cn.hutool.json.JSONUtil;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mental.common.enums.ResultCode;
import com.mental.common.exception.BusinessException;
import com.mental.dto.AssessmentSubmitDTO;
import com.mental.entity.*;
import com.mental.mapper.*;
import com.mental.service.AssessmentService;
import com.mental.vo.ReportVO;
import com.mental.vo.ScaleDetailVO;
import com.mental.vo.ScaleVO;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class AssessmentServiceImpl implements AssessmentService {
    
    private final ScaleMapper scaleMapper;
    private final QuestionMapper questionMapper;
    private final AssessmentMapper assessmentMapper;
    private final AssessmentAnswerMapper answerMapper;
    private final UserMapper userMapper;
    
    @Override
    public List<ScaleVO> getScaleList(String category) {
        LambdaQueryWrapper<Scale> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Scale::getStatus, 1);
        if (StrUtil.isNotBlank(category)) {
            wrapper.eq(Scale::getCategory, category);
        }
        wrapper.orderByAsc(Scale::getCreatedAt);
        
        List<Scale> scales = scaleMapper.selectList(wrapper);
        return BeanUtil.copyToList(scales, ScaleVO.class);
    }
    
    @Override
    public ScaleDetailVO getScaleDetail(Long scaleId) {
        Scale scale = scaleMapper.selectById(scaleId);
        if (scale == null) {
            throw new BusinessException(ResultCode.SCALE_NOT_FOUND);
        }
        
        LambdaQueryWrapper<Question> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Question::getScaleId, scaleId)
                .orderByAsc(Question::getOrderNum);
        List<Question> questions = questionMapper.selectList(wrapper);
        
        ScaleDetailVO vo = BeanUtil.copyProperties(scale, ScaleDetailVO.class);
        vo.setQuestions(questions.stream().map(q -> {
            ScaleDetailVO.QuestionVO qvo = new ScaleDetailVO.QuestionVO();
            qvo.setId(q.getId());
            qvo.setOrderNum(q.getOrderNum());
            qvo.setContent(q.getContent());
            qvo.setOptions(q.getOptions());
            return qvo;
        }).collect(Collectors.toList()));
        
        return vo;
    }
    
    @Override
    @Transactional
    public ReportVO submitAssessment(AssessmentSubmitDTO dto) {
        Scale scale = scaleMapper.selectById(dto.getScaleId());
        if (scale == null) {
            throw new BusinessException(ResultCode.SCALE_NOT_FOUND);
        }
        
        int totalScore = 0;
        for (AssessmentSubmitDTO.AnswerItem item : dto.getAnswers()) {
            totalScore += item.getAnswer();
        }
        
        String riskLevel = calculateRiskLevel(scale, totalScore);
        
        Assessment assessment = new Assessment();
        assessment.setUserId(getCurrentUserId());
        assessment.setScaleId(dto.getScaleId());
        assessment.setTotalScore(BigDecimal.valueOf(totalScore));
        assessment.setRiskLevel(riskLevel);
        assessmentMapper.insert(assessment);
        
        for (AssessmentSubmitDTO.AnswerItem item : dto.getAnswers()) {
            AssessmentAnswer answer = new AssessmentAnswer();
            answer.setAssessmentId(assessment.getId());
            answer.setQuestionId(item.getQuestionId());
            answer.setAnswer(item.getAnswer());
            answerMapper.insert(answer);
        }
        
        return buildReport(assessment, scale, totalScore);
    }
    
    @Override
    public ReportVO getReport(Long assessmentId) {
        Assessment assessment = assessmentMapper.selectById(assessmentId);
        if (assessment == null) {
            throw new BusinessException(ResultCode.ASSESSMENT_NOT_FOUND);
        }
        
        Scale scale = scaleMapper.selectById(assessment.getScaleId());
        return buildReport(assessment, scale, assessment.getTotalScore().intValue());
    }
    
    @Override
    public Page<ReportVO> getAssessmentHistory(Integer current, Integer size) {
        Long userId = getCurrentUserId();
        
        Page<Assessment> page = new Page<>(current, size);
        LambdaQueryWrapper<Assessment> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Assessment::getUserId, userId)
                .orderByDesc(Assessment::getCreatedAt);
        
        Page<Assessment> assessmentPage = assessmentMapper.selectPage(page, wrapper);
        
        Page<ReportVO> voPage = new Page<>(assessmentPage.getCurrent(), assessmentPage.getSize(), assessmentPage.getTotal());
        voPage.setRecords(assessmentPage.getRecords().stream()
                .map(a -> {
                    Scale scale = scaleMapper.selectById(a.getScaleId());
                    return buildReport(a, scale, a.getTotalScore().intValue());
                })
                .collect(Collectors.toList()));
        
        return voPage;
    }
    
    private String calculateRiskLevel(Scale scale, int totalScore) {
        String interpretation = scale.getInterpretation();
        if (StrUtil.isBlank(interpretation)) {
            return "low";
        }
        
        JSONArray rules = JSONUtil.parseArray(interpretation);
        for (int i = 0; i < rules.size(); i++) {
            cn.hutool.json.JSONObject rule = rules.getJSONObject(i);
            int min = rule.getInt("min", 0);
            int max = rule.getInt("max", Integer.MAX_VALUE);
            if (totalScore >= min && totalScore <= max) {
                return rule.getStr("level", "low");
            }
        }
        return "low";
    }
    
    private ReportVO buildReport(Assessment assessment, Scale scale, int totalScore) {
        ReportVO vo = new ReportVO();
        vo.setAssessmentId(assessment.getId());
        vo.setScaleId(scale.getId());
        vo.setScaleName(scale.getName());
        vo.setTotalScore(BigDecimal.valueOf(totalScore));
        vo.setRiskLevel(assessment.getRiskLevel());
        vo.setCreatedAt(assessment.getCreatedAt());
        
        String interpretation = scale.getInterpretation();
        if (StrUtil.isNotBlank(interpretation)) {
            JSONArray rules = JSONUtil.parseArray(interpretation);
            for (int i = 0; i < rules.size(); i++) {
                cn.hutool.json.JSONObject rule = rules.getJSONObject(i);
                int min = rule.getInt("min", 0);
                int max = rule.getInt("max", Integer.MAX_VALUE);
                if (totalScore >= min && totalScore <= max) {
                    vo.setRiskText(rule.getStr("text", ""));
                    break;
                }
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
}
