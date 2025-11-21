"""텍스트 정제를 위한 유틸리티 함수."""
from __future__ import annotations

import re
import unicodedata
from typing import Callable, Optional


def normalize_whitespace(text: str) -> str:
    """중복 공백과 제어 문자를 정돈한다."""

    collapsed = re.sub(r"[\t\r\f\v]+", " ", text)
    collapsed = re.sub(r" +", " ", collapsed)
    collapsed = re.sub(r"\n{3,}", "\n\n", collapsed)
    return collapsed.strip()


def clean_text(text: str, extra_rules: Optional[Callable[[str], str]] = None) -> str:
    """기본 정규화(유니코드, 공백)를 수행하고 추가 규칙을 적용한다."""

    normalized = unicodedata.normalize("NFKC", text)
    normalized = normalized.replace("\x00", "")
    normalized = normalize_whitespace(normalized)
    if extra_rules:
        normalized = extra_rules(normalized)
    return normalized
