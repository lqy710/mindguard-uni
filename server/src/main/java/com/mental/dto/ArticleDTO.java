package com.mental.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

/**
 * 知识文章新增 / 更新请求
 */
@Data
public class ArticleDTO {

    /** 更新时必填，新增时忽略 */
    private Long id;

    @NotNull(message = "分类不能为空")
    private Long categoryId;

    @NotBlank(message = "标题不能为空")
    private String title;

    private String summary;

    @NotBlank(message = "正文不能为空")
    private String content;

    private String coverImage;

    private String author;

    /** 1-已发布 0-草稿，默认发布 */
    private Integer status = 1;
}
