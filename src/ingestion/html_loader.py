"""HTML ingestion utilities using BeautifulSoup."""
from pathlib import Path

from .document import Document

try:
    from bs4 import BeautifulSoup
except Exception:  # pragma: no cover - optional dependency
    BeautifulSoup = None  # type: ignore


def load_html(path: str, parser: str = "html.parser") -> Document:
    """Load an HTML file into a :class:`Document`, stripping tags to text."""
    if BeautifulSoup is None:
        raise ImportError("beautifulsoup4 is required to load HTML files")

    file_path = Path(path)
    html = file_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, parser)
    content = soup.get_text(separator="\n")
    return Document(content=content, source=str(file_path), metadata={"format": "html", "parser": parser})
