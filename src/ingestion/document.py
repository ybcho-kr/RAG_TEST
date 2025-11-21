from dataclasses import dataclass, field
from typing import Dict
import uuid


@dataclass
class Document:
    """Represents a normalized document loaded from an external source."""

    content: str
    source: str
    metadata: Dict[str, str] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def with_metadata(self, **kwargs: str) -> "Document":
        updated = dict(self.metadata)
        updated.update({k: v for k, v in kwargs.items() if v is not None})
        return Document(content=self.content, source=self.source, metadata=updated, id=self.id)
