package com.mental.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mental.dto.ArticleDTO;
import com.mental.entity.Article;
import com.mental.entity.ArticleCategory;
import com.mental.mapper.ArticleCategoryMapper;
import com.mental.mapper.ArticleMapper;
import com.mental.service.KnowledgeService;
import com.mental.service.PythonAiService;
import com.mental.vo.ArticleCategoryVO;
import com.mental.vo.ArticleDetailVO;
import com.mental.vo.ArticleVO;
import com.mental.vo.KnowledgeReferenceVO;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class KnowledgeServiceImpl implements KnowledgeService {

    /** 已发布状态 */
    private static final int STATUS_PUBLISHED = 1;

    private final ArticleMapper articleMapper;
    private final ArticleCategoryMapper articleCategoryMapper;
    private final PythonAiService pythonAiService;

    @Override
    public Page<ArticleVO> getArticlePage(Integer current, Integer size, Long categoryId, String keyword) {
        Page<Article> page = new Page<>(current == null ? 1 : current, size == null ? 10 : size);

        LambdaQueryWrapper<Article> wrapper = new LambdaQueryWrapper<Article>()
                .eq(Article::getStatus, STATUS_PUBLISHED)
                .eq(categoryId != null, Article::getCategoryId, categoryId)
                .orderByDesc(Article::getCreatedAt);

        if (keyword != null && !keyword.isBlank()) {
            String kw = keyword.trim();
            // 标题或摘要命中即可
            wrapper.and(w -> w.like(Article::getTitle, kw).or().like(Article::getSummary, kw));
        }

        Page<Article> entityPage = articleMapper.selectPage(page, wrapper);

        Page<ArticleVO> voPage = new Page<>(entityPage.getCurrent(), entityPage.getSize(), entityPage.getTotal());
        voPage.setRecords(toVoList(entityPage.getRecords()));
        return voPage;
    }

    @Override
    public ArticleDetailVO getArticleDetail(Long id) {
        Article article = articleMapper.selectById(id);
        if (article == null || !Integer.valueOf(STATUS_PUBLISHED).equals(article.getStatus())) {
            return null;
        }

        // 浏览量自增，用 SQL 自增避免并发覆盖
        articleMapper.update(null, new LambdaUpdateWrapper<Article>()
                .eq(Article::getId, id)
                .setSql("view_count = view_count + 1"));

        ArticleDetailVO vo = new ArticleDetailVO();
        BeanUtils.copyProperties(article, vo);
        vo.setCategoryName(resolveCategoryName(article.getCategoryId()));
        // 回填自增后的值，避免前端显示比实际少 1
        vo.setViewCount(article.getViewCount() == null ? 1 : article.getViewCount() + 1);
        return vo;
    }

    @Override
    public List<ArticleVO> getHotArticles(Integer limit) {
        int size = (limit == null || limit <= 0) ? 5 : Math.min(limit, 50);

        Page<Article> page = new Page<>(1, size);
        Page<Article> entityPage = articleMapper.selectPage(page, new LambdaQueryWrapper<Article>()
                .eq(Article::getStatus, STATUS_PUBLISHED)
                .orderByDesc(Article::getViewCount)
                .orderByDesc(Article::getCreatedAt));

        return toVoList(entityPage.getRecords());
    }

    @Override
    public List<ArticleCategoryVO> getCategories() {
        List<ArticleCategory> categories = articleCategoryMapper.selectList(
                new LambdaQueryWrapper<ArticleCategory>().orderByAsc(ArticleCategory::getSort));

        if (categories.isEmpty()) {
            return Collections.emptyList();
        }

        // 一次查出全部已发布文章的分类，避免 N+1 count
        Map<Long, Long> countMap = articleMapper.selectList(new LambdaQueryWrapper<Article>()
                        .select(Article::getCategoryId)
                        .eq(Article::getStatus, STATUS_PUBLISHED))
                .stream()
                .filter(a -> a.getCategoryId() != null)
                .collect(Collectors.groupingBy(Article::getCategoryId, Collectors.counting()));

        return categories.stream().map(c -> {
            ArticleCategoryVO vo = new ArticleCategoryVO();
            BeanUtils.copyProperties(c, vo);
            vo.setArticleCount(countMap.getOrDefault(c.getId(), 0L));
            return vo;
        }).collect(Collectors.toList());
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Long createArticle(ArticleDTO dto) {
        Article article = new Article();
        BeanUtils.copyProperties(dto, article);
        article.setId(null);
        article.setViewCount(0);
        article.setStatus(dto.getStatus() == null ? STATUS_PUBLISHED : dto.getStatus());

        articleMapper.insert(article);
        log.info("新增知识文章: id={}, title={}", article.getId(), article.getTitle());

        refreshIndexQuietly();
        return article.getId();
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void updateArticle(Long id, ArticleDTO dto) {
        Article existing = articleMapper.selectById(id);
        if (existing == null) {
            throw new IllegalArgumentException("文章不存在: " + id);
        }

        Article article = new Article();
        BeanUtils.copyProperties(dto, article);
        article.setId(id);
        // 浏览量不通过更新接口改写
        article.setViewCount(null);

        articleMapper.updateById(article);
        log.info("更新知识文章: id={}", id);

        refreshIndexQuietly();
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public void deleteArticle(Long id) {
        if (articleMapper.selectById(id) == null) {
            throw new IllegalArgumentException("文章不存在: " + id);
        }
        articleMapper.deleteById(id);
        log.info("删除知识文章: id={}", id);

        refreshIndexQuietly();
    }

    @Override
    public List<KnowledgeReferenceVO> retrieve(String query, Integer topK) {
        if (query == null || query.isBlank()) {
            return Collections.emptyList();
        }

        int k = (topK == null || topK <= 0) ? 3 : Math.min(topK, 10);

        List<Map<String, Object>> raw = pythonAiService.retrieveKnowledge(query.trim(), k);
        return raw.stream().map(item -> {
            KnowledgeReferenceVO vo = new KnowledgeReferenceVO();
            vo.setArticleId(toLong(item.get("articleId")));
            vo.setTitle(asString(item.get("title")));
            vo.setCategory(asString(item.get("category")));
            vo.setSnippet(asString(item.get("snippet")));
            vo.setScore(toDouble(item.get("score")));
            return vo;
        }).collect(Collectors.toList());
    }

    @Override
    public int reindex() {
        List<Article> articles = articleMapper.selectList(new LambdaQueryWrapper<Article>()
                .eq(Article::getStatus, STATUS_PUBLISHED));

        if (articles.isEmpty()) {
            log.warn("知识库为空，跳过索引重建");
            return 0;
        }

        Map<Long, String> categoryNames = loadCategoryNames();

        List<Map<String, Object>> payload = articles.stream().map(a -> {
            Map<String, Object> m = new HashMap<>();
            m.put("id", a.getId());
            m.put("title", a.getTitle());
            m.put("summary", a.getSummary());
            m.put("content", a.getContent());
            m.put("category", categoryNames.getOrDefault(a.getCategoryId(), ""));
            return m;
        }).collect(Collectors.toList());

        int chunks = pythonAiService.reindexKnowledge(payload);
        log.info("知识库索引重建完成: {} 篇 -> {} 片段", articles.size(), chunks);
        return chunks;
    }

    /**
     * 文章变更后刷新向量索引。
     * 索引失败不应导致业务事务回滚，因此吞掉异常只记日志。
     */
    private void refreshIndexQuietly() {
        try {
            reindex();
        } catch (Exception e) {
            log.warn("刷新知识库索引失败，稍后可手动调用 /api/knowledge/reindex: {}", e.getMessage());
        }
    }

    private List<ArticleVO> toVoList(List<Article> articles) {
        if (articles == null || articles.isEmpty()) {
            return Collections.emptyList();
        }
        Map<Long, String> names = loadCategoryNames();
        return articles.stream().map(a -> {
            ArticleVO vo = new ArticleVO();
            BeanUtils.copyProperties(a, vo);
            vo.setCategoryName(names.getOrDefault(a.getCategoryId(), ""));
            return vo;
        }).collect(Collectors.toList());
    }

    private Map<Long, String> loadCategoryNames() {
        return articleCategoryMapper.selectList(null).stream()
                .collect(Collectors.toMap(ArticleCategory::getId, ArticleCategory::getName, (a, b) -> a));
    }

    private String resolveCategoryName(Long categoryId) {
        if (categoryId == null) {
            return "";
        }
        ArticleCategory category = articleCategoryMapper.selectById(categoryId);
        return category == null ? "" : category.getName();
    }

    private static String asString(Object value) {
        return value == null ? null : String.valueOf(value);
    }

    private static Long toLong(Object value) {
        if (value instanceof Number n) {
            return n.longValue();
        }
        try {
            return value == null ? null : Long.valueOf(String.valueOf(value));
        } catch (NumberFormatException e) {
            return null;
        }
    }

    private static Double toDouble(Object value) {
        if (value instanceof Number n) {
            return n.doubleValue();
        }
        try {
            return value == null ? null : Double.valueOf(String.valueOf(value));
        } catch (NumberFormatException e) {
            return null;
        }
    }
}
