"""Chunking utilities to split cleaned text into retrievable units."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Literal, Optional
import uuid

from ..ingestion import Document


@dataclass
class Chunk:
    id: str
    document_id: str
    text: str
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class ChunkingConfig:
    strategy: Literal["characters", "tokens"] = "tokens"
    chunk_size: int = 500
    overlap: int = 50

    def __post_init__(self) -> None:
        if self.overlap >= self.chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")


def _tokenize(text: str) -> List[str]:
    return text.split()


def _chunk_indices(length: int, size: int, overlap: int) -> Iterable[range]:
    step = size - overlap
    for start in range(0, length, step):
        end = min(start + size, length)
        yield range(start, end)
        if end == length:
            break


def chunk_document(document: Document, config: Optional[ChunkingConfig] = None) -> List[Chunk]:
    config = config or ChunkingConfig()
    text = document.content

    if config.strategy == "characters":
        units = list(text)
    else:
        units = _tokenize(text)

    ranges = list(_chunk_indices(len(units), config.chunk_size, config.overlap))
    chunks: List[Chunk] = []
    for idx, span in enumerate(ranges):
        if config.strategy == "characters":
            chunk_text = "".join(units[i] for i in span)
        else:
            chunk_text = " ".join(units[i] for i in span)

        metadata = {
            **document.metadata,
            "chunk_index": str(idx),
            "chunk_size": str(len(span)),
            "strategy": config.strategy,
        }

        chunks.append(
            Chunk(
                id=str(uuid.uuid4()),
                document_id=document.id,
                text=chunk_text,
                metadata=metadata,
            )
        )
    return chunks
