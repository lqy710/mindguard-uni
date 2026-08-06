package com.mental.vo;

import lombok.Data;

import java.util.List;

@Data
public class StatisticsVO {
    
    private Long totalUsers;
    
    private Long todayNewUsers;
    
    private Long totalAssessments;
    
    private Long todayAssessments;
    
    private Long totalDiaries;
    
    private Long todayDiaries;
    
    private Long pendingWarnings;
    
    private Long highRiskUsers;
    
    private List<ChartData> assessmentTrend;
    
    private List<ChartData> emotionDistribution;
    
    @Data
    public static class ChartData {
        private String label;
        private Long value;
    }
}
