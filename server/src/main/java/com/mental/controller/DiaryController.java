package com.mental.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mental.common.result.Result;
import com.mental.dto.DiaryDTO;
import com.mental.service.DiaryService;
import com.mental.vo.DiaryVO;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@Tag(name = "日记接口")
@RestController
@RequestMapping("/api/diary")
@RequiredArgsConstructor
public class DiaryController {
    
    private final DiaryService diaryService;
    
    @Operation(summary = "创建日记")
    @PostMapping
    public Result<DiaryVO> create(@Valid @RequestBody DiaryDTO dto) {
        return Result.success(diaryService.create(dto));
    }
    
    @Operation(summary = "获取日记详情")
    @GetMapping("/{id}")
    public Result<DiaryVO> getById(@PathVariable Long id) {
        return Result.success(diaryService.getById(id));
    }
    
    @Operation(summary = "获取日记列表")
    @GetMapping("/page")
    public Result<Page<DiaryVO>> getPage(
            @RequestParam(defaultValue = "1") Integer current,
            @RequestParam(defaultValue = "10") Integer size,
            @RequestParam(required = false) String emotionType) {
        return Result.success(diaryService.getPage(current, size, emotionType));
    }
    
    @Operation(summary = "删除日记")
    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        diaryService.delete(id);
        return Result.success();
    }
    
    @Operation(summary = "获取日记统计")
    @GetMapping("/statistics")
    public Result<Map<String, Object>> getStatistics() {
        return Result.success(diaryService.getStatistics());
    }
    
    @Operation(summary = "获取情绪趋势")
    @GetMapping("/trend")
    public Result<List<Map<String, Object>>> getEmotionTrend(
            @RequestParam(defaultValue = "30") Integer days) {
        return Result.success(diaryService.getEmotionTrend(days));
    }
}
