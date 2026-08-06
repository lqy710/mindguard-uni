package com.mental.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

/**
 * 知识库检索请求
 */
@Data
public class RetrieveDTO {

    @NotBlank(message = "查询内容不能为空")
    private String query;

    /** 返回条数，服务端会裁剪到 1~10 */
    private Integer topK = 3;
}
