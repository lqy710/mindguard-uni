package com.mental.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mental.dto.AssessmentSubmitDTO;
import com.mental.vo.ReportVO;
import com.mental.vo.ScaleDetailVO;
import com.mental.vo.ScaleVO;

import java.util.List;

public interface AssessmentService {
    
    List<ScaleVO> getScaleList(String category);
    
    ScaleDetailVO getScaleDetail(Long scaleId);
    
    ReportVO submitAssessment(AssessmentSubmitDTO dto);
    
    ReportVO getReport(Long assessmentId);
    
    Page<ReportVO> getAssessmentHistory(Integer current, Integer size);
}
