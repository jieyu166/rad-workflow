from __future__ import annotations

import json
import math
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Mapping


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    segment_index: int | None = None
    path: str | None = None


def _frame_time(path: str) -> float | None:
    stem = Path(path).stem
    marker = stem.rsplit("_", 1)[-1]
    try:
        return float(marker.replace("-", "."))
    except ValueError:
        return None


def segment_start(segment: Mapping[str, Any]) -> float:
    if "start_sec" in segment:
        return float(segment["start_sec"])
    return float(segment["start"])


def segment_end(segment: Mapping[str, Any]) -> float:
    if "end_sec" in segment:
        return float(segment["end_sec"])
    return float(segment["end"])


def normalize_lecture(data: Mapping[str, Any]) -> dict[str, Any]:
    result = json.loads(json.dumps(data, ensure_ascii=False))
    top_level_ocr = result.pop("frame_ocr", {}) or {}
    if not isinstance(top_level_ocr, Mapping):
        top_level_ocr = {}

    segments = result.get("segments", [])
    if not isinstance(segments, list):
        return result

    for segment in segments:
        if not isinstance(segment, dict):
            continue
        segment["start_sec"] = segment_start(segment)
        segment["end_sec"] = segment_end(segment)
        segment.pop("start", None)
        segment.pop("end", None)

        if "takeaways_zh" not in segment:
            bullets = segment.pop("bullets_zh", [])
            segment["takeaways_zh"] = list(bullets) if isinstance(bullets, list) else bullets
        else:
            segment.pop("bullets_zh", None)
        segment.setdefault("editorial_notes_zh", [])

        segment_ocr: dict[str, Any] = {}
        legacy_segment_ocr = segment.pop("frame_ocr", []) or []
        if isinstance(legacy_segment_ocr, list):
            for item in legacy_segment_ocr:
                if not isinstance(item, Mapping):
                    continue
                frame_path = item.get("frame")
                if isinstance(frame_path, str):
                    segment_ocr[frame_path] = item.get("text", "")

        frames = segment.get("frames", [])
        if not isinstance(frames, list):
            segment["frames"] = frames
            continue

        normalized_frames = []
        for frame in frames:
            if isinstance(frame, str):
                normalized_path = frame.replace("\\", "/")
                normalized_frames.append({
                    "time": _frame_time(normalized_path),
                    "ocr": segment_ocr.get(frame, top_level_ocr.get(frame, "")),
                    "path": normalized_path,
                })
            elif isinstance(frame, Mapping):
                raw_path = frame.get("path", "")
                normalized_path = raw_path.replace("\\", "/") if isinstance(raw_path, str) else raw_path
                normalized_frame = {
                    "time": frame.get("time"),
                    "path": normalized_path,
                }
                if "ocr" in frame:
                    normalized_frame["ocr"] = frame["ocr"]
                normalized_frames.append(normalized_frame)
            else:
                normalized_frames.append(frame)
        segment["frames"] = normalized_frames

    return result


def time_signature(data: Mapping[str, Any]) -> tuple[tuple[float, float], ...]:
    segments = data.get("segments", [])
    if not isinstance(segments, list):
        raise ValueError("segments must be a list")
    return tuple((segment_start(segment), segment_end(segment)) for segment in segments)


def _segment_label(segment: Any, fallback_index: int) -> Any:
    if isinstance(segment, Mapping) and "index" in segment:
        return segment["index"]
    return fallback_index


def _same_json_scalar(old_value: Any, new_value: Any) -> bool:
    return type(old_value) is type(new_value) and old_value == new_value


def _segment_time_value(segment: Mapping[str, Any], canonical: str, alias: str) -> Any:
    if canonical in segment:
        return segment[canonical]
    return segment[alias]


def assert_times_unchanged(before: Mapping[str, Any], after: Mapping[str, Any]) -> None:
    old_segments = before.get("segments", [])
    new_segments = after.get("segments", [])
    if not isinstance(old_segments, list) or not isinstance(new_segments, list):
        raise ValueError("segments must be lists")
    if len(old_segments) != len(new_segments):
        raise ValueError(f"segment count changed: {len(old_segments)} != {len(new_segments)}")

    for position, (old_segment, new_segment) in enumerate(zip(old_segments, new_segments)):
        label = _segment_label(old_segment, position)
        if not isinstance(old_segment, Mapping) or not isinstance(new_segment, Mapping):
            raise ValueError(f"segment {label} must remain an object")

        old_has_index = "index" in old_segment
        new_has_index = "index" in new_segment
        old_index = old_segment.get("index")
        new_index = new_segment.get("index")
        if (
            old_has_index != new_has_index
            or (old_has_index and not _same_json_scalar(old_index, new_index))
        ):
            raise ValueError(f"segment {label} index changed: {old_index!r} != {new_index!r}")

        try:
            old_start = _segment_time_value(old_segment, "start_sec", "start")
            new_start = _segment_time_value(new_segment, "start_sec", "start")
            old_end = _segment_time_value(old_segment, "end_sec", "end")
            new_end = _segment_time_value(new_segment, "end_sec", "end")
        except KeyError as exc:
            raise ValueError(f"segment {label} has invalid time data") from exc

        if not _same_json_scalar(old_start, new_start):
            raise ValueError(
                f"segment {label} time changed: start changed from {old_start!r} to {new_start!r}"
            )
        if not _same_json_scalar(old_end, new_end):
            raise ValueError(
                f"segment {label} time changed: end changed from {old_end!r} to {new_end!r}"
            )


