package com.mental.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.mental.common.result.Result;
import com.mental.dto.ArticleDTO;
import com.mental.dto.RetrieveDTO;
import com.mental.service.KnowledgeService;
import com.mental.vo.ArticleCategoryVO;
import com.mental.vo.ArticleDetailVO;
import com.mental.vo.ArticleVO;
import com.mental.vo.KnowledgeReferenceVO;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Tag(name = "知识库接口")
@RestController
@RequestMapping("/api/knowledge")
@RequiredArgsConstructor
public class KnowledgeController {

    private final KnowledgeService knowledgeService;

    @Operation(summary = "获取文章列表")
    @GetMapping("/articles")
    public Result<Page<ArticleVO>> getArticlePage(
            @RequestParam(defaultValue = "1") Integer current,
            @RequestParam(defaultValue = "10") Integer size,
            @RequestParam(required = false) Long categoryId,
            @RequestParam(required = false) String keyword) {
        return Result.success(knowledgeService.getArticlePage(current, size, categoryId, keyword));
    }

    @Operation(summary = "获取文章详情")
    @GetMapping("/article/{id}")
    public Result<ArticleDetailVO> getArticleDetail(@PathVariable Long id) {
        ArticleDetailVO detail = knowledgeService.getArticleDetail(id);
        if (detail == null) {
            return Result.error("文章不存在或已下架");
        }
        return Result.success(detail);
    }

    @Operation(summary = "获取热门文章")
    @GetMapping("/hot")
    public Result<List<ArticleVO>> getHotArticles(@RequestParam(defaultValue = "5") Integer limit) {
        return Result.success(knowledgeService.getHotArticles(limit));
    }

    @Operation(summary = "获取文章分类")
    @GetMapping("/categories")
    public Result<List<ArticleCategoryVO>> getCategories() {
        return Result.success(knowledgeService.getCategories());
    }

    @Operation(summary = "知识库检索（RAG）")
    @PostMapping("/retrieve")
    public Result<Map<String, Object>> retrieve(@Valid @RequestBody RetrieveDTO dto) {
        List<KnowledgeReferenceVO> references =
                knowledgeService.retrieve(dto.getQuery(), dto.getTopK());

        Map<String, Object> data = new HashMap<>();
        data.put("query", dto.getQuery());
        data.put("references", references);
        return Result.success(data);
    }

    @Operation(summary = "新增文章")
    @PostMapping("/article")
    public Result<Long> createArticle(@Valid @RequestBody ArticleDTO dto) {
        return Result.success(knowledgeService.createArticle(dto));
    }

    @Operation(summary = "更新文章")
    @PutMapping("/article/{id}")
    public Result<Void> updateArticle(@PathVariable Long id, @Valid @RequestBody ArticleDTO dto) {
        knowledgeService.updateArticle(id, dto);
        return Result.success();
    }

    @Operation(summary = "删除文章")
    @DeleteMapping("/article/{id}")
    public Result<Void> deleteArticle(@PathVariable Long id) {
        knowledgeService.deleteArticle(id);
        return Result.success();
    }

    @Operation(summary = "重建知识库向量索引")
    @PostMapping("/reindex")
    public Result<Map<String, Object>> reindex() {
        int chunkCount = knowledgeService.reindex();
        Map<String, Object> data = new HashMap<>();
        data.put("chunkCount", chunkCount);
        return Result.success(data);
    }
}
