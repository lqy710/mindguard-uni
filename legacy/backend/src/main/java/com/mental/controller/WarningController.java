package com.mental.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mental.common.result.Result;
import com.mental.service.WarningService;
import com.mental.vo.StatisticsVO;
import com.mental.vo.WarningVO;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@Tag(name = "预警管理接口")
@RestController
@RequestMapping("/api/admin")
@RequiredArgsConstructor
public class WarningController {
    
    private final WarningService warningService;
    
    @Operation(summary = "获取预警列表")
    @GetMapping("/warnings")
    public Result<Page<WarningVO>> getPage(
            @RequestParam(defaultValue = "1") Integer current,
            @RequestParam(defaultValue = "10") Integer size,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String riskLevel) {
        return Result.success(warningService.getPage(current, size, status, riskLevel));
    }
    
    @Operation(summary = "获取预警详情")
    @GetMapping("/warning/{id}")
    public Result<WarningVO> getById(@PathVariable Long id) {
        return Result.success(warningService.getById(id));
    }
    
    @Operation(summary = "处理预警")
    @PutMapping("/warning/{id}/handle")
    public Result<Void> handle(@PathVariable Long id, @RequestParam String handleNote) {
        warningService.handle(id, handleNote);
        return Result.success();
    }
    
    @Operation(summary = "获取仪表盘统计数据")
    @GetMapping("/dashboard")
    public Result<StatisticsVO> getDashboardStatistics() {
        return Result.success(warningService.getDashboardStatistics());
    }
}
