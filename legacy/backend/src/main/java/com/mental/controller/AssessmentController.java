package com.mental.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mental.common.result.Result;
import com.mental.dto.AssessmentSubmitDTO;
import com.mental.service.AssessmentService;
import com.mental.vo.ReportVO;
import com.mental.vo.ScaleDetailVO;
import com.mental.vo.ScaleVO;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Tag(name = "测评接口")
@RestController
@RequestMapping("/api/assessment")
@RequiredArgsConstructor
public class AssessmentController {
    
    private final AssessmentService assessmentService;
    
    @Operation(summary = "获取量表列表")
    @GetMapping("/scales")
    public Result<List<ScaleVO>> getScaleList(@RequestParam(required = false) String category) {
        return Result.success(assessmentService.getScaleList(category));
    }
    
    @Operation(summary = "获取量表详情")
    @GetMapping("/scales/{scaleId}")
    public Result<ScaleDetailVO> getScaleDetail(@PathVariable Long scaleId) {
        return Result.success(assessmentService.getScaleDetail(scaleId));
    }
    
    @Operation(summary = "提交测评")
    @PostMapping("/submit")
    public Result<ReportVO> submitAssessment(@Valid @RequestBody AssessmentSubmitDTO dto) {
        return Result.success(assessmentService.submitAssessment(dto));
    }
    
    @Operation(summary = "获取测评报告")
    @GetMapping("/report/{assessmentId}")
    public Result<ReportVO> getReport(@PathVariable Long assessmentId) {
        return Result.success(assessmentService.getReport(assessmentId));
    }
    
    @Operation(summary = "获取测评历史")
    @GetMapping("/history")
    public Result<Page<ReportVO>> getAssessmentHistory(
            @RequestParam(defaultValue = "1") Integer current,
            @RequestParam(defaultValue = "10") Integer size) {
        return Result.success(assessmentService.getAssessmentHistory(current, size));
    }
}
