"""문서 전처리와 임베딩 저장을 CLI로 수행하는 스크립트."""
from __future__ import annotations

import argparse

from src.ingestion.loaders import load_documents
from src.preprocessing.cleaning import clean_text
from src.preprocessing.chunker import TextChunker
from src.vectordb.client import VectorClient


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="문서를 정제·청크화 후 벡터 DB에 저장합니다.")
    parser.add_argument("inputs", nargs="+", help="처리할 파일 경로 목록")
    parser.add_argument("--max-length", type=int, default=500, help="청크 최대 길이(문자 또는 토큰 기준)")
    parser.add_argument("--overlap", type=int, default=50, help="청크 간 오버랩 길이")
    parser.add_argument("--by-tokens", action="store_true", help="토큰 단위로 청크를 분할")
    parser.add_argument("--dry-run", action="store_true", help="임베딩 없이 청크 결과만 확인")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    print("[1/4] 파일 로드 중...")
    documents = load_documents(args.inputs)
    print(f"총 {len(documents)}개 문서 로드 완료")

    print("[2/4] 텍스트 정제 중...")
    cleaned_documents = []
    for doc in documents:
        cleaned_content = clean_text(doc.content)
        cleaned_documents.append(doc.with_metadata(cleaned=True))
        cleaned_documents[-1].content = cleaned_content
    print("정제 완료")

    print("[3/4] 청크 생성 중...")
    chunker = TextChunker(max_length=args.max_length, overlap=args.overlap, by_tokens=args.by_tokens)
    chunks = chunker.chunk_documents(cleaned_documents)
    print(f"생성된 청크 수: {len(chunks)}")

    if args.dry_run:
        print("드라이런 모드: 임베딩을 건너뜁니다.")
        return

    print("[4/4] 벡터 저장소에 업서트 중...")
    client = VectorClient()
    ids = client.upsert(chunks)
    print(f"저장 완료: {len(ids)}개 레코드")


if __name__ == "__main__":
    main()
