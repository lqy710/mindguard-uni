package com.mental.vo;

import lombok.Data;

import java.time.LocalDateTime;

/**
 * 文章详情。
 * 在 ArticleVO 的字段基础上增加正文，列表接口仍用 ArticleVO 以免传输大字段。
 */
@Data
public class ArticleDetailVO {

    private Long id;

    private Long categoryId;

    private String categoryName;

    private String title;

    private String summary;

    /** 文章正文 */
    private String content;

    private String coverImage;

    private String author;

    private Integer viewCount;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;
}
