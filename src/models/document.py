"""문서 데이터 모델 정의 모듈."""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class Document:
    """정규화된 단일 문서를 표현하는 데이터 클래스."""

    content: str
    source: str
    page: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def with_metadata(self, **extra: Any) -> "Document":
        """기존 메타데이터에 추가 정보를 병합한 새 Document를 반환한다."""

        combined = {**self.metadata, **extra}
        return Document(content=self.content, source=self.source, page=self.page, metadata=combined)
