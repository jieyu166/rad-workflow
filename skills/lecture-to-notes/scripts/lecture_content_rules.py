from __future__ import annotations

import re
import unicodedata
from functools import lru_cache
from typing import Any, Mapping

from lecture_model import Finding

_MIN_SUMMARY_HAN = 250
_MAX_SUMMARY_HAN = 600
_MAX_TITLE_CHARS = 120
_MAX_TAKEAWAY_HAN = 80

_GENERIC_TITLE = re.compile(
    r"^(?:focused|overview|summary|chapter\s*\d+|重點|介紹|病例|第[一二三四五六七八九十百0-9]+章)$",
    re.IGNORECASE,
)
_UNFINISHED_LATIN = re.compile(
    r"(?:T[\W_]*O[\W_]*D[\W_]*O|T[\W_]*B[\W_]*D|F[\W_]*I[\W_]*X[\W_]*M[\W_]*E|"
    r"P[\W_]*L[\W_]*A[\W_]*C[\W_]*E[\W_]*H[\W_]*O[\W_]*L[\W_]*D[\W_]*E[\W_]*R)",
    re.IGNORECASE,
)
_UNFINISHED_ZH = (
    "請補充",
    "待確認",
    "此處填入",
    "內容待補",
    "尚未完成",
    "核心重點一",
)
_TAIWAN_CONTEXT_TERMS = ("干擾",)


def _normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFC", value).replace("\r\n", "\n").replace("\r", "\n")
    return "".join(
        character
        for character in normalized
        if unicodedata.category(character) != "Cf"
    )


def _han_count(text: str) -> int:
    return sum(
        "㐀" <= character <= "䶿"
        or "一" <= character <= "鿿"
        or "豈" <= character <= "﫿"
        for character in text
    )


def _comparison_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text).casefold()
    return "".join(character for character in normalized if character.isalnum())


@lru_cache(maxsize=1)
def _load_opencc_converter():
    from opencc import OpenCC

    failures: list[BaseException] = []
    for configuration in ("s2tw.json", "s2tw"):
        try:
            return OpenCC(configuration)
        except (OSError, RuntimeError, ValueError) as exc:
            failures.append(exc)
    raise RuntimeError("OpenCC Simplified-to-Traditional converter is unavailable") from failures[-1]


def _simplified_finding(text: str) -> Finding | None:
    try:
        converter = _load_opencc_converter()
    except (ImportError, OSError, RuntimeError, ValueError):
        return Finding(
            "error",
            "opencc_unavailable",
            "OpenCC Simplified-to-Traditional validation is unavailable",
        )

    try:
        normalized = _normalize_text(text)
        protected = normalized
        for index, term in enumerate(_TAIWAN_CONTEXT_TERMS):
            protected = protected.replace(term, f"{index}")
        if converter.convert(protected) != protected:
            return Finding(
                "error",
                "simplified_chinese",
                "content contains Simplified Chinese-only characters",
            )
    except Exception:
        return Finding(
            "error",
            "opencc_failure",
            "OpenCC Simplified-to-Traditional validation failed",
        )
    return None


def _append(findings: list[Finding], code: str, message: str) -> None:
    findings.append(Finding("error", code, message))


def validate_segment_content(
    segment: Mapping[str, Any],
    transcript_text: str,
) -> list[Finding]:
    findings: list[Finding] = []
    if not isinstance(segment, Mapping):
        return [Finding("error", "segment_type", "segment must be an object")]
    if not isinstance(transcript_text, str):
        _append(findings, "transcript_type", "transcript_text must be a string")
        transcript_text = ""

    title_value = segment.get("title")
    title = _normalize_text(title_value).strip() if isinstance(title_value, str) else ""
    compact_title = re.sub(r"\s+", " ", title)
    if (
        not isinstance(title_value, str)
        or not title
        or len(title) > _MAX_TITLE_CHARS
        or "\n" in title
        or title.isdigit()
        or _GENERIC_TITLE.fullmatch(compact_title)
    ):
        _append(
            findings,
            "title_focus",
            "title must identify one diagnosis, finding, anatomy, or reading task",
        )

    summary_value = segment.get("summary_zh")
    if not isinstance(summary_value, str):
        _append(findings, "summary_type", "summary_zh must be a string")
        summary = ""
    else:
        summary = _normalize_text(summary_value).strip()
        summary_han = _han_count(summary)
        if not _MIN_SUMMARY_HAN <= summary_han <= _MAX_SUMMARY_HAN:
            _append(
                findings,
                "summary_length",
                "summary_zh must contain 250 to 600 Han characters",
            )
        paragraphs = [part for part in re.split(r"\n[^\S\n]*\n", summary) if part.strip()]
        if not 1 <= len(paragraphs) <= 2:
            _append(
                findings,
                "summary_paragraphs",
                "summary_zh must contain one or two paragraphs",
            )

    takeaways_value = segment.get("takeaways_zh")
    takeaways: list[str] = []
    if not isinstance(takeaways_value, list):
        _append(findings, "takeaway_count", "takeaways_zh must contain exactly four items")
    else:
        if len(takeaways_value) != 4:
            _append(findings, "takeaway_count", "takeaways_zh must contain exactly four items")
        for value in takeaways_value:
            if not isinstance(value, str):
                _append(findings, "takeaway_type", "every takeaway must be a string")
                continue
            item = _normalize_text(value).strip()
            takeaways.append(item)
            if not item:
                _append(findings, "takeaway_empty", "takeaways must not be empty")
            elif _han_count(item) > _MAX_TAKEAWAY_HAN:
                _append(findings, "takeaway_length", "takeaways must be concise")
        comparable = [_comparison_text(item) for item in takeaways if item]
        if len(comparable) != len(set(comparable)):
            _append(findings, "takeaway_duplicate", "takeaways must be distinct")

    editorial_value = segment.get("editorial_notes_zh")
    editorial: list[str] = []
    if not isinstance(editorial_value, list) or any(
        not isinstance(value, str) or not value.strip() for value in editorial_value
    ):
        _append(
            findings,
            "editorial_type",
            "editorial_notes_zh must be a list of non-empty strings",
        )
    elif isinstance(editorial_value, list):
        editorial = [_normalize_text(value).strip() for value in editorial_value]

    combined = "\n".join([title, summary, *takeaways, *editorial])
    if _UNFINISHED_LATIN.search(unicodedata.normalize("NFKC", combined)) or any(
        phrase in combined for phrase in _UNFINISHED_ZH
    ):
        _append(
            findings,
            "unfinished_marker",
            "content contains an unfinished or template marker",
        )

    language_finding = _simplified_finding(combined)
    if language_finding is not None:
        findings.append(language_finding)

    transcript_lines = [
        _comparison_text(line)
        for line in _normalize_text(transcript_text).splitlines()
        if _han_count(line) >= 20
    ]
    normalized_summary = _comparison_text(summary)
    if transcript_lines:
        copied_lines = sum(1 for line in transcript_lines if line and line in normalized_summary)
        if copied_lines / len(transcript_lines) > 0.5:
            _append(
                findings,
                "transcript_copy",
                "summary_zh copies excessive transcript text verbatim",
            )
        normalized_transcript = _comparison_text(transcript_text)
        if any(
            _han_count(item) >= 20 and _comparison_text(item) in normalized_transcript
            for item in takeaways
        ):
            _append(
                findings,
                "takeaway_transcript_copy",
                "a takeaway copies a long transcript passage verbatim",
            )

    return findings
