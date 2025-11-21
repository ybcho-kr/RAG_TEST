"""간단한 인메모리 벡터 저장소 클라이언트."""
from __future__ import annotations

import importlib.util
import uuid
from dataclasses import dataclass
from typing import Callable, Iterable, List, Sequence

import numpy as np

from src.preprocessing.chunker import Chunk


@dataclass
class VectorRecord:
    """벡터와 함께 원본 데이터를 보관하는 구조체."""

    id: str
    embedding: np.ndarray
    metadata: dict
    text: str


class VectorClient:
    """간단한 코사인 유사도 기반 검색 클라이언트."""

    def __init__(self, embedder: Callable[[Sequence[str]], np.ndarray] | None = None):
        self.embedder = embedder or self._default_embedder()
        self.records: List[VectorRecord] = []

    def _default_embedder(self) -> Callable[[Sequence[str]], np.ndarray]:
        if importlib.util.find_spec("sentence_transformers") is None:
            raise ImportError(
                "기본 임베더를 사용하려면 sentence-transformers 패키지를 설치하세요 \n"
                "예: pip install sentence-transformers"
            )

        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer("all-MiniLM-L6-v2")
        return lambda texts: np.asarray(model.encode(list(texts), convert_to_numpy=True))

    def clear(self) -> None:
        """저장된 모든 레코드를 초기화한다."""

        self.records.clear()

    def upsert(self, chunks: Iterable[Chunk]) -> List[str]:
        """청크를 임베딩하여 저장하고 식별자 목록을 반환한다."""

        texts = [chunk.content for chunk in chunks]
        embeddings = self.embedder(texts)
        ids: List[str] = []
        for chunk, vector in zip(chunks, embeddings):
            record_id = str(uuid.uuid4())
            ids.append(record_id)
            self.records.append(
                VectorRecord(
                    id=record_id,
                    embedding=np.asarray(vector, dtype=float),
                    metadata=chunk.metadata,
                    text=chunk.content,
                )
            )
        return ids

    def delete(self, ids: Iterable[str]) -> None:
        """지정한 ID의 레코드를 제거한다."""

        target = set(ids)
        self.records = [record for record in self.records if record.id not in target]

    def search(self, query: str, top_k: int = 5) -> List[VectorRecord]:
        """코사인 유사도 순으로 상위 결과를 반환한다."""

        if not self.records:
            return []

        query_vec = self.embedder([query])[0]
        matrix = np.stack([record.embedding for record in self.records])
        scores = self._cosine_similarity(query_vec, matrix)
        ranked_indices = np.argsort(scores)[::-1][:top_k]
        return [self.records[int(idx)] for idx in ranked_indices]

    @staticmethod
    def _cosine_similarity(query_vec: np.ndarray, matrix: np.ndarray) -> np.ndarray:
        query_norm = query_vec / (np.linalg.norm(query_vec) + 1e-10)
        matrix_norm = matrix / (np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-10)
        return matrix_norm @ query_norm
