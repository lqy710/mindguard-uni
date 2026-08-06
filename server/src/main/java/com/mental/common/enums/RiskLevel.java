package com.mental.common.enums;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public enum RiskLevel {
    LOW("low", "低风险"),
    MEDIUM("medium", "中风险"),
    HIGH("high", "高风险");
    
    private final String code;
    private final String desc;
    
    public static RiskLevel fromCode(String code) {
        for (RiskLevel level : values()) {
            if (level.getCode().equals(code)) {
                return level;
            }
        }
        return LOW;
    }
}
