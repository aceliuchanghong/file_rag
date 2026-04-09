import os
import sys
import numpy as np

from typing import Sequence
from openai import AsyncOpenAI
from dotenv import load_dotenv

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../")),
)

from z_utils.logging_config import get_logger

load_dotenv()
logger = get_logger(__name__)


class OpenAIEmbeddingModel:
    """OpenAI 嵌入模型"""

    def __init__(
        self,
        model_name: str = os.getenv("EMB_MODEL", "text-embedding-3-small"),
    ) -> None:
        self.client = AsyncOpenAI(
            base_url=os.getenv("EMB_BASE_URL"),
            api_key=os.getenv("EMB_API_KEY"),
        )
        self.model_name = model_name

        self._dimension = os.getenv("EMB_DIMENSION", 1024)

    @property
    def dimension(self) -> int:
        """返回向量维度"""
        return self._dimension

    async def embed(self, texts: Sequence[str]) -> np.ndarray:
        """
        调用 OpenAI API 获取嵌入向量。
        返回一个形状为 (len(texts), dimension) 的二维 numpy 数组。
        """
        response = await self.client.embeddings.create(
            input=texts, model=self.model_name
        )
        # 从 API 响应中提取所有的向量，并转换为 numpy 数组
        embeddings = [item.embedding for item in response.data]
        return np.array(embeddings)


def _normalize(vectors: np.ndarray) -> np.ndarray:
    """将向量归一化为单位长度，并安全处理零向量以避免报错。"""
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0  # 避免除以零的情况
    return vectors / norms


def average_embeddings(child_vectors: Sequence[np.ndarray]) -> np.ndarray:
    # 确保输入不为空
    if child_vectors is None or len(child_vectors) == 0:
        raise ValueError("average_embeddings 至少需要一个子向量作为输入。")

    # 统一转换为 numpy 数组，如果是 list 则堆叠，如果是 ndarray 则维持原样
    stacked = np.asarray(child_vectors)

    # 确保是二维的 (n, dim)
    if stacked.ndim == 1:
        stacked = stacked.reshape(1, -1)

    # 计算均值并归一化
    return _normalize(np.mean(stacked, axis=0, keepdims=True))[0]


if __name__ == "__main__":
    """
    uv run z_utils/embeddings.py
    """
    import asyncio

    async def main():
        model = OpenAIEmbeddingModel()
        texts = ["这是一个测试句子。", "这是另一个测试句子。"]
        embeddings = await model.embed(texts)
        print("嵌入向量形状:", embeddings.shape)
        average_embeddings_result = average_embeddings(embeddings)
        print("平均嵌入向量形状:", average_embeddings_result.shape)

    asyncio.run(main())
