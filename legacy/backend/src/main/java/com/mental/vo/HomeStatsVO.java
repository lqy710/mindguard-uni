package com.mental.vo;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class HomeStatsVO {
    
    private Long userCount;
    
    private Long assessmentCount;
    
    private Long diaryCount;
    
    private Long articleCount;
    
    private Long scaleCount;
}
