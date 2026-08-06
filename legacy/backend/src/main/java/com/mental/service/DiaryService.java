package com.mental.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mental.dto.DiaryDTO;
import com.mental.vo.DiaryVO;

import java.util.List;
import java.util.Map;

public interface DiaryService {
    
    DiaryVO create(DiaryDTO dto);
    
    DiaryVO getById(Long id);
    
    Page<DiaryVO> getPage(Integer current, Integer size, String emotionType);
    
    void delete(Long id);
    
    Map<String, Object> getStatistics();
    
    List<Map<String, Object>> getEmotionTrend(Integer days);
}
