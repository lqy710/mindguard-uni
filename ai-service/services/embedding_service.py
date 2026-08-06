"""
向量化服务

仅使用远程 API：硅基流动（SiliconFlow）的稠密向量模型，无需本地下载大模型，
跨环境（本机 / 生产 / Docker）只需联网 + API Key 即可使用。

未配置 SILICONFLOW_API_KEY 时直接抛错，不再静默降级到本地模型或 TF-IDF 兜底，
避免「看似可用实则是假检索」的隐患。所有向量在返回前均已做 L2 归一化，
因此余弦相似度 == 点积。
"""

import logging
import threading
from typing import List, Optional

import numpy as np

logger = logging.getLogger(__name__)


def _l2_normalize(matrix: np.ndarray) -> np.ndarray:
    """对二维矩阵按行做 L2 归一化，原位返回。"""
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    matrix /= norms
    return matrix


class _RemoteEmbeddingService:
    """基于硅基流动（SiliconFlow）/ OpenAI 兼容 embeddings 接口的远程编码器。"""

    def __init__(self, api_key: str, model: str, base_url: str):
        import requests  # 延迟导入，避免无网络环境下也强制依赖

        self._requests = requests
        self._api_key = api_key
        self._model = model
        self._url = base_url.rstrip("/") + "/embeddings"
        self._lock = threading.Lock()
        self._dim: Optional[int] = None
        logger.info("远程 embedding 编码器就绪: %s", model)

    @property
    def dimension(self) -> int:
        if self._dim is None:
            # 用一条样本探测维度
            self._dim = len(self.encode_one("探测维度"))
        return self._dim

    @property
    def is_dense(self) -> bool:
        # 远程 SiliconFlow 稠密向量模型，恒为 True
        return True

    def _call(self, texts: List[str]) -> np.ndarray:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": self._model, "input": texts, "encoding_format": "float"}
        resp = self._requests.post(self._url, headers=headers, json=payload, timeout=30)
        if resp.status_code != 200:
            raise RuntimeError(
                f"SiliconFlow embedding 接口返回 {resp.status_code}: {resp.text[:300]}"
            )
        data = resp.json()["data"]
        # 接口返回顺序与输入顺序一致，按 index 排序更稳妥
        data.sort(key=lambda d: d["index"])
        return np.asarray([d["embedding"] for d in data], dtype=np.float32)

    def encode(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, self.dimension if self._dim else 0), dtype=np.float32)
        with self._lock:
            vecs = self._call(texts)
        _l2_normalize(vecs)
        return vecs

    def encode_one(self, text: str) -> np.ndarray:
        return self.encode([text])[0]


class EmbeddingService:
    """
    统一向量化入口：仅使用硅基流动（SiliconFlow）远程稠密向量模型，
    对外暴露 encode / encode_one / is_dense / dimension /
    min_score / relevance_floor，调用方无需关心底层实现。
    """

    def __init__(self):
        self._impl = self._build()
        # min_score: 单个片段被保留的最低分
        # relevance_floor: 整条 query 是否算"命中知识库"的最高分门槛
        # 稠密模型（bge）对任意中文都有偏高基线，闲聊最高分约 0.38，
        # 相关提问最高分普遍 0.47+，取 0.42 区分。
        self.min_score = 0.30
        self.relevance_floor = 0.42
        logger.info(
            "EmbeddingService 使用【%s】编码器, dim=%s, is_dense=%s, "
            "min_score=%s, relevance_floor=%s",
            type(self._impl).__name__,
            self._impl.dimension,
            self._impl.is_dense,
            self.min_score,
            self.relevance_floor,
        )

    @staticmethod
    def _build():
        # 仅使用远程 API（SiliconFlow），不提供本地/兜底降级。
        # 未配置 API Key 时直接抛错，避免「看似可用实则是假检索」。
        from config import (
            SILICONFLOW_API_KEY,
            SILICONFLOW_EMBEDDING_MODEL,
            SILICONFLOW_BASE_URL,
        )

        if not (SILICONFLOW_API_KEY and SILICONFLOW_EMBEDDING_MODEL):
            raise RuntimeError(
                "未配置 SILICONFLOW_API_KEY / SILICONFLOW_EMBEDDING_MODEL，"
                "embedding 服务无法启动（已移除本地/兜底降级）。"
            )
        return _RemoteEmbeddingService(
            api_key=SILICONFLOW_API_KEY,
            model=SILICONFLOW_EMBEDDING_MODEL,
            base_url=SILICONFLOW_BASE_URL,
        )

    @property
    def is_dense(self) -> bool:
        return self._impl.is_dense

    @property
    def dimension(self) -> int:
        return self._impl.dimension

    def encode(self, texts: List[str]) -> np.ndarray:
        return self._impl.encode(texts)

    def encode_one(self, text: str) -> np.ndarray:
        return self._impl.encode_one(text)


# 模块级单例，所有调用方共享
embedding_service = EmbeddingService()
