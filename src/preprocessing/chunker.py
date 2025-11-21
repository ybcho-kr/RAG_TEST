"""텍스트를 청크 단위로 분할하는 모듈."""
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

from src.models.document import Document


def _split_tokens(text: str) -> List[str]:
    """단순 공백 기반 토큰 분할."""

    return text.split()


@dataclass
class Chunk:
    """청크 결과를 표현하는 데이터 클래스."""

    content: str
    metadata: Dict[str, object]


class TextChunker:
    """텍스트 청크 생성기."""

    def __init__(self, max_length: int = 500, overlap: int = 50, by_tokens: bool = False):
        if overlap >= max_length:
            raise ValueError("overlap 값은 max_length 보다 작아야 합니다.")
        self.max_length = max_length
        self.overlap = overlap
        self.by_tokens = by_tokens

    def _window(self, tokens: List[str]) -> Iterable[List[str]]:
        step = self.max_length - self.overlap
        for start in range(0, len(tokens), step):
            yield tokens[start : start + self.max_length]

    def chunk_text(self, text: str, base_metadata: Optional[Dict[str, object]] = None) -> List[Chunk]:
        """문자열을 설정에 맞게 청크로 나눈다."""

        base_metadata = base_metadata or {}
        if self.by_tokens:
            tokens = _split_tokens(text)
            windows = [" ".join(window) for window in self._window(tokens)]
        else:
            windows = []
            step = self.max_length - self.overlap
            for start in range(0, len(text), step):
                windows.append(text[start : start + self.max_length])

        chunks: List[Chunk] = []
        for idx, window in enumerate(windows):
            metadata = {**base_metadata, "chunk_index": idx}
            chunks.append(Chunk(content=window, metadata=metadata))
        return chunks

    def chunk_documents(self, documents: Iterable[Document]) -> List[Chunk]:
        """Document 시퀀스를 받아 순차적으로 청크를 생성한다."""

        chunks: List[Chunk] = []
        for doc in documents:
            base_metadata = {"source": doc.source, **(doc.metadata or {})}
            if doc.page is not None:
                base_metadata["page"] = doc.page
            chunks.extend(self.chunk_text(doc.content, base_metadata=base_metadata))
        return chunks
