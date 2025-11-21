# RAG Test Project

## Overview
This repository provides a lightweight reference implementation for preprocessing unstructured documents, chunking content into retrieval-friendly pieces, and storing the resulting embeddings in a vector database. The ingestion pipeline performs the following high-level steps:

1. **Document discovery** – Locate raw files from configured sources (local folders, cloud buckets, or URLs) and normalize them into a consistent text format.
2. **Preprocessing** – Clean content (e.g., strip markup, normalize whitespace, and remove unsupported binary content) to improve downstream chunk quality.
3. **Chunking** – Split normalized text into overlapping segments to preserve context while respecting vector limits. Typical defaults might use a chunk size of 500–1,000 tokens with an overlap of 50–200 tokens.
4. **Embedding generation** – Pass each chunk through the configured embedding model to create dense vector representations.
5. **Vector storage** – Upsert embeddings, metadata, and document references into the configured vector database for efficient similarity search.

## Prerequisites
- Python 3.10+ with `pip` available
- Access to an embeddings provider (e.g., OpenAI, Azure OpenAI, or a local model)
- Access credentials for your vector database (e.g., local file-backed store or a managed service)

## Installation
Install dependencies in an isolated environment to avoid version conflicts.

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Ingestion CLI Usage
Use the ingestion command to preprocess, chunk, embed, and store documents. Replace placeholders with your values.

```bash
python -m cli.ingest \
  --input-path ./data/raw \
  --output-index my-collection \
  --chunk-size 800 \
  --chunk-overlap 120 \
  --embedding-model gpt-embedding-v1 \
  --vector-db qdrant \
  --vector-db-url http://localhost:6333 \
  --vector-db-api-key <QDRANT_API_KEY>
```

Key parameters:
- `--chunk-size` / `--chunk-overlap`: Control chunk granularity to balance context retention and vector cost.
- `--embedding-model`: Name of the embedding model to call; ensure credentials are configured via environment variables.
- `--vector-db`: Backend to use (e.g., `qdrant`, `pinecone`, or `chroma`).
- `--vector-db-url` and `--vector-db-api-key`: Connection details for the vector store service.
- `--dry-run`: Optionally run the pipeline without writing to the database to verify preprocessing and chunk statistics.

## Testing Strategy
- **Unit tests** cover preprocessing utilities, chunking logic, and vector-store adapters.
- **Integration tests** validate end-to-end ingestion by running the CLI against a local vector database instance.
- **Static checks** (linting/formatting) ensure code quality before merging.

Run available checks with:

```bash
pytest
```

## Directory Structure
- `cli/` – Command-line entry points for ingestion and related utilities.
- `data/` – Example raw input files (gitignored in production).
- `ingestion/` – Preprocessing, chunking, and embedding orchestration code.
- `vector_store/` – Adapters for supported vector databases and related configuration helpers.
- `tests/` – Unit and integration tests for the ingestion pipeline.
- `requirements.txt` – Python dependencies for local development and CI.

## Contributor Notes
- Prefer small, reviewable pull requests that include relevant tests.
- Use descriptive commit messages and keep documentation updated alongside code changes.
