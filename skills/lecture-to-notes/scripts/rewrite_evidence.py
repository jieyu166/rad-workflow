from __future__ import annotations

import hashlib
import json
import math
import re
import unicodedata
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any, Mapping, Sequence

from lecture_content_rules import validate_segment_content
from lecture_model import Finding

_MAX_SCAN_CHARS = 2_000_000
_MAX_LECTURE_ID_CHARS = 256
_MAX_TRANSCRIPT_CHARS = 2_000_000
_MAX_OCR_CHARS = 200_000
_MAX_PATH_CHARS = 1_024
_MAX_REVIEWER_CHARS = 128

SENSITIVE_PATTERNS = (
    (
        "medical_record_number",
        re.compile(
            r"(?:病\s*歷\s*(?:號碼|號)|m\s*r\s*n)\s*[:#-]?\s*"
            r"(?=[a-z0-9-]{0,16}\d)[a-z0-9](?:[a-z0-9-]{4,30}[a-z0-9])",
            re.IGNORECASE,
        ),
    ),
    (
        "patient_name",
        re.compile(r"(?:病\s*人\s*)?姓\s*名\s*[:：-]*\s*[㐀-鿿](?:\s*[㐀-鿿]){1,3}"),
    ),
    (
        "birth_date",
        re.compile(r"(?:生\s*日|出\s*生(?:\s*日\s*期)?)\s*[:：-]*\s*(?:(?:19|20)\d{2}|\d{2,3})\s*[/.年-]\s*\d{1,2}\s*[/.月-]\s*\d{1,2}(?:\s*日)?"),
    ),
    (
        "phone",
        re.compile(r"(?<!\d)(?:\+?886\s*[- ]?\s*9|0\s*9)\s*\d\s*\d(?:\s*[- ]?\s*\d){6}(?!\d)"),
    ),
    (
        "national_id",
        re.compile(r"(?<![a-z0-9])[a-z]\s*[12](?:\s*[- ]?\s*\d){8}(?!\d)", re.IGNORECASE),
    ),
    (
        "email",
        re.compile(r"[a-z0-9._%+-]+\s*@\s*[a-z0-9.-]+\s*\.\s*[a-z]{2,}", re.IGNORECASE),
    ),
    (
        "identifier",
        re.compile(r"(?:病\s*人\s*識\s*別\s*碼|病\s*患\s*識\s*別\s*碼|patient\s*id|identifier|accession)\s*[:：#-]*\s*[a-z0-9](?:[a-z0-9 -]{3,40}[a-z0-9])", re.IGNORECASE),
    ),
)


def _normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).replace("\r\n", "\n").replace("\r", "\n")
    return "".join(character for character in normalized if unicodedata.category(character) != "Cf")


def _security_view(text: str) -> str:
    normalized = _normalize_text(text)
    result: list[str] = []
    for character in normalized:
        category = unicodedata.category(character)
        if category == "Pd":
            result.append("-")
        elif character in {"/", "\\"}:
            result.append("-")
        elif character in {"@", ".", "+", "-"}:
            result.append(character)
        elif category.startswith("P"):
            result.append(" ")
        else:
            result.append(character)
    return "".join(result)


def contains_sensitive_data(text: str) -> list[str]:
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if len(text) > _MAX_SCAN_CHARS:
        raise ValueError("text exceeds maximum length")
    normalized = _security_view(text)
    compact = re.sub(r"\s+", "", normalized)
    return [
        name
        for name, pattern in SENSITIVE_PATTERNS
        if pattern.search(normalized)
        or (name != "medical_record_number" and pattern.search(compact))
    ]


