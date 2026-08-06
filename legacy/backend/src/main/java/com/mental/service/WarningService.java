package com.mental.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mental.vo.StatisticsVO;
import com.mental.vo.WarningVO;

import java.util.Map;

public interface WarningService {
    
    Page<WarningVO> getPage(Integer current, Integer size, String status, String riskLevel);
    
    WarningVO getById(Long id);
    
    void handle(Long id, String handleNote);
    
    StatisticsVO getDashboardStatistics();
    
    Map<String, Object> assessUserRisk(Long userId);
    
    /**
     * 创建一条预警记录并推送给管理端。
     * <p>
     * 供 AI 对话的 trigger_warning 工具回调使用。为避免同一用户短时间内
     * 重复刷预警，实现里会做去重：若该用户已有同源未处理的预警，则不再新建。
     *
     * @param userId         触发预警的用户
     * @param riskLevel      high / medium / low
     * @param triggerSource  触发来源，如 ai_chat
     * @param triggerContent 触发内容原文
     * @return 预警记录 id；被去重或忽略时返回 null
     */
    Long createWarning(Long userId, String riskLevel, String triggerSource, String triggerContent);
}
