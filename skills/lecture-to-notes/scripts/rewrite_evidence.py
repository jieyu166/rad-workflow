from __future__ import annotations

import copy
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
    identity: str,
    path: str,
    time: float,
    ocr: str,
    asset_sha256: str | None,
) -> dict[str, Any]:
    return {
        "identity": identity,
        "path": path,
        "time": time,
        "ocr": ocr,
        "asset_sha256": asset_sha256,
    }


def _frame_source_record(
    identity: str,
    path: str,
    time: float,
    ocr: str,
    asset_sha256: str | None,
) -> dict[str, Any]:
    payload = _frame_source_payload(identity, path, time, ocr, asset_sha256)
    return {**payload, "source_sha256": _packet_digest(payload)}


def _frame_evidence_record(source: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source": "frame_ocr",
        "identity": source["identity"],
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
    for frame_index, frame in enumerate(frames, start=1):
        if not isinstance(frame, Mapping):
            raise TypeError("every frame must be an object")
        frame_time = _require_number("frame time", frame.get("time"))
        if frame_time < normalized_start or frame_time > normalized_end:
            raise ValueError("frame time must be inside the segment range")
        frame_sources.append(_frame_source_record(
            _require_text(
                "frame identity",
                frame.get("identity", f"frame-{frame_index:04d}"),
                128,
            ),
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

    paragraph_evidence = []
    for index, paragraph in enumerate(_paragraphs(normalized_transcript), start=1):
        identity = f"p-{index:04d}"
        source_payload = {"identity": identity, "text": paragraph}
        paragraph_evidence.append({
            "source": "transcript",
            "paragraph_index": index,
            **source_payload,
            "source_sha256": _packet_digest(source_payload),
        })
    existing_content = _existing_content(existing_segment)
    source_citations = [
        f"transcript:{item['identity']}" for item in paragraph_evidence
    ]
    source_citations.extend(
        f"frame:{item['identity']}" for item in frame_evidence
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


# Mechanical validation proves only coverage, integrity, trust, and reviewer
# binding. Semantic source support remains the named human reviewer's duty.
_HEX_SHA256 = re.compile(r"[0-9a-f]{64}")
_CASE_CONTEXT = re.compile(
    r"(?:本病例|本案|此病例|該病例|患者|病人|個案|此病灶|該病灶|"
    r"\d{1,3}\s*歲|男性|女性|男童|女童|左側|右側|雙側|"
    r"影像(?:顯示|可見|呈現)|診斷為|確診為|證實為|病理證實|"
    r"術後追蹤|病史|既往接受|新發|"
    r"伴有|伴隨|合併|周邊水腫|[（(][^）)]*(?:歲|男性|女性)[^）)]*[）)])"
)
_EDITORIAL_CASE_ASSERTION = re.compile(
    r"(?:本病例|本案|此病例|該病例|患者|病人|個案).{0,24}"
    r"(?:確診|診斷|為|顯示|可見|呈現|具有|合併|伴隨)"
)


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and bool(_HEX_SHA256.fullmatch(value))


def _normalized_claim(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    return re.sub(r"\s+", " ", _normalize_text(value)).strip()


def _claim_sha256(value: Any) -> str | None:
    normalized = _normalized_claim(value)
    if normalized is None:
        return None
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _normalized_reviewer(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    normalized = unicodedata.normalize("NFC", value).strip()
    if not normalized or all(unicodedata.category(char) == "Cf" for char in normalized):
        return ""
    return normalized


def _content_units(candidate: Mapping[str, Any]) -> dict[str, Any]:
    units: dict[str, Any] = {"summary_zh": candidate.get("summary_zh")}
    takeaways = candidate.get("takeaways_zh")
    if isinstance(takeaways, list):
        for index, value in enumerate(takeaways[:4]):
            units[f"takeaways_zh[{index}]"] = value
    units["title"] = candidate.get("title")
    return units


def _requires_title_evidence(title: Any) -> bool:
    if not isinstance(title, str):
        return True
    return bool(_CASE_CONTEXT.search(_normalize_text(title).strip()))


def _allowed_review_units(
    candidate: Mapping[str, Any],
    title_kind: Any,
) -> set[str]:
    allowed = {"summary_zh", *(f"takeaways_zh[{index}]" for index in range(4))}
    if title_kind == "case_claim" or _requires_title_evidence(candidate.get("title")):
        allowed.add("title")
    return allowed


def _canonical_citation(value: Any) -> dict[str, str] | None:
    if not isinstance(value, Mapping):
        return None
    identity = value.get("identity")
    citation_type = value.get("type")
    source_sha256 = value.get("source_sha256")
    if (
        not isinstance(identity, str)
        or not identity.strip()
        or citation_type not in {"transcript", "frame"}
        or not _is_sha256(source_sha256)
    ):
        return None
    citation = {
        "identity": identity,
        "type": citation_type,
        "source_sha256": source_sha256,
    }
    if citation_type == "frame":
        asset_sha256 = value.get("asset_sha256")
        if not _is_sha256(asset_sha256):
            return None
        citation["asset_sha256"] = asset_sha256
    return citation


def _citation_sort_key(citation: Mapping[str, str]) -> tuple[str, str, str, str]:
    return (
        citation["identity"],
        citation["type"],
        citation["source_sha256"],
        citation.get("asset_sha256", ""),
    )


def _canonical_citations(value: Any) -> list[dict[str, str]] | None:
    if not isinstance(value, list):
        return None
    citations: list[dict[str, str]] = []
    for item in value:
        citation = _canonical_citation(item)
        if citation is None:
            return None
        citations.append(citation)
    citations.sort(key=_citation_sort_key)
    if any(citations[index] == citations[index - 1] for index in range(1, len(citations))):
        return None
    return citations


def _records_by_unit(
    value: Any,
    allowed_units: set[str],
) -> dict[str, Mapping[str, Any]]:
    if not isinstance(value, list):
        return {}
    records: dict[str, Mapping[str, Any]] = {}
    for item in value:
        if not isinstance(item, Mapping):
            continue
        unit = item.get("content_unit")
        if (
            isinstance(unit, str)
            and unit in allowed_units
            and unit not in records
        ):
            records[unit] = item
    return records


def _canonical_citation_map(value: Any) -> list[dict[str, Any]] | None:
    if not isinstance(value, list):
        return None
    canonical: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, Mapping):
            return None
        unit = item.get("content_unit")
        citations = _canonical_citations(item.get("citations"))
        if not isinstance(unit, str) or not unit or unit in seen or citations is None:
            return None
        seen.add(unit)
        canonical.append({"content_unit": unit, "citations": citations})
    canonical.sort(key=lambda item: item["content_unit"])
    return canonical


def _candidate_payload(
    packet: Mapping[str, Any],
    candidate: Mapping[str, Any],
    review: Mapping[str, Any],
) -> dict[str, Any] | None:
    takeaways = candidate.get("takeaways_zh")
    editorial = candidate.get("editorial_notes_zh")
    title_kind = review.get("title_kind")
    canonical_map = _canonical_citation_map(review.get("citation_map"))
    if (
        not isinstance(candidate.get("title"), str)
        or not isinstance(candidate.get("summary_zh"), str)
        or not isinstance(takeaways, list)
        or len(takeaways) != 4
        or any(not isinstance(item, str) for item in takeaways)
        or not isinstance(editorial, list)
        or any(not isinstance(item, str) for item in editorial)
        or type(title_kind) is not str
        or title_kind not in {"topical", "case_claim"}
        or canonical_map is None
        or any(
            item["content_unit"] not in _allowed_review_units(
                candidate,
                title_kind,
            )
            for item in (canonical_map or [])
        )
    ):
        return None
    return {
        "lecture_id": packet.get("lecture_id"),
        "segment_index": packet.get("segment_index"),
        "start_sec": packet.get("start_sec"),
        "end_sec": packet.get("end_sec"),
        "title": candidate["title"],
        "title_kind": title_kind,
        "summary_zh": candidate["summary_zh"],
        "takeaways_zh": list(takeaways),
        "editorial_notes_zh": list(editorial),
        "citation_map": canonical_map,
    }


def _candidate_digest(
    packet: Mapping[str, Any],
    candidate: Mapping[str, Any],
    review: Mapping[str, Any],
) -> str | None:
    payload = _candidate_payload(packet, candidate, review)
    return _packet_digest(payload) if payload is not None else None


def _canonical_attestations(
    candidate: Mapping[str, Any],
    value: Any,
    title_kind: Any,
) -> list[dict[str, Any]] | None:
    if not isinstance(value, list):
        return None
    units = _content_units(candidate)
    allowed_units = _allowed_review_units(candidate, title_kind)
    canonical: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, Mapping):
            return None
        unit = item.get("content_unit")
        citations = _canonical_citations(item.get("citations"))
        if (
            not isinstance(unit, str)
            or unit not in units
            or unit not in allowed_units
            or unit in seen
            or citations is None
        ):
            return None
        seen.add(unit)
        claim_sha = _claim_sha256(units[unit])
        if claim_sha is None:
            return None
        canonical.append({
            "content_unit": unit,
            "normalized_claim_sha256": claim_sha,
            "citations": citations,
            "support_confirmed": item.get("support_confirmed"),
        })
    canonical.sort(key=lambda item: item["content_unit"])
    return canonical


def _review_payload(
    packet: Mapping[str, Any],
    candidate: Mapping[str, Any],
    review: Mapping[str, Any],
    candidate_digest: str | None,
) -> dict[str, Any] | None:
    attestations = _canonical_attestations(
        candidate,
        review.get("claim_attestations"),
        review.get("title_kind"),
    )
    if candidate_digest is None or attestations is None:
        return None
    return {
        "approved_candidate_sha256": candidate_digest,
        "evidence_packet_sha256": review.get("evidence_packet_sha256"),
        "claim_attestations": attestations,
        "topical_title_confirmed": review.get("topical_title_confirmed"),
        "reviewer_id": _normalized_reviewer(review.get("reviewer_id")),
        "source_support_confirmed": review.get("source_support_confirmed"),
        "case_facts_confirmed": review.get("case_facts_confirmed"),
        "editorial_separation_confirmed": review.get("editorial_separation_confirmed"),
        "review_schema": review.get("review_schema"),
        "review_version": review.get("review_version"),
    }


def _review_digest(
    packet: Mapping[str, Any],
    candidate: Mapping[str, Any],
    review: Mapping[str, Any],
    candidate_digest: str | None,
) -> str | None:
    payload = _review_payload(packet, candidate, review, candidate_digest)
    return _packet_digest(payload) if payload is not None else None


def finalize_review_record(
    packet: Mapping[str, Any],
    candidate: Mapping[str, Any],
    review: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(packet, Mapping) or not isinstance(candidate, Mapping) or not isinstance(review, Mapping):
        raise TypeError("packet, candidate, and review must be objects")
    finalized = copy.deepcopy(dict(review))
    units = _content_units(candidate)
    attestations = finalized.get("claim_attestations")
    if isinstance(attestations, list):
        for attestation in attestations:
            if isinstance(attestation, dict):
                unit = attestation.get("content_unit")
                if isinstance(unit, str) and unit in units:
                    attestation["normalized_claim_sha256"] = _claim_sha256(units[unit])
    candidate_digest = _candidate_digest(packet, candidate, finalized)
    finalized["approved_candidate_sha256"] = candidate_digest
    finalized["review_attestation_sha256"] = _review_digest(
        packet,
        candidate,
        finalized,
        candidate_digest,
    )
    return finalized


def _expected_paragraph_evidence(packet: Mapping[str, Any]) -> list[dict[str, Any]] | None:
    transcript = packet.get("transcript_text")
    if not isinstance(transcript, str):
        return None
    records: list[dict[str, Any]] = []
    for index, text in enumerate(_paragraphs(_normalize_text(transcript)), start=1):
        identity = f"p-{index:04d}"
        payload = {"identity": identity, "text": text}
        records.append({
            "source": "transcript",
            "paragraph_index": index,
            **payload,
            "source_sha256": _packet_digest(payload),
        })
    return records


def _expected_source_citations(packet: Mapping[str, Any]) -> list[str] | None:
    paragraphs = _expected_paragraph_evidence(packet)
    frames = _derived_frame_evidence(packet)
    existing = packet.get("existing_content")
    if paragraphs is None or frames is None or not isinstance(existing, Mapping):
        return None
    citations = [f"transcript:{item['identity']}" for item in paragraphs]
    citations.extend(f"frame:{item['identity']}" for item in frames)
    if existing.get("title"):
        citations.append("existing:title")
    if existing.get("summary_zh"):
        citations.append("existing:summary_zh")
    takeaways = existing.get("takeaways_zh")
    if isinstance(takeaways, list):
        citations.extend(
            f"existing:takeaways_zh:{index}"
            for index, item in enumerate(takeaways, start=1)
            if item
        )
    return citations


def _packet_evidence_is_derived(
    packet: Mapping[str, Any],
    trusted_frame_sources: Sequence[Mapping[str, Any]] | None = None,
) -> bool:
    del trusted_frame_sources
    expected_paragraphs = _expected_paragraph_evidence(packet)
    expected_frames = _derived_frame_evidence(packet)
    expected_citations = _expected_source_citations(packet)
    return (
        expected_paragraphs is not None
        and packet.get("paragraph_evidence") == expected_paragraphs
        and expected_frames is not None
        and packet.get("frame_evidence") == expected_frames
        and expected_citations is not None
        and packet.get("source_citations") == expected_citations
    )


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
        "identity", "path", "time", "ocr", "asset_sha256", "source_sha256"
    }
    seen: set[str] = set()
    for source in sources:
        if not isinstance(source, Mapping) or set(source) != expected_keys:
            return None
        identity = source.get("identity")
        time = source.get("time")
        ocr = source.get("ocr")
        if (
            not isinstance(identity, str)
            or not identity
            or identity in seen
            or isinstance(time, bool)
            or not isinstance(time, (int, float))
            or not math.isfinite(float(time))
            or float(time) < float(start)
            or float(time) > float(end)
            or not isinstance(ocr, str)
        ):
            return None
        seen.add(identity)
        try:
            path = _require_relative_path(source.get("path"))
            normalized_ocr = _require_text("frame ocr", ocr, _MAX_OCR_CHARS, allow_empty=True)
            asset_sha256 = _asset_sha256(source.get("asset_sha256"))
        except (TypeError, ValueError):
            return None
        payload = _frame_source_payload(identity, path, float(time), normalized_ocr, asset_sha256)
        if (
            path != source.get("path")
            or normalized_ocr != ocr
            or source.get("source_sha256") != _packet_digest(payload)
        ):
            return None
        derived.append(_frame_evidence_record(source))
    return derived


def _trusted_frame_lookup(
    trusted_frame_sources: Sequence[Mapping[str, Any]] | None,
) -> dict[str, dict[str, Any]]:
    if (
        trusted_frame_sources is None
        or isinstance(trusted_frame_sources, (str, bytes))
        or not isinstance(trusted_frame_sources, Sequence)
    ):
        return {}
    trusted: dict[str, dict[str, Any]] = {}
    expected_keys = {
        "identity",
        "path",
        "time",
        "ocr",
        "asset_sha256",
        "source_sha256",
    }
    for source in trusted_frame_sources:
        if not isinstance(source, Mapping) or set(source) != expected_keys:
            return {}
        identity = source.get("identity")
        time = source.get("time")
        ocr = source.get("ocr")
        if (
            not isinstance(identity, str)
            or not identity
            or identity in trusted
            or isinstance(time, bool)
            or not isinstance(time, (int, float))
            or not math.isfinite(float(time))
            or not isinstance(ocr, str)
        ):
            return {}
        try:
            record = _frame_source_record(
                identity,
                _require_relative_path(source.get("path")),
                float(time),
                _require_text("frame ocr", ocr, _MAX_OCR_CHARS, allow_empty=True),
                _asset_sha256(source.get("asset_sha256")),
            )
        except (TypeError, ValueError):
            return {}
        if (
            record["asset_sha256"] is None
            or source.get("source_sha256") != record["source_sha256"]
        ):
            return {}
        trusted[identity] = record
    return trusted


def _trusted_transcript_lookup(packet: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    paragraphs = _expected_paragraph_evidence(packet)
    if paragraphs is None or packet.get("paragraph_evidence") != paragraphs:
        return {}
    return {item["identity"]: item for item in paragraphs}


def _citation_is_trusted(
    citation: Mapping[str, str],
    packet: Mapping[str, Any],
    trusted_frames: Mapping[str, Mapping[str, Any]],
    transcript_packet_approved: bool,
) -> bool:
    if citation["type"] == "transcript":
        source = _trusted_transcript_lookup(packet).get(citation["identity"])
        return (
            transcript_packet_approved
            and source is not None
            and source["source_sha256"] == citation["source_sha256"]
        )
    source = trusted_frames.get(citation["identity"])
    packet_sources = packet.get("frame_sources")
    packet_source = next(
        (
            item for item in packet_sources
            if isinstance(item, Mapping) and item.get("identity") == citation["identity"]
        ),
        None,
    ) if isinstance(packet_sources, list) else None
    return (
        source is not None
        and packet_source == source
        and source["source_sha256"] == citation["source_sha256"]
        and source["asset_sha256"] == citation.get("asset_sha256")
    )


def _path_finding(code: str, message: str, path: str) -> Finding:
    return Finding("error", code, message, path=path)


def _validate_claim_contract(
    packet: Mapping[str, Any],
    candidate: Mapping[str, Any],
    review: Mapping[str, Any],
    trusted_frame_sources: Sequence[Mapping[str, Any]] | None,
    transcript_packet_approved: bool,
) -> list[Finding]:
    findings: list[Finding] = []
    units = _content_units(candidate)
    title_kind = review.get("title_kind")
    topical_title_confirmed = review.get("topical_title_confirmed")
    forced_case_claim = _requires_title_evidence(units.get("title"))
    required = ["summary_zh", *(f"takeaways_zh[{index}]" for index in range(4))]
    if type(title_kind) is not str or title_kind not in {"topical", "case_claim"}:
        findings.append(_path_finding(
            "title_kind_invalid",
            "title kind must be exactly topical or case_claim",
            "title",
        ))
    elif title_kind == "topical":
        if topical_title_confirmed is not True:
            findings.append(_path_finding(
                "topical_title_confirmation",
                "topical title confirmation must be boolean true",
                "title",
            ))
        if forced_case_claim:
            findings.append(_path_finding(
                "title_classification_conflict",
                "mechanical case red flags require case-claim review",
                "title",
            ))
            required.append("title")
    else:
        if topical_title_confirmed is not False:
            findings.append(_path_finding(
                "topical_title_confirmation",
                "case-claim title confirmation must be boolean false",
                "title",
            ))
        required.append("title")
    allowed_units = _allowed_review_units(candidate, title_kind)
    for field in ("citation_map", "claim_attestations"):
        records = review.get(field)
        if not isinstance(records, list):
            continue
        seen_units: set[str] = set()
        for record in records:
            unit = record.get("content_unit") if isinstance(record, Mapping) else None
            if (
                not isinstance(unit, str)
                or unit not in allowed_units
                or unit in seen_units
            ):
                findings.append(_path_finding(
                    "review_unit_invalid",
                    "review record contains an invalid or duplicate content unit",
                    field,
                ))
            if isinstance(unit, str):
                seen_units.add(unit)
    citation_records = _records_by_unit(
        review.get("citation_map"),
        allowed_units,
    )
    attestation_records = _records_by_unit(
        review.get("claim_attestations"),
        allowed_units,
    )
    trusted_frames = _trusted_frame_lookup(trusted_frame_sources)

    topical_title_has_evidence = any(
        isinstance(item, Mapping) and item.get("content_unit") == "title"
        for records in (
            review.get("citation_map"),
            review.get("claim_attestations"),
        )
        if isinstance(records, list)
        for item in records
    )
    if title_kind == "topical" and topical_title_has_evidence:
        findings.append(_path_finding(
            "topical_title_evidence_invalid",
            "topical titles must not carry citations or claim attestations",
            "title",
        ))

    if not isinstance(review.get("citation_map"), list):
        citation_records = {}
    if not isinstance(review.get("claim_attestations"), list):
        attestation_records = {}

    for unit in required:
        citation_record = citation_records.get(unit)
        citations = (
            _canonical_citations(citation_record.get("citations"))
            if citation_record is not None
            else None
        )
        if not citations:
            findings.append(_path_finding(
                "missing_citation",
                "reviewed content unit requires one or more trusted citations",
                unit,
            ))
        elif any(
            not _citation_is_trusted(
                item,
                packet,
                trusted_frames,
                transcript_packet_approved,
            )
            for item in citations
        ):
            findings.append(_path_finding(
                "untrusted_citation",
                "citation does not resolve to a trusted source",
                unit,
            ))

        attestation = attestation_records.get(unit)
        if attestation is None:
            findings.append(_path_finding(
                "missing_attestation",
                "reviewed content unit requires a human support attestation",
                unit,
            ))
            continue
        attested_citations = _canonical_citations(attestation.get("citations"))
        if citations is not None and attested_citations != citations:
            findings.append(_path_finding(
                "citation_binding_mismatch",
                "attestation citations do not match the candidate citation set",
                unit,
            ))
        if attestation.get("support_confirmed") is not True:
            findings.append(_path_finding(
                "attestation_invalid",
                "support confirmation must be boolean true",
                unit,
            ))
        expected_claim_hash = _claim_sha256(units.get(unit))
        if attestation.get("normalized_claim_sha256") != expected_claim_hash:
            findings.append(_path_finding(
                "claim_hash_mismatch",
                "attestation claim hash does not match the reviewed content unit",
                unit,
            ))

    for unit, record in citation_records.items():
        citations = record.get("citations")
        if isinstance(citations, list):
            for citation in citations:
                if isinstance(citation, Mapping) and citation.get("type") == "editorial":
                    findings.append(_path_finding(
                        "citation_type_invalid",
                        "editorial content is not an allowed evidence source",
                        unit,
                    ))
                    break
                if _canonical_citation(citation) is None:
                    findings.append(_path_finding(
                        "citation_type_invalid",
                        "citation type or hash fields are invalid",
                        unit,
                    ))
                    break

    editorial = candidate.get("editorial_notes_zh")
    if isinstance(editorial, list):
        for index, note in enumerate(editorial):
            if isinstance(note, str) and _EDITORIAL_CASE_ASSERTION.search(_normalize_text(note)):
                findings.append(_path_finding(
                    "editorial_case_assertion",
                    "editorial note contains an unsupported case-specific assertion",
                    f"editorial_notes_zh[{index}]",
                ))
    return findings


def _packet_identity_is_valid(packet: Mapping[str, Any]) -> bool:
    lecture_id = packet.get("lecture_id")
    segment_index = packet.get("segment_index")
    start = packet.get("start_sec")
    end = packet.get("end_sec")
    try:
        normalized_lecture_id = _require_text(
            "lecture_id",
            lecture_id,
            _MAX_LECTURE_ID_CHARS,
        )
    except (TypeError, ValueError):
        return False
    return (
        normalized_lecture_id == lecture_id
        and type(segment_index) is int
        and segment_index >= 0
        and type(start) in {int, float}
        and type(end) in {int, float}
        and math.isfinite(float(start))
        and math.isfinite(float(end))
        and float(start) >= 0
        and float(end) > float(start)
    )


def validate_review_record(
    packet: Mapping[str, Any],
    rewritten: Mapping[str, Any],
    review: Mapping[str, Any],
    *,
    trusted_frame_sources: Sequence[Mapping[str, Any]] | None = None,
    approved_run: Mapping[str, Any] | None = None,
    approved_packet_sha256: str | None = None,
) -> list[Finding]:
    findings: list[Finding] = []
    if not isinstance(packet, Mapping):
        return [_finding("packet_type", "evidence packet must be an object")]
    if not isinstance(rewritten, Mapping):
        return [_finding("rewritten_type", "rewritten content must be an object")]
    if not isinstance(review, Mapping):
        review = {}
        findings.append(_finding("review_type", "review record must be an object"))

    stored_hash = packet.get("packet_sha256")
    try:
        calculated_hash = _packet_digest(_packet_without_hash(packet))
    except (TypeError, ValueError, OverflowError):
        calculated_hash = None
    if not _is_sha256(stored_hash) or calculated_hash != stored_hash:
        findings.append(_finding("packet_hash_invalid", "evidence packet hash is invalid"))
    transcript_packet_approved = (
        _is_sha256(approved_packet_sha256)
        and approved_packet_sha256 == stored_hash
    )
    if not transcript_packet_approved:
        findings.append(_finding(
            "approved_packet_mismatch",
            "evidence packet does not match the external approval anchor",
        ))
    if not _packet_identity_is_valid(packet):
        findings.append(_finding(
            "packet_identity_invalid",
            "evidence packet chapter identity or timing is invalid",
        ))
    if not _packet_evidence_is_derived(packet):
        findings.append(_finding(
            "packet_evidence_mismatch",
            "evidence packet records do not match their source fields",
        ))
    if review.get("evidence_packet_sha256") != stored_hash:
        findings.append(_finding(
            "review_packet_mismatch",
            "review does not match the evidence packet",
        ))

    reviewer = _normalized_reviewer(review.get("reviewer_id"))
    if not reviewer or len(reviewer) > _MAX_REVIEWER_CHARS:
        findings.append(_finding("reviewer_missing", "a non-empty reviewer identity is required"))
    confirmation_fields = (
        ("source_support_confirmed", "source_support_confirmation"),
        ("case_facts_confirmed", "case_facts_confirmation"),
        ("editorial_separation_confirmed", "editorial_confirmation"),
    )
    for field, code in confirmation_fields:
        if review.get(field) is not True:
            findings.append(_finding(code, f"{field} must be boolean true"))
    if review.get("review_schema") != "lecture-content-review":
        findings.append(_finding("review_schema_invalid", "review schema is invalid"))
    version = review.get("review_version")
    if type(version) is not int or version != 1:
        findings.append(_finding("review_version_invalid", "review version must be integer 1"))

    try:
        detected_sensitive = contains_sensitive_data(_packet_sensitive_text(packet))
    except (TypeError, ValueError):
        detected_sensitive = ["scan_failure"]
    if packet.get("sensitive_findings") != detected_sensitive:
        findings.append(_finding("packet_sensitive_mismatch", "evidence packet sensitive scan is invalid"))
    if detected_sensitive:
        findings.append(_finding("sensitive_evidence", "evidence packet contains sensitive-data patterns"))

    findings.extend(_validate_claim_contract(
        packet,
        rewritten,
        review,
        trusted_frame_sources,
        transcript_packet_approved,
    ))

    candidate_digest = _candidate_digest(packet, rewritten, review)
    if candidate_digest is None or review.get("approved_candidate_sha256") != candidate_digest:
        findings.append(_finding(
            "candidate_digest_mismatch",
            "approved candidate digest does not match reviewed content",
        ))
    review_digest = _review_digest(packet, rewritten, review, candidate_digest)
    if review_digest is None or review.get("review_attestation_sha256") != review_digest:
        findings.append(_finding(
            "review_attestation_mismatch",
            "review attestation digest does not match the review record",
        ))

    if not isinstance(approved_run, Mapping):
        approved_run = {}
    for field, calculated in (
        ("approved_candidate_sha256", candidate_digest),
        ("review_attestation_sha256", review_digest),
    ):
        external = approved_run.get(field)
        if not _is_sha256(external):
            findings.append(_finding(
                "approved_run_digest_missing",
                "approved run must contain both review digests",
            ))
        elif external != calculated:
            findings.append(_finding(
                "approved_run_digest_mismatch",
                "approved run digest does not match recomputed review state",
            ))

    transcript = packet.get("transcript_text")
    findings.extend(validate_segment_content(
        rewritten,
        transcript if isinstance(transcript, str) else "",
    ))
    return findings