def _require_text(name: str, value: Any, maximum: int, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    normalized = _normalize_text(value)
    if not allow_empty and not normalized.strip():
        raise ValueError(f"{name} must not be empty")
    if len(normalized) > maximum:
        raise ValueError(f"{name} exceeds maximum length")
    return normalized


def _require_number(name: str, value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a finite number")
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError(f"{name} must be a finite number")
    return parsed


def _require_index(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("segment_index must be an integer")
    if value < 0:
        raise ValueError("segment_index must be non-negative")
    return value


def _require_relative_path(value: Any) -> str:
    path = _require_text("frame path", value, _MAX_PATH_CHARS)
    posix = PurePosixPath(path.replace("\\", "/"))
    windows = PureWindowsPath(path)
    if (
        any(ord(character) < 32 for character in path)
        or posix.is_absolute()
        or windows.is_absolute()
        or windows.drive
        or ".." in posix.parts
    ):
        raise ValueError("frame path must be a safe relative path")
    return posix.as_posix()


def _existing_content(segment: Mapping[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key in ("title", "summary_zh"):
        result[key] = _require_text(key, segment.get(key, ""), _MAX_TRANSCRIPT_CHARS, allow_empty=True)
    for key in ("takeaways_zh", "editorial_notes_zh"):
        value = segment.get(key, [])
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            raise TypeError(f"{key} must be a string list")
        result[key] = [_require_text(key, item, _MAX_TRANSCRIPT_CHARS, allow_empty=True) for item in value]
    return result


def canonical_packet_bytes(packet_without_hash: Mapping[str, Any]) -> bytes:
    return json.dumps(
        packet_without_hash,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _packet_digest(packet_without_hash: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_packet_bytes(packet_without_hash)).hexdigest()


def _packet_without_hash(packet: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in packet.items() if key != "packet_sha256"}


def _paragraphs(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"\n[ \t]*\n", text) if part.strip()]


def _asset_sha256(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError("frame asset_sha256 must be a string")
    if not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ValueError("frame asset_sha256 must be lowercase SHA-256")
    return value


def _frame_source_payload(
    path: str,
    time: float,
    ocr: str,
    asset_sha256: str | None,
) -> dict[str, Any]:
    return {
        "path": path,
        "time": time,
        "ocr": ocr,
        "asset_sha256": asset_sha256,
    }


def _frame_source_record(
    path: str,
    time: float,
    ocr: str,
    asset_sha256: str | None,
) -> dict[str, Any]:
    payload = _frame_source_payload(path, time, ocr, asset_sha256)
    return {**payload, "source_sha256": _packet_digest(payload)}


def _frame_evidence_record(source: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source": "frame_ocr",
        "time": source["time"],
        "ocr": source["ocr"],
        "path": source["path"],
        "asset_sha256": source["asset_sha256"],
        "source_sha256": source["source_sha256"],
    }


def build_evidence_packet(
    lecture_id: str,
    segment_index: int,
    start: float,
    end: float,
    transcript_text: str,
    frames: Sequence[Mapping[str, Any]],
    existing_segment: Mapping[str, Any],
) -> dict[str, Any]:
    normalized_lecture_id = _require_text("lecture_id", lecture_id, _MAX_LECTURE_ID_CHARS)
    normalized_index = _require_index(segment_index)
    normalized_start = _require_number("start", start)
    normalized_end = _require_number("end", end)
    if normalized_start < 0 or normalized_end <= normalized_start:
        raise ValueError("start and end must define a positive non-negative range")
    normalized_transcript = _require_text(
        "transcript_text",
        transcript_text,
        _MAX_TRANSCRIPT_CHARS,
        allow_empty=True,
    )
    if isinstance(frames, (str, bytes)) or not isinstance(frames, Sequence):
        raise TypeError("frames must be a sequence of objects")
    if not isinstance(existing_segment, Mapping):
        raise TypeError("existing_segment must be an object")

    frame_sources: list[dict[str, Any]] = []
    for frame in frames:
        if not isinstance(frame, Mapping):
            raise TypeError("every frame must be an object")
        frame_time = _require_number("frame time", frame.get("time"))
        if frame_time < normalized_start or frame_time > normalized_end:
            raise ValueError("frame time must be inside the segment range")
        frame_sources.append(_frame_source_record(
            _require_relative_path(frame.get("path")),
            frame_time,
            _require_text(
                "frame ocr",
                frame.get("ocr", ""),
                _MAX_OCR_CHARS,
                allow_empty=True,
            ),
            _asset_sha256(frame.get("asset_sha256")),
        ))
    frame_evidence = [_frame_evidence_record(source) for source in frame_sources]

    paragraph_evidence = [
        {"source": "transcript", "paragraph_index": index, "text": paragraph}
        for index, paragraph in enumerate(_paragraphs(normalized_transcript), start=1)
    ]
    existing_content = _existing_content(existing_segment)
    source_citations = [f"transcript:p{item['paragraph_index']}" for item in paragraph_evidence]
    source_citations.extend(
        f"frame:{item['path']}@{item['time']:.6f}" for item in frame_evidence
    )
    if existing_content["title"]:
        source_citations.append("existing:title")
    if existing_content["summary_zh"]:
        source_citations.append("existing:summary_zh")
    source_citations.extend(
        f"existing:takeaways_zh:{index}"
        for index, item in enumerate(existing_content["takeaways_zh"], start=1)
        if item
    )
    sensitive_payload = "\n".join([
        normalized_transcript,
        *(item["ocr"] for item in frame_sources),
        json.dumps(existing_content, ensure_ascii=False, sort_keys=True),
    ])

    packet: dict[str, Any] = {
        "schema_version": 1,
        "lecture_id": normalized_lecture_id,
        "segment_index": normalized_index,
        "start_sec": normalized_start,
        "end_sec": normalized_end,
        "transcript_text": normalized_transcript,
        "paragraph_evidence": paragraph_evidence,
        "frame_sources": frame_sources,
        "frame_evidence": frame_evidence,
        "source_citations": source_citations,
        "existing_content": existing_content,
        "sensitive_findings": contains_sensitive_data(sensitive_payload),
    }
    packet["packet_sha256"] = _packet_digest(packet)
    return packet


def _finding(code: str, message: str) -> Finding:
    return Finding("error", code, message)


def _packet_sensitive_text(packet: Mapping[str, Any]) -> str:
    pieces: list[str] = []
    transcript = packet.get("transcript_text")
    if isinstance(transcript, str):
        pieces.append(transcript)
    frames = packet.get("frame_sources")
    if isinstance(frames, list):
        for frame in frames:
            if isinstance(frame, Mapping) and isinstance(frame.get("ocr"), str):
                pieces.append(frame["ocr"])
    existing = packet.get("existing_content")
    if isinstance(existing, Mapping):
        pieces.append(json.dumps(existing, ensure_ascii=False, sort_keys=True, default=str))
    return "\n".join(pieces)


_NEGATION = re.compile(r"(?:沒有|並無|並非|不是|不位於|無|未見|未顯示|未發現|未證實|未|否認|不見|排除)")
_CLAUSE_BOUNDARY = re.compile(
    r"[，,；;。！？!?：:\n]+|"
    r"(?:並且|並|且)(?=(?:合併|伴有|伴隨|伴|可見|呈現|顯示|未見|不見))|"
    r"(?:但|然而|惟)(?=(?:可見|呈現|顯示|未見|不見|有|無|沒有|並無))|"
    r"(?:合併|伴有|伴隨|伴)(?=[㐀-鿿])"
)
_ASSERTION_PREFIX = re.compile(
    r"^(?:另|另外|並|且|但|然而|惟)?"
    r"(?:可見|呈現|顯示|發現|見到|另見|未見|不見|未顯示|未發現|"
    r"合併|伴有|伴隨|伴|有|無|沒有|並無)"
)


def _atomic_clauses(text: str) -> list[str]:
    return [
        part.strip()
        for part in _CLAUSE_BOUNDARY.split(_normalize_text(text))
        if part.strip()
    ]


def _claim_key(text: str) -> str:
    return re.sub(r"[\s，,、；;。！？!?：:]+", "", _normalize_text(text)).strip()


def _speaker_case_claims(rewritten: Mapping[str, Any]) -> list[tuple[str, str, list[str]]]:
    claims: list[tuple[str, str, list[str]]] = []
    fields: list[tuple[str, Any]] = [("summary_zh", rewritten.get("summary_zh"))]
    takeaways = rewritten.get("takeaways_zh")
    if isinstance(takeaways, list):
        fields.extend((f"takeaways_zh[{index}]", item) for index, item in enumerate(takeaways))
    for path, value in fields:
        if not isinstance(value, str):
            continue
        for sentence in re.split(r"(?<=[。！？!?；;])|\n+", _normalize_text(value)):
            claim = sentence.strip()
            clauses = _atomic_clauses(claim)
            if clauses:
                claims.append((path, claim, clauses))
    return claims


def _derived_frame_evidence(packet: Mapping[str, Any]) -> list[dict[str, Any]] | None:
    start = packet.get("start_sec")
    end = packet.get("end_sec")
    if (
        isinstance(start, bool)
        or isinstance(end, bool)
        or not isinstance(start, (int, float))
        or not isinstance(end, (int, float))
        or not math.isfinite(float(start))
        or not math.isfinite(float(end))
        or float(start) < 0
        or float(end) <= float(start)
    ):
        return None
    sources = packet.get("frame_sources")
    if not isinstance(sources, list):
        return None

    derived: list[dict[str, Any]] = []
    expected_keys = {
        "path",
        "time",
        "ocr",
        "asset_sha256",
        "source_sha256",
    }
    for source in sources:
        if not isinstance(source, Mapping) or set(source) != expected_keys:
            return None
        time = source.get("time")
        ocr = source.get("ocr")
        if (
            isinstance(time, bool)
            or not isinstance(time, (int, float))
            or not math.isfinite(float(time))
            or float(time) < float(start)
            or float(time) > float(end)
            or not isinstance(ocr, str)
        ):
            return None
        try:
            path = _require_relative_path(source.get("path"))
            normalized_ocr = _require_text(
                "frame ocr",
                ocr,
                _MAX_OCR_CHARS,
                allow_empty=True,
            )
            asset_sha256 = _asset_sha256(source.get("asset_sha256"))
        except (TypeError, ValueError):
            return None
        if path != source.get("path") or normalized_ocr != ocr:
            return None
        payload = _frame_source_payload(
            path,
            float(time),
            normalized_ocr,
            asset_sha256,
        )
        if source.get("source_sha256") != _packet_digest(payload):
            return None
        derived.append(_frame_evidence_record(source))
    return derived


def _trusted_frame_records(
    trusted_frame_sources: Sequence[Mapping[str, Any]] | None,
) -> list[dict[str, Any]] | None:
    if (
        trusted_frame_sources is None
        or isinstance(trusted_frame_sources, (str, bytes))
        or not isinstance(trusted_frame_sources, Sequence)
    ):
        return None
    records: list[dict[str, Any]] = []
    expected_keys = {"path", "time", "ocr", "asset_sha256"}
    for source in trusted_frame_sources:
        if not isinstance(source, Mapping) or set(source) != expected_keys:
            return None
        time = source.get("time")
        ocr = source.get("ocr")
        if (
            isinstance(time, bool)
            or not isinstance(time, (int, float))
            or not math.isfinite(float(time))
            or not isinstance(ocr, str)
        ):
            return None
        try:
            path = _require_relative_path(source.get("path"))
            normalized_ocr = _require_text(
                "frame ocr",
                ocr,
                _MAX_OCR_CHARS,
                allow_empty=True,
            )
            asset_sha256 = _asset_sha256(source.get("asset_sha256"))
        except (TypeError, ValueError):
            return None
        if (
            path != source.get("path")
            or normalized_ocr != ocr
            or asset_sha256 is None
        ):
            return None
        records.append(_frame_source_record(
            path,
            float(time),
            normalized_ocr,
            asset_sha256,
        ))
    return records


def _trusted_frame_evidence(
    packet: Mapping[str, Any],
    trusted_frame_sources: Sequence[Mapping[str, Any]] | None,
) -> list[dict[str, Any]] | None:
    trusted_records = _trusted_frame_records(trusted_frame_sources)
    if trusted_records is None or packet.get("frame_sources") != trusted_records:
        return None
    trusted_evidence = [_frame_evidence_record(source) for source in trusted_records]
    if (
        _derived_frame_evidence(packet) != trusted_evidence
        or packet.get("frame_evidence") != trusted_evidence
    ):
        return None
    return trusted_evidence


def _citation_evidence(packet: Mapping[str, Any]) -> dict[str, str]:
    evidence: dict[str, str] = {}
    transcript = packet.get("transcript_text")
    if isinstance(transcript, str):
        for index, text in enumerate(_paragraphs(_normalize_text(transcript)), start=1):
            evidence[f"transcript:p{index}"] = text
    frames = _derived_frame_evidence(packet)
    if frames is not None:
        for item in frames:
            evidence[f"frame:{item['path']}@{item['time']:.6f}"] = item["ocr"]
    existing = packet.get("existing_content")
    if isinstance(existing, Mapping):
        title = existing.get("title")
        summary = existing.get("summary_zh")
        if isinstance(title, str) and title:
            evidence["existing:title"] = title
        if isinstance(summary, str) and summary:
            evidence["existing:summary_zh"] = summary
        takeaways = existing.get("takeaways_zh")
        if isinstance(takeaways, list):
            for index, item in enumerate(takeaways, start=1):
                if isinstance(item, str) and item:
                    evidence[f"existing:takeaways_zh:{index}"] = item
    return evidence


def _case_citation_evidence(
    packet: Mapping[str, Any],
    trusted_frame_sources: Sequence[Mapping[str, Any]] | None,
    approved_packet_sha256: str | None,
) -> dict[str, str]:
    evidence = {
        citation: text
        for citation, text in _citation_evidence(packet).items()
        if not citation.startswith("frame:")
    }
    if approved_packet_sha256 != packet.get("packet_sha256"):
        return evidence
    trusted_evidence = _trusted_frame_evidence(packet, trusted_frame_sources)
    if trusted_evidence is None:
        return evidence
    for item in trusted_evidence:
        evidence[f"frame:{item['path']}@{item['time']:.6f}"] = item["ocr"]
    return evidence


def _packet_evidence_is_derived(
    packet: Mapping[str, Any],
    trusted_frame_sources: Sequence[Mapping[str, Any]] | None = None,
) -> bool:
    transcript = packet.get("transcript_text")
    if not isinstance(transcript, str):
        return False
    expected_paragraphs = [
        {"source": "transcript", "paragraph_index": index, "text": text}
        for index, text in enumerate(_paragraphs(_normalize_text(transcript)), start=1)
    ]
    if packet.get("paragraph_evidence") != expected_paragraphs:
        return False

    expected_frames = _derived_frame_evidence(packet)
    if expected_frames is None or packet.get("frame_evidence") != expected_frames:
        return False
    if (
        trusted_frame_sources is not None
        and _trusted_frame_evidence(packet, trusted_frame_sources) is None
    ):
        return False

    citations = packet.get("source_citations")
    return isinstance(citations, list) and citations == list(_citation_evidence(packet))


def _is_negated(text: str) -> bool:
    return bool(_NEGATION.search(text))


def _assertion_content(text: str) -> str:
    normalized = _claim_key(text)
    previous = None
    while previous != normalized:
        previous = normalized
        normalized = _ASSERTION_PREFIX.sub("", normalized)
    return normalized


def _semantic_match(left: str, right: str) -> bool:
    left_content = _assertion_content(left)
    right_content = _assertion_content(right)
    return bool(left_content) and left_content == right_content


def _claim_has_support(claim_clause: str, citations: Sequence[Any], evidence: Mapping[str, str]) -> bool:
    if isinstance(citations, (str, bytes)) or not isinstance(citations, Sequence):
        return False
    evidence_clauses: list[str] = []
    for citation in citations:
        if not isinstance(citation, str) or citation not in evidence:
            return False
        evidence_clauses.extend(_atomic_clauses(evidence[citation]))
    matches = [clause for clause in evidence_clauses if _semantic_match(claim_clause, clause)]
    if not matches:
        return False
    claim_negated = _is_negated(claim_clause)
    if any(_is_negated(clause) != claim_negated for clause in matches):
        return False
    return any(_is_negated(clause) == claim_negated for clause in matches)


def _existing_citation_for_path(path: str) -> str | None:
    if path == "summary_zh":
        return "existing:summary_zh"
    match = re.fullmatch(r"takeaways_zh\[(\d+)]", path)
    if match:
        return f"existing:takeaways_zh:{int(match.group(1)) + 1}"
    return None


def _is_unchanged_existing_clause(
    path: str,
    clause: str,
    evidence: Mapping[str, str],
) -> bool:
    citation = _existing_citation_for_path(path)
    if citation is None or citation not in evidence:
        return False
    clause_key = _claim_key(clause)
    return clause_key in {
        _claim_key(existing_clause)
        for existing_clause in _atomic_clauses(evidence[citation])
    }


def _validate_case_claims(
    packet: Mapping[str, Any],
    rewritten: Mapping[str, Any],
    review: Mapping[str, Any],
    trusted_frame_sources: Sequence[Mapping[str, Any]] | None,
    approved_packet_sha256: str | None,
) -> list[Finding]:
    findings: list[Finding] = []
    records = review.get("case_claim_citations")
    records = records if isinstance(records, list) else []
    evidence = _case_citation_evidence(
        packet,
        trusted_frame_sources,
        approved_packet_sha256,
    )
    for path, claim, clauses in _speaker_case_claims(rewritten):
        sentence_key = _claim_key(claim)
        unsupported = False
        for clause in clauses:
            if _is_unchanged_existing_clause(path, clause, evidence):
                continue
            clause_key = _claim_key(clause)
            clause_supported = False
            for record in records:
                if not isinstance(record, Mapping) or record.get("path") != path:
                    continue
                record_claim = record.get("claim")
                if not isinstance(record_claim, str) or _claim_key(record_claim) not in {
                    sentence_key,
                    clause_key,
                }:
                    continue
                if _claim_has_support(clause, record.get("citations"), evidence):
                    clause_supported = True
                    break
            if not clause_supported:
                unsupported = True
                break
        if unsupported:
            findings.append(Finding(
                "error",
                "unsupported_case_claim",
                "case-specific speaker clause lacks packet-bound evidence support",
                path=path,
            ))
    return findings


def validate_review_record(
    packet: Mapping[str, Any],
    rewritten: Mapping[str, Any],
    review: Mapping[str, Any],
    *,
    trusted_frame_sources: Sequence[Mapping[str, Any]] | None = None,
    approved_packet_sha256: str | None = None,
) -> list[Finding]:
    findings: list[Finding] = []
    if not isinstance(packet, Mapping):
        return [_finding("packet_type", "evidence packet must be an object")]
    if not isinstance(rewritten, Mapping):
        findings.append(_finding("rewritten_type", "rewritten content must be an object"))
    if not isinstance(review, Mapping):
        findings.append(_finding("review_type", "review record must be an object"))
        review = {}

    stored_hash = packet.get("packet_sha256")
    try:
        calculated_hash = _packet_digest(_packet_without_hash(packet))
    except (TypeError, ValueError, OverflowError):
        calculated_hash = None
    if not isinstance(stored_hash, str) or calculated_hash is None or stored_hash != calculated_hash:
        findings.append(_finding("packet_hash_invalid", "evidence packet hash is invalid"))
    if not _packet_evidence_is_derived(packet, trusted_frame_sources):
        findings.append(_finding(
            "packet_evidence_mismatch",
            "evidence packet records do not match their source fields",
        ))
    if review.get("packet_sha256") != stored_hash:
        findings.append(_finding("review_packet_mismatch", "review does not match the evidence packet"))
    if (
        approved_packet_sha256 is not None
        and approved_packet_sha256 != stored_hash
    ):
        findings.append(_finding(
            "approved_packet_mismatch",
            "evidence packet does not match the externally approved digest",
        ))

    reviewer = review.get("reviewer")
    normalized_reviewer = _normalize_text(reviewer).strip() if isinstance(reviewer, str) else ""
    if (
        not isinstance(reviewer, str)
        or not normalized_reviewer
        or len(normalized_reviewer) > _MAX_REVIEWER_CHARS
    ):
        findings.append(_finding("reviewer_missing", "a non-empty reviewer identity is required"))
    if review.get("source_faithful") is not True:
        findings.append(_finding("source_faithful_missing", "review must confirm source faithfulness"))
    if review.get("case_details_verified") is not True:
        findings.append(_finding("case_detail_check_missing", "review must confirm case details are evidence-bound"))
    if review.get("editorial_separated") is not True:
        findings.append(_finding("editorial_check_missing", "review must confirm editorial separation"))

    try:
        detected_sensitive = contains_sensitive_data(_packet_sensitive_text(packet))
    except (TypeError, ValueError):
        detected_sensitive = ["scan_failure"]
    recorded_sensitive = packet.get("sensitive_findings")
    if not isinstance(recorded_sensitive, list) or recorded_sensitive != detected_sensitive:
        findings.append(_finding("packet_sensitive_mismatch", "evidence packet sensitive scan is invalid"))
    if detected_sensitive:
        findings.append(_finding("sensitive_evidence", "evidence packet contains sensitive-data patterns"))

    if isinstance(rewritten, Mapping):
        findings.extend(_validate_case_claims(
            packet,
            rewritten,
            review,
            trusted_frame_sources,
            approved_packet_sha256,
        ))
        transcript = packet.get("transcript_text", "")
        if not isinstance(transcript, str):
            transcript = ""
        findings.extend(validate_segment_content(rewritten, transcript))
    return findings
