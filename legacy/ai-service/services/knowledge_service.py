"""
知识库检索服务（RAG 的 R）

- 文章正文按段落切成 chunk，逐 chunk 向量化后存在内存 numpy 矩阵中
- 检索时对 query 编码，用矩阵乘法一次算出全部余弦相似度，取 top_k
- 语料来源：后端通过 /api/knowledge/reindex 推送，或回退到本地 seed 语料

数据量在万级 chunk 以内时，numpy 暴力检索的延迟完全可接受（毫秒级），
无需引入 faiss / pgvector 等额外依赖。
"""

import logging
import re
import threading
from typing import Any, Dict, List, Optional

import numpy as np

from services.embedding_service import embedding_service

logger = logging.getLogger(__name__)

# 单个 chunk 的目标字符数与重叠字符数
CHUNK_SIZE = 320
CHUNK_OVERLAP = 60

# 相关性阈值默认取自当前编码器（稠密/稀疏量纲不同），传 None 即自适应

_HTML_TAG = re.compile(r"<[^>]+>")
_MULTI_SPACE = re.compile(r"[ \t\r\f\v]+")
_MULTI_NEWLINE = re.compile(r"\n{2,}")


def strip_html(text: str) -> str:
    """去掉文章正文里的 HTML 标签，保留段落换行。"""
    if not text:
        return ""
    # 块级标签转换成换行，避免段落粘连
    text = re.sub(r"</(p|div|h[1-6]|li|br)>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = _HTML_TAG.sub("", text)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
    text = _MULTI_SPACE.sub(" ", text)
    text = _MULTI_NEWLINE.sub("\n", text)
    return text.strip()


def split_into_chunks(
    text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP
) -> List[str]:
    """
    先按自然段切，段落过长再按滑动窗口切；过短的段落合并到下一段。
    """
    text = (text or "").strip()
    if not text:
        return []

    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks: List[str] = []
    buffer = ""

    def flush_buffer() -> None:
        nonlocal buffer
        if buffer.strip():
            chunks.append(buffer.strip())
        buffer = ""

    for para in paragraphs:
        if len(para) > chunk_size:
            flush_buffer()
            step = max(chunk_size - overlap, 1)
            for start in range(0, len(para), step):
                piece = para[start : start + chunk_size].strip()
                if piece:
                    chunks.append(piece)
                if start + chunk_size >= len(para):
                    break
        elif len(buffer) + len(para) + 1 <= chunk_size:
            buffer = f"{buffer}\n{para}" if buffer else para
        else:
            flush_buffer()
            buffer = para

    flush_buffer()
    return chunks


class KnowledgeService:
    """内存向量索引 + 余弦检索。写操作加锁，读操作无锁（快照替换保证一致性）。"""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        # 每个元素: {article_id, title, category, chunk_index, text}
        self._chunks: List[Dict[str, Any]] = []
        self._matrix: Optional[np.ndarray] = None
        self._seeded = False

    # ---------- 索引构建 ----------

    def build_index(self, articles: List[Dict[str, Any]]) -> int:
        """
        用给定文章全量重建索引。

        articles 元素形如:
            {"id": 1, "title": "...", "content": "...",
             "summary": "...", "category": "焦虑情绪"}

        返回生成的 chunk 数量。
        """
        chunks: List[Dict[str, Any]] = []

        for article in articles or []:
            article_id = article.get("id")
            title = (article.get("title") or "").strip()
            category = (article.get("category") or "").strip()
            summary = strip_html(article.get("summary") or "")
            body = strip_html(article.get("content") or "")

            # 摘要单独作为一个 chunk，通常最能概括文章主旨
            pieces: List[str] = []
            if summary:
                pieces.append(summary)
            pieces.extend(split_into_chunks(body))

            if not pieces and title:
                pieces = [title]

            for idx, piece in enumerate(pieces):
                # 把标题拼进待编码文本，提升主题相关性
                embed_text = f"{title}。{piece}" if title else piece
                chunks.append(
                    {
                        "article_id": article_id,
                        "title": title,
                        "category": category,
                        "chunk_index": idx,
                        "text": piece,
                        "_embed_text": embed_text,
                    }
                )

        if chunks:
            matrix = embedding_service.encode([c["_embed_text"] for c in chunks])
        else:
            matrix = None

        for chunk in chunks:
            chunk.pop("_embed_text", None)

        with self._lock:
            self._chunks = chunks
            self._matrix = matrix
            self._seeded = True

        logger.info("知识库索引重建完成：%s 篇文章 -> %s 个片段", len(articles or []), len(chunks))
        return len(chunks)

    def ensure_seeded(self) -> None:
        """索引为空时装载内置兜底语料，保证 RAG 至少有内容可用。"""
        if self._seeded:
            return
        with self._lock:
            if self._seeded:
                return
        self.build_index(SEED_ARTICLES)

    # ---------- 检索 ----------

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        min_score: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        检索与 query 最相关的知识片段。

        返回按相似度降序排列的列表，每项含
        article_id / title / category / snippet / score。
        同一篇文章只保留得分最高的片段，避免引用重复。
        """
        query = (query or "").strip()
        if not query:
            return []

        if min_score is None:
            min_score = embedding_service.min_score

        self.ensure_seeded()

        chunks = self._chunks
        matrix = self._matrix
        if not chunks or matrix is None or matrix.shape[0] == 0:
            return []

        query_vec = embedding_service.encode_one(query)
        # 向量均已归一化，点积即余弦相似度
        scores = matrix @ query_vec

        # 取足够多候选，供后续按文章去重
        candidate_n = int(min(scores.shape[0], max(top_k * 4, top_k)))
        if candidate_n >= scores.shape[0]:
            # argpartition 要求 kth < n，候选数等于总数时直接全排序
            top_idx = np.argsort(-scores)
        else:
            top_idx = np.argpartition(-scores, candidate_n - 1)[:candidate_n]
            top_idx = top_idx[np.argsort(-scores[top_idx])]

        # 相关性门槛（按最高分判定整条 query 是否命中知识库）。
        # bge 这类模型对任意中文文本都会给出偏高的基线相似度，
        # 闲聊（"你好呀"/"谢谢你"）最高分约 0.32~0.38，
        # 真正相关的提问最高分普遍在 0.47 以上，
        # 因此先用最高分卡一道：整体不够相关就直接不返回引用，
        # 避免给 AI 回复挂上牛头不对马嘴的"参考来源"。
        best_score = float(scores[top_idx[0]]) if len(top_idx) else 0.0
        if best_score < embedding_service.relevance_floor:
            return []

        # 相对阈值：低于最高分一定比例的结果通常是"蹭词"噪声。
        relative_floor = best_score * 0.55

        results: List[Dict[str, Any]] = []
        seen_articles = set()

        for idx in top_idx:
            score = float(scores[idx])
            if score < min_score or score < relative_floor:
                continue

            chunk = chunks[int(idx)]
            article_id = chunk["article_id"]
            if article_id in seen_articles:
                continue
            seen_articles.add(article_id)

            results.append(
                {
                    "articleId": article_id,
                    "title": chunk["title"],
                    "category": chunk["category"],
                    "snippet": chunk["text"],
                    "score": round(score, 4),
                }
            )

            if len(results) >= top_k:
                break

        return results

    def build_context(self, references: List[Dict[str, Any]], max_chars: int = 1500) -> str:
        """把检索结果拼成注入 system prompt 的知识上下文文本。"""
        if not references:
            return ""

        blocks: List[str] = []
        used = 0
        for i, ref in enumerate(references, start=1):
            snippet = ref.get("snippet", "").strip()
            if not snippet:
                continue
            block = f"[资料{i}]《{ref.get('title', '')}》\n{snippet}"
            if used + len(block) > max_chars:
                break
            blocks.append(block)
            used += len(block)

        return "\n\n".join(blocks)

    def stats(self) -> Dict[str, Any]:
        return {
            "chunkCount": len(self._chunks),
            "articleCount": len({c["article_id"] for c in self._chunks}),
            "dimension": embedding_service.dimension,
            "denseModel": embedding_service.is_dense,
            "seeded": self._seeded,
        }


# 后端尚未推送语料时的内置兜底知识，覆盖最常见的求助主题
SEED_ARTICLES: List[Dict[str, Any]] = [
    {
        "id": -1,
        "title": "认识抑郁：它不只是心情不好",
        "category": "抑郁情绪",
        "summary": "抑郁症是持续影响思维、情感与日常功能的心理疾病，不同于短暂的情绪低落。",
        "content": (
            "抑郁的常见表现包括：持续的悲伤、空虚或绝望感；对以前喜欢的活动失去兴趣；"
            "睡眠问题（失眠或睡眠过多）；疲劳和精力不足；食欲变化；注意力难以集中；自责或无价值感。\n"
            "如果这些状态持续两周以上并影响到工作、学习或人际关系，建议尽快寻求专业帮助。"
            "心理咨询、规律作息与适度运动都能有效改善抑郁症状。"
        ),
    },
    {
        "id": -2,
        "title": "焦虑症的自我调节方法",
        "category": "焦虑情绪",
        "summary": "焦虑是正常情绪反应，过度或持续过久时可通过呼吸、放松与认知重构缓解。",
        "content": (
            "深呼吸练习：4-7-8 呼吸法，吸气 4 秒、屏息 7 秒、呼气 8 秒，可激活副交感神经帮助身体放松。\n"
            "渐进式肌肉放松：从头到脚依次紧张再放松各肌肉群，帮助识别并释放身体紧张。\n"
            "正念冥想：不加评判地观察当下的想法和感受，减少对未来的过度担忧。\n"
            "认知重构：识别并挑战消极的自动思维，用更客观合理的想法替代它们。"
        ),
    },
    {
        "id": -3,
        "title": "压力管理：让生活更轻松",
        "category": "压力管理",
        "summary": "压力来自工作、学习、人际与经济等多方面，可通过时间管理与社会支持系统应对。",
        "content": (
            "时间管理：设置优先级、拆分任务、避免拖延，能显著减少因时间紧迫带来的压力。\n"
            "运动锻炼：规律运动促进内啡肽分泌，改善心情并增强抗压能力。\n"
            "社交支持：与家人朋友保持联系、分享感受，是缓冲压力最有效的因素之一。\n"
            "健康生活方式：保证充足睡眠、均衡饮食，限制咖啡因和酒精摄入。"
        ),
    },
    {
        "id": -4,
        "title": "改善睡眠质量的实用建议",
        "category": "睡眠健康",
        "summary": "失眠与情绪问题互相影响，稳定的睡眠节律是心理健康的基础。",
        "content": (
            "固定起床时间比固定入睡时间更重要，即使前一晚没睡好也尽量按时起床。\n"
            "睡前一小时避免使用手机等蓝光设备，可用阅读、温水泡脚替代。\n"
            "床只用于睡觉：若躺下 20 分钟仍无睡意，起身到别处做放松活动，有困意再回床。\n"
            "白天保持适度光照和运动，午后避免摄入咖啡因。"
        ),
    },
    {
        "id": -5,
        "title": "情绪调节的基本技巧",
        "category": "情绪调节",
        "summary": "情绪没有好坏之分，识别并接纳情绪是有效调节的第一步。",
        "content": (
            "命名情绪：用具体词汇描述当下感受（如失落、烦躁、委屈），仅仅命名就能降低情绪强度。\n"
            "接纳而非对抗：允许情绪存在，不因为产生负面情绪而责备自己。\n"
            "表达性书写：把困扰写下来，有助于理清思绪、减轻反刍思维。\n"
            "行为激活：即便情绪低落，也安排一些小而可完成的活动，通过行动带动情绪回升。"
        ),
    },
]


# 进程内共享实例
knowledge_service = KnowledgeService()
