"""Plain text ingestion utilities."""
from pathlib import Path

from .document import Document


def load_txt(path: str, encoding: str = "utf-8") -> Document:
    """Load a plain text file into a :class:`Document`."""
    file_path = Path(path)
    content = file_path.read_text(encoding=encoding)
    return Document(content=content, source=str(file_path), metadata={"format": "txt", "encoding": encoding})
