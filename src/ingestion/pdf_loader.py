"""PDF ingestion utilities using pypdf."""
from pathlib import Path

from .document import Document

try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover - optional dependency
    PdfReader = None  # type: ignore


def load_pdf(path: str) -> Document:
    """
    Load a PDF file into a :class:`Document`.

    If :mod:`pypdf` is not installed, an informative error is raised.
    """

    if PdfReader is None:
        raise ImportError("pypdf is required to load PDF files")

    file_path = Path(path)
    reader = PdfReader(str(file_path))
    pages = [page.extract_text() or "" for page in reader.pages]
    content = "\n".join(pages)

    return Document(content=content, source=str(file_path), metadata={"format": "pdf"})