def _safe_relative_frame_path(value: Any) -> PurePosixPath | None:
    if not isinstance(value, str):
        return None
    normalized = value.replace("\\", "/")
    posix = PurePosixPath(normalized)
    windows = PureWindowsPath(value)
    if (
        not normalized
        or any(ord(character) < 32 for character in normalized)
        or posix.is_absolute()
        or windows.is_absolute()
        or bool(windows.drive)
        or ".." in posix.parts
    ):
        return None
    return posix


def _finite_number(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return parsed if math.isfinite(parsed) else None


def _path_within_base(base_dir: Path, relative_path: PurePosixPath) -> Path | None:
    base = base_dir.resolve()
    candidate = (base / Path(*relative_path.parts)).resolve(strict=False)
    try:
        candidate.relative_to(base)
    except ValueError:
        return None
    return candidate


def validate_lecture_schema(
    data: Mapping[str, Any],
    base_dir: Path,
    frame_tolerance_seconds: float = 0.25,
) -> list[Finding]:
    findings: list[Finding] = []
    base_dir = Path(base_dir)
    tolerance = _finite_number(frame_tolerance_seconds)
    if tolerance is None or tolerance < 0:
        raise ValueError("frame_tolerance_seconds must be finite and non-negative")

    segments = data.get("segments")
    if not isinstance(segments, list) or not segments:
        return [Finding("error", "segments_missing", "segments must be a non-empty list")]

    for position, segment in enumerate(segments):
        if not isinstance(segment, Mapping):
            findings.append(Finding("error", "segment_type", "segment must be an object", position))
            continue

        start = _finite_number(segment.get("start_sec", segment.get("start")))
        end = _finite_number(segment.get("end_sec", segment.get("end")))
        valid_range = start is not None and end is not None and start >= 0.0 and end > start
        if not valid_range:
            findings.append(Finding("error", "time_range", "invalid segment time range", position))

        if not isinstance(segment.get("title"), str):
            findings.append(Finding("error", "title_type", "title must be a string", position))
        if not isinstance(segment.get("summary_zh"), str):
            findings.append(Finding("error", "summary_type", "summary_zh must be a string", position))

        takeaways = segment.get("takeaways_zh")
        if not isinstance(takeaways, list) or len(takeaways) != 4:
            findings.append(Finding(
                "error",
                "takeaway_count",
                "takeaways_zh must contain exactly four items",
                position,
            ))
        elif not all(isinstance(item, str) for item in takeaways):
            findings.append(Finding("error", "takeaway_type", "takeaways_zh must be a string list", position))

        editorial = segment.get("editorial_notes_zh")
        if not isinstance(editorial, list) or not all(isinstance(item, str) for item in editorial):
            findings.append(Finding(
                "error",
                "editorial_type",
                "editorial_notes_zh must be a string list",
                position,
            ))

        frames = segment.get("frames")
        if not isinstance(frames, list) or not 1 <= len(frames) <= 4:
            findings.append(Finding("error", "frame_count", "frames must contain one to four items", position))
            if not isinstance(frames, list):
                continue

        for frame in frames:
            if not isinstance(frame, Mapping):
                findings.append(Finding("error", "frame_type", "frame must be an object", position))
                continue

            raw_path = frame.get("path", "")
            finding_path = raw_path if isinstance(raw_path, str) else str(raw_path)
            pure = _safe_relative_frame_path(raw_path)
            candidate = _path_within_base(base_dir, pure) if pure is not None else None
            if pure is None or candidate is None:
                findings.append(Finding(
                    "error",
                    "frame_path",
                    "frame path must be a safe relative path",
                    position,
                    finding_path,
                ))

            timestamp = _finite_number(frame.get("time"))
            if (
                timestamp is None
                or timestamp < 0.0
                or (
                    valid_range
                    and (timestamp < start - tolerance or timestamp > end + tolerance)
                )
            ):
                findings.append(Finding(
                    "error",
                    "frame_time",
                    "frame timestamp must be finite, non-negative, and inside segment bounds",
                    position,
                    finding_path,
                ))

            if "ocr" not in frame:
                findings.append(Finding(
                    "error",
                    "frame_ocr_missing",
                    "frame ocr key is required",
                    position,
                    finding_path,
                ))
            elif not isinstance(frame["ocr"], str):
                findings.append(Finding(
                    "error",
                    "frame_ocr_type",
                    "frame ocr must be a string",
                    position,
                    finding_path,
                ))

            if candidate is not None and not candidate.is_file():
                findings.append(Finding(
                    "error",
                    "frame_missing",
                    "frame file does not exist",
                    position,
                    finding_path,
                ))

    return findings


def load_lecture(path: Path) -> dict[str, Any]:
    source = Path(path)
    return normalize_lecture(json.loads(source.read_text(encoding="utf-8-sig")))


def write_json_atomic(path: Path, data: Mapping[str, Any]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(
        prefix=f".{destination.name}.",
        suffix=".tmp",
        dir=destination.parent,
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        json.loads(Path(temp_name).read_text(encoding="utf-8"))
        os.replace(temp_name, destination)
    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise
