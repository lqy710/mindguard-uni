package com.mental.vo;

import lombok.Data;

/**
 * 文章分类
 */
@Data
public class ArticleCategoryVO {

    private Long id;

    private String name;

    private String description;

    private Integer sort;

    /** 该分类下已发布的文章数 */
    private Long articleCount;
}
