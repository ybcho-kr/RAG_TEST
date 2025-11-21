# RAG 전처리 및 벡터 저장 파이프라인

문서 수집부터 청크화, 임베딩 저장까지 한 번에 실행할 수 있는 최소 구성 예제입니다. PDF, DOCX, TXT, HTML을 정규화된 `Document` 형태로 변환하고, 간단한 정제·청크 로직을 거쳐 벡터 저장소에 업서트합니다.

## 주요 기능
- **포맷별 로더**: PDF(pypdf), DOCX(python-docx), HTML(BeautifulSoup), TXT를 공통 `Document` 모델로 변환.
- **텍스트 정제**: 유니코드 정규화, 공백/제어문자 정돈.
- **청크 생성**: 문자 길이 또는 공백 기반 토큰 길이에 따른 슬라이딩 윈도우 청크화 및 오버랩.
- **벡터 저장소**: `sentence-transformers` 기반 임베딩과 코사인 유사도 검색을 제공하는 인메모리 클라이언트.
- **CLI 파이프라인**: 입력 파일을 받아 정제 → 청크 → 임베딩 → 업서트 순으로 처리.

## 설치
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 사용 방법
```bash
python -m src.pipeline.ingest data/sample.pdf data/manual.docx \
  --max-length 600 --overlap 80 --by-tokens
```

- `--by-tokens`: 공백 단위 토큰 길이로 청크를 나눌 때 활성화합니다. 기본값은 문자 길이입니다.
- `--dry-run`: 임베딩/업서트 없이 청크 개수만 확인할 때 사용합니다.

## 모듈 구성
- `src/ingestion/loaders.py`: 파일 포맷별 로더와 진입점 `load_documents`.
- `src/preprocessing/cleaning.py`: 공통 텍스트 정제 함수.
- `src/preprocessing/chunker.py`: 청크 분할기와 결과 모델.
- `src/vectordb/client.py`: 인메모리 벡터 검색 클라이언트.
- `src/pipeline/ingest.py`: CLI 파이프라인.
- `src/models/document.py`: 정규화된 문서 데이터 클래스.

## 테스트
- 현재 자동 테스트 스위트는 포함되어 있지 않습니다. 필요에 따라 입력 파일을 준비한 뒤 `--dry-run` 옵션으로 로딩/정제/청크 단계를 먼저 검증하세요.
