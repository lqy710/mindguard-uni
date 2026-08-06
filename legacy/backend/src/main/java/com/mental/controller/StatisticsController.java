package com.mental.controller;

import com.mental.common.result.Result;
import com.mental.service.StatisticsService;
import com.mental.vo.HomeStatsVO;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@Tag(name = "统计接口")
@RestController
@RequestMapping("/api/stats")
@RequiredArgsConstructor
public class StatisticsController {
    
    private final StatisticsService statisticsService;
    
    @Operation(summary = "获取首页统计数据")
    @GetMapping("/home")
    public Result<HomeStatsVO> getHomeStats() {
        return Result.success(statisticsService.getHomeStats());
    }
}
