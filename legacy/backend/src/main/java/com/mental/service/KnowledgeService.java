package com.mental.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mental.dto.ArticleDTO;
import com.mental.vo.ArticleCategoryVO;
import com.mental.vo.ArticleDetailVO;
import com.mental.vo.ArticleVO;
import com.mental.vo.KnowledgeReferenceVO;

import java.util.List;

public interface KnowledgeService {

    Page<ArticleVO> getArticlePage(Integer current, Integer size, Long categoryId, String keyword);

    ArticleDetailVO getArticleDetail(Long id);

    List<ArticleVO> getHotArticles(Integer limit);

    /** 全部分类（含文章数） */
    List<ArticleCategoryVO> getCategories();

    Long createArticle(ArticleDTO dto);

    void updateArticle(Long id, ArticleDTO dto);

    void deleteArticle(Long id);

    /** RAG 检索：返回与 query 最相关的知识片段 */
    List<KnowledgeReferenceVO> retrieve(String query, Integer topK);

    /** 把数据库中已发布文章全量推送到 AI 服务重建向量索引，返回片段数 */
    int reindex();
}
