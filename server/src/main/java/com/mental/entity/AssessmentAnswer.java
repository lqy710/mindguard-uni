package com.mental.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("assessment_answer")
public class AssessmentAnswer {
    
    @TableId(type = IdType.AUTO)
    private Long id;
    
    private Long assessmentId;
    
    private Long questionId;
    
    private Integer answer;
    
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;
}
