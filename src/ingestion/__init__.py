"""Ingestion package exposing format-specific loaders and the :class:`Document` model."""
from .document import Document
from .pdf_loader import load_pdf
from .docx_loader import load_docx
from .txt_loader import load_txt
from .html_loader import load_html

__all__ = [
    "Document",
    "load_pdf",
    "load_docx",
    "load_txt",
    "load_html",
]
