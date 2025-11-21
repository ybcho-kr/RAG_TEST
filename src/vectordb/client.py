"""Lightweight vector database wrapper with in-memory fallback."""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Dict, Iterable, List, Sequence, Tuple

try:  # pragma: no cover - optional dependency
    import chromadb
except Exception:  # pragma: no cover - optional dependency
    chromadb = None  # type: ignore


@dataclass
class VectorRecord:
    id: str
    vector: List[float]
    metadata: Dict[str, str]
    text: str


class InMemoryVectorStore:
    """Simple cosine-similarity store used when no external backend is configured."""

    def __init__(self, dim: int):
        self.dim = dim
        self._store: Dict[str, VectorRecord] = {}

    def upsert(self, records: Iterable[VectorRecord]) -> None:
        for rec in records:
            if len(rec.vector) != self.dim:
                raise ValueError(f"Vector dimension mismatch: expected {self.dim}, got {len(rec.vector)}")
            self._store[rec.id] = rec

    def delete(self, ids: Sequence[str]) -> None:
        for id_ in ids:
            self._store.pop(id_, None)

    def search(self, query: List[float], top_k: int = 5) -> List[Tuple[VectorRecord, float]]:
        def cosine(a: List[float], b: List[float]) -> float:
            denom = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(x * x for x in b))
            if denom == 0:
                return 0.0
            return sum(x * y for x, y in zip(a, b)) / denom

        scores = [(rec, cosine(query, rec.vector)) for rec in self._store.values()]
        scores.sort(key=lambda pair: pair[1], reverse=True)
        return scores[:top_k]


class VectorDBClient:
    """Wrapper for vector operations with optional Chroma backend."""

    def __init__(self, dimension: int, collection_name: str = "documents"):
        self.dimension = dimension
        self.collection_name = collection_name
        self._client = chromadb.Client() if chromadb else None
        self._collection = None
        if self._client:
            self._collection = self._client.get_or_create_collection(name=collection_name)
        else:
            self._collection = InMemoryVectorStore(dim=dimension)

    def upsert(self, vectors: Iterable[VectorRecord]) -> None:
        if self._client:
            ids = [v.id for v in vectors]
            texts = [v.text for v in vectors]
            metadatas = [v.metadata for v in vectors]
            embeddings = [v.vector for v in vectors]
            self._collection.upsert(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)  # type: ignore[attr-defined]
        else:
            self._collection.upsert(vectors)  # type: ignore[arg-type]

    def delete(self, ids: Sequence[str]) -> None:
        if self._client:
            self._collection.delete(ids=ids)  # type: ignore[attr-defined]
        else:
            self._collection.delete(ids)

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Tuple[VectorRecord, float]]:
        if self._client:
            results = self._collection.query(query_embeddings=[query_vector], n_results=top_k)  # type: ignore[attr-defined]
            matches: List[Tuple[VectorRecord, float]] = []
            for i in range(len(results["ids"][0])):
                record = VectorRecord(
                    id=results["ids"][0][i],
                    text=results["documents"][0][i],
                    metadata=results["metadatas"][0][i],
                    vector=query_vector,
                )
                matches.append((record, results["distances"][0][i]))
            return matches
        return self._collection.search(query_vector, top_k=top_k)


def simple_embed(text: str, dimension: int = 8) -> List[float]:
    """
    Deterministic, lightweight embedding suitable for tests.

    It hashes each character into ``dimension`` buckets and normalizes the result
    to unit length.
    """

    buckets = [0.0] * dimension
    for ch in text:
        buckets[hash(ch) % dimension] += 1.0
    norm = math.sqrt(sum(v * v for v in buckets)) or 1.0
    return [v / norm for v in buckets]
