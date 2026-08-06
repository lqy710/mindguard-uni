package com.mental.config;

import com.mental.service.KnowledgeService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;

/**
 * 应用启动后把知识库文章推送到 AI 服务构建向量索引。
 *
 * 在独立守护线程中执行：AI 服务可能尚未就绪或向量化耗时较长，不应阻塞应用启动。
 * 项目未启用 @EnableAsync，故不使用 @Async，避免注解失效反而变成同步阻塞。
 * 初始化失败不影响主流程，可随时调用 /api/knowledge/reindex 手动重建。
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class KnowledgeIndexInitializer {

    private final KnowledgeService knowledgeService;

    @EventListener(ApplicationReadyEvent.class)
    public void initIndex() {
        Thread worker = new Thread(() -> {
            try {
                int chunks = knowledgeService.reindex();
                if (chunks > 0) {
                    log.info("知识库向量索引初始化完成，共 {} 个片段", chunks);
                } else {
                    log.warn("知识库向量索引未生成，AI 将使用内置兜底语料");
                }
            } catch (Exception e) {
                log.warn("知识库向量索引初始化失败: {}", e.getMessage());
            }
        }, "knowledge-index-init");

        worker.setDaemon(true);
        worker.start();
    }
}
