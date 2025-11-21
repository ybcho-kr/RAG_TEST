"""CLI entrypoint to ingest documents into the vector store."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List

from ..ingestion import Document, load_docx, load_html, load_pdf, load_txt
from ..preprocessing.cleaning import CleaningConfig, annotate_language, clean_text
from ..preprocessing.chunker import ChunkingConfig, chunk_document
from ..vectordb.client import VectorDBClient, VectorRecord, simple_embed


LOADER_MAP = {
    ".pdf": load_pdf,
    ".docx": load_docx,
    ".txt": load_txt,
    ".html": load_html,
    ".htm": load_html,
}


def load_document(path: Path) -> Document:
    loader = LOADER_MAP.get(path.suffix.lower())
    if not loader:
        raise ValueError(f"Unsupported file extension: {path.suffix}")
    return loader(str(path))


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ingest files into a vector database")
    parser.add_argument("inputs", nargs="+", help="Paths to files to ingest")
    parser.add_argument("--chunk-size", type=int, default=500, help="Chunk size (tokens or characters)")
    parser.add_argument("--overlap", type=int, default=50, help="Overlap between chunks")
    parser.add_argument("--strategy", choices=["tokens", "characters"], default="tokens", help="Chunking strategy")
    parser.add_argument("--detect-language", action="store_true", help="Detect and annotate language")
    parser.add_argument("--vector-dim", type=int, default=8, help="Embedding dimension for the simple embedder")
    parser.add_argument("--collection", default="documents", help="Vector collection name")
    return parser


def ingest_documents(paths: Iterable[Path], cleaning_config: CleaningConfig, chunk_config: ChunkingConfig, vector_dim: int, collection: str) -> None:
    client = VectorDBClient(dimension=vector_dim, collection_name=collection)
    for path in paths:
        document = load_document(path)
        cleaned = clean_text(document.content, config=cleaning_config)
        document = Document(content=cleaned, source=document.source, metadata=document.metadata, id=document.id)
        document.metadata = annotate_language(document.metadata, cleaned, config=cleaning_config)

        chunks = chunk_document(document, config=chunk_config)
        records: List[VectorRecord] = []
        for chunk in chunks:
            vector = simple_embed(chunk.text, dimension=vector_dim)
            records.append(
                VectorRecord(
                    id=chunk.id,
                    text=chunk.text,
                    metadata=chunk.metadata,
                    vector=vector,
                )
            )
        client.upsert(records)
        print(f"Ingested {len(records)} chunks from {path}")


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()
    cleaning_config = CleaningConfig(detect_language=args.detect_language)
    chunk_config = ChunkingConfig(strategy=args.strategy, chunk_size=args.chunk_size, overlap=args.overlap)
    ingest_documents(paths=[Path(p) for p in args.inputs], cleaning_config=cleaning_config, chunk_config=chunk_config, vector_dim=args.vector_dim, collection=args.collection)


if __name__ == "__main__":
    main()
