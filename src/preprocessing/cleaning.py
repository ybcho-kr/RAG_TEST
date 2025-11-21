"""Language-agnostic text cleanup helpers."""
from dataclasses import dataclass
import re
from typing import Callable, Optional

try:  # pragma: no cover - optional dependency
    from langdetect import detect  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    detect = None


@dataclass
class CleaningConfig:
    normalize_whitespace: bool = True
    strip_control_characters: bool = True
    detect_language: bool = False


def fix_encoding(text: str) -> str:
    """Best-effort encoding fix using unicode replacements."""
    return text.encode("utf-8", errors="replace").decode("utf-8")


def remove_control_characters(text: str) -> str:
    control_chars = ''.join(map(chr, list(range(0, 32)) + [127]))
    control_char_re = re.compile(f"[{re.escape(control_chars)}]")
    return control_char_re.sub(" ", text)


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def detect_language_code(text: str) -> Optional[str]:
    if not detect:
        return None
    try:
        return detect(text)
    except Exception:
        return None


def clean_text(text: str, config: Optional[CleaningConfig] = None) -> str:
    config = config or CleaningConfig()
    cleaned = fix_encoding(text)
    if config.strip_control_characters:
        cleaned = remove_control_characters(cleaned)
    if config.normalize_whitespace:
        cleaned = normalize_whitespace(cleaned)
    return cleaned


def annotate_language(metadata: dict, text: str, config: Optional[CleaningConfig] = None) -> dict:
    config = config or CleaningConfig()
    if config.detect_language:
        lang = detect_language_code(text)
        if lang:
            metadata = {**metadata, "language": lang}
    return metadata
