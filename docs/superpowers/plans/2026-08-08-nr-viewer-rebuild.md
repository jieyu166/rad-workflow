# NR Viewer 全課重建 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 改善 canonical `skills/lecture-to-notes/`，建立可測試、可稽核、可重跑且具講次交易式回復能力的流程，並在取得獨立 NAS 操作授權後安全重建 `\\jieyu_nas\web\files\2015\08\20150804 NR 神放複習` 11 講。

**Architecture:** 正式 JSON 是唯一內容來源；extract 只產生 staging evidence 與候選影格，curate 選出每章正式 1–4 圖，rewrite 以 evidence packet 產生或匯入內容，render 生成 viewer/PBF/`.v4.md`/首頁，audit 以結構化 findings 阻擋不合格講次。發布採每講 manifest、同檔案系統 staging、完整備份、逐檔 `os.replace()` 與失敗後全講 rollback；首頁最後獨立切換。

**Tech Stack:** Python 3.10+ 標準庫、`scenedetect>=0.6.4,<0.8`、ffmpeg/ffprobe、RapidOCR/OpenCC（既有依賴）、HTML/CSS/vanilla JavaScript、Python `unittest`、Node VM、Chrome/Edge headless；可選 Claude API Python SDK僅用於通過敏感資料 preflight 且明確允許外送的重寫流程。

## Global Constraints

- 本計畫只描述後續實作；執行本計畫前不得修改 NAS，且實際三講／11 講 rollout 必須另行取得使用者明確授權。
- 不更改任何既有章節起訖時間或重新切分章節；`assert_times_unchanged()` 是 render/publish 前硬性 gate。
- 所有通用能力只實作於 canonical `skills/lecture-to-notes/`；不得建立 NR 專用生成器、第二套 viewer 或 NAS hotfix。
- 只修改 `skills/lecture-to-notes/` canonical 後執行 `python .\sync_skills.py`；不得直接修改 `.claude/skills/`、`.agents/skills/`、`.opencode/skills/`。
- 主控台輸出必須可由 cp950 strict 編碼；進度字元只使用 ASCII 與 cp950 可表示的繁體中文，禁止 Unicode 箭頭、勾號、數學比較符號。
- JSON、HTML、Markdown、manifest 與 audit report 使用 UTF-8；PBF 延續既有編碼選項與測試契約。
- Viewer 的 `application/json` script 內容必須是可由 browser `JSON.parse(textContent)` 直接解析的 raw JSON；只以 `.replace("</", "<\\/")` 防止 script close，不得 `html.escape()`。
- Viewer 只有一條 canonical data flow：`main()` 依序呼叫 `load_lecture()` 與 `load_srt()` 各一次，再呼叫 five-argument `render(data, cues, title, video_rel, media_dir: Path)`；`render()` 內部只呼叫 `build_blocks(data, cues)` 一次，不得保留舊 segments/media 平行參數。
- candidate frames 只存在 staging；正式 JSON 與 viewer 只可出現 `frames[]` 內選定的 1–4 圖。
- 每章 `takeaways_zh` 正好 4 項；`editorial_notes_zh` 與講者內容分離；零正式影格為 hard failure。
- 病患資料、正式逐字稿、正式影格、NAS 產物、備份、staging、audit 實例與敏感路徑不得進入 Git。
- 若使用外部 LLM，憑證只由環境或官方 SDK credential chain 取得；不得在程式碼、plan、log、manifest 放入 API key/token。
- 外部 LLM 預設關閉；只有 `--allow-external-llm`、敏感資料 preflight 通過及人工確認三者同時成立才可送出 evidence text；影像與原始檔不得上傳。
- 長流程必須同步在前景執行並持續顯示講次、階段、章節數、完成比例及失敗摘要；不得 detached 或靜默長跑。
- PowerShell 版本為 Windows PowerShell 5.1；不得使用 `&&`、`||` 或 PowerShell 7 專屬語法。
- PySceneDetect 必須固定為 `scenedetect>=0.6.4,<0.8`；preflight 必須讀取實際安裝版本，不在此範圍就 hard fail，官方 API 依據保留於 References。
- 實作期間工作樹可能含使用者的其他 viewer 變更；每個 commit 只 stage task 明列路徑，禁止 `git add .`、`git add -A`、stash、reset、clean 或 amend。

---

## Scope Check

設計涵蓋三個責任域：canonical data/rewrite core、viewer/render/audit、local orchestration/NAS publication。它們原可拆成三份相依 plan，但本次核准設計與交付明確要求單一 `docs/superpowers/plans/2026-08-08-nr-viewer-rebuild.md`，因此保留單一 plan，並以 Task 1–6、7–10、11–16 三個可獨立 review gate 分段。Task 1–12 只用 synthetic/local fixture；Task 13–16 才包含需獨立授權的真實課程執行 handoff。

## File Responsibility Map

### Create

- `skills/lecture-to-notes/scripts/lecture_model.py` — canonical schema、normalization、時間不變性與 JSON I/O。
- `skills/lecture-to-notes/scripts/lecture_content_rules.py` — title/summary/takeaways/editorial/language/content gate。
- `skills/lecture-to-notes/scripts/rewrite_evidence.py` — SRT/OCR/frame evidence packet、敏感資料 preflight、人工 review record。
- `skills/lecture-to-notes/scripts/rewrite_lecture.py` —正式可重跑 rewrite CLI；manual import 為預設，可選 Claude API structured output。
- `skills/lecture-to-notes/scripts/frame_curator.py` — candidate manifest 驗證、去重/低資訊篩除、正式 1–4 圖選取。
- `skills/lecture-to-notes/scripts/render_v4_note.py` — canonical JSON 到 deterministic `.v4.md`。
- `skills/lecture-to-notes/scripts/lecture_audit.py` — structured findings、跨衍生檔一致性與 report serialization。
- `skills/lecture-to-notes/scripts/rebuild_course.py` — preflight、extract/curate/rewrite/render/audit orchestration 與進度。
- `skills/lecture-to-notes/scripts/publish_transaction.py` — manifest、backup、replace、rollback、recovery report。
- `skills/lecture-to-notes/requirements-rebuild.txt` — 可安裝的 rebuild dependency contract；明列 `scenedetect>=0.6.4,<0.8`，與 preflight runtime gate 使用相同範圍。
- `tests/test_lecture_model.py`
- `tests/test_lecture_content_rules.py`
- `tests/test_lecture_rewrite.py`
- `tests/test_lecture_frame_curator.py`
- `tests/test_lecture_renderers.py`
- `tests/test_lecture_audit.py`
- `tests/test_lecture_rebuild_pipeline.py`
- `tests/test_lecture_publish_transaction.py`
- `tests/test_lecture_viewer_e2e.py`
- `tests/test_lecture_console_encoding.py`
- `tests/test_sync_skills.py`
- `tests/fixtures/lecture_rebuild/course/` — self-contained synthetic MP4/SRT/JSON/PNG/OCR；正式 PNG 位於 `course/frames/`，不得包含正式 NR 內容。Task 12 直接測 fixture pipeline 的 staging viewer，不維護另一份 golden HTML/media tree。

### Modify

- `skills/lecture-to-notes/scripts/slide_frames.py:detect_scenes(), extract_frame(), main()` — scene extraction 改輸出 staging candidate manifest，不直接寫正式 `frames`。
- `skills/lecture-to-notes/scripts/ocr_frames.py:collect_frames(), main()` — OCR 寫回 candidate manifest/frame object，不維護第二份正式媒體索引。
- `skills/lecture-to-notes/scripts/build_lecture_viewer.py:build_blocks(), render(), main()` —新 schema、詳細型 UI、2x2/768px、modal/seek、typed search、逐字稿/OCR details。
- `skills/lecture-to-notes/scripts/json_to_pbf.py:json_to_pbf_lines(), convert_one()` — consume normalized canonical JSON 並提供一致性資料。
- `skills/lecture-to-notes/scripts/build_course_hub.py:collect(), build_index(), render()` — 11 講狀態、標題/summary/editorial 索引與正式連結。
- `skills/lecture-to-notes/scripts/check_lecture.py:main()` — 保留 CLI facade，改呼叫 `lecture_audit.audit_lecture()`。
- `skills/lecture-to-notes/scripts/batch_course.py:main()` — deprecated compatibility wrapper，轉呼叫 `rebuild_course.main()` 並正確回傳 exit code。
- `skills/lecture-to-notes/SKILL.md:workflow/schema/commands/audit/rollout sections` — canonical 使用方式、正式重跑入口與安全限制。
- `sync_skills.py:check/copy comparison symbols` — `--check` 比對相對檔案集合與 bytes/hash，不只 skill 名稱。

---

### Task 1: Canonical Schema、Normalization 與時間不變性

**Files:**
- Create: `skills/lecture-to-notes/scripts/lecture_model.py`
- Create: `tests/test_lecture_model.py`

**Interfaces:**
- Consumes: existing canonical JSON with `start_sec`/`end_sec`, optional migration aliases `start`/`end`, legacy `bullets_zh`, string `frames`, segment-level `frame_ocr`, and older top-level `frame_ocr` maps.
- Produces: `Finding`, `segment_start(segment) -> float`, `segment_end(segment) -> float`, `normalize_lecture(data: Mapping[str, Any]) -> dict[str, Any]` whose output always retains canonical `start_sec`/`end_sec`, `validate_lecture_schema(data: Mapping[str, Any], base_dir: Path, frame_tolerance_seconds: float = 0.25) -> list[Finding]`, `time_signature(data: Mapping[str, Any]) -> tuple[tuple[float, float], ...]`, `assert_times_unchanged(before, after) -> None`, `load_lecture(path: Path) -> dict[str, Any]`, `write_json_atomic(path: Path, data: Mapping[str, Any]) -> None`.

- [ ] **Step 1: Write failing schema and migration tests**

```python
# tests/test_lecture_model.py
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "lecture-to-notes" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lecture_model import (
    assert_times_unchanged,
    normalize_lecture,
    validate_lecture_schema,
    write_json_atomic,
)


class LectureModelTests(unittest.TestCase):
    def test_normalize_migrates_legacy_segment_without_changing_times(self):
        source = {
            "title": "Synthetic lecture",
            "segments": [{
                "index": 1,
                "start_sec": 10.0,
                "end_sec": 20.0,
                "title": "Focused title",
                "summary_zh": "整理內容",
                "bullets_zh": ["甲", "乙", "丙", "丁"],
                "frames": ["frames/f001.jpg"],
                "frame_ocr": [{"frame": "frames/f001.jpg", "text": "Slide text"}],
            }],
        }
        result = normalize_lecture(source)
        self.assertEqual((result["segments"][0]["start_sec"], result["segments"][0]["end_sec"]), (10.0, 20.0))
        self.assertNotIn("start", result["segments"][0])
        self.assertNotIn("end", result["segments"][0])
        self.assertEqual(result["segments"][0]["takeaways_zh"], ["甲", "乙", "丙", "丁"])
        self.assertEqual(result["segments"][0]["editorial_notes_zh"], [])
        self.assertEqual(result["segments"][0]["frames"], [{
            "time": 0.0,
            "ocr": "Slide text",
            "path": "frames/f001.jpg",
        }])
        self.assertNotIn("frame_ocr", result["segments"][0])
        self.assertNotIn("bullets_zh", result["segments"][0])

    def test_schema_rejects_zero_frames_and_wrong_takeaway_count(self):
        with tempfile.TemporaryDirectory() as td:
            data = {"segments": [{
                "start_sec": 0.0,
                "end_sec": 5.0,
                "title": "腦部腫瘤判讀",
                "summary_zh": "合格內容",
                "takeaways_zh": ["一", "二", "三"],
                "editorial_notes_zh": [],
                "frames": [],
            }]}
            findings = validate_lecture_schema(data, Path(td))
        codes = {item.code for item in findings}
        self.assertTrue({"takeaway_count", "frame_count"}.issubset(codes))

    def test_schema_rejects_windows_and_posix_absolute_paths_bad_ocr_and_out_of_range_time(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            data = {"segments": [{
                "start_sec": 0.0,
                "end_sec": 5.0,
                "title": "腦部腫瘤判讀",
                "summary_zh": "合格內容",
                "takeaways_zh": ["一", "二", "三", "四"],
                "editorial_notes_zh": [],
                "frames": [
                    {"time": 1.0, "ocr": "A", "path": "/absolute/a.jpg"},
                    {"time": 2.0, "ocr": "B", "path": "C:/absolute/b.jpg"},
                    {"time": 9.0, "ocr": None, "path": "frames/missing.jpg"},
                ],
            }]}
            findings = validate_lecture_schema(data, root)
        by_code = {}
        for item in findings:
            by_code.setdefault(item.code, []).append(item)
        self.assertEqual({item.path for item in by_code["frame_path"]}, {"/absolute/a.jpg", "C:/absolute/b.jpg"})
        self.assertEqual([item.path for item in by_code["frame_time"]], ["frames/missing.jpg"])
        self.assertEqual([item.path for item in by_code["frame_ocr_type"]], ["frames/missing.jpg"])
        self.assertEqual([item.path for item in by_code["frame_missing"]], ["frames/missing.jpg"])

    def test_malformed_frame_times_are_structured_findings_and_validation_continues(self):
        with tempfile.TemporaryDirectory() as td:
            data = normalize_lecture({"segments": [{
                "start_sec": 0.0,
                "end_sec": 5.0,
                "title": "腦部腫瘤判讀",
                "summary_zh": "合格內容",
                "takeaways_zh": ["一", "二", "三", "四"],
                "editorial_notes_zh": [],
                "frames": [
                    {"time": "not-a-time", "ocr": "A", "path": "frames/a.jpg"},
                    {"time": None, "ocr": None, "path": "frames/b.jpg"},
                    {"time": -1.0, "ocr": "C", "path": "frames/c.jpg"},
                    {"time": float("inf"), "ocr": "D", "path": "frames/d.jpg"},
                ],
            }]})
            findings = validate_lecture_schema(data, Path(td))
        frame_time_paths = {item.path for item in findings if item.code == "frame_time"}
        missing_paths = {item.path for item in findings if item.code == "frame_missing"}
        self.assertEqual(frame_time_paths, {"frames/a.jpg", "frames/b.jpg", "frames/c.jpg", "frames/d.jpg"})
        self.assertEqual(missing_paths, {"frames/a.jpg", "frames/b.jpg", "frames/c.jpg", "frames/d.jpg"})
        self.assertIn("frames/b.jpg", {item.path for item in findings if item.code == "frame_ocr_type"})

    def test_assert_times_unchanged_reports_segment_index(self):
        before = {"segments": [{"start_sec": 1.0, "end_sec": 2.0}]}
        after = {"segments": [{"start_sec": 1.0, "end_sec": 2.1}]}
        with self.assertRaisesRegex(ValueError, "segment 0"):
            assert_times_unchanged(before, after)

    def test_atomic_writer_leaves_valid_json(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "lecture.json"
            write_json_atomic(target, {"segments": []})
            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), {"segments": []})
            self.assertEqual(list(Path(td).glob("*.tmp")), [])
```

- [ ] **Step 2: Run the tests and verify RED**

Run:

```powershell
python -m unittest tests.test_lecture_model -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'lecture_model'`.

- [ ] **Step 3: Implement the canonical model**

```python
# skills/lecture-to-notes/scripts/lecture_model.py
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


def _frame_time(path: str) -> float:
    stem = Path(path).stem
    marker = stem.rsplit("_", 1)[-1]
    try:
        return float(marker.replace("-", "."))
    except ValueError:
        return 0.0


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
    for segment in result.get("segments", []):
        segment["start_sec"] = segment_start(segment)
        segment["end_sec"] = segment_end(segment)
        segment.pop("start", None)
        segment.pop("end", None)
        if "takeaways_zh" not in segment:
            segment["takeaways_zh"] = list(segment.pop("bullets_zh", []))
        else:
            segment.pop("bullets_zh", None)
        segment.setdefault("editorial_notes_zh", [])
        segment_ocr = {
            str(item.get("frame", "")): str(item.get("text", ""))
            for item in segment.pop("frame_ocr", []) or []
            if isinstance(item, Mapping)
        }
        normalized_frames = []
        for frame in segment.get("frames", []):
            if isinstance(frame, str):
                normalized_frames.append({
                    "time": _frame_time(frame),
                    "ocr": segment_ocr.get(frame, str(top_level_ocr.get(frame, ""))),
                    "path": frame.replace("\\", "/"),
                })
            else:
                normalized_frames.append({
                    # Preserve malformed values for structured schema findings instead of crashing normalization.
                    "time": frame.get("time"),
                    "ocr": frame.get("ocr", ""),
                    "path": str(frame.get("path", "")).replace("\\", "/"),
                })
        segment["frames"] = normalized_frames
    return result


def time_signature(data: Mapping[str, Any]) -> tuple[tuple[float, float], ...]:
    return tuple((segment_start(s), segment_end(s)) for s in data.get("segments", []))


def assert_times_unchanged(before: Mapping[str, Any], after: Mapping[str, Any]) -> None:
    old = time_signature(before)
    new = time_signature(after)
    if len(old) != len(new):
        raise ValueError(f"segment count changed: {len(old)} != {len(new)}")
    for index, (old_range, new_range) in enumerate(zip(old, new)):
        if old_range != new_range:
            raise ValueError(f"segment {index} time changed: {old_range} != {new_range}")


def _safe_relative_frame_path(value: str) -> PurePosixPath | None:
    normalized = value.replace("\\", "/")
    posix = PurePosixPath(normalized)
    windows = PureWindowsPath(value)
    if (
        not normalized
        or posix.is_absolute()
        or windows.is_absolute()
        or windows.drive
        or ".." in posix.parts
    ):
        return None
    return posix


def _finite_frame_time(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return parsed if math.isfinite(parsed) and parsed >= 0.0 else None


def validate_lecture_schema(
    data: Mapping[str, Any],
    base_dir: Path,
    frame_tolerance_seconds: float = 0.25,
) -> list[Finding]:
    findings: list[Finding] = []
    segments = data.get("segments")
    if not isinstance(segments, list) or not segments:
        return [Finding("error", "segments_missing", "segments must be a non-empty list")]
    for index, segment in enumerate(segments):
        try:
            start = segment_start(segment)
            end = segment_end(segment)
        except (KeyError, TypeError, ValueError):
            start, end = -1.0, -1.0
        if start < 0 or end <= start:
            findings.append(Finding("error", "time_range", "invalid segment time range", index))
        takeaways = segment.get("takeaways_zh")
        if not isinstance(takeaways, list) or len(takeaways) != 4:
            findings.append(Finding("error", "takeaway_count", "takeaways_zh must contain exactly four items", index))
        editorial = segment.get("editorial_notes_zh")
        if not isinstance(editorial, list) or not all(isinstance(x, str) for x in editorial):
            findings.append(Finding("error", "editorial_type", "editorial_notes_zh must be a string list", index))
        frames = segment.get("frames")
        if not isinstance(frames, list) or not 1 <= len(frames) <= 4:
            findings.append(Finding("error", "frame_count", "frames must contain one to four items", index))
            continue
        for frame in frames:
            rel = str(frame.get("path", ""))
            pure = _safe_relative_frame_path(rel)
            if pure is None:
                findings.append(Finding("error", "frame_path", "frame path must be a safe relative path", index, rel))
                continue
            timestamp = _finite_frame_time(frame.get("time"))
            if (
                timestamp is None
                or timestamp < start - frame_tolerance_seconds
                or timestamp > end + frame_tolerance_seconds
            ):
                findings.append(Finding("error", "frame_time", "frame timestamp must be finite, non-negative, and inside segment bounds", index, rel))
            if not (base_dir / Path(*pure.parts)).is_file():
                findings.append(Finding("error", "frame_missing", "frame file does not exist", index, rel))
            if not isinstance(frame.get("ocr", ""), str):
                findings.append(Finding("error", "frame_ocr_type", "frame ocr must be a string", index, rel))
    return findings


def load_lecture(path: Path) -> dict[str, Any]:
    return normalize_lecture(json.loads(path.read_text(encoding="utf-8-sig")))


def write_json_atomic(path: Path, data: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        json.loads(Path(temp_name).read_text(encoding="utf-8"))
        os.replace(temp_name, path)
    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise
```

- [ ] **Step 4: Run tests and verify GREEN**

Run: `python -m unittest tests.test_lecture_model -v`

Expected: PASS；zero-frame/count、Windows/POSIX absolute path、missing path、non-string OCR、out-of-range time，以及 invalid string/null/negative/nonfinite frame time 都成為 structured `Finding` 且不阻斷其餘錯誤蒐集；time immutability and atomic-write assertions all pass。

- [ ] **Step 5: Commit only this task**

```powershell
git add -- "skills/lecture-to-notes/scripts/lecture_model.py" "tests/test_lecture_model.py"
git commit -m "feat(lecture): add canonical lecture schema"
```

---

### Task 2: Content Rules、來源分離與敏感資料 Preflight

**Files:**
- Create: `skills/lecture-to-notes/scripts/lecture_content_rules.py`
- Create: `skills/lecture-to-notes/scripts/rewrite_evidence.py`
- Create: `tests/test_lecture_content_rules.py`

**Interfaces:**
- Consumes: normalized segment dict、segment SRT text、frame OCR text。
- Produces: `validate_segment_content(segment: Mapping[str, Any], transcript_text: str) -> list[Finding]`, `contains_sensitive_data(text: str) -> list[str]`, `build_evidence_packet(...) -> dict[str, Any]`, `validate_review_record(packet, rewritten, review) -> list[Finding]`.

- [ ] **Step 1: Write failing rule and privacy tests**

```python
# tests/test_lecture_content_rules.py
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "lecture-to-notes" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lecture_content_rules import validate_segment_content
from rewrite_evidence import contains_sensitive_data, validate_review_record


class LectureContentRuleTests(unittest.TestCase):
    def valid_segment(self):
        return {
            "title": "Glioblastoma 的影像判讀與鑑別",
            "summary_zh": "腫瘤在影像上呈現不規則增強與壞死，判讀時需整合病灶位置、周邊水腫、擴散與灌流資訊。講者依序說明主要表現、常見鑑別與容易誤判之處，並強調結論只能建立在本病例已呈現的影像與課堂敘述。" * 4,
            "takeaways_zh": ["重點甲", "重點乙", "重點丙", "重點丁"],
            "editorial_notes_zh": ["編輯補充：一般分類資訊，不代表本病例診斷。"],
        }

    def test_valid_segment_has_no_errors(self):
        findings = validate_segment_content(self.valid_segment(), "講者原始逐字稿")
        self.assertEqual([f for f in findings if f.severity == "error"], [])

    def test_rejects_generic_focused_titles(self):
        for title in ("Focused", "Overview", "Summary", "Chapter 3", "重點", "介紹", "病例"):
            with self.subTest(title=title):
                segment = self.valid_segment()
                segment["title"] = title
                self.assertIn(
                    "title_focus",
                    {f.code for f in validate_segment_content(segment, "原始逐字稿")},
                )

    def test_rejects_short_summary_wrong_paragraph_count_and_unfinished_markers(self):
        segment = self.valid_segment()
        segment["summary_zh"] = ("TO" + "DO") + "\n\n甲\n\n乙"
        codes = {f.code for f in validate_segment_content(segment, "原始逐字稿")}
        self.assertTrue({"summary_length", "summary_paragraphs", "unfinished_marker"}.issubset(codes))

    def test_opencc_gate_rejects_simplified_medical_text_without_flagging_taiwan_terms(self):
        simplified = self.valid_segment()
        simplified["summary_zh"] = "脑肿瘤影像显示强化与水肿，医生需要结合扩散、灌注与临床资料进行鉴别。" * 8
        self.assertIn("simplified_chinese", {f.code for f in validate_segment_content(simplified, "")})
        traditional = self.valid_segment()
        traditional["summary_zh"] = "臺灣常用的神經放射學術語與影像判讀內容。" * 20
        self.assertNotIn("simplified_chinese", {f.code for f in validate_segment_content(traditional, "")})

    def test_sensitive_scanner_catches_mrn_birthdate_and_phone(self):
        text = "病歷號 12345678，生日 1980/01/02，電話 0912-345-678"
        kinds = set(contains_sensitive_data(text))
        self.assertEqual(kinds, {"medical_record_number", "birth_date", "phone"})

    def test_review_record_requires_evidence_and_hallucination_check(self):
        packet = {"packet_sha256": "abc", "segment_index": 2}
        rewritten = self.valid_segment()
        review = {"packet_sha256": "abc", "reviewer": "A80748", "source_faithful": True}
        codes = {f.code for f in validate_review_record(packet, rewritten, review)}
        self.assertIn("case_detail_check_missing", codes)
```

- [ ] **Step 2: Run and verify RED**

Run: `python -m unittest tests.test_lecture_content_rules -v`

Expected: FAIL because `lecture_content_rules` and `rewrite_evidence` do not exist.

- [ ] **Step 3: Implement deterministic content and privacy gates**

```python
# skills/lecture-to-notes/scripts/lecture_content_rules.py
from __future__ import annotations

import re
from functools import lru_cache
from typing import Any, Mapping

from opencc import OpenCC
from lecture_model import Finding

UNFINISHED = re.compile(r"\b(?:TO" + r"DO|T" + r"BD|PLACE" + r"HOLDER)\b", re.IGNORECASE)
TEMPLATE_PHRASES = ("請補充", "待確認", "此處填入", "核心重點一")
FOCUSED_TITLE_FORBIDDEN = re.compile(
    r"^(?:focused|overview|summary|chapter\s*\d+|重點|介紹|病例)$",
    re.IGNORECASE,
)
TRADITIONAL_VARIANT_ALLOWLIST = frozenset("臺裡著乾")


@lru_cache(maxsize=1)
def _s2t_converter() -> OpenCC:
    return OpenCC("s2t")


def _contains_simplified(text: str) -> bool:
    converter = _s2t_converter()
    for char in text:
        converted = converter.convert(char)
        if converted != char and char not in TRADITIONAL_VARIANT_ALLOWLIST:
            return True
    return False


def _han_count(text: str) -> int:
    return sum("\u3400" <= char <= "\u9fff" for char in text)


def validate_segment_content(segment: Mapping[str, Any], transcript_text: str) -> list[Finding]:
    findings: list[Finding] = []
    title = str(segment.get("title", "")).strip()
    if len(title) < 6 or title.isdigit() or FOCUSED_TITLE_FORBIDDEN.fullmatch(title):
        findings.append(Finding("error", "title_focus", "title must identify a diagnosis, finding, anatomy, or reading task"))
    summary = str(segment.get("summary_zh", "")).strip()
    count = _han_count(summary)
    if count < 250 or count > 600:
        findings.append(Finding("error", "summary_length", f"summary_zh contains {count} Han characters; expected 250-600"))
    paragraphs = [part for part in re.split(r"\n\s*\n", summary) if part.strip()]
    if not 1 <= len(paragraphs) <= 2:
        findings.append(Finding("error", "summary_paragraphs", "summary_zh must contain one or two paragraphs"))
    takeaways = segment.get("takeaways_zh", [])
    if len(takeaways) != 4 or any(not str(item).strip() for item in takeaways):
        findings.append(Finding("error", "takeaway_count", "takeaways_zh must contain four non-empty items"))
    normalized = [re.sub(r"\s+", "", str(item)) for item in takeaways]
    if len(set(normalized)) != len(normalized):
        findings.append(Finding("error", "takeaway_duplicate", "takeaways_zh items must be distinct"))
    editorial = segment.get("editorial_notes_zh")
    if not isinstance(editorial, list):
        findings.append(Finding("error", "editorial_type", "editorial_notes_zh must be a list"))
    combined = "\n".join([title, summary, *map(str, takeaways), *map(str, editorial or [])])
    if UNFINISHED.search(combined) or any(phrase in combined for phrase in TEMPLATE_PHRASES):
        findings.append(Finding("error", "unfinished_marker", "content contains an unfinished or template marker"))
    if _contains_simplified(combined):
        findings.append(Finding("error", "simplified_chinese", "content contains simplified-only characters"))
    transcript_lines = {line.strip() for line in transcript_text.splitlines() if len(line.strip()) >= 20}
    copied = sum(1 for line in transcript_lines if line in summary)
    if transcript_lines and copied / len(transcript_lines) > 0.5:
        findings.append(Finding("error", "transcript_copy", "summary repeats too many transcript lines verbatim"))
    return findings
```

```python
# skills/lecture-to-notes/scripts/rewrite_evidence.py
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from build_lecture_viewer import load_srt
from lecture_model import Finding, load_lecture, segment_end, segment_start, write_json_atomic

SENSITIVE_PATTERNS = {
    "medical_record_number": re.compile(r"(?:病歷號|MRN)\s*[:：]?\s*[A-Z0-9-]{6,12}", re.IGNORECASE),
    "birth_date": re.compile(r"(?:生日|出生)\s*[:：]?\s*(?:19|20)\d{2}[/-]\d{1,2}[/-]\d{1,2}"),
    "phone": re.compile(r"(?<!\d)09\d{2}[- ]?\d{3}[- ]?\d{3}(?!\d)"),
    "national_id": re.compile(r"(?<![A-Z0-9])[A-Z][12]\d{8}(?!\d)"),
    "email": re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE),
}


def contains_sensitive_data(text: str) -> list[str]:
    return [name for name, pattern in SENSITIVE_PATTERNS.items() if pattern.search(text)]


def build_evidence_packet(
    lecture_id: str,
    segment_index: int,
    start: float,
    end: float,
    transcript_text: str,
    frames: Sequence[Mapping[str, Any]],
    existing_segment: Mapping[str, Any],
) -> dict[str, Any]:
    packet = {
        "lecture_id": lecture_id,
        "segment_index": segment_index,
        "start": start,
        "end": end,
        "transcript_text": transcript_text,
        "frame_evidence": [{"time": f["time"], "ocr": f.get("ocr", ""), "path": f["path"]} for f in frames],
        "existing_content": {
            "title": existing_segment.get("title", ""),
            "summary_zh": existing_segment.get("summary_zh", ""),
        },
    }
    encoded = json.dumps(packet, ensure_ascii=False, sort_keys=True).encode("utf-8")
    packet["packet_sha256"] = hashlib.sha256(encoded).hexdigest()
    packet["sensitive_findings"] = contains_sensitive_data(transcript_text + "\n" + "\n".join(f.get("ocr", "") for f in frames))
    return packet


def validate_review_record(
    packet: Mapping[str, Any],
    rewritten: Mapping[str, Any],
    review: Mapping[str, Any],
) -> list[Finding]:
    findings: list[Finding] = []
    if review.get("packet_sha256") != packet.get("packet_sha256"):
        findings.append(Finding("error", "review_packet_mismatch", "review record does not match evidence packet"))
    if not str(review.get("reviewer", "")).strip():
        findings.append(Finding("error", "reviewer_missing", "reviewer is required"))
    if review.get("source_faithful") is not True:
        findings.append(Finding("error", "source_faithful_missing", "review must confirm speaker content is source-faithful"))
    if review.get("case_details_verified") is not True:
        findings.append(Finding("error", "case_detail_check_missing", "review must confirm no unsupported case detail was added"))
    if review.get("editorial_separated") is not True:
        findings.append(Finding("error", "editorial_check_missing", "review must confirm editorial notes are separated"))
    if packet.get("sensitive_findings"):
        findings.append(Finding("error", "sensitive_evidence", "evidence packet contains sensitive-data patterns"))
    return findings


def write_evidence_packets(lecture_path: Path, srt_path: Path, output_path: Path) -> list[dict[str, Any]]:
    data = load_lecture(lecture_path)
    cues = load_srt(srt_path)
    packets = []
    lecture_id = str(data.get("lecture_id", lecture_path.stem))
    for index, segment in enumerate(data["segments"]):
        start, end = segment_start(segment), segment_end(segment)
        transcript = "\n".join(cue["text"] for cue in cues if start <= float(cue["start"]) < end)
        packets.append(build_evidence_packet(lecture_id, index, start, end, transcript, segment["frames"], segment))
    write_json_atomic(output_path, packets)
    return packets


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("lecture", type=Path)
    parser.add_argument("--srt", type=Path, required=True)
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args(argv)
    packets = write_evidence_packets(args.lecture, args.srt, args.output)
    print(f"[evidence] segments={len(packets)} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run and verify GREEN**

Run: `python -m unittest tests.test_lecture_content_rules -v`

Expected: PASS；generic `Focused`/overview/chapter titles, content/privacy failures and valid focused medical title assertions all behave exactly as tested。

- [ ] **Step 5: Commit**

```powershell
git add -- "skills/lecture-to-notes/scripts/lecture_content_rules.py" "skills/lecture-to-notes/scripts/rewrite_evidence.py" "tests/test_lecture_content_rules.py"
git commit -m "feat(lecture): validate content and rewrite evidence"
```

---

### Task 3: Candidate Frame Staging 與正式 1–4 圖策展

**Files:**
- Create: `skills/lecture-to-notes/scripts/frame_curator.py`
- Modify: `skills/lecture-to-notes/scripts/slide_frames.py:detect_scenes(), main()`
- Modify: `skills/lecture-to-notes/scripts/ocr_frames.py:collect_frames(), main()`
- Create: `tests/test_lecture_frame_curator.py`

**Interfaces:**
- Consumes: PySceneDetect `(start_time, end_time)` results、staging candidate manifest、OCR results。
- Produces: candidate dictionaries with `time/path/ocr/sharpness/luma/phash` and normalized legacy candidates additionally tagged `source="legacy-formal"`, `score_candidate(item: Mapping[str, Any]) -> float`, `materialize_legacy_candidates(data: Mapping[str, Any], live_root: Path, staging_root: Path) -> list[dict[str, Any]]`, `merge_existing_candidates(data, extracted) -> list[dict[str, Any]]`, `curate_segment(candidates, start, end, max_frames=4, tolerance=0.25) -> list[dict[str, Any]]`; 第一講既有 72 張正式影格必須先以 `shutil.copy2()` 實體複製到該講 staging、驗 SHA-256 相同，再正規化並依 `(path,time)` 去重後全部併入 staging candidate pool；curator 只能讀 staging 內候選資產，每章僅選 1–4 張正式影格；`slide_frames.py --staging <dir>` writes `candidate_frames.json` and never mutates canonical JSON。

- [ ] **Step 1: Write failing curation tests**

```python
# tests/test_lecture_frame_curator.py
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "lecture-to-notes" / "scripts"))

from frame_curator import curate_segment, materialize_legacy_candidates, merge_existing_candidates
from slide_frames import build_candidate_manifest


class FrameCuratorTests(unittest.TestCase):
    def test_candidate_manifest_records_exact_scenedetect_dependency_contract(self):
        manifest = build_candidate_manifest(
            video_name="01.mp4", detector_type="adaptive", threshold=3.0,
            min_scene_len=1.5, candidates=[], scenedetect_version="0.6.4",
        )
        self.assertEqual(manifest["detector"]["scenedetect_version"], "0.6.4")
        self.assertEqual(manifest["detector"]["required_scenedetect"], ">=0.6.4,<0.8")

    def test_first_lecture_all_72_legacy_assets_are_copied_hashed_and_deduplicated_in_staging(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); live_root = root / "live"; staging_root = root / "stage"
            live_root.mkdir(); staging_root.mkdir()
            segments = []
            expected_hashes = {}
            for chapter in range(18):
                frames = []
                for offset in range(4):
                    relative = f"legacy/ch{chapter:02d}-{offset}.jpg"
                    source = live_root / relative
                    source.parent.mkdir(parents=True, exist_ok=True)
                    source.write_bytes(f"frame-{chapter}-{offset}".encode("ascii"))
                    expected_hashes[relative] = hashlib.sha256(source.read_bytes()).hexdigest()
                    frames.append({"time": chapter * 10.0 + offset + 0.5, "path": relative, "ocr": f"OCR {chapter}-{offset}"})
                segments.append({"start_sec": chapter * 10.0, "end_sec": (chapter + 1) * 10.0, "frames": frames})
            data = {"lecture_id": "01", "segments": segments}
            legacy = materialize_legacy_candidates(data, live_root, staging_root)
            duplicate_new = [dict(legacy[0]), dict(legacy[0])]
            pool = merge_existing_candidates({"segments": []}, [*legacy, *duplicate_new])
            legacy_paths = {frame["path"] for segment in segments for frame in segment["frames"]}
            self.assertEqual(len(legacy_paths), 72)
            self.assertEqual(len(pool), 72)
            self.assertTrue(legacy_paths.issubset({item["path"] for item in pool}))
            by_path = {item["path"]: item for item in pool}
            for relative in legacy_paths:
                staged = staging_root / relative
                self.assertTrue(staged.is_file())
                self.assertEqual(hashlib.sha256(staged.read_bytes()).hexdigest(), expected_hashes[relative])
                self.assertEqual(by_path[relative]["source"], "legacy-formal")
            formal = [curate_segment(pool, segment["start_sec"], segment["end_sec"]) for segment in segments]
            self.assertTrue(all(1 <= len(frames) <= 4 for frames in formal))

    def test_curate_keeps_best_unique_frames_in_time_order(self):
        candidates = [
            {"time": 1.0, "path": "frames/a.jpg", "ocr": "A", "sharpness": 20.0, "luma": 80.0, "phash": "aa"},
            {"time": 2.0, "path": "frames/b.jpg", "ocr": "B", "sharpness": 80.0, "luma": 90.0, "phash": "aa"},
            {"time": 3.0, "path": "frames/c.jpg", "ocr": "C", "sharpness": 70.0, "luma": 100.0, "phash": "cc"},
            {"time": 4.0, "path": "frames/d.jpg", "ocr": "", "sharpness": 60.0, "luma": 110.0, "phash": "dd"},
            {"time": 5.0, "path": "frames/e.jpg", "ocr": "E", "sharpness": 90.0, "luma": 120.0, "phash": "ee"},
        ]
        result = curate_segment(candidates, 0.0, 6.0, max_frames=4)
        self.assertEqual([f["path"] for f in result], ["frames/b.jpg", "frames/c.jpg", "frames/d.jpg", "frames/e.jpg"])

    def test_zero_valid_frames_raises_hard_failure(self):
        candidates = [{"time": 20.0, "path": "frames/x.jpg", "ocr": "", "sharpness": 1.0, "luma": 0.0, "phash": "x"}]
        with self.assertRaisesRegex(ValueError, "no valid frame"):
            curate_segment(candidates, 0.0, 5.0)
```

- [ ] **Step 2: Run and verify RED**

Run: `python -m unittest tests.test_lecture_frame_curator -v`

Expected: FAIL because `frame_curator` does not exist.

- [ ] **Step 3: Implement deterministic curator**

```python
# skills/lecture-to-notes/scripts/frame_curator.py
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping

from lecture_model import load_lecture, segment_end, segment_start, write_json_atomic


def score_candidate(item: Mapping[str, Any]) -> float:
    sharpness = float(item.get("sharpness", 0.0))
    luma = float(item.get("luma", 0.0))
    ocr_bonus = min(len(str(item.get("ocr", ""))), 120) / 12.0
    exposure_penalty = 100.0 if luma < 8.0 or luma > 247.0 else 0.0
    return sharpness + ocr_bonus - exposure_penalty


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def materialize_legacy_candidates(
    data: Mapping[str, Any],
    live_root: Path,
    staging_root: Path,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for segment in data.get("segments", []):
        for frame in segment.get("frames", []):
            relative = PurePosixPath(str(frame["path"]).replace("\\", "/"))
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError(f"unsafe legacy frame path: {relative.as_posix()}")
            native_relative = Path(*relative.parts)
            source = live_root / native_relative
            target = staging_root / native_relative
            if not source.is_file():
                raise FileNotFoundError(f"legacy frame missing: {source}")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            if _file_sha256(target) != _file_sha256(source):
                raise IOError(f"legacy frame staging hash mismatch: {relative.as_posix()}")
            candidates.append({
                "time": float(frame["time"]),
                "path": relative.as_posix(),
                "ocr": str(frame.get("ocr", "")),
                "sharpness": float(frame.get("sharpness", 100.0)),
                "luma": float(frame.get("luma", 128.0)),
                "phash": str(frame.get("phash") or f"legacy:{relative.as_posix().casefold()}"),
                "source": "legacy-formal",
            })
    return candidates


def merge_existing_candidates(
    data: Mapping[str, Any],
    extracted: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Normalize legacy formal frames into the staging pool, then deduplicate path/time pairs."""
    merged: dict[tuple[str, float], dict[str, Any]] = {}
    for raw in extracted:
        item = dict(raw)
        key = (str(item["path"]).replace("\\", "/").casefold(), round(float(item["time"]), 3))
        merged[key] = item
    for segment in data.get("segments", []):
        for frame in segment.get("frames", []):
            path = str(frame["path"]).replace("\\", "/")
            item = {
                "time": float(frame["time"]),
                "path": path,
                "ocr": str(frame.get("ocr", "")),
                "sharpness": float(frame.get("sharpness", 100.0)),
                "luma": float(frame.get("luma", 128.0)),
                "phash": str(frame.get("phash") or f"legacy:{path.casefold()}"),
                "source": "legacy-formal",
            }
            key = (path.casefold(), round(item["time"], 3))
            current = merged.get(key)
            if current is None or score_candidate(item) > score_candidate(current):
                merged[key] = item
    return sorted(merged.values(), key=lambda item: (float(item["time"]), str(item["path"])))


def curate_segment(
    candidates: Iterable[Mapping[str, Any]],
    start: float,
    end: float,
    max_frames: int = 4,
    tolerance: float = 0.25,
) -> list[dict[str, Any]]:
    in_range = [dict(item) for item in candidates if start - tolerance <= float(item["time"]) <= end + tolerance]
    best_by_hash: dict[str, dict[str, Any]] = {}
    for item in in_range:
        if float(item.get("sharpness", 0.0)) < 5.0 or float(item.get("luma", 0.0)) < 8.0:
            continue
        key = str(item.get("phash") or item["path"])
        current = best_by_hash.get(key)
        if current is None or score_candidate(item) > score_candidate(current):
            best_by_hash[key] = item
    ranked = sorted(best_by_hash.values(), key=lambda item: (-score_candidate(item), float(item["time"])))[:max_frames]
    if not ranked:
        raise ValueError(f"no valid frame in segment {start:.3f}-{end:.3f}")
    return [
        {"time": float(item["time"]), "ocr": str(item.get("ocr", "")), "path": str(item["path"]).replace("\\", "/")}
        for item in sorted(ranked, key=lambda item: float(item["time"]))
    ]


def curate_lecture(
    source_path: Path,
    manifest_path: Path,
    output_path: Path,
    live_root: Path,
    staging_root: Path,
) -> dict[str, Any]:
    data = load_lecture(source_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    legacy = materialize_legacy_candidates(data, live_root, staging_root)
    candidates = merge_existing_candidates({"segments": []}, [*manifest["candidates"], *legacy])
    manifest["candidates"] = candidates
    write_json_atomic(manifest_path, manifest)
    for index, segment in enumerate(data["segments"]):
        segment["frames"] = curate_segment(candidates, segment_start(segment), segment_end(segment))
        if len(segment["frames"]) < 4:
            segment.setdefault("audit_notes", []).append({"code": "frame_below_target", "count": len(segment["frames"])})
    write_json_atomic(output_path, data)
    return data


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--live-root", type=Path, required=True)
    parser.add_argument("--staging-root", type=Path, required=True)
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args(argv)
    data = curate_lecture(args.source, args.manifest, args.output, args.live_root, args.staging_root)
    print(f"[curate] segments={len(data['segments'])} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Modify `slide_frames.py` so its public extraction result is a staging manifest. The core write path must be exactly this shape:

```python
from importlib.metadata import version as distribution_version


def build_candidate_manifest(
    video_name: str,
    detector_type: str,
    threshold: float | None,
    min_scene_len: float,
    candidates: list[dict[str, object]],
    scenedetect_version: str | None = None,
) -> dict[str, object]:
    installed = scenedetect_version or distribution_version("scenedetect")
    return {
        "schema_version": 1,
        "video": video_name,
        "detector": {
            "type": detector_type,
            "threshold": threshold,
            "min_scene_len": min_scene_len,
            "frame_skip": 0,
            "scenedetect_version": installed,
            "required_scenedetect": ">=0.6.4,<0.8",
        },
        "candidates": candidates,
    }

manifest = build_candidate_manifest(
    video_name=video_path.name,
    detector_type=detector_type,
    threshold=threshold,
    min_scene_len=min_scene_len,
    candidates=candidates,
)
write_json_atomic(staging_dir / "candidate_frames.json", manifest)
print(f"[extract] candidates={len(candidates)} staging={staging_dir}")
```

Remove the current block that directly merges every scene image into JSON `segments[].frames`. Add CLI option:

```python
parser.add_argument("--staging", type=Path, required=True, help="Same-filesystem staging directory")
```

For PySceneDetect, set parameters explicitly and preserve seconds from `FrameTimecode.get_seconds()`:

```python
sm.detect_scenes(video=video, frame_skip=0, show_progress=False)
out = [
    _mk((start_tc.get_seconds() + end_tc.get_seconds()) / 2.0)
    for start_tc, end_tc in sm.get_scene_list(start_in_scene=True)
]
if not out:
    out = [_mk(0.0)]
```

Modify `ocr_frames.py` to read and rewrite only `candidate_frames.json`:

```python
manifest_path = staging_dir / "candidate_frames.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
for item in manifest["candidates"]:
    item["ocr"] = ocr_one(engine, staging_dir / item["path"], min_conf)
write_json_atomic(manifest_path, manifest)
```

Replace `slide_frames.py:main()` completely; remove `--json`, `--json-out`, `--out-dir` and every cp950-unsafe arrow literal:

```python
def analyze_frame(path: Path) -> dict[str, object]:
    from PIL import Image, ImageStat
    with Image.open(path) as image:
        gray = image.convert("L").resize((64, 36))
        pixels = list(gray.getdata())
    mean = sum(pixels) / len(pixels)
    diffs = [pixels[index] - pixels[index - 1] for index in range(1, len(pixels))]
    sharpness = sum(value * value for value in diffs) / max(len(diffs), 1)
    digest = hashlib.sha256(bytes(pixels)).hexdigest()[:16]
    return {"luma": round(mean, 3), "sharpness": round(sharpness, 3), "phash": digest}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("video", type=Path)
    parser.add_argument("--staging", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--detector", choices=("adaptive", "content", "ffmpeg"), default="adaptive")
    parser.add_argument("--threshold", type=float)
    parser.add_argument("--min-scene-len", type=float, default=1.5)
    args = parser.parse_args(argv)
    if not args.video.is_file():
        print(f"ERROR: video not found {args.video}", file=sys.stderr)
        return 1
    frame_root = args.staging / "frames" / args.video.stem
    candidates = []
    scenes = detect_scenes(str(args.video), args.detector, args.threshold, args.min_scene_len)
    for index, scene in enumerate(scenes, 1):
        timestamp = float(scene["timestamp_sec"]) + 0.4
        relative = Path("frames") / args.video.stem / f"candidate-{index:04d}.jpg"
        output = args.staging / relative
        if not extract_frame(str(args.video), timestamp, str(output), args.width):
            raise RuntimeError(f"frame extraction failed at {timestamp:.3f}s")
        candidates.append({"time": timestamp, "path": relative.as_posix(), "ocr": "", **analyze_frame(output)})
        print(f"[extract] frame={index}/{len(scenes)} time={timestamp:.3f}")
    manifest = build_candidate_manifest(
        video_name=args.video.name,
        detector_type=args.detector,
        threshold=args.threshold,
        min_scene_len=args.min_scene_len,
        candidates=candidates,
    )
    write_json_atomic(args.staging / "candidate_frames.json", manifest)
    print(f"[extract] candidates={len(candidates)} staging={args.staging}")
    return 0
```

Replace `ocr_frames.py:main()` completely:

```python
def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--staging", type=Path, required=True)
    parser.add_argument("--min-conf", type=float, default=0.5)
    args = parser.parse_args(argv)
    manifest_path = args.staging / "candidate_frames.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    engine = load_engine()
    total = len(manifest["candidates"])
    for index, item in enumerate(manifest["candidates"], 1):
        item["ocr"] = ocr_one(engine, args.staging / item["path"], args.min_conf)
        print(f"[ocr] frame={index}/{total} chars={len(item['ocr'])}")
    write_json_atomic(manifest_path, manifest)
    print(f"[ocr] candidates={total} manifest={manifest_path}")
    return 0
```

Add `import hashlib` and `from lecture_model import write_json_atomic` to `slide_frames.py`; add `from lecture_model import write_json_atomic` to `ocr_frames.py`. Reuse the existing `load_engine()` and `ocr_one()` symbols exactly; do not add a second OCR initialization path.

- [ ] **Step 4: Run unit tests and CLI syntax checks**

Run:

```powershell
python -m unittest tests.test_lecture_frame_curator -v
python -m py_compile ".\skills\lecture-to-notes\scripts\slide_frames.py" ".\skills\lecture-to-notes\scripts\ocr_frames.py" ".\skills\lecture-to-notes\scripts\frame_curator.py"
```

Expected: tests PASS；all 72 legacy files exist under staging with hashes equal to live sources, the deduplicated pool still contains exactly 72 legacy candidates, and every curated chapter has 1–4 frames；`py_compile` exit code 0. Do not run video extraction in this step.

- [ ] **Step 5: Commit**

```powershell
git add -- "skills/lecture-to-notes/scripts/frame_curator.py" "skills/lecture-to-notes/scripts/slide_frames.py" "skills/lecture-to-notes/scripts/ocr_frames.py" "tests/test_lecture_frame_curator.py"
git commit -m "feat(lecture): stage and curate representative frames"
```

---

### Task 4: 正式 Rewrite CLI、Manual Review 與可選 Claude Structured Output

**Files:**
- Create: `skills/lecture-to-notes/scripts/rewrite_lecture.py`
- Create: `tests/test_lecture_rewrite.py`

**Interfaces:**
- Consumes: `evidence_packets.json`, reviewer-approved `rewrite_results.json`, optional official Anthropic SDK credential chain。
- Produces: `rewrite_manual(...)`, `rewrite_with_claude(...)`, `apply_rewrites(...)`; CLI `rewrite_lecture.py <lecture.json> --evidence <...> --provider manual|claude --review <...>`.

- [ ] **Step 1: Write failing tests for safe default and exact time preservation**

```python
# tests/test_lecture_rewrite.py
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "lecture-to-notes" / "scripts"))

from rewrite_lecture import apply_rewrites, require_external_llm_permission


class RewriteLectureTests(unittest.TestCase):
    def test_external_llm_requires_flag_confirmation_and_clean_full_payload(self):
        packet = {"sensitive_findings": [], "existing_content": {"title": "Synthetic"}}
        with self.assertRaisesRegex(PermissionError, "allow-external-llm"):
            require_external_llm_permission(packet, allow_external_llm=False, confirmation="TEXT-EVIDENCE-ONLY")
        with self.assertRaisesRegex(PermissionError, "confirmation"):
            require_external_llm_permission(packet, allow_external_llm=True, confirmation="")
        sensitive = {"sensitive_findings": [], "existing_content": {"title": "病歷號 12345678"}}
        with self.assertRaisesRegex(PermissionError, "sensitive"):
            require_external_llm_permission(sensitive, allow_external_llm=True, confirmation="TEXT-EVIDENCE-ONLY")

    def test_apply_rewrites_preserves_times_and_requires_review(self):
        source = {"segments": [{"start_sec": 1.0, "end_sec": 2.0, "title": "old", "frames": [{"time": 1.5, "ocr": "", "path": "frames/a.jpg"}]}]}
        rewritten = [{"title": "new", "summary_zh": "文" * 300, "takeaways_zh": ["一", "二", "三", "四"], "editorial_notes_zh": []}]
        reviews = [{"packet_sha256": "abc", "reviewer": "A80748", "source_faithful": True, "case_details_verified": True, "editorial_separated": True}]
        packets = [{"packet_sha256": "abc", "sensitive_findings": []}]
        result = apply_rewrites(source, packets, rewritten, reviews)
        self.assertEqual((result["segments"][0]["start_sec"], result["segments"][0]["end_sec"]), (1.0, 2.0))
        self.assertEqual(result["segments"][0]["title"], "new")
        self.assertEqual(result["segments"][0]["frames"], source["segments"][0]["frames"])
```

- [ ] **Step 2: Run and verify RED**

Run: `python -m unittest tests.test_lecture_rewrite -v`

Expected: FAIL because `rewrite_lecture` does not exist.

- [ ] **Step 3: Implement manual-first rewrite entry and external-call gate**

```python
# skills/lecture-to-notes/scripts/rewrite_lecture.py
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from lecture_content_rules import validate_segment_content
from lecture_model import assert_times_unchanged, load_lecture, write_json_atomic
from rewrite_evidence import contains_sensitive_data, validate_review_record


def require_external_llm_permission(
    packet: Mapping[str, Any],
    allow_external_llm: bool,
    confirmation: str,
) -> str:
    if not allow_external_llm:
        raise PermissionError("external rewrite requires --allow-external-llm")
    if confirmation != "TEXT-EVIDENCE-ONLY":
        raise PermissionError("external rewrite requires --confirm-external-llm TEXT-EVIDENCE-ONLY")
    outbound = json.dumps(packet, ensure_ascii=False, sort_keys=True)
    findings = sorted(set(packet.get("sensitive_findings", [])) | set(contains_sensitive_data(outbound)))
    if findings:
        raise PermissionError("external rewrite blocked by sensitive-data preflight: " + ",".join(findings))
    return hashlib.sha256(outbound.encode("utf-8")).hexdigest()


def apply_rewrites(
    source: Mapping[str, Any],
    packets: Sequence[Mapping[str, Any]],
    rewritten: Sequence[Mapping[str, Any]],
    reviews: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    if not (len(source["segments"]) == len(packets) == len(rewritten) == len(reviews)):
        raise ValueError("source, evidence, rewrite, and review counts must match")
    result = json.loads(json.dumps(source, ensure_ascii=False))
    for index, (packet, content, review) in enumerate(zip(packets, rewritten, reviews)):
        review_errors = [f for f in validate_review_record(packet, content, review) if f.severity == "error"]
        content_errors = [f for f in validate_segment_content(content, str(packet.get("transcript_text", ""))) if f.severity == "error"]
        if review_errors or content_errors:
            codes = [f.code for f in review_errors + content_errors]
            raise ValueError(f"segment {index} rewrite rejected: {','.join(codes)}")
        for field in ("title", "summary_zh", "takeaways_zh", "editorial_notes_zh"):
            result["segments"][index][field] = content[field]
    assert_times_unchanged(source, result)
    return result


def rewrite_with_claude(
    packet: Mapping[str, Any],
    allow_external_llm: bool,
    confirmation: str,
) -> dict[str, Any]:
    payload_sha256 = require_external_llm_permission(packet, allow_external_llm, confirmation)
    import anthropic
    client = anthropic.Anthropic()
    schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "summary_zh": {"type": "string"},
            "takeaways_zh": {"type": "array", "items": {"type": "string"}},
            "editorial_notes_zh": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["title", "summary_zh", "takeaways_zh", "editorial_notes_zh"],
        "additionalProperties": False,
    }
    prompt = (
        "依 evidence 產生繁體中文章節內容。summary 與 takeaways 只能陳述講者或 evidence 可確認內容；"
        "一般背景知識只能放 editorial_notes_zh；不得補造病例細節。輸出必須符合 schema。\n\n"
        + json.dumps(packet, ensure_ascii=False, sort_keys=True)
    )
    response = client.messages.create(
        model="claude-opus-5",
        max_tokens=16000,
        thinking={"type": "adaptive"},
        output_config={"effort": "high", "format": {"type": "json_schema", "schema": schema}},
        messages=[{"role": "user", "content": prompt}],
    )
    if response.stop_reason != "end_turn":
        request_id = getattr(response, "_request_id", "unknown")
        raise RuntimeError(f"rewrite model stopped with {response.stop_reason}; request_id={request_id}")
    text = next((block.text for block in response.content if block.type == "text"), None)
    if text is None:
        request_id = getattr(response, "_request_id", "unknown")
        raise RuntimeError(f"rewrite model returned no text block; request_id={request_id}")
    result = json.loads(text)
    result["_external_review_meta"] = {"provider": "claude", "payload_sha256": payload_sha256}
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("lecture", type=Path)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--rewrite", type=Path, required=True)
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--provider", choices=("manual", "claude"), default="manual")
    parser.add_argument("--allow-external-llm", action="store_true")
    parser.add_argument("--confirm-external-llm", default="")
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args()
    source = load_lecture(args.lecture)
    packets = json.loads(args.evidence.read_text(encoding="utf-8"))
    rewrites = json.loads(args.rewrite.read_text(encoding="utf-8"))
    reviews = json.loads(args.review.read_text(encoding="utf-8"))
    if args.provider == "claude":
        rewrites = [rewrite_with_claude(packet, args.allow_external_llm, args.confirm_external_llm) for packet in packets]
        write_json_atomic(args.rewrite, rewrites)
        raise SystemExit("Claude output generated; complete human review records before applying")
    write_json_atomic(args.output, apply_rewrites(source, packets, rewrites, reviews))
    print(f"[rewrite] segments={len(rewrites)} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

The provider `manual` remains the production default. `claude` only generates a review candidate; it never directly publishes canonical JSON. The SDK constructor must remain zero-argument so credentials come from environment/profile resolution and never from source code.

- [ ] **Step 4: Run tests and import check**

Run:

```powershell
python -m unittest tests.test_lecture_rewrite -v
python -m py_compile ".\skills\lecture-to-notes\scripts\rewrite_lecture.py"
```

Expected: tests PASS and syntax check exit 0 without making a network request.

- [ ] **Step 5: Commit**

```powershell
git add -- "skills/lecture-to-notes/scripts/rewrite_lecture.py" "tests/test_lecture_rewrite.py"
git commit -m "feat(lecture): add reviewed rewrite workflow"
```

---

### Task 5: 詳細型 Viewer、2x2/768px、Modal/Seek 與 Typed Search

**Files:**
- Modify: `skills/lecture-to-notes/scripts/build_lecture_viewer.py:build_blocks(), render(), main()`
- Create: `tests/test_lecture_renderers.py`

**Interfaces:**
- Consumes: normalized canonical JSON plus SRT/video paths；`media_dir` is always a resolved `Path`, never a string and never a second segment data source。
- Produces: `parse_srt_text(text: str) -> list[dict[str, Any]]`, `load_srt(path: Path) -> list[dict[str, Any]]`, `build_blocks(data: Mapping[str, Any], cues: Sequence[Mapping[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]` and final `render(data: Mapping[str, Any], cues: Sequence[Mapping[str, Any]], title: str, video_rel: str, media_dir: Path) -> str`。`load_srt()` 是唯一接受 `Path` 的 UTF-8-SIG wrapper，且只呼叫 `parse_srt_text()`；其他模組不得把 `Path` 傳給 text parser。`main(argv=None) -> int` loads/normalizes once, loads SRT once, derives `video_rel`, passes exactly those five arguments to `render()`, and writes its returned HTML；舊的 `segments` positional argument與任何 parallel media list 必須刪除。
- HTML contains `.frame-grid`, `.frame-card`, `.editorial-note`, populated transcript/OCR `<details>`, source-tagged search entries, `#canonical-snapshot`, retained `?t=<seconds>` deep links and stable chapter hashes。Every `application/json` script uses raw JSON text from `json.dumps(..., ensure_ascii=False).replace("</", "<\\/")`，不得使用 `html.escape()`。

- [ ] **Step 1: Write failing renderer contract tests**

```python
# tests/test_lecture_renderers.py
import importlib.util
import inspect
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
VIEWER = ROOT / "skills" / "lecture-to-notes" / "scripts" / "build_lecture_viewer.py"

spec = importlib.util.spec_from_file_location("build_lecture_viewer", VIEWER)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class LectureRendererTests(unittest.TestCase):
    def test_viewer_contains_required_content_and_only_formal_frames(self):
        data = {"segments": [{
            "start_sec": 0.0,
            "end_sec": 10.0,
            "title": "Glioblastoma imaging features",
            "summary_zh": "第一段。\n\n第二段。",
            "takeaways_zh": ["A", "B", "C", "D"],
            "editorial_notes_zh": ["補充"],
            "frames": [{"time": 2.5, "ocr": "OCR", "path": "frames/a.jpg"}],
        }]}
        html = module.render(data, [], "Lecture", "video.mp4", Path(".").resolve())
        self.assertIn('class="frame-grid"', html)
        self.assertIn('data-frame-time="2.500"', html)
        self.assertIn('class="editorial-note"', html)
        self.assertIn('<details class="transcript-details">', html)
        self.assertIn('<details class="ocr-details">', html)
        self.assertNotIn("candidate_frames", html)

    def test_css_has_exact_responsive_boundary(self):
        html = module.render({"segments": []}, [], "Lecture", "video.mp4", Path(".").resolve())
        self.assertIn("grid-template-columns:repeat(2,minmax(0,1fr))", html.replace(" ", ""))
        self.assertIn("@media(max-width:768px)", html.replace(" ", ""))
        self.assertIn("grid-template-columns:1fr", html.replace(" ", ""))

    def test_application_json_is_raw_parseable_and_script_close_safe(self):
        hostile = "</script><img src=x onerror=alert(1)> & quoted"
        data = {"segments": [{
            "start_sec": 0.0, "end_sec": 10.0, "title": hostile,
            "summary_zh": "摘要", "takeaways_zh": ["A", "B", "C", "D"],
            "editorial_notes_zh": [],
            "frames": [{"time": 2.5, "ocr": hostile, "path": "frames/a.jpg"}],
        }]}
        rendered = module.render(data, [], "Lecture", "video.mp4", Path(".").resolve())
        for script_id in ("canonical-snapshot", "search-data"):
            match = re.search(
                rf'<script id="{script_id}" type="application/json">(.*?)</script>',
                rendered,
                re.DOTALL,
            )
            self.assertIsNotNone(match)
            payload = match.group(1)
            self.assertNotIn("</script", payload.casefold())
            self.assertNotIn("&quot;", payload)
            json.loads(payload)

    def test_srt_text_and_path_contracts_are_unambiguous(self):
        text = "1\n00:00:00,000 --> 00:00:01,000\nCue\n"
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "lecture.srt"
            path.write_text(text, encoding="utf-8-sig")
            with patch.object(module, "parse_srt_text", wraps=module.parse_srt_text) as parser:
                cues = module.load_srt(path)
        parser.assert_called_once_with(text)
        self.assertEqual(cues, [{"start": 0.0, "end": 1.0, "text": "Cue"}])
        with self.assertRaises(TypeError):
            module.parse_srt_text(path)

    def test_main_uses_one_load_one_parse_one_build_and_five_argument_render(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); source = root / "lecture.json"; srt = root / "lecture.srt"
            video = root / "lecture.mp4"; output = root / "viewer.html"
            source.write_text("{}", encoding="utf-8")
            srt.write_text("1\n00:00:00,000 --> 00:00:01,000\nCue\n", encoding="utf-8")
            video.write_bytes(b"video")
            data = {"title": "Lecture", "segments": []}
            cues = [{"start": 0.0, "end": 1.0, "text": "Cue"}]
            with (
                patch.object(module, "load_lecture", return_value=data) as lecture_loader,
                patch.object(module, "load_srt", return_value=cues) as srt_loader,
                patch.object(module, "build_blocks", return_value=([], [])) as block_builder,
                patch.object(module, "render", wraps=module.render) as render_spy,
            ):
                exit_code = module.main([
                    str(source), "--video", str(video), "--srt", str(srt), "-o", str(output),
                ])
                output_text = output.read_text(encoding="utf-8")
        self.assertEqual(exit_code, 0)
        lecture_loader.assert_called_once_with(source)
        srt_loader.assert_called_once_with(srt)
        block_builder.assert_called_once_with(data, cues)
        self.assertEqual(len(render_spy.call_args.args), 5)
        self.assertEqual(render_spy.call_args.args[:2], (data, cues))
        self.assertIsInstance(render_spy.call_args.args[4], Path)
        self.assertEqual(render_spy.call_args.args[4], source.parent.resolve())
        self.assertEqual(
            list(inspect.signature(module.render).parameters),
            ["data", "cues", "title", "video_rel", "media_dir"],
        )
        self.assertIn("<html", output_text.casefold())
```

- [ ] **Step 2: Run and verify RED**

Run: `python -m unittest tests.test_lecture_renderers.LectureRendererTests -v`

Expected: FAIL because current viewer lacks frame-object handling/required classes, still HTML-escapes `application/json`, and does not expose the exact five-argument `render()` plus single-flow `main()` contract。

- [ ] **Step 3: Replace old summary-block rendering with explicit chapter markup**

In `render()`, generate every segment with this exact structure:

```python
# final signatures and call chain in skills/lecture-to-notes/scripts/build_lecture_viewer.py
import argparse
import html
import json
import os
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from lecture_model import load_lecture, segment_end, segment_start


SRT_TIMING_RE = re.compile(
    r"^(?P<start>\d{2}:\d{2}:\d{2}[,.]\d{3})\s+-->\s+(?P<end>\d{2}:\d{2}:\d{2}[,.]\d{3})$"
)


def _srt_seconds(value: str) -> float:
    hours, minutes, rest = value.replace(",", ".").split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(rest)


def parse_srt_text(text: str) -> list[dict[str, Any]]:
    if not isinstance(text, str):
        raise TypeError("parse_srt_text requires str")
    cues: list[dict[str, Any]] = []
    for block in re.split(r"\r?\n\s*\r?\n", text.strip()):
        lines = [line.strip() for line in block.splitlines()]
        timing_index = next((index for index, line in enumerate(lines) if SRT_TIMING_RE.fullmatch(line)), None)
        if timing_index is None:
            continue
        match = SRT_TIMING_RE.fullmatch(lines[timing_index])
        assert match is not None
        cue_text = "\n".join(lines[timing_index + 1:]).strip()
        cues.append({
            "start": _srt_seconds(match.group("start")),
            "end": _srt_seconds(match.group("end")),
            "text": cue_text,
        })
    return cues


def load_srt(path: Path) -> list[dict[str, Any]]:
    if not isinstance(path, Path):
        raise TypeError("load_srt requires pathlib.Path")
    return parse_srt_text(path.read_text(encoding="utf-8-sig"))


def format_time(seconds: float) -> str:
    value = max(0, int(seconds))
    return f"{value // 60:02d}:{value % 60:02d}"


def json_script_payload(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def build_blocks(
    data: Mapping[str, Any],
    cues: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    segs: list[dict[str, Any]] = []
    blocks: list[dict[str, Any]] = []
    for index, segment in enumerate(data.get("segments", [])):
        sid = f"s{int(segment.get('index', index + 1))}"
        start, end = segment_start(segment), segment_end(segment)
        segs.append({"id": sid, "index": index, "title": segment["title"], "start": start, "end": end, "frames": segment["frames"]})
        blocks.extend([
            {"id": f"{sid}-title", "seg": sid, "kind": "title", "label": "章節標題", "start": start, "end": end, "text": segment["title"], "est": False},
            {"id": f"{sid}-summary", "seg": sid, "kind": "summary", "label": "整理稿", "start": start, "end": end, "text": segment["summary_zh"], "est": False},
        ])
        for item_index, item in enumerate(segment["takeaways_zh"]):
            blocks.append({"id": f"{sid}-takeaway-{item_index}", "seg": sid, "kind": "takeaway", "label": "核心重點", "start": start, "end": end, "text": item, "est": False})
        for item_index, item in enumerate(segment["editorial_notes_zh"]):
            blocks.append({"id": f"{sid}-editorial-{item_index}", "seg": sid, "kind": "editorial", "label": "編輯補充", "start": start, "end": end, "text": item, "est": False})
        for frame_index, frame in enumerate(segment["frames"]):
            blocks.append({"id": f"{sid}-ocr-{frame_index}", "seg": sid, "kind": "slide", "label": "OCR", "start": frame["time"], "end": frame["time"] + 1.0, "text": frame["ocr"], "est": False})
    for cue_index, cue in enumerate(cues):
        seg = next((item for item in segs if item["start"] <= cue["start"] < item["end"]), None)
        if seg is not None:
            blocks.append({"id": f"transcript-{cue_index}", "seg": seg["id"], "kind": "transcript", "label": "逐字稿", "start": cue["start"], "end": cue["end"], "text": cue["text"], "est": False})
    return segs, blocks


def render_segment(segment: Mapping[str, Any], segment_index: int, segment_blocks: Sequence[Mapping[str, Any]]) -> str:
    escape = html.escape
    s0, s1 = segment_start(segment), segment_end(segment)
    paragraphs = "".join(f"<p>{escape(part)}</p>" for part in segment["summary_zh"].split("\n\n") if part.strip())
    takeaways = "".join(f"<li>{escape(item)}</li>" for item in segment["takeaways_zh"])
    frames = "".join(
        f'''<button class="frame-card" data-frame-time="{frame['time']:.3f}" data-full-src="{escape(frame['path'])}">
<img src="{escape(frame['path'])}" alt="{escape(frame['ocr'] or segment['title'])}" loading="lazy">
<span>{format_time(frame['time'])}</span>
</button>'''
        for frame in segment["frames"]
    )
    editorial = ""
    if segment["editorial_notes_zh"]:
        items = "".join(f"<li>{escape(item)}</li>" for item in segment["editorial_notes_zh"])
        editorial = f'<aside class="editorial-note"><h3>編輯補充</h3><ul>{items}</ul></aside>'
    transcript = "".join(
        f'<button class="transcript-cue" data-time="{block["start"]:.3f}" data-end="{block["end"]:.3f}"><span>{format_time(block["start"])}</span>{escape(block["text"])}</button>'
        for block in segment_blocks if block["kind"] == "transcript"
    )
    ocr = "".join(
        f'<button class="ocr-hit" data-time="{frame["time"]:.3f}">{escape(frame["ocr"] or "無可辨識文字")}</button>'
        for frame in segment["frames"]
    )
    stable_id = f"chapter-{segment_index + 1:02d}-{round(s0 * 1000)}"
    return f'''<article id="{stable_id}" class="chapter" data-start="{s0}" data-end="{s1}">
<h2>{escape(segment['title'])}</h2>
<div class="summary">{paragraphs}</div>
<ol class="takeaways">{takeaways}</ol>
<div class="frame-grid">{frames}</div>
{editorial}
<details class="transcript-details"><summary>逐字稿</summary>{transcript}</details>
<details class="ocr-details"><summary>OCR</summary>{ocr}</details>
</article>'''


def canonical_snapshot(data: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {"index": int(segment.get("index", index + 1)), "start_sec": segment_start(segment), "end_sec": segment_end(segment), "title": segment["title"]}
        for index, segment in enumerate(data["segments"])
    ]


def render(
    data: Mapping[str, Any],
    cues: Sequence[Mapping[str, Any]],
    title: str,
    video_rel: str,
    media_dir: Path,
) -> str:
    if not isinstance(media_dir, Path) or not media_dir.is_absolute():
        raise TypeError("media_dir must be an absolute pathlib.Path")
    segs, blocks = build_blocks(data, cues)
    by_segment = {segment["id"]: [] for segment in segs}
    for block in blocks:
        by_segment.setdefault(block["seg"], []).append(block)
    chapters_html = "".join(
        render_segment(segment, index, by_segment.get(f"s{int(segment.get('index', index + 1))}", []))
        for index, segment in enumerate(data["segments"])
    )
    snapshot_json = json_script_payload(canonical_snapshot(data))
    search_json = json_script_payload(blocks)
    data_json = json_script_payload({"segments": segs, "blocks": blocks})
    snapshot_tag = f'<script id="canonical-snapshot" type="application/json">{snapshot_json}</script>'
    modal_html = '''<dialog id="frame-modal"><button id="modal-close" aria-label="關閉">關閉</button><img id="modal-image" alt=""><button id="modal-seek">跳至影片時間</button></dialog>'''
    nav_html = "".join(
        f'<button class="segcard" data-seg="{segment["id"]}" data-t="{segment["start"]}"><b>{segment["index"] + 1}</b>{html.escape(segment["title"])}</button>'
        for segment in segs
    )
    return f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>{CSS}</style></head>
<body><header><h1>{html.escape(title)}</h1><button data-mode="split">雙欄</button><button data-mode="sum">整理稿</button><button data-mode="tr">逐字稿</button><button id="autoscroll">自動捲動</button><button id="float">浮動播放器</button><button id="zin">放大</button><button id="zout">縮小</button><div class="search"><input id="q" aria-label="全文搜尋"><div id="results"></div></div></header>
<main><section id="vpane"><video id="player" controls preload="metadata" src="{html.escape(video_rel)}"></video><div id="now"></div><nav id="segnav">{nav_html}</nav></section><div id="vsplit"></div><section id="notes"><div id="spane" class="pane">{chapters_html}</div><div id="hsplit"></div><div id="tpane" class="pane"></div></section></main>
{modal_html}{snapshot_tag}<script id="search-data" type="application/json">{search_json}</script><script>const DATA={data_json};{JS}</script></body></html>'''


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--srt", type=Path, required=True)
    parser.add_argument("--title")
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args(argv)
    data = load_lecture(args.source)
    cues = load_srt(args.srt)
    media_dir = args.source.parent.resolve()
    video_rel = os.path.relpath(args.video.resolve(), args.output.parent.resolve()).replace("\\", "/")
    rendered = render(data, cues, args.title or str(data.get("title", args.source.stem)), video_rel, media_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8", newline="\n")
    return 0
```

Add exact CSS contracts:

```css
.frame-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.frame-card{display:flex;min-width:0;aspect-ratio:16/9;padding:0;overflow:hidden;background:#111;border:1px solid #52606d;border-radius:8px;position:relative}
.frame-card img{width:100%;height:100%;object-fit:contain;background:#000}
.frame-card span{position:absolute;right:6px;bottom:6px;background:rgba(0,0,0,.78);color:#fff;padding:2px 6px;border-radius:4px}
.editorial-note{border-left:4px solid #c98a22;background:#fff8e8;padding:12px 16px;margin-top:16px}
@media(max-width:768px){.frame-grid{grid-template-columns:1fr}.frame-card{width:100%}}
```

Add modal and seek behavior:

```javascript
const video=document.getElementById('player');
const modal=document.getElementById('frame-modal');
const modalImage=document.getElementById('modal-image');
const modalSeek=document.getElementById('modal-seek');
function seekTo(seconds){const value=Number(seconds);video.currentTime=value;activateChapterForTime(value);video.play().catch(()=>{});}
function closeModal(){if(modal.open)modal.close();}
document.addEventListener('click',event=>{
  const timed=event.target.closest('.transcript-cue,.ocr-hit');
  if(timed){seekTo(timed.dataset.time);return;}
  const card=event.target.closest('.frame-card');
  if(!card)return;
  modalImage.src=card.dataset.fullSrc;
  modalSeek.dataset.time=card.dataset.frameTime;
  modal.showModal();
});
document.getElementById('modal-close').addEventListener('click',closeModal);
modalSeek.addEventListener('click',()=>{seekTo(modalSeek.dataset.time);closeModal();});
modal.addEventListener('click',event=>{if(event.target===modal)closeModal();});
document.addEventListener('keydown',event=>{if(event.key==='Escape')closeModal();});
```

`build_blocks()` returned `blocks` is the only search index；不得建立 `search_entries` or a second schema。Every search object uses the already-defined fields `kind`, `label`, `start`, `end`, `text`，and `render()` serializes that exact `blocks` list into `#search-data`。Title、summary、takeaway、editorial、slide OCR and transcript entries are all created in the complete `build_blocks()` implementation above。

Use this result row in the retained JavaScript `search()` function:

```javascript
return '<button class="sr" data-t="'+b.start+'"><span class="k">'+esc(b.label)+'</span><span class="t">'+t+'</span><span class="ts">'+fmt(b.start)+'</span></button>';
```

Keep the existing click handler `seek(Number(el.dataset.t))`; every result now identifies its source and navigates to its exact chapter/time.

Preserve old `?t=<seconds>` behavior and add stable chapter mapping without changing time ranges:

```javascript
function activateChapterForTime(seconds){
  const chapter=[...document.querySelectorAll('.chapter')].find(item=>Number(item.dataset.start)<=seconds&&seconds<Number(item.dataset.end));
  document.querySelectorAll('.chapter,.segcard').forEach(item=>item.classList.remove('on'));
  if(!chapter)return;
  chapter.classList.add('on');
  const card=document.querySelector(`.segcard[data-t="${chapter.dataset.start}"]`);
  if(card)card.classList.add('on');
}
function activateTranscriptForTime(seconds){
  const cues=[...document.querySelectorAll('.transcript-cue')];
  cues.forEach(item=>item.classList.remove('on'));
  const active=cues.find(item=>Number(item.dataset.time)<=seconds&&seconds<Number(item.dataset.end));
  if(active)active.classList.add('on');
}
video.addEventListener('timeupdate',()=>{
  activateChapterForTime(video.currentTime);
  activateTranscriptForTime(video.currentTime);
});
const params=new URLSearchParams(location.search);
const requested=Number(params.get('t'));
if(Number.isFinite(requested)){seekTo(requested);}
if(location.hash.startsWith('#chapter-')){
  const target=document.querySelector(location.hash);
  if(target){seekTo(Number(target.dataset.start));target.scrollIntoView({block:'start'});}
}
```

- [ ] **Step 4: Run renderer tests and compile**

Run:

```powershell
python -m unittest tests.test_lecture_renderers.LectureRendererTests -v
python -m py_compile ".\skills\lecture-to-notes\scripts\build_lecture_viewer.py"
```

Expected: tests PASS and syntax check exit 0.

- [ ] **Step 5: Commit**

```powershell
git add -- "skills/lecture-to-notes/scripts/build_lecture_viewer.py" "tests/test_lecture_renderers.py"
git commit -m "feat(lecture): render detailed responsive viewer"
```

---

### Task 6: `.v4.md`、PBF、Course Hub 與 JSON 同源渲染

**Files:**
- Create: `skills/lecture-to-notes/scripts/render_v4_note.py`
- Modify: `skills/lecture-to-notes/scripts/json_to_pbf.py:json_to_pbf_lines(), convert_one()`
- Modify: `skills/lecture-to-notes/scripts/build_course_hub.py:collect(), build_index(), render()`
- Modify: `tests/test_lecture_renderers.py`

**Interfaces:**
- Consumes: normalized canonical JSON only。
- Produces: `render_v4(data) -> str`, `json_to_pbf_lines(data) -> list[str]`, hub lecture records containing `lecture_number`, `status`, `title`, `viewer`, `summary`，以及 `build_index(items) -> list[dict]`。Hub 與 lecture viewer 共用唯一 semantic search contract：每筆至少有 `kind`, `label`, `start`, `end`, `text`；hub-specific metadata 只能使用明確欄位 `viewer`, `lecture_id`, `lecture_number`，不得使用縮寫 key 或另一套 type/time schema。

- [ ] **Step 1: Add failing V4/PBF/hub consistency tests**

```python
# append to tests/test_lecture_renderers.py
class DerivedRendererTests(unittest.TestCase):
    def setUp(self):
        self.data = {"title": "Synthetic", "segments": [{
            "start_sec": 1.0, "end_sec": 2.0, "title": "Glioblastoma imaging features",
            "summary_zh": "整理稿", "takeaways_zh": ["A", "B", "C", "D"],
            "editorial_notes_zh": ["補充"],
            "frames": [{"time": 1.5, "ocr": "OCR", "path": "frames/a.jpg"}],
        }]}

    def test_v4_contains_all_canonical_content(self):
        from render_v4_note import render_v4
        text = render_v4(self.data)
        for expected in ("Glioblastoma imaging features", "整理稿", "A", "B", "C", "D", "編輯補充", "補充", "frames/a.jpg"):
            self.assertIn(expected, text)

    def test_pbf_uses_same_title_and_start(self):
        from json_to_pbf import json_to_pbf_lines
        lines = json_to_pbf_lines(self.data)
        self.assertTrue(any("Glioblastoma imaging features" in line and "1" in line for line in lines))
```

- [ ] **Step 2: Run and verify RED**

Run: `python -m unittest tests.test_lecture_renderers.DerivedRendererTests -v`

Expected: FAIL because `render_v4_note` does not exist or old PBF assumptions fail.

- [ ] **Step 3: Implement deterministic V4 renderer and normalize other renderers**

```python
# skills/lecture-to-notes/scripts/render_v4_note.py
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Mapping

from lecture_model import load_lecture


def render_v4(data: Mapping[str, Any]) -> str:
    lines = [f"# {data.get('title', 'Lecture')}", ""]
    for index, segment in enumerate(data["segments"], 1):
        lines.extend([f"## {index}. {segment['title']}", "", segment["summary_zh"], "", "### 核心重點"])
        lines.extend(f"- {item}" for item in segment["takeaways_zh"])
        if segment["editorial_notes_zh"]:
            lines.extend(["", "> [!note] 編輯補充"])
            lines.extend(f"> - {item}" for item in segment["editorial_notes_zh"])
        lines.extend(["", "### 代表影格"])
        lines.extend(f"![[{frame['path']}]] <!-- {frame['time']:.3f}s -->" for frame in segment["frames"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("json", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()
    output = args.output or args.json.with_suffix(".v4.md")
    output.write_text(render_v4(load_lecture(args.json)), encoding="utf-8", newline="\n")
    print(f"[render-v4] output={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Replace `json_to_pbf.py:convert_one()` with this normalized implementation and add `from lecture_model import load_lecture`:

```python
def convert_one(json_path: Path, out: Path | None, bom: bool) -> str | None:
    try:
        data = load_lecture(json_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return f"[skip] {json_path.name} parse failed: {exc}"
    if not data.get("segments"):
        return f"[skip] {json_path.name} has no segments"
    if out is None:
        out_stem, note = match_video_stem(json_path)
        out = json_path.parent / (out_stem + ".pbf")
    else:
        note = "explicit output"
    text = "\n".join(json_to_pbf_lines(data)) + "\n"
    out.write_text(text, encoding="utf-8-sig" if bom else "utf-8", newline="\n")
    return f"[ok] {out.name} chapters={len(data['segments'])} source={note}"
```

The complete `build_course_hub.py:collect()` replacement below constructs the search text; no second search-index builder may maintain chapter content independently.

Replace `collect()` with a recursive implementation that works for both formal flat roots and per-lecture staging directories, while emitting final flat viewer links:

```python
from lecture_model import load_lecture, segment_end, segment_start


def formal_json_paths(folder: Path) -> list[Path]:
    course_run = folder / "course-run.json"
    if course_run.is_file():
        report = json.loads(course_run.read_text(encoding="utf-8"))
        return [Path(item["outputs"]["formal_json"]) for item in report["lectures"] if item.get("status") == "complete"]
    excluded = (".frames.json", ".frames_ocr.json", ".audit.json")
    return [
        path for path in sorted(folder.glob("*.json"))
        if not path.name.startswith("_") and not path.name.endswith(excluded)
        and path.name not in {"course-run.json", "preflight.json", "course.audit.json"}
    ]


def collect(folder: Path) -> list[dict]:
    items = []
    titles = load_titles(folder)
    for json_path in formal_json_paths(folder):
        data = load_lecture(json_path)
        stem = json_path.stem
        viewer = json_path.with_name(stem + ".viewer.html")
        pbf = json_path.with_name(stem + ".pbf")
        v4 = json_path.with_name(stem + ".v4.md")
        audit = json_path.with_name(stem + ".audit.json")
        audit_data = json.loads(audit.read_text(encoding="utf-8")) if audit.is_file() else {"ok": False}
        status = "complete" if viewer.is_file() and pbf.is_file() and v4.is_file() and audit_data.get("ok") is True else "blocked"
        no, speaker, topic = parse_name(stem)
        override = titles.get(stem) or {}
        no, speaker, topic = override.get("lecture_number", no), override.get("speaker", speaker), override.get("topic", topic)
        frames = [frame for segment in data["segments"] for frame in segment["frames"]]
        items.append({
            "lecture_id": str(data.get("lecture_id", no or stem.split()[0])),
            "lecture_number": no, "speaker": speaker, "topic": topic, "stem": stem,
            "title": str(data.get("title", topic or stem)), "viewer": viewer.name,
            "segments": data["segments"], "frames": frames,
            "thumb": frames[0]["path"] if frames else None,
            "minutes": round(segment_end(data["segments"][-1]) / 60),
            "summary": str(data.get("overall_summary_zh", ""))[:150],
            "takeaways": list(data.get("takeaways_zh", [])),
            "status": status,
        })
    return sorted(items, key=lambda item: (item["lecture_number"] or "zz", item["stem"]))


def build_index(items: list[dict]) -> list[dict]:
    index = []
    for lecture in items:
        metadata = {
            "viewer": lecture["viewer"],
            "lecture_id": lecture["lecture_id"],
            "lecture_number": lecture["lecture_number"],
        }
        for item in lecture["takeaways"]:
            index.append({
                **metadata, "kind": "takeaway", "label": "全片重點",
                "start": 0.0, "end": 0.0, "text": str(item),
            })
        for segment in lecture["segments"]:
            start = segment_start(segment)
            end = segment_end(segment)
            fields = [
                ("title", "章節標題", segment["title"]),
                ("summary", "整理稿", segment["summary_zh"]),
            ]
            fields.extend(("takeaway", "核心重點", item) for item in segment["takeaways_zh"])
            fields.extend(("editorial", "編輯補充", item) for item in segment["editorial_notes_zh"])
            for kind, label, text in fields:
                index.append({
                    **metadata, "kind": kind, "label": label,
                    "start": start, "end": end, "text": str(text),
                })
            for frame in segment["frames"]:
                if frame["ocr"].strip():
                    frame_time = float(frame["time"])
                    index.append({
                        **metadata, "kind": "slide", "label": "OCR",
                        "start": frame_time, "end": frame_time + 1.0, "text": frame["ocr"],
                    })
    return index


def require_complete_course(items: list[dict], expected_count: int = 11) -> None:
    if len(items) != expected_count or len({item["lecture_id"] for item in items}) != expected_count:
        raise ValueError(f"course homepage requires {expected_count} unique lectures")
    blocked = [item["lecture_id"] for item in items if item["status"] != "complete"]
    if blocked:
        raise ValueError(f"course homepage blocked by lectures: {blocked}")

# In main():
parser.add_argument("--require-complete", type=int)
items = collect(folder)
if args.require_complete is not None:
    require_complete_course(items, args.require_complete)
index = build_index(items)
output.write_text(render(items, index, args.title), encoding="utf-8", newline="\n")
```

In `build_course_hub.py:render()`, serialize `index` unchanged, render lecture cards from `lecture_number`（not an abbreviated metadata key）, and make every search property access use the same semantic fields。The retained result-row helper must use this exact contract:

```javascript
function hubResultRow(entry){
  const href=entry.viewer+'?t='+encodeURIComponent(entry.start);
  return '<a class="hub-search-result" href="'+esc(href)+'"><span class="kind">'+esc(entry.label)+'</span><span class="text">'+esc(entry.text)+'</span></a>';
}
```

Append this exact hub isolation/gate test to `tests/test_lecture_renderers.py`:

```python
    def test_hub_collects_only_course_run_formal_outputs_and_enforces_count_and_status(self):
        import json
        import tempfile
        from build_course_hub import build_index, collect, require_complete_course
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); lecture_root = root / "01"; lecture_root.mkdir()
            formal = lecture_root / "01 Synthetic.json"
            data = {
                "lecture_id": "01", "title": "Synthetic", "overall_summary_zh": "全課摘要",
                "takeaways_zh": ["全課重點"],
                "segments": [{
                    "start_sec": 1.0, "end_sec": 2.0, "title": "Glioblastoma imaging features",
                    "summary_zh": "整理稿", "takeaways_zh": ["A", "B", "C", "D"],
                    "editorial_notes_zh": ["編輯補充"],
                    "frames": [{"time": 1.5, "ocr": "OCR text", "path": "frames/a.jpg"}],
                }],
            }
            formal.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            for suffix in ("viewer.html", "pbf", "v4.md"):
                formal.with_name(f"{formal.stem}.{suffix}").write_text("derived", encoding="utf-8")
            formal.with_name(f"{formal.stem}.audit.json").write_text('{"ok":true}', encoding="utf-8")
            for name in ("curated.json", "rewritten.json", "evidence_packets.json", "review_records.json"):
                (lecture_root / name).write_text("{}", encoding="utf-8")
            (root / "course-run.json").write_text(json.dumps({"lectures": [{"status": "complete", "outputs": {"formal_json": str(formal)}}]}), encoding="utf-8")
            items = collect(root)
            self.assertEqual([item["lecture_id"] for item in items], ["01"])
            self.assertEqual(items[0]["viewer"], "01 Synthetic.viewer.html")
            self.assertEqual(items[0]["lecture_number"], "01")
            search_index = build_index(items)
            labels = {entry["label"] for entry in search_index}
            self.assertTrue({"全片重點", "章節標題", "整理稿", "核心重點", "編輯補充", "OCR"}.issubset(labels))
            expected_keys = {"kind", "label", "start", "end", "text", "viewer", "lecture_id", "lecture_number"}
            self.assertTrue(all(set(entry) == expected_keys for entry in search_index))
            with self.assertRaisesRegex(ValueError, "2 unique"):
                require_complete_course(items, expected_count=2)
            items[0]["status"] = "blocked"
            with self.assertRaisesRegex(ValueError, "blocked"):
                require_complete_course(items, expected_count=1)
```

- [ ] **Step 4: Run tests**

Run:

```powershell
python -m unittest tests.test_lecture_renderers -v
python -m py_compile ".\skills\lecture-to-notes\scripts\render_v4_note.py" ".\skills\lecture-to-notes\scripts\json_to_pbf.py" ".\skills\lecture-to-notes\scripts\build_course_hub.py"
```

Expected: PASS and syntax exit 0.

- [ ] **Step 5: Commit**

```powershell
git add -- "skills/lecture-to-notes/scripts/render_v4_note.py" "skills/lecture-to-notes/scripts/json_to_pbf.py" "skills/lecture-to-notes/scripts/build_course_hub.py" "tests/test_lecture_renderers.py"
git commit -m "feat(lecture): derive notes bookmarks and hub from JSON"
```

---

### Task 7: Structured Audit 與跨衍生檔一致性

**Files:**
- Create: `skills/lecture-to-notes/scripts/lecture_audit.py`
- Modify: `skills/lecture-to-notes/scripts/check_lecture.py:main()`
- Create: `tests/test_lecture_audit.py`

**Interfaces:**
- Consumes: canonical JSON、viewer HTML、PBF、V4、course metadata、optional browser result。
- Produces: `AuditReport`, `audit_lecture(...) -> AuditReport`, `compare_derived(...) -> list[Finding]`, report JSON with lecture/stage/errors/warnings/input hashes.

- [ ] **Step 1: Write failing structured audit tests**

```python
# tests/test_lecture_audit.py
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "lecture-to-notes" / "scripts"))

from lecture_audit import audit_lecture


class LectureAuditTests(unittest.TestCase):
    def test_zero_frame_and_v4_title_mismatch_are_errors(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            data = {"title": "L", "segments": [{
                "start_sec": 0.0, "end_sec": 1.0, "title": "Glioblastoma imaging features",
                "summary_zh": "文" * 300, "takeaways_zh": ["A", "B", "C", "D"],
                "editorial_notes_zh": [], "frames": [],
            }]}
            (root / "lecture.v4.md").write_text("# L\n## Wrong\n", encoding="utf-8")
            report = audit_lecture(data, root, v4_path=root / "lecture.v4.md")
        codes = {f.code for f in report.findings}
        self.assertTrue({"frame_count", "v4_content_mismatch"}.issubset(codes))
        self.assertFalse(report.ok)

    def test_one_to_three_frames_are_warning_not_error(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "frames").mkdir()
            (root / "frames" / "a.jpg").write_bytes(b"x")
            data = {"segments": [{
                "start_sec": 0.0, "end_sec": 1.0, "title": "Glioblastoma imaging features",
                "summary_zh": "文" * 300, "takeaways_zh": ["A", "B", "C", "D"],
                "editorial_notes_zh": [],
                "frames": [{"time": 0.5, "ocr": "", "path": "frames/a.jpg"}],
            }]}
            report = audit_lecture(data, root)
        self.assertTrue(report.ok)
        self.assertIn("frame_below_target", {f.code for f in report.findings})

    def test_viewer_snapshot_audit_parses_raw_json_without_html_entity_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); (root / "frames").mkdir(); (root / "frames" / "a.jpg").write_bytes(b"x")
            title = "A &copy; </script> finding"
            data = {"segments": [{
                "index": 1, "start_sec": 0.0, "end_sec": 1.0, "title": title,
                "summary_zh": "文" * 300, "takeaways_zh": ["A", "B", "C", "D"],
                "editorial_notes_zh": [],
                "frames": [{"time": 0.5, "ocr": "", "path": "frames/a.jpg"}],
            }]}
            snapshot = [{"index": 1, "start_sec": 0.0, "end_sec": 1.0, "title": title}]
            payload = json.dumps(snapshot, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
            viewer = root / "viewer.html"
            viewer.write_text(f'<script id="canonical-snapshot" type="application/json">{payload}</script>', encoding="utf-8")
            report = audit_lecture(data, root, viewer_path=viewer)
        self.assertNotIn("viewer_snapshot_mismatch", {f.code for f in report.findings})
```

- [ ] **Step 2: Run and verify RED**

Run: `python -m unittest tests.test_lecture_audit -v`

Expected: FAIL because `lecture_audit` does not exist.

- [ ] **Step 3: Implement report and thin CLI facade**

```python
# skills/lecture-to-notes/scripts/lecture_audit.py
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from json_to_pbf import json_to_pbf_lines
from lecture_content_rules import validate_segment_content
from lecture_model import Finding, segment_end, segment_start, validate_lecture_schema
from render_v4_note import render_v4

SNAPSHOT_RE = re.compile(r'<script id="canonical-snapshot" type="application/json">(.*?)</script>', re.DOTALL)


@dataclass
class AuditReport:
    lecture_id: str
    stage: str
    findings: list[Finding]
    input_hashes: dict[str, str]
    browser_result: dict[str, Any] | None = None

    @property
    def ok(self) -> bool:
        return not any(item.severity == "error" for item in self.findings)

    @property
    def errors(self) -> int:
        return sum(item.severity == "error" for item in self.findings)

    @property
    def warnings(self) -> int:
        return sum(item.severity == "warning" for item in self.findings)

    def to_dict(self) -> dict[str, Any]:
        return {
            "lecture_id": self.lecture_id,
            "stage": self.stage,
            "ok": self.ok,
            "errors": self.errors,
            "warnings": self.warnings,
            "findings": [asdict(item) for item in self.findings],
            "input_hashes": self.input_hashes,
            "browser_result": self.browser_result,
        }


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_snapshot(data: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "index": int(segment.get("index", index + 1)),
            "start_sec": segment_start(segment),
            "end_sec": segment_end(segment),
            "title": segment["title"],
        }
        for index, segment in enumerate(data.get("segments", []))
    ]


def compare_derived(
    data: Mapping[str, Any],
    viewer_path: Path | None,
    pbf_path: Path | None,
    v4_path: Path | None,
) -> list[Finding]:
    findings: list[Finding] = []
    if viewer_path is not None:
        if not viewer_path.is_file():
            findings.append(Finding("error", "viewer_missing", "viewer output is missing", path=str(viewer_path)))
        else:
            match = SNAPSHOT_RE.search(viewer_path.read_text(encoding="utf-8"))
            actual = None if match is None else json.loads(match.group(1))
            if actual != canonical_snapshot(data):
                findings.append(Finding("error", "viewer_snapshot_mismatch", "viewer chapter order, times, or titles differ from JSON", path=str(viewer_path)))
    if pbf_path is not None:
        if not pbf_path.is_file():
            findings.append(Finding("error", "pbf_missing", "PBF output is missing", path=str(pbf_path)))
        else:
            expected = "\n".join(json_to_pbf_lines(dict(data))) + "\n"
            actual = pbf_path.read_text(encoding="utf-8-sig")
            if actual != expected:
                findings.append(Finding("error", "pbf_mismatch", "PBF chapter order, times, or titles differ from JSON", path=str(pbf_path)))
    if v4_path is not None:
        if not v4_path.is_file():
            findings.append(Finding("error", "v4_missing", "V4 note is missing", path=str(v4_path)))
        elif v4_path.read_text(encoding="utf-8") != render_v4(data):
            findings.append(Finding("error", "v4_content_mismatch", "V4 title, summary, takeaways, editorial notes, or frames differ from JSON", path=str(v4_path)))
    return findings


def audit_lecture(
    data: Mapping[str, Any],
    base_dir: Path,
    transcripts: Mapping[int, str] | None = None,
    viewer_path: Path | None = None,
    pbf_path: Path | None = None,
    v4_path: Path | None = None,
    browser_result: Mapping[str, Any] | None = None,
) -> AuditReport:
    findings = validate_lecture_schema(data, base_dir)
    transcript_map = transcripts or {}
    for index, segment in enumerate(data.get("segments", [])):
        for finding in validate_segment_content(segment, transcript_map.get(index, "")):
            findings.append(Finding(finding.severity, finding.code, finding.message, index, finding.path))
        if 1 <= len(segment.get("frames", [])) < 4:
            findings.append(Finding("warning", "frame_below_target", "segment has fewer than four valid frames", index))
    findings.extend(compare_derived(data, viewer_path, pbf_path, v4_path))
    if browser_result is not None and browser_result.get("ok") is not True:
        findings.append(Finding("error", "browser_e2e", "browser functional audit failed"))
    hashes = {
        label: _sha(path)
        for label, path in (("viewer", viewer_path), ("pbf", pbf_path), ("v4", v4_path))
        if path is not None and path.is_file()
    }
    return AuditReport(str(data.get("lecture_id", data.get("title", "unknown"))), "audit", findings, hashes, dict(browser_result) if browser_result else None)


def audit_course(
    report_paths: Sequence[Path],
    homepage_path: Path,
    expected_viewer_names: Sequence[str],
    expected_count: int = 11,
) -> AuditReport:
    findings: list[Finding] = []
    reports = [json.loads(path.read_text(encoding="utf-8")) for path in report_paths]
    lecture_ids = [str(report["lecture_id"]) for report in reports]
    if len(reports) != expected_count or len(set(lecture_ids)) != expected_count:
        findings.append(Finding("error", "course_lecture_count", f"expected {expected_count} unique lecture reports"))
    for report in reports:
        if report.get("ok") is not True:
            findings.append(Finding("error", "course_lecture_failed", f"lecture {report.get('lecture_id')} audit failed"))
    if not homepage_path.is_file():
        findings.append(Finding("error", "homepage_missing", "staged course homepage is missing", path=str(homepage_path)))
    else:
        homepage = homepage_path.read_text(encoding="utf-8")
        for viewer_name in expected_viewer_names:
            if viewer_name not in homepage:
                findings.append(Finding("error", "homepage_link_missing", f"homepage is missing {viewer_name}"))
    hashes = {"homepage": _sha(homepage_path)} if homepage_path.is_file() else {}
    return AuditReport("course", "course-audit", findings, hashes)
```

Replace `check_lecture.py` with this complete thin facade; it parses the SRT so transcript-copy checks run during formal audit:

```python
import argparse
import json
from pathlib import Path

from build_lecture_viewer import load_srt
from lecture_audit import audit_lecture
from lecture_model import load_lecture, segment_end, segment_start, write_json_atomic


def transcript_map(data: dict, srt_path: Path | None) -> dict[int, str]:
    if srt_path is None:
        return {}
    cues = load_srt(srt_path)
    result = {}
    for index, segment in enumerate(data["segments"]):
        start, end = segment_start(segment), segment_end(segment)
        result[index] = "\n".join(cue["text"] for cue in cues if start <= float(cue["start"]) < end)
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("json", type=Path)
    parser.add_argument("--srt", type=Path)
    parser.add_argument("--viewer", type=Path)
    parser.add_argument("--pbf", type=Path)
    parser.add_argument("--note", type=Path)
    parser.add_argument("--browser-result", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)
    data = load_lecture(args.json)
    browser = None if args.browser_result is None else json.loads(args.browser_result.read_text(encoding="utf-8"))
    report = audit_lecture(
        data,
        args.json.parent,
        transcripts=transcript_map(data, args.srt),
        viewer_path=args.viewer,
        pbf_path=args.pbf,
        v4_path=args.note,
        browser_result=browser,
    )
    write_json_atomic(args.report, report.to_dict())
    print(f"[audit] lecture={report.lecture_id} errors={report.errors} warnings={report.warnings}")
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run tests and strict CLI output check**

Run:

```powershell
python -m unittest tests.test_lecture_audit -v
$Old = $env:PYTHONIOENCODING; $env:PYTHONIOENCODING = "cp950:strict"; python -m unittest tests.test_lecture_audit -v; $env:PYTHONIOENCODING = $Old
```

Expected: both runs PASS with no `UnicodeEncodeError`.

- [ ] **Step 5: Commit**

```powershell
git add -- "skills/lecture-to-notes/scripts/lecture_audit.py" "skills/lecture-to-notes/scripts/check_lecture.py" "tests/test_lecture_audit.py"
git commit -m "feat(lecture): add structured cross-output audit"
```

---

### Task 8: Preflight、Canonical Skill Drift 與依賴檢查

**Files:**
- Modify: `sync_skills.py:TARGETS loop and mirror reconciliation`
- Create: `tests/test_sync_skills.py`
- Create: `tests/test_lecture_rebuild_pipeline.py`
- Create: `skills/lecture-to-notes/scripts/rebuild_course.py` (preflight-only first slice)
- Create: `skills/lecture-to-notes/requirements-rebuild.txt` (canonical installable dependency range)

**Interfaces:**
- Produces: `PreflightResult`, duplicate-safe `pair_lectures(root: Path) -> list[LectureInputs]`, `run_preflight(root, staging_root=None, backup_root=None, expected_lecture_count=11, allow_replace_probe=False, ...) -> PreflightResult`, explicit opt-in `probe_replace_semantics(live_root, staging_root) -> None`, and `sync_skills.py --check` exit 2 on any mirror file-set/content drift。Preflight 必須驗證 live course root 可寫、`scenedetect>=0.6.4,<0.8`，且只有 `allow_replace_probe=True` 才可在 live/staging 各自建立唯一 disposable probe，跨兩根目錄執行 create/read/hash/`os.replace()`/cleanup；不得使用正式檔名。

- [ ] **Step 1: Write failing preflight and drift tests**

```python
# tests/test_lecture_rebuild_pipeline.py
import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "lecture-to-notes" / "scripts"))

from rebuild_course import pair_lectures, run_preflight


class RebuildPreflightTests(unittest.TestCase):
    def test_rebuild_requirements_declares_same_scenedetect_range_as_runtime_gate(self):
        requirement = (ROOT / "skills" / "lecture-to-notes" / "requirements-rebuild.txt").read_text(encoding="utf-8").splitlines()
        self.assertIn("scenedetect>=0.6.4,<0.8", requirement)

    def test_pairing_requires_exactly_one_mp4_srt_json_per_lecture(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for suffix in ("mp4", "srt", "json"):
                (root / f"01 Brain.{suffix}").write_bytes(b"x")
            pairs = pair_lectures(root)
        self.assertEqual(pairs[0].lecture_id, "01")

    def test_pairing_ignores_derivative_and_run_json_beside_formal_json(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for suffix in ("mp4", "srt", "json"):
                (root / f"01 Brain.{suffix}").write_text("{}", encoding="utf-8")
            for name in (
                "01 Brain.frames.json", "01 Brain.frames_ocr.json",
                "01 Brain.audit.json", "course-run.json", "course.audit.json",
                "preflight.json", "manifest.json", "report.json", "package.json",
                "rewrite_results.json", "review_records.json", "evidence_packets.json",
                "01 Brain.package.json", "01 Brain.report.json", "01 Brain.manifest.json",
                "01 Brain.rewrite.json", "01 Brain.review.json", "01 Brain.transaction.json",
            ):
                (root / name).write_text("{}", encoding="utf-8")
            pairs = pair_lectures(root)
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0].json.name, "01 Brain.json")

    def test_preflight_does_not_write_when_dependency_is_missing(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result = run_preflight(
                root,
                expected_lecture_count=0,
                command_lookup=lambda command: None,
                dependency_version=lambda name: "0.6.4",
                module_available=lambda name: object(),
            )
            self.assertFalse(result.ok)
            self.assertIn("ffmpeg_missing", {f.code for f in result.findings})
            self.assertEqual(list(root.iterdir()), [])

    def test_preflight_blocks_unwritable_live_root(self):
        with tempfile.TemporaryDirectory() as td, patch("rebuild_course.os.access", return_value=False):
            result = run_preflight(
                Path(td), expected_lecture_count=0,
                command_lookup=lambda command: "tool.exe",
                dependency_version=lambda name: "0.6.4",
                module_available=lambda name: object(),
                browser_available=lambda: True,
            )
        self.assertIn("live_root_not_writable", {f.code for f in result.findings})

    def test_preflight_blocks_scenedetect_outside_supported_range(self):
        with tempfile.TemporaryDirectory() as td:
            result = run_preflight(
                Path(td), expected_lecture_count=0,
                command_lookup=lambda command: "tool.exe",
                dependency_version=lambda name: "0.8.0" if name == "scenedetect" else "1.0",
                module_available=lambda name: object(),
                browser_available=lambda: True,
            )
        self.assertIn("scenedetect_version", {f.code for f in result.findings})

    def test_expected_lecture_count_three_passes_and_eleven_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for lecture_id in ("01", "02", "03"):
                for suffix in ("mp4", "srt", "json"):
                    (root / f"{lecture_id} Sample.{suffix}").write_text("{}" if suffix == "json" else "x", encoding="utf-8")
            common = dict(
                command_lookup=lambda command: "tool.exe",
                dependency_version=lambda name: "0.6.4" if name == "scenedetect" else "1.0",
                module_available=lambda name: object(),
                browser_available=lambda: True,
                validate_existing_frames=False,
            )
            self.assertTrue(run_preflight(root, expected_lecture_count=3, **common).ok)
            failed = run_preflight(root, expected_lecture_count=11, **common)
        self.assertIn("lecture_count", {f.code for f in failed.findings})

    def test_duplicate_mp4_is_pairing_conflict(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for name in ("01 Brain.mp4", "01 Brain copy.mp4", "01 Brain.srt", "01 Brain.json"):
                (root / name).write_bytes(b"x")
            with self.assertRaisesRegex(ValueError, "pairing conflict"):
                pair_lectures(root)

    def test_replace_probe_is_explicit_cross_root_and_disposable(self):
        from rebuild_course import probe_replace_semantics
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); live = root / "live"; stage = root / "stage"
            live.mkdir(); stage.mkdir()
            probe_replace_semantics(live, stage)
            self.assertEqual(list(live.iterdir()), [])
            self.assertEqual(list(stage.iterdir()), [])

    def test_preflight_does_not_probe_without_opt_in_and_probes_when_enabled(self):
        with tempfile.TemporaryDirectory() as td, patch("rebuild_course.probe_replace_semantics") as probe:
            root = Path(td); stage = root / "stage"; stage.mkdir()
            kwargs = dict(
                staging_root=stage, expected_lecture_count=0,
                command_lookup=lambda command: "tool.exe",
                dependency_version=lambda name: "0.6.4" if name == "scenedetect" else "1.0",
                module_available=lambda name: object(),
                browser_available=lambda: True,
                minimum_free_bytes=0,
            )
            run_preflight(root, allow_replace_probe=False, **kwargs)
            probe.assert_not_called()
            run_preflight(root, allow_replace_probe=True, **kwargs)
            probe.assert_called_once_with(root, stage)
```

```python
# tests/test_sync_skills.py
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("sync_skills", ROOT / "sync_skills.py")
sync_skills = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync_skills)


class SyncSkillsTests(unittest.TestCase):
    def test_sync_tree_removes_stale_nested_files_and_check_detects_drift(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            src = root / "src"; dst = root / "dst"
            (src / "scripts").mkdir(parents=True)
            (dst / "scripts").mkdir(parents=True)
            (src / "SKILL.md").write_text("canonical", encoding="utf-8")
            (src / "scripts" / "keep.py").write_text("new", encoding="utf-8")
            (dst / "SKILL.md").write_text("old", encoding="utf-8")
            (dst / "scripts" / "stale.py").write_text("stale", encoding="utf-8")
            self.assertNotEqual(sync_skills.tree_snapshot(src), sync_skills.tree_snapshot(dst))
            sync_skills.sync_tree(src, dst)
            self.assertEqual(sync_skills.tree_snapshot(src), sync_skills.tree_snapshot(dst))
            self.assertFalse((dst / "scripts" / "stale.py").exists())
```

- [ ] **Step 2: Run and verify RED**

Run:

```powershell
python -m unittest tests.test_lecture_rebuild_pipeline.RebuildPreflightTests tests.test_sync_skills -v
```

Expected: FAIL because `rebuild_course`, `tree_snapshot()`、`sync_tree()` and `skills/lecture-to-notes/requirements-rebuild.txt` do not exist。

- [ ] **Step 3: Implement read-only-by-default preflight, explicit disposable replace probe and hash-based sync check**

Create the installable dependency declaration with this exact content:

```text
# skills/lecture-to-notes/requirements-rebuild.txt
scenedetect>=0.6.4,<0.8
```

Install and verify it with Windows PowerShell 5.1 before running the Python implementation below:

```powershell
python -m pip install -r ".\skills\lecture-to-notes\requirements-rebuild.txt"
if ($?) { python -c "from importlib.metadata import version; import sys; sys.path.insert(0, r'.\skills\lecture-to-notes\scripts'); from rebuild_course import _version_tuple; v=version('scenedetect'); assert (0,6,4) <= _version_tuple(v) < (0,8,0), v; print('scenedetect=' + v)" }
```

Expected: PASS；pip resolves an installed version in `>=0.6.4,<0.8` and the second command exits 0。If the environment cannot satisfy the range, Expected FAIL before any course processing; do not weaken the requirement or bypass preflight。

```python
# initial slice of skills/lecture-to-notes/scripts/rebuild_course.py
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import re
import shutil
import subprocess
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from lecture_model import Finding, load_lecture
from rewrite_evidence import contains_sensitive_data


@dataclass(frozen=True)
class LectureInputs:
    lecture_id: str
    mp4: Path
    srt: Path
    json: Path


@dataclass
class PreflightResult:
    pairs: list[LectureInputs]
    findings: list[Finding]

    @property
    def ok(self) -> bool:
        return not any(item.severity == "error" for item in self.findings)


DERIVATIVE_JSON_NAMES = {
    "course-run.json", "course.audit.json", "preflight.json",
    "manifest.json", "report.json", "package.json",
    "rewrite_results.json", "review_records.json", "evidence_packets.json",
}
DERIVATIVE_JSON_SUFFIXES = (
    ".frames.json", ".frames_ocr.json", ".audit.json", ".package.json",
    ".report.json", ".manifest.json", ".rewrite.json", ".review.json",
    ".transaction.json",
)


def _is_formal_lecture_json(path: Path) -> bool:
    name = path.name.casefold()
    return (
        path.suffix.casefold() == ".json"
        and name not in DERIVATIVE_JSON_NAMES
        and not name.endswith(DERIVATIVE_JSON_SUFFIXES)
    )


def pair_lectures(root: Path) -> list[LectureInputs]:
    groups: dict[str, dict[str, list[Path]]] = {}
    for path in root.iterdir():
        suffix = path.suffix.lower()
        if suffix not in {".mp4", ".srt", ".json"}:
            continue
        if suffix == ".json" and not _is_formal_lecture_json(path):
            continue
        lecture_id = path.stem.split()[0]
        groups.setdefault(lecture_id, {}).setdefault(suffix, []).append(path)
    pairs = []
    for lecture_id, files in sorted(groups.items()):
        conflicts = {suffix: paths for suffix, paths in files.items() if len(paths) != 1}
        if set(files) != {".mp4", ".srt", ".json"} or conflicts:
            detail = {suffix: [str(path) for path in paths] for suffix, paths in files.items()}
            raise ValueError(f"lecture {lecture_id} pairing conflict: {detail}")
        pairs.append(LectureInputs(lecture_id, files[".mp4"][0], files[".srt"][0], files[".json"][0]))
    return pairs


def _existing_parent(path: Path) -> Path:
    current = path
    while not current.exists() and current != current.parent:
        current = current.parent
    return current


def _browser_available() -> bool:
    return any(path.exists() for path in (
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    ))


def _version_tuple(value: str) -> tuple[int, ...]:
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)", value)
    if match is None:
        raise ValueError(f"unparseable version: {value}")
    return tuple(int(part) for part in match.groups())


def probe_replace_semantics(live_root: Path, staging_root: Path) -> None:
    token = uuid.uuid4().hex
    live_probe = live_root / f".nr-rebuild-live-probe-{token}.tmp"
    staged_probe = staging_root / f".nr-rebuild-stage-probe-{token}.tmp"
    try:
        live_probe.write_bytes(b"old-probe")
        staged_probe.write_bytes(b"new-probe")
        if hashlib.sha256(live_probe.read_bytes()).hexdigest() != hashlib.sha256(b"old-probe").hexdigest():
            raise IOError("live probe read/hash verification failed")
        if hashlib.sha256(staged_probe.read_bytes()).hexdigest() != hashlib.sha256(b"new-probe").hexdigest():
            raise IOError("staging probe read/hash verification failed")
        os.replace(staged_probe, live_probe)
        if hashlib.sha256(live_probe.read_bytes()).hexdigest() != hashlib.sha256(b"new-probe").hexdigest():
            raise IOError("cross-root replace verification failed")
    finally:
        for path in (staged_probe, live_probe):
            try:
                path.unlink()
            except FileNotFoundError:
                pass


def run_preflight(
    root: Path,
    staging_root: Path | None = None,
    backup_root: Path | None = None,
    expected_lecture_count: int = 11,
    command_lookup: Callable[[str], str | None] = shutil.which,
    dependency_version: Callable[[str], str] = importlib.metadata.version,
    module_available: Callable[[str], object | None] = importlib.util.find_spec,
    browser_available: Callable[[], bool] = _browser_available,
    sync_check: Callable[[], int] | None = None,
    minimum_free_bytes: int = 5 * 1024**3,
    allow_replace_probe: bool = False,
    validate_existing_frames: bool = True,
) -> PreflightResult:
    findings: list[Finding] = []
    if not root.is_dir():
        return PreflightResult([], [Finding("error", "root_missing", "course root is not readable", path=str(root))])
    if not os.access(root, os.W_OK):
        findings.append(Finding("error", "live_root_not_writable", "live course root is not writable", path=str(root)))
    try:
        pairs = pair_lectures(root)
    except ValueError as exc:
        return PreflightResult([], findings + [Finding("error", "pairing_conflict", str(exc))])
    if len(pairs) != expected_lecture_count:
        findings.append(Finding("error", "lecture_count", f"expected {expected_lecture_count} paired lectures, found {len(pairs)}"))
    for command in ("ffmpeg", "ffprobe"):
        if command_lookup(command) is None:
            findings.append(Finding("error", f"{command}_missing", f"{command} is not available"))
    for module_name in ("scenedetect", "rapidocr_onnxruntime", "opencc"):
        if module_available(module_name) is None:
            findings.append(Finding("error", f"{module_name}_missing", f"Python module {module_name} is not available"))
    try:
        scenedetect_version = dependency_version("scenedetect")
        if not ((0, 6, 4) <= _version_tuple(scenedetect_version) < (0, 8, 0)):
            findings.append(Finding("error", "scenedetect_version", f"scenedetect {scenedetect_version} is unsupported; require >=0.6.4,<0.8"))
    except Exception as exc:
        findings.append(Finding("error", "scenedetect_version", f"cannot verify scenedetect>=0.6.4,<0.8: {exc}"))
    if not browser_available():
        findings.append(Finding("error", "browser_missing", "Chrome or Edge headless browser is not available"))
    for label, target in (("staging", staging_root), ("backup", backup_root)):
        if target is None:
            continue
        parent = _existing_parent(target)
        if not parent.exists() or not os.access(parent, os.W_OK):
            findings.append(Finding("error", f"{label}_not_writable", f"{label} parent is not writable", path=str(parent)))
        elif shutil.disk_usage(parent).free < minimum_free_bytes:
            findings.append(Finding("error", f"{label}_space", f"{label} has less than {minimum_free_bytes} free bytes", path=str(parent)))
    if pairs and validate_existing_frames:
        first = load_lecture(pairs[0].json)
        existing = [frame["path"] for segment in first.get("segments", []) for frame in segment.get("frames", [])]
        if len(existing) != 72 or any(not (root / path).is_file() for path in existing):
            findings.append(Finding("error", "first_lecture_frames", "first lecture must expose 72 readable existing frames for candidate migration"))
    for pair in pairs:
        text = pair.srt.read_text(encoding="utf-8-sig", errors="replace") + "\n" + pair.json.read_text(encoding="utf-8-sig", errors="replace")
        sensitive = contains_sensitive_data(text)
        if sensitive:
            findings.append(Finding("warning", "sensitive_input", f"lecture {pair.lecture_id} contains: {','.join(sensitive)}; external LLM is disabled for this lecture", path=str(pair.json)))
    if sync_check is not None and sync_check() != 0:
        findings.append(Finding("error", "skill_drift", "canonical skill mirrors are not synchronized"))
    if allow_replace_probe:
        if staging_root is None:
            findings.append(Finding("error", "replace_probe_staging_missing", "replace probe requires staging_root"))
        elif not any(item.severity == "error" for item in findings):
            try:
                staging_root.mkdir(parents=True, exist_ok=True)
                probe_replace_semantics(root, staging_root)
            except Exception as exc:
                findings.append(Finding("error", "replace_probe_failed", str(exc)))
    return PreflightResult(pairs, findings)
```

Change `sync_skills.py` to reconcile every canonical skill directory exactly, using the existing `TARGETS` symbol:

```python
import hashlib


def tree_snapshot(root: Path) -> dict[str, str]:
    if not root.exists():
        return {}
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*")
        if path.is_file()
    }


def sync_tree(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    source_files = {path.relative_to(src) for path in src.rglob("*") if path.is_file()}
    for path in sorted((p for p in dst.rglob("*") if p.is_file()), reverse=True):
        if path.relative_to(dst) not in source_files:
            path.unlink()
    for directory in sorted((p for p in dst.rglob("*") if p.is_dir()), reverse=True):
        if not any(directory.iterdir()):
            directory.rmdir()
    shutil.copytree(src, dst, dirs_exist_ok=True)


def skill_drift(src_root: Path, target_root: Path, skill_names: list[str]) -> list[str]:
    drift = []
    for name in skill_names:
        if tree_snapshot(src_root / name) != tree_snapshot(target_root / name):
            drift.append(name)
    return drift

# Inside the existing `for tgt in TARGETS:` loop:
if check:
    drift_names = skill_drift(SRC, tgt, names)
    have = {d.name for d in iter_skill_dirs(tgt)}
    extra = sorted(have - set(names))
    status = "OK" if not drift_names and not extra else "DRIFT"
    drift = drift or status == "DRIFT"
    print(f"  [{status}] {rel} drift={drift_names} extra={extra}")
    continue
for skill_dir in src_skills:
    sync_tree(skill_dir, tgt / skill_dir.name)
```

Retain the existing best-effort pruning of skill directories absent from canonical. The new nested-file reconciliation is strict for files within a retained skill.

- [ ] **Step 4: Run focused tests and real read-only drift check**

Run:

```powershell
python -m unittest tests.test_lecture_rebuild_pipeline.RebuildPreflightTests tests.test_sync_skills -v
python -c "import sys; from importlib.metadata import version; sys.path.insert(0, r'.\skills\lecture-to-notes\scripts'); from rebuild_course import _version_tuple; v=version('scenedetect'); assert (0,6,4) <= _version_tuple(v) < (0,8,0), v; print('scenedetect=' + v)"
python ".\sync_skills.py" --check
```

Expected: tests PASS；版本命令輸出實際 `scenedetect` 版本且 exit 0；current mirror state exits 0。若版本低於 0.6.4 或達 0.8.0，Expected FAIL 為 `AssertionError`，preflight 同樣以 `scenedetect_version` 阻擋。Do not run `python sync_skills.py` until all canonical edits are complete.

- [ ] **Step 5: Commit**

```powershell
git add -- "skills/lecture-to-notes/scripts/rebuild_course.py" "skills/lecture-to-notes/requirements-rebuild.txt" "sync_skills.py" "tests/test_sync_skills.py" "tests/test_lecture_rebuild_pipeline.py"
git commit -m "feat(lecture): add rebuild preflight and drift checks"
```

---

### Task 9: Pipeline Orchestration、失敗隔離與 cp950-safe 進度

**Files:**
- Modify: `skills/lecture-to-notes/scripts/rebuild_course.py:run_stage(), rebuild_lecture(), rebuild_course(), main()`
- Modify: `skills/lecture-to-notes/scripts/frame_curator.py:curate_lecture()` — 發出逐章完成／失敗事件。
- Modify: `skills/lecture-to-notes/scripts/batch_course.py:main()`
- Modify: `tests/test_lecture_rebuild_pipeline.py`
- Create: `tests/test_lecture_console_encoding.py`

**Interfaces:**
- Produces: `ProgressEvent(lecture_id, stage, completed, total, status, chapter_completed, chapter_total, failure_summary)`, `emit_progress(event)`, per-chapter curate events, `rebuild_lecture(pair: LectureInputs, root: Path, stages=STAGE_ORDER, specs_factory=build_stage_specs, stage_runner=run_stage) -> dict[str, object]`, `rebuild_course(...) -> CourseRunResult`; stage order `extract, curate, evidence, rewrite-apply, render, audit`。

- [ ] **Step 1: Add failing isolation and progress tests**

```python
# append to tests/test_lecture_rebuild_pipeline.py
from rebuild_course import ProgressEvent, emit_progress, rebuild_course


class RebuildOrchestrationTests(unittest.TestCase):
    def test_one_lecture_failure_does_not_stop_next_lecture(self):
        calls = []
        def fake_rebuild(pair, *args, **kwargs):
            calls.append(pair.lecture_id)
            if pair.lecture_id == "01":
                raise RuntimeError("synthetic failure")
            return {"lecture_id": pair.lecture_id, "ok": True}
        pairs = [type("P", (), {"lecture_id": value})() for value in ("01", "02")]
        with tempfile.TemporaryDirectory() as td:
            result = rebuild_course(pairs, Path(td), rebuild_one=fake_rebuild)
        self.assertEqual(calls, ["01", "02"])
        self.assertFalse(result.ok)
        self.assertEqual(result.failed_lectures, ["01"])

    def test_progress_text_has_exact_cp950_safe_chapter_fields(self):
        event = ProgressEvent(
            lecture_id="03", stage="curate", completed=2, total=10, status="running",
            chapter_completed=7, chapter_total=12, failure_summary="無",
        )
        text = emit_progress(event, writer=None)
        self.assertEqual(
            text,
            "[progress] lecture=03 stage=curate completed=2/10 percent=20.0% status=running chapter_completed=7 chapter_total=12 failure_summary=無",
        )
        self.assertEqual(text.encode("cp950", errors="strict").decode("cp950"), text)

    def test_curate_emits_each_chapter_and_failure_summary(self):
        from frame_curator import curate_lecture
        events = []
        data = {"lecture_id": "03", "segments": [
            {"start_sec": 0.0, "end_sec": 5.0, "frames": []},
            {"start_sec": 5.0, "end_sec": 10.0, "frames": []},
        ]}
        manifest = {"candidates": [
            {"time": 1.0, "path": "a.jpg", "ocr": "A", "sharpness": 10.0, "luma": 100.0, "phash": "a"},
        ]}
        with tempfile.TemporaryDirectory() as td, patch("frame_curator.load_lecture", return_value=data):
            root = Path(td); manifest_path = root / "candidate_frames.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "no valid frame"):
                curate_lecture(
                    root / "source.json", manifest_path, root / "out.json",
                    live_root=root, staging_root=root, progress_writer=events.append,
                )
        self.assertEqual((events[0].completed, events[0].total), (1, 2))
        self.assertEqual(events[0].chapter_completed, 1)
        self.assertEqual(events[0].chapter_total, 2)
        self.assertEqual((events[-1].completed, events[-1].total), (1, 2))
        self.assertEqual(events[-1].chapter_completed, 1)
        self.assertEqual(events[-1].status, "failed")
        self.assertIn("ValueError: no valid frame", events[-1].failure_summary)
        failure_text = emit_progress(events[-1], writer=None)
        self.assertEqual(
            failure_text,
            "[progress] lecture=03 stage=curate completed=1/2 percent=50.0% status=failed chapter_completed=1 chapter_total=2 failure_summary=ValueError: no valid frame",
        )
        self.assertEqual(failure_text.encode("cp950", errors="strict").decode("cp950"), failure_text)
```

```python
# tests/test_lecture_console_encoding.py
import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "lecture-to-notes" / "scripts"
MODIFIED_CLIS = (
    "slide_frames.py", "ocr_frames.py", "frame_curator.py", "rewrite_evidence.py",
    "rewrite_lecture.py", "build_lecture_viewer.py", "json_to_pbf.py",
    "render_v4_note.py", "build_course_hub.py", "check_lecture.py",
    "rebuild_course.py", "publish_transaction.py", "batch_course.py",
)


class LectureConsoleEncodingTests(unittest.TestCase):
    def test_all_print_literal_parts_are_cp950_encodable(self):
        failures = []
        for name in MODIFIED_CLIS:
            path = SCRIPTS / name
            tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name) or node.func.id != "print":
                    continue
                for child in ast.walk(node):
                    if isinstance(child, ast.Constant) and isinstance(child.value, str):
                        try:
                            child.value.encode("cp950", errors="strict")
                        except UnicodeEncodeError:
                            failures.append(f"{name}:{child.lineno}:{child.value!r}")
        self.assertEqual(failures, [])
```

- [ ] **Step 2: Run and verify RED**

Run: `python -m unittest tests.test_lecture_rebuild_pipeline.RebuildOrchestrationTests -v`

Expected: FAIL because orchestration symbols are absent.

- [ ] **Step 3: Implement stage runner and compatibility wrapper**

```python
# append to skills/lecture-to-notes/scripts/rebuild_course.py
import sys
from datetime import datetime, timezone
from typing import Sequence

from lecture_model import write_json_atomic

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parents[2]
PRE_REVIEW_STAGES = ("extract", "curate", "evidence")
POST_REVIEW_STAGES = ("rewrite-apply", "render", "audit")
STAGE_ORDER = PRE_REVIEW_STAGES + POST_REVIEW_STAGES


@dataclass(frozen=True)
class ProgressEvent:
    lecture_id: str
    stage: str
    completed: int
    total: int
    status: str
    chapter_completed: int = 0
    chapter_total: int = 0
    failure_summary: str = "無"


@dataclass(frozen=True)
class StageSpec:
    name: str
    commands: tuple[tuple[str, ...], ...]
    outputs: tuple[Path, ...]


def _cp950_safe(value: object) -> str:
    return str(value).encode("cp950", errors="replace").decode("cp950")


def emit_progress(event: ProgressEvent, writer=print) -> str:
    percent = 100.0 if event.total == 0 else event.completed * 100.0 / event.total
    text = (
        f"[progress] lecture={_cp950_safe(event.lecture_id)} stage={_cp950_safe(event.stage)} "
        f"completed={event.completed}/{event.total} percent={percent:.1f}% status={_cp950_safe(event.status)} "
        f"chapter_completed={event.chapter_completed} chapter_total={event.chapter_total} "
        f"failure_summary={_cp950_safe(event.failure_summary)}"
    )
    text.encode("cp950", errors="strict")
    if writer is not None:
        writer(text, flush=True)
    return text


def stage_paths(pair: LectureInputs, root: Path) -> dict[str, Path]:
    stem = pair.json.stem
    return {
        "candidate": root / "candidate_frames.json",
        "curated": root / "curated.json",
        "evidence": root / "evidence_packets.json",
        "rewrite": root / "rewrite_results.json",
        "review": root / "review_records.json",
        "rewritten": root / "rewritten.json",
        "formal_json": root / pair.json.name,
        "viewer": root / f"{stem}.viewer.html",
        "pbf": root / f"{stem}.pbf",
        "v4": root / f"{stem}.v4.md",
        "audit": root / f"{stem}.audit.json",
    }


def build_stage_specs(pair: LectureInputs, root: Path) -> dict[str, StageSpec]:
    p = stage_paths(pair, root)
    py = sys.executable
    return {
        "extract": StageSpec("extract", (
            (py, str(SCRIPTS / "slide_frames.py"), str(pair.mp4), "--staging", str(root), "--width", "1280"),
            (py, str(SCRIPTS / "ocr_frames.py"), "--staging", str(root), "--min-conf", "0.5"),
        ), (p["candidate"],)),
        "curate": StageSpec("curate", (
            (py, str(SCRIPTS / "frame_curator.py"), str(pair.json), str(p["candidate"]), "--live-root", str(pair.json.parent), "--staging-root", str(root), "-o", str(p["curated"])),
        ), (p["curated"],)),
        "evidence": StageSpec("evidence", (
            (py, str(SCRIPTS / "rewrite_evidence.py"), str(p["curated"]), "--srt", str(pair.srt), "-o", str(p["evidence"])),
        ), (p["evidence"],)),
        "rewrite-apply": StageSpec("rewrite-apply", (
            (py, str(SCRIPTS / "rewrite_lecture.py"), str(p["curated"]), "--evidence", str(p["evidence"]), "--rewrite", str(p["rewrite"]), "--review", str(p["review"]), "--provider", "manual", "-o", str(p["rewritten"])),
        ), (p["rewritten"],)),
        "render": StageSpec("render", (
            (py, str(SCRIPTS / "build_lecture_viewer.py"), str(p["formal_json"]), "--video", str(pair.mp4), "--srt", str(pair.srt), "-o", str(p["viewer"])),
            (py, str(SCRIPTS / "json_to_pbf.py"), str(p["formal_json"]), "-o", str(p["pbf"])),
            (py, str(SCRIPTS / "render_v4_note.py"), str(p["formal_json"]), "-o", str(p["v4"])),
        ), (p["formal_json"], p["viewer"], p["pbf"], p["v4"])),
        "audit": StageSpec("audit", (
            (py, str(SCRIPTS / "check_lecture.py"), str(p["formal_json"]), "--srt", str(pair.srt), "--viewer", str(p["viewer"]), "--pbf", str(p["pbf"]), "--note", str(p["v4"]), "--report", str(p["audit"]), "--strict"),
        ), (p["audit"],)),
    }


def run_stage(pair: LectureInputs, root: Path, spec: StageSpec) -> None:
    root.mkdir(parents=True, exist_ok=True)
    if spec.name == "render":
        source = stage_paths(pair, root)["rewritten"]
        if not source.is_file():
            raise FileNotFoundError(f"render input missing: {source}")
        shutil.copy2(source, stage_paths(pair, root)["formal_json"])
    for command in spec.commands:
        completed = subprocess.run(command, cwd=pair.json.parent, text=True, encoding="utf-8", errors="replace")
        if completed.returncode != 0:
            raise RuntimeError(f"stage {spec.name} exited {completed.returncode}: {' '.join(command)}")
    missing = [str(path) for path in spec.outputs if not path.is_file()]
    if missing:
        raise RuntimeError(f"stage {spec.name} did not create: {missing}")


def rebuild_lecture(
    pair: LectureInputs,
    root: Path,
    stages: Sequence[str] = STAGE_ORDER,
    specs_factory=build_stage_specs,
    stage_runner=run_stage,
) -> dict[str, object]:
    specs = specs_factory(pair, root)
    for index, stage in enumerate(stages, 1):
        if stage not in specs:
            raise ValueError(f"unsupported lecture stage: {stage}")
        emit_progress(ProgressEvent(pair.lecture_id, stage, index - 1, len(stages), "running"))
        stage_runner(pair, root, specs[stage])
        emit_progress(ProgressEvent(pair.lecture_id, stage, index, len(stages), "complete"))
    status = "awaiting_review" if tuple(stages) == PRE_REVIEW_STAGES else "complete"
    paths = stage_paths(pair, root)
    return {"lecture_id": pair.lecture_id, "ok": True, "status": status, "outputs": {name: str(path) for name, path in paths.items()}}


@dataclass
class CourseRunResult:
    run_id: str
    lectures: list[dict]
    failed_lectures: list[str]
    source_hashes: dict[str, str]

    @property
    def ok(self) -> bool:
        return not self.failed_lectures

    @property
    def completed_lectures(self) -> list[str]:
        return [str(item["lecture_id"]) for item in self.lectures if item.get("status") == "complete"]

    @property
    def awaiting_review(self) -> list[str]:
        return [str(item["lecture_id"]) for item in self.lectures if item.get("status") == "awaiting_review"]

    def to_dict(self) -> dict[str, object]:
        return {"run_id": self.run_id, "ok": self.ok, "lectures": self.lectures, "failed_lectures": self.failed_lectures, "awaiting_review": self.awaiting_review, "source_hashes": self.source_hashes}


def rebuild_course(pairs, staging_root: Path, rebuild_one=rebuild_lecture, stages: Sequence[str] = STAGE_ORDER) -> CourseRunResult:
    results = []
    failed = []
    for index, pair in enumerate(pairs, 1):
        emit_progress(ProgressEvent(pair.lecture_id, "lecture", index - 1, len(pairs), "running"))
        try:
            try:
                item = rebuild_one(pair, staging_root / pair.lecture_id, stages=stages)
            except TypeError as exc:
                if "stages" not in str(exc):
                    raise
                item = rebuild_one(pair, staging_root / pair.lecture_id)
            results.append(item)
        except Exception as exc:
            failed.append(pair.lecture_id)
            results.append({"lecture_id": pair.lecture_id, "ok": False, "error_type": type(exc).__name__, "error": str(exc)})
            emit_progress(ProgressEvent(
                lecture_id=pair.lecture_id, stage="lecture", completed=index, total=len(pairs), status="failed",
                chapter_completed=0, chapter_total=0,
                failure_summary=f"{type(exc).__name__}: {exc}",
            ))
            continue
        emit_progress(ProgressEvent(pair.lecture_id, "lecture", index, len(pairs), "complete"))
    hashes = {
        pair.lecture_id: source_hash(pair)
        for pair in pairs
        if all(hasattr(pair, name) and Path(getattr(pair, name)).is_file() for name in ("mp4", "srt", "json"))
    }
    result = CourseRunResult(datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ"), results, failed, hashes)
    write_json_atomic(staging_root / "course-run.json", result.to_dict())
    return result


def _content_sha256(path: Path) -> bytes:
    # Full-content identity is required; stream in 1 MiB chunks so large MP4 files are not loaded into memory.
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.digest()


def source_hash(pair: LectureInputs) -> str:
    digest = hashlib.sha256()
    for path in (pair.mp4, pair.srt, pair.json):
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(_content_sha256(path))
    return digest.hexdigest()


def select_pairs(
    pairs: list[LectureInputs],
    only: str | None,
    resume_failed: Path | None,
    resume_awaiting_review: Path | None = None,
) -> list[LectureInputs]:
    selected = pairs
    if only:
        wanted = {item.strip() for item in only.split(",") if item.strip()}
        selected = [pair for pair in selected if pair.lecture_id in wanted]
        missing = wanted - {pair.lecture_id for pair in selected}
        if missing:
            raise ValueError(f"unknown lecture ids: {sorted(missing)}")
    resume_path = resume_failed or resume_awaiting_review
    if resume_path:
        report = json.loads(resume_path.read_text(encoding="utf-8"))
        wanted_state = "failed_lectures" if resume_failed else "awaiting_review"
        wanted = set(report[wanted_state])
        expected_hashes = report["source_hashes"]
        selected = [pair for pair in selected if pair.lecture_id in wanted]
        for pair in selected:
            if expected_hashes.get(pair.lecture_id) != source_hash(pair):
                raise ValueError(f"source changed since recorded run: {pair.lecture_id}")
            if resume_awaiting_review:
                paths = stage_paths(pair, resume_path.parent / pair.lecture_id)
                for required in (paths["evidence"], paths["rewrite"], paths["review"]):
                    if not required.is_file():
                        raise FileNotFoundError(f"review resume input missing: {required}")
    return selected
```

Modify `frame_curator.py` after `ProgressEvent` exists. Add `from rebuild_course import ProgressEvent, emit_progress`, then replace `curate_lecture()` with this exact signature and implementation so every completed chapter and the first failed chapter produces a structured event:

```python
def curate_lecture(
    source_path: Path,
    manifest_path: Path,
    output_path: Path,
    live_root: Path,
    staging_root: Path,
    progress_writer=print,
) -> dict[str, Any]:
    data = load_lecture(source_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    legacy = materialize_legacy_candidates(data, live_root, staging_root)
    candidates = merge_existing_candidates({"segments": []}, [*manifest["candidates"], *legacy])
    manifest["candidates"] = candidates
    write_json_atomic(manifest_path, manifest)
    lecture_id = str(data.get("lecture_id", source_path.stem))
    total = len(data["segments"])
    for index, segment in enumerate(data["segments"], 1):
        try:
            segment["frames"] = curate_segment(candidates, segment_start(segment), segment_end(segment))
        except Exception as exc:
            event = ProgressEvent(
                lecture_id=lecture_id, stage="curate", completed=index - 1, total=total, status="failed",
                chapter_completed=index - 1, chapter_total=total,
                failure_summary=f"{type(exc).__name__}: {exc}",
            )
            emit_progress(event, writer=None)
            progress_writer(event)
            raise
        if len(segment["frames"]) < 4:
            segment.setdefault("audit_notes", []).append({"code": "frame_below_target", "count": len(segment["frames"])})
        event = ProgressEvent(
            lecture_id=lecture_id, stage="curate", completed=index, total=total, status="running",
            chapter_completed=index, chapter_total=total, failure_summary="無",
        )
        emit_progress(event, writer=None)
        progress_writer(event)
    write_json_atomic(output_path, data)
    return data
```

In `frame_curator.py:main()`, pass a writer that prints the already validated event text rather than the dataclass representation:

```python
def write_chapter_event(event: ProgressEvent) -> None:
    emit_progress(event)

# main()
data = curate_lecture(
    args.source, args.manifest, args.output,
    live_root=args.live_root, staging_root=args.staging_root,
    progress_writer=write_chapter_event,
)
```

Append the following exact orchestration tests to `tests/test_lecture_rebuild_pipeline.py` before GREEN:

```python
    def test_select_pairs_uses_exact_comma_separated_ids(self):
        from rebuild_course import select_pairs
        pairs = [type("P", (), {"lecture_id": value})() for value in ("01", "011", "02")]
        self.assertEqual([p.lecture_id for p in select_pairs(pairs, "01,02", None)], ["01", "02"])

    @patch("rebuild_course.subprocess.run")
    def test_run_stage_stops_on_nonzero_exit(self, run):
        from rebuild_course import LectureInputs, StageSpec, run_stage
        run.return_value.returncode = 7
        pair = LectureInputs("01", Path("v.mp4"), Path("t.srt"), Path("j.json"))
        spec = StageSpec("extract", (("python", "tool.py"),), ())
        with tempfile.TemporaryDirectory() as td, self.assertRaisesRegex(RuntimeError, "exited 7"):
            run_stage(pair, Path(td), spec)

    def test_resume_rejects_changed_source_hash(self):
        from rebuild_course import LectureInputs, select_pairs, source_hash
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths = [root / name for name in ("01.mp4", "01.srt", "01.json")]
            for path in paths:
                path.write_bytes(b"old")
            pair = LectureInputs("01", *paths)
            report = root / "course-run.json"
            report.write_text(json.dumps({"failed_lectures": ["01"], "source_hashes": {"01": source_hash(pair)}}), encoding="utf-8")
            paths[1].write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "source changed"):
                select_pairs([pair], None, report)

    def test_mp4_content_change_is_detected_even_when_size_and_mtime_are_preserved(self):
        from rebuild_course import LectureInputs, source_hash
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            mp4 = root / "01.mp4"; srt = root / "01.srt"; lecture = root / "01.json"
            mp4.write_bytes(b"AAAA"); srt.write_bytes(b"srt"); lecture.write_bytes(b"json")
            pair = LectureInputs("01", mp4, srt, lecture)
            original_stat = mp4.stat()
            original_hash = source_hash(pair)
            mp4.write_bytes(b"BBBB")
            os.utime(mp4, ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns))
            self.assertEqual(mp4.stat().st_size, original_stat.st_size)
            self.assertEqual(mp4.stat().st_mtime_ns, original_stat.st_mtime_ns)
            self.assertNotEqual(source_hash(pair), original_hash)
```

`batch_course.py` becomes a compatibility wrapper:

```python
from rebuild_course import main
if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run tests with cp950 strict**

Run:

```powershell
$Old = $env:PYTHONIOENCODING; $env:PYTHONIOENCODING = "cp950:strict"; python -m unittest tests.test_lecture_rebuild_pipeline tests.test_lecture_console_encoding -v; $env:PYTHONIOENCODING = $Old
```

Expected: PASS, no encoding error, failed synthetic lecture recorded while the next lecture completes；`source_hash()` streams full MP4/SRT/JSON contents, and changing MP4 bytes while preserving size and nanosecond mtime changes the recorded identity。

- [ ] **Step 5: Commit**

```powershell
git add -- "skills/lecture-to-notes/scripts/rebuild_course.py" "skills/lecture-to-notes/scripts/frame_curator.py" "skills/lecture-to-notes/scripts/batch_course.py" "tests/test_lecture_rebuild_pipeline.py" "tests/test_lecture_console_encoding.py"
git commit -m "feat(lecture): orchestrate rebuild with progress"
```

---

### Task 10: 每講 Manifest、Backup、交易式多檔切換與 Rollback

**Files:**
- Create: `skills/lecture-to-notes/scripts/publish_transaction.py`
- Create: `tests/test_lecture_publish_transaction.py`

**Interfaces:**
- Produces: `ManifestEntry`, `LectureManifest`, `build_manifest(run_id, lecture_id, ...)`, `publish_lecture()`, `rollback_lecture()`, `recover_incomplete_transaction()`, `publish_course_homepage()` and CLI subcommand `rollback --manifest <transaction.json>`。所有 `ManifestEntry(...)` 建構一律使用具名參數。既有 live file 必須記錄 `old_exists=True` 與實際 `old_sha256`；本次新增 frame asset 必須記錄 `old_exists=False`, `old_sha256=None`，rollback 時刪除該交易建立的 live file。`entry.staged` 是 immutable/versioned staging source；每次 replace 前先複製成 live 同目錄 disposable temp，再以 `os.replace()` 切換，因此 successful replace 不消耗 staging，lecture/homepage rollback 後可用同一 manifest retry。`LectureManifest.recovery_path` 必須位於 transaction directory 外的 `backup_root/_recovery/`；transaction directory 持續不可寫時仍可留下 recovery evidence。

- [ ] **Step 1: Write failure-injection transaction tests**

```python
# tests/test_lecture_publish_transaction.py
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "lecture-to-notes" / "scripts"))

from publish_transaction import (
    ManifestEntry, _write_manifest, build_manifest, load_manifest, sha256,
    publish_course_homepage, publish_lecture, recover_incomplete_transaction,
)


class PublishTransactionTests(unittest.TestCase):
    def test_build_manifest_records_existing_and_new_assets_with_named_fields(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); live = root / "live"; stage = root / "stage"; backup = root / "backup"
            live.mkdir(); stage.mkdir(); backup.mkdir()
            (live / "lecture.json").write_text("old", encoding="utf-8")
            (stage / "lecture.json").write_text("new", encoding="utf-8")
            (stage / "frames").mkdir()
            (stage / "frames" / "new.jpg").write_bytes(b"new-frame")
            manifest = build_manifest("run-build", "01", live, stage, backup, ["lecture.json", "frames/new.jpg"])
        old_entry, new_entry = manifest.entries
        self.assertIsInstance(old_entry, ManifestEntry)
        self.assertTrue(old_entry.old_exists)
        self.assertIsNotNone(old_entry.old_sha256)
        self.assertNotEqual(old_entry.old_sha256, old_entry.new_sha256)
        self.assertFalse(new_entry.old_exists)
        self.assertIsNone(new_entry.old_sha256)
        self.assertEqual(len(new_entry.new_sha256), 64)

    def test_second_replace_failure_rolls_back_entire_lecture(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            live = root / "live"; stage = root / "stage"; backup = root / "backup"
            live.mkdir(); stage.mkdir(); backup.mkdir()
            for name in ("lecture.json", "lecture.viewer.html"):
                (live / name).write_text("old-" + name, encoding="utf-8")
                (stage / name).write_text("new-" + name, encoding="utf-8")
            manifest = build_manifest("run-001", "01", live, stage, backup, ["lecture.json", "lecture.viewer.html"])
            calls = 0
            def fail_second(src, dst):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("injected replace failure")
                Path(dst).write_bytes(Path(src).read_bytes())
                Path(src).unlink()
            result = publish_lecture(manifest, replace_func=fail_second)
            self.assertFalse(result.ok)
            self.assertTrue(result.rolled_back)
            self.assertEqual((live / "lecture.json").read_text(encoding="utf-8"), "old-lecture.json")
            self.assertEqual((live / "lecture.viewer.html").read_text(encoding="utf-8"), "old-lecture.viewer.html")

    def test_failed_publish_keeps_immutable_staging_and_same_manifest_retry_commits(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); live = root / "live"; stage = root / "stage"; backup = root / "backup"
            live.mkdir(); stage.mkdir(); backup.mkdir()
            (live / "lecture.json").write_text("old", encoding="utf-8")
            (stage / "lecture.json").write_text("new", encoding="utf-8")
            manifest = build_manifest("run-retry", "01", live, stage, backup, ["lecture.json"])
            immutable_bytes = Path(manifest.entries[0].staged).read_bytes()
            def fail_once(src, dst):
                raise OSError("first attempt fails")
            first = publish_lecture(manifest, replace_func=fail_once)
            self.assertFalse(first.ok)
            self.assertTrue(first.rolled_back)
            self.assertEqual(Path(manifest.entries[0].staged).read_bytes(), immutable_bytes)
            second = publish_lecture(manifest)
            self.assertTrue(second.ok)
            self.assertEqual((live / "lecture.json").read_text(encoding="utf-8"), "new")
            self.assertEqual(Path(manifest.entries[0].staged).read_bytes(), immutable_bytes)

    def test_replace_success_then_hash_mismatch_still_rolls_back_changed_file(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); live = root / "live"; stage = root / "stage"; backup = root / "backup"
            live.mkdir(); stage.mkdir(); backup.mkdir()
            (live / "lecture.json").write_text("old", encoding="utf-8")
            (stage / "lecture.json").write_text("new", encoding="utf-8")
            manifest = build_manifest("run-002", "01", live, stage, backup, ["lecture.json"])
            calls = 0
            def corrupt_after_replace(src, dst):
                nonlocal calls
                calls += 1
                if calls == 1:
                    Path(dst).write_text("corrupt", encoding="utf-8")
                    Path(src).unlink()
                else:
                    Path(dst).write_bytes(Path(src).read_bytes())
                    Path(src).unlink()
            result = publish_lecture(manifest, replace_func=corrupt_after_replace)
            self.assertFalse(result.ok)
            self.assertEqual((live / "lecture.json").read_text(encoding="utf-8"), "old")

    def test_homepage_requires_eleven_committed_manifests_and_passing_audit(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); backup = root / "backup"
            staged = root / "staged.html"; live = root / "index.html"
            staged.write_text("new", encoding="utf-8"); live.write_text("old", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "11 unique"):
                publish_course_homepage("run-003", staged, live, backup, [], {"ok": True})

    def test_homepage_publish_writes_manifest_with_correct_named_hash_fields(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); backup = root / "backup"; live_root = root / "live"; stage_root = root / "stage"
            backup.mkdir(); live_root.mkdir(); stage_root.mkdir()
            manifest_paths = []
            for number in range(1, 12):
                name = f"{number:02d}.json"
                (live_root / name).write_text("old", encoding="utf-8")
                (stage_root / name).write_text("new", encoding="utf-8")
                manifest = build_manifest("run-home", f"{number:02d}", live_root, stage_root, backup, [name])
                shutil.copy2(stage_root / name, live_root / name)
                manifest.state = "committed"
                _write_manifest(manifest)
                manifest_paths.append(Path(manifest.manifest_path))
            staged_homepage = stage_root / "index.html"; live_homepage = live_root / "index.html"
            staged_homepage.write_text("new-home", encoding="utf-8")
            live_homepage.write_text("old-home", encoding="utf-8")
            def fail_homepage_once(src, dst):
                raise OSError("injected homepage replace failure")
            first = publish_course_homepage(
                "run-home", staged_homepage, live_homepage, backup, manifest_paths, {"ok": True}, fail_homepage_once
            )
            self.assertFalse(first.ok)
            self.assertTrue(first.rolled_back)
            self.assertEqual(live_homepage.read_text(encoding="utf-8"), "old-home")
            self.assertTrue(staged_homepage.is_file())
            result = publish_course_homepage(
                "run-home", staged_homepage, live_homepage, backup, manifest_paths, {"ok": True}
            )
            saved = load_manifest(backup / "run-home" / "course-homepage" / "transaction.json")
            self.assertTrue(staged_homepage.is_file())
            self.assertEqual(staged_homepage.read_text(encoding="utf-8"), "new-home")
        self.assertTrue(result.ok)
        self.assertEqual(saved.state, "committed")
        self.assertTrue(saved.entries[0].old_exists)
        self.assertIsNotNone(saved.entries[0].old_sha256)
        self.assertNotEqual(saved.entries[0].old_sha256, saved.entries[0].new_sha256)

    def test_each_replace_position_restores_old_files_and_deletes_new_live_asset(self):
        relative_paths = ["lecture.json", "lecture.viewer.html", "frames/new.jpg", "lecture.audit.json"]
        for fail_at in range(1, len(relative_paths) + 1):
            with self.subTest(fail_at=fail_at), tempfile.TemporaryDirectory() as td:
                root = Path(td); live = root / "live"; stage = root / "stage"; backup = root / "backup"
                live.mkdir(); stage.mkdir(); backup.mkdir(); (live / "frames").mkdir(); (stage / "frames").mkdir()
                old_names = ["lecture.json", "lecture.viewer.html", "lecture.audit.json"]
                for name in old_names:
                    (live / name).write_text("old-" + name, encoding="utf-8")
                    (stage / name).write_text("new-" + name, encoding="utf-8")
                (stage / "frames" / "new.jpg").write_bytes(b"new-frame")
                manifest = build_manifest(f"run-matrix-{fail_at}", "01", live, stage, backup, relative_paths)
                calls = 0
                def injected(src, dst):
                    nonlocal calls
                    calls += 1
                    if calls == fail_at:
                        raise OSError(f"failure at replace {fail_at}")
                    Path(dst).parent.mkdir(parents=True, exist_ok=True)
                    Path(dst).write_bytes(Path(src).read_bytes())
                    Path(src).unlink()
                result = publish_lecture(manifest, replace_func=injected)
                self.assertFalse(result.ok)
                self.assertEqual(
                    [(live / name).read_text(encoding="utf-8") for name in old_names],
                    ["old-" + name for name in old_names],
                )
                self.assertFalse((live / "frames" / "new.jpg").exists())
                self.assertIn(load_manifest(Path(manifest.manifest_path)).state, {"rolled_back", "recovery_required"})

    def test_intermittent_manifest_write_failure_before_first_replace_keeps_old_live_hashes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); live = root / "live"; stage = root / "stage"; backup = root / "backup"
            live.mkdir(); stage.mkdir(); backup.mkdir()
            for name in ("lecture.json", "lecture.viewer.html"):
                (live / name).write_text("old-" + name, encoding="utf-8")
                (stage / name).write_text("new-" + name, encoding="utf-8")
            manifest = build_manifest("run-write-fail", "01", live, stage, backup, ["lecture.json", "lecture.viewer.html"])
            real_write = _write_manifest
            calls = 0
            def fail_once(value):
                nonlocal calls
                calls += 1
                if calls == 1:
                    raise OSError("manifest write failed")
                real_write(value)
            with patch("publish_transaction._write_manifest", side_effect=fail_once):
                result = publish_lecture(manifest)
            self.assertFalse(result.ok)
            self.assertTrue(result.rolled_back)
            self.assertEqual(
                [(live / name).read_text(encoding="utf-8") for name in ("lecture.json", "lecture.viewer.html")],
                ["old-lecture.json", "old-lecture.viewer.html"],
            )
            self.assertTrue(load_manifest(Path(manifest.manifest_path)).persistence_errors)

    def test_unwritable_transaction_directory_still_rolls_back_and_writes_external_recovery_evidence(self):
        import publish_transaction as transaction_module
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); live = root / "live"; stage = root / "stage"; backup = root / "backup"
            live.mkdir(); stage.mkdir(); backup.mkdir()
            (live / "lecture.json").write_text("old", encoding="utf-8")
            (stage / "lecture.json").write_text("new", encoding="utf-8")
            manifest = build_manifest("run-persistent-write-fail", "01", live, stage, backup, ["lecture.json"])
            transaction_dir = Path(manifest.manifest_path).parent
            real_atomic = transaction_module.write_json_atomic
            def reject_transaction_directory(path, data):
                candidate = Path(path)
                if candidate == transaction_dir or transaction_dir in candidate.parents:
                    raise OSError("transaction directory is read-only")
                return real_atomic(candidate, data)
            with patch("publish_transaction.write_json_atomic", side_effect=reject_transaction_directory):
                result = publish_lecture(manifest)
            evidence = Path(manifest.recovery_path)
            self.assertFalse(result.ok)
            self.assertTrue(result.rolled_back)
            self.assertEqual((live / "lecture.json").read_text(encoding="utf-8"), "old")
            self.assertTrue(evidence.is_file())
            self.assertNotEqual(evidence.parent, transaction_dir)
            saved = json.loads(evidence.read_text(encoding="utf-8"))
            self.assertTrue(saved["persistence_errors"])
            self.assertIn("transaction manifest persistence failed", saved["error"])
            self.assertIn("transaction manifest persistence failed", result.error)
            self.assertEqual(saved["entries"][0]["old_sha256"], sha256(live / "lecture.json"))

    def test_recover_replace_started_restores_all_old_files_or_records_recovery_error(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); live = root / "live"; stage = root / "stage"; backup = root / "backup"
            live.mkdir(); stage.mkdir(); backup.mkdir()
            names = ["lecture.json", "lecture.viewer.html"]
            for name in names:
                (live / name).write_text("old-" + name, encoding="utf-8")
                (stage / name).write_text("new-" + name, encoding="utf-8")
            manifest = build_manifest("run-recover", "01", live, stage, backup, names)
            for entry in manifest.entries:
                target = Path(entry.backup); target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(entry.live, target)
            Path(manifest.entries[0].live).write_text("new-lecture.json", encoding="utf-8")
            manifest.entries[0].state = "replace_started"
            manifest.state = "backed_up"
            _write_manifest(manifest)
            result = recover_incomplete_transaction(Path(manifest.manifest_path))
            saved = load_manifest(Path(manifest.manifest_path))
            if result.rolled_back:
                self.assertEqual(
                    [(live / name).read_text(encoding="utf-8") for name in names],
                    ["old-" + name for name in names],
                )
            else:
                self.assertEqual(saved.state, "recovery_required")
                self.assertTrue(saved.rollback_errors)
```

- [ ] **Step 2: Run and verify RED**

Run: `python -m unittest tests.test_lecture_publish_transaction -v`

Expected: FAIL because `publish_transaction` does not exist.

- [ ] **Step 3: Implement same-filesystem manifest transaction**

```python
# skills/lecture-to-notes/scripts/publish_transaction.py
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Mapping, Sequence

from lecture_model import write_json_atomic


@dataclass
class ManifestEntry:
    relative_path: str
    live: str
    staged: str
    backup: str
    old_exists: bool
    old_sha256: str | None
    new_sha256: str
    state: str = "prepared"
    verified_sha256: str | None = None


@dataclass
class LectureManifest:
    run_id: str
    lecture_id: str
    manifest_path: str
    recovery_path: str
    created_at: str
    updated_at: str
    state: str
    entries: list[ManifestEntry]
    error: str | None = None
    rollback_errors: list[str] = field(default_factory=list)
    persistence_errors: list[str] = field(default_factory=list)


@dataclass
class PublishResult:
    ok: bool
    rolled_back: bool
    error: str | None


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_manifest(
    run_id: str,
    lecture_id: str,
    live_root: Path,
    stage_root: Path,
    backup_root: Path,
    relative_paths: list[str],
) -> LectureManifest:
    if live_root.anchor.casefold() != stage_root.anchor.casefold():
        raise ValueError("live and staging roots must use the same filesystem anchor")
    transaction_root = backup_root / run_id / "lectures" / lecture_id
    manifest_path = transaction_root / "transaction.json"
    recovery_path = backup_root / "_recovery" / f"{run_id}-{lecture_id}.json"
    if manifest_path.exists():
        raise FileExistsError(f"transaction already exists: {manifest_path}")
    entries = []
    for relative in relative_paths:
        live = live_root / relative
        staged = stage_root / relative
        backup = transaction_root / "files" / relative
        if not staged.is_file():
            raise FileNotFoundError(f"staged manifest input missing: {relative}")
        old_exists = live.is_file()
        entries.append(ManifestEntry(
            relative_path=relative,
            live=str(live),
            staged=str(staged),
            backup=str(backup),
            old_exists=old_exists,
            old_sha256=sha256(live) if old_exists else None,
            new_sha256=sha256(staged),
        ))
    now = utc_now()
    return LectureManifest(
        run_id=run_id, lecture_id=lecture_id, manifest_path=str(manifest_path),
        recovery_path=str(recovery_path), created_at=now, updated_at=now,
        state="prepared", entries=entries,
    )


def _write_manifest(manifest: LectureManifest) -> None:
    manifest.updated_at = utc_now()
    write_json_atomic(Path(manifest.manifest_path), asdict(manifest))


def _persist_or_record(manifest: LectureManifest) -> bool:
    try:
        _write_manifest(manifest)
        return True
    except Exception as exc:
        manifest.persistence_errors.append(f"{type(exc).__name__}: {exc}")
        return False


def _require_manifest_write(manifest: LectureManifest) -> None:
    if not _persist_or_record(manifest):
        raise IOError("transaction manifest persistence failed")


def _write_recovery_evidence(manifest: LectureManifest) -> Path:
    path = Path(manifest.recovery_path)
    transaction_dir = Path(manifest.manifest_path).parent.resolve()
    if path.parent.resolve() == transaction_dir or transaction_dir in path.resolve().parents:
        raise ValueError("recovery evidence must be outside transaction directory")
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json_atomic(path, asdict(manifest))
    return path


def rollback_lecture(manifest: LectureManifest, replace_func: Callable = os.replace) -> PublishResult:
    manifest.rollback_errors = []
    for entry in reversed(manifest.entries):
        live = Path(entry.live)
        try:
            if not entry.old_exists:
                if live.exists():
                    if not live.is_file() or sha256(live) != entry.new_sha256:
                        raise IOError("new live asset changed after this transaction")
                    live.unlink()
                entry.state = "rolled_back_deleted_new"
                entry.verified_sha256 = None
            else:
                if entry.old_sha256 is None:
                    raise IOError("old_exists entry is missing old_sha256")
                if live.is_file() and sha256(live) == entry.old_sha256:
                    entry.state = "old_verified"
                    entry.verified_sha256 = entry.old_sha256
                else:
                    backup = Path(entry.backup)
                    if not backup.is_file() or sha256(backup) != entry.old_sha256:
                        raise IOError("backup missing or hash mismatch")
                    restore_temp = live.with_name("." + live.name + ".rollback")
                    shutil.copy2(backup, restore_temp)
                    replace_func(restore_temp, live)
                    if sha256(live) != entry.old_sha256:
                        raise IOError("rollback hash mismatch")
                    entry.state = "rolled_back"
                    entry.verified_sha256 = entry.old_sha256
        except Exception as rollback_exc:
            entry.state = "rollback_failed"
            manifest.rollback_errors.append(f"{entry.relative_path}: {rollback_exc}")
        _persist_or_record(manifest)
    manifest.state = "rolled_back" if not manifest.rollback_errors else "recovery_required"
    _persist_or_record(manifest)
    if manifest.persistence_errors:
        try:
            _write_recovery_evidence(manifest)
        except Exception as evidence_exc:
            manifest.persistence_errors.append(f"recovery evidence: {type(evidence_exc).__name__}: {evidence_exc}")
    return PublishResult(
        False,
        not manifest.rollback_errors,
        None if not manifest.rollback_errors else " | ".join(manifest.rollback_errors),
    )


def _copy_replace_source(entry: ManifestEntry) -> Path:
    immutable = Path(entry.staged)
    if not immutable.is_file() or sha256(immutable) != entry.new_sha256:
        raise IOError(f"immutable staging source missing or changed: {entry.relative_path}")
    live = Path(entry.live)
    live.parent.mkdir(parents=True, exist_ok=True)
    temp = live.with_name(f".{live.name}.{entry.new_sha256[:12]}.publish")
    try:
        temp.unlink()
    except FileNotFoundError:
        pass
    shutil.copy2(immutable, temp)
    if sha256(temp) != entry.new_sha256:
        temp.unlink(missing_ok=True)
        raise IOError(f"replace temp hash mismatch: {entry.relative_path}")
    return temp


def publish_lecture(manifest: LectureManifest, replace_func: Callable = os.replace) -> PublishResult:
    try:
        _require_manifest_write(manifest)
        for entry in manifest.entries:
            if entry.old_exists:
                if entry.old_sha256 is None:
                    raise IOError(f"old hash missing: {entry.relative_path}")
                backup = Path(entry.backup)
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(entry.live, backup)
                if sha256(backup) != entry.old_sha256:
                    raise IOError(f"backup hash mismatch: {entry.relative_path}")
                entry.state = "backed_up"
            else:
                entry.state = "no_old_file"
            _require_manifest_write(manifest)
        manifest.state = "backed_up"
        _require_manifest_write(manifest)
        for entry in manifest.entries:
            entry.state = "replace_started"
            _require_manifest_write(manifest)
            replace_source = _copy_replace_source(entry)
            try:
                replace_func(replace_source, entry.live)
            finally:
                try:
                    replace_source.unlink()
                except FileNotFoundError:
                    pass
            entry.state = "live_changed"
            _require_manifest_write(manifest)
            actual = sha256(Path(entry.live))
            if actual != entry.new_sha256:
                raise IOError(f"published hash mismatch: {entry.relative_path}")
            entry.state = "new_verified"
            entry.verified_sha256 = actual
            _require_manifest_write(manifest)
        manifest.state = "committed"
        _require_manifest_write(manifest)
        return PublishResult(True, False, None)
    except Exception as exc:
        manifest.error = f"{type(exc).__name__}: {exc}"
        _persist_or_record(manifest)
        rollback = rollback_lecture(manifest, replace_func)
        message = manifest.error
        if rollback.error:
            message += "; rollback errors=" + rollback.error
        if manifest.persistence_errors:
            message += "; persistence errors=" + " | ".join(manifest.persistence_errors)
        return PublishResult(False, rollback.rolled_back, message)


def load_manifest(path: Path) -> LectureManifest:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return LectureManifest(
        run_id=raw["run_id"], lecture_id=raw["lecture_id"], manifest_path=raw["manifest_path"],
        recovery_path=raw["recovery_path"], created_at=raw["created_at"],
        updated_at=raw["updated_at"], state=raw["state"],
        entries=[ManifestEntry(**entry) for entry in raw["entries"]],
        error=raw.get("error"),
        rollback_errors=list(raw.get("rollback_errors", [])),
        persistence_errors=list(raw.get("persistence_errors", [])),
    )


def recover_incomplete_transaction(path: Path, replace_func: Callable = os.replace) -> PublishResult:
    manifest = load_manifest(path)
    if manifest.state == "committed" and all(Path(entry.live).is_file() and sha256(Path(entry.live)) == entry.new_sha256 for entry in manifest.entries):
        return PublishResult(True, False, None)
    old_state_restored = all(
        (entry.old_exists and Path(entry.live).is_file() and sha256(Path(entry.live)) == entry.old_sha256)
        or (not entry.old_exists and not Path(entry.live).exists())
        for entry in manifest.entries
    )
    if manifest.state == "rolled_back" and old_state_restored:
        return PublishResult(False, True, None)
    return rollback_lecture(manifest, replace_func)


def publish_course_homepage(
    run_id: str,
    staged_homepage: Path,
    live_homepage: Path,
    backup_root: Path,
    lecture_manifest_paths: Sequence[Path],
    course_audit: Mapping[str, object],
    replace_func: Callable = os.replace,
) -> PublishResult:
    manifests = [load_manifest(path) for path in lecture_manifest_paths]
    if len(manifests) != 11 or len({item.lecture_id for item in manifests}) != 11:
        raise ValueError("homepage publish requires 11 unique lecture manifests")
    if any(item.run_id != run_id or item.state != "committed" for item in manifests):
        raise ValueError("homepage publish requires 11 committed manifests from the same run")
    if any(
        not Path(entry.live).is_file() or sha256(Path(entry.live)) != entry.new_sha256
        for manifest in manifests for entry in manifest.entries
    ):
        raise ValueError("homepage publish requires every committed live hash to match its manifest")
    if course_audit.get("ok") is not True:
        raise ValueError("homepage publish requires a passing course audit")
    transaction_root = backup_root / run_id / "course-homepage"
    old_exists = live_homepage.is_file()
    entry = ManifestEntry(
        relative_path=live_homepage.name,
        live=str(live_homepage),
        staged=str(staged_homepage),
        backup=str(transaction_root / "files" / live_homepage.name),
        old_exists=old_exists,
        old_sha256=sha256(live_homepage) if old_exists else None,
        new_sha256=sha256(staged_homepage),
    )
    now = utc_now()
    manifest = LectureManifest(
        run_id=run_id,
        lecture_id="course-homepage",
        manifest_path=str(transaction_root / "transaction.json"),
        recovery_path=str(backup_root / "_recovery" / f"{run_id}-course-homepage.json"),
        created_at=now,
        updated_at=now,
        state="prepared",
        entries=[entry],
    )
    return publish_lecture(manifest, replace_func)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    rollback_parser = subparsers.add_parser("rollback")
    rollback_parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args(argv)
    result = rollback_lecture(load_manifest(args.manifest))
    print(f"[rollback] status={'complete' if result.rolled_back else 'recovery_required'}")
    return 0 if result.rolled_back else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

Implementation rule: staging and live roots must have equal `Path.anchor` and be verified by an opt-in filesystem probe before NAS publish. `shutil.move()` must not be used as the commit primitive because cross-filesystem behavior can become copy-then-delete. All handles must be closed before `os.replace()`.

- [ ] **Step 4: Run transaction matrix**

Run:

```powershell
python -m unittest tests.test_lecture_publish_transaction -v
```

Expected: `Ran 10 tests ... OK`；build manifest 與 homepage manifest 的 `old_exists`/`old_sha256`/`new_sha256` assertions PASS；四個 replace 位置逐一注入失敗後，兩個舊 live files 恢復且本交易新增的 `frames/new.jpg` 不存在；immutable staging 在 lecture/homepage replace 後仍存在，同一 manifest rollback 後 retry 可 committed；transaction directory 持續不可寫時，best-effort rollback 與外部 recovery evidence assertions PASS。

- [ ] **Step 5: Commit**

```powershell
git add -- "skills/lecture-to-notes/scripts/publish_transaction.py" "tests/test_lecture_publish_transaction.py"
git commit -m "feat(lecture): publish lectures transactionally"
```

---

### Task 11: Synthetic Fixture Integration：Extract 到 Audit

**Files:**
- Create: `tests/fixtures/lecture_rebuild/course/01 Synthetic.mp4`
- Create: `tests/fixtures/lecture_rebuild/course/01 Synthetic.srt`
- Create: `tests/fixtures/lecture_rebuild/course/01 Synthetic.json`
- Create: `tests/fixtures/lecture_rebuild/course/02 Failure.mp4`
- Create: `tests/fixtures/lecture_rebuild/course/02 Failure.srt`
- Create: `tests/fixtures/lecture_rebuild/course/02 Failure.json`
- Create: `tests/fixtures/lecture_rebuild/01.candidates.json`
- Create: `tests/fixtures/lecture_rebuild/02.candidates.json`
- Create: `tests/fixtures/lecture_rebuild/01.rewrite_results.json`
- Create: `tests/fixtures/lecture_rebuild/01.review_records.json`
- Create: `tests/fixtures/lecture_rebuild/02.rewrite_results.json`
- Create: `tests/fixtures/lecture_rebuild/02.review_records.json`
- Create: `tests/fixtures/lecture_rebuild/invalid-schema.json` — synthetic invalid paths/OCR/time fixture，not part of pairing inventory。
- Create: `tests/fixtures/lecture_rebuild/course/frames/` synthetic PNG files；與 canonical `frames/...` paths、legacy materialization live root 及 staging viewer relative URLs 使用同一根目錄契約。
- Modify: `tests/test_lecture_rebuild_pipeline.py`

**Interfaces:**
- Fixture contains only generated slides/text, no clinical identifiers, no official NR transcript。
- `rebuild_course.py --fixture-mode` injects fake detector/OCR by default; `--real-media-tools` is separate integration opt-in.

- [ ] **Step 1: Add failing fixture integration test**

```python
# append to tests/test_lecture_rebuild_pipeline.py
class FixturePipelineTests(unittest.TestCase):
    def test_fixture_pipeline_covers_four_frames_partial_frames_and_isolated_failure(self):
        fixture = ROOT / "tests" / "fixtures" / "lecture_rebuild" / "course"
        with tempfile.TemporaryDirectory() as td:
            result = run_fixture_pipeline(fixture, Path(td))
            self.assertEqual(result.completed_lectures, ["01"])
            self.assertEqual(result.failed_lectures, ["02"])
            report = json.loads((Path(td) / "01" / "01 Synthetic.audit.json").read_text(encoding="utf-8"))
            self.assertTrue(report["ok"])
            rendered = (Path(td) / "01" / "01 Synthetic.viewer.html").read_text(encoding="utf-8")
            self.assertEqual(rendered.count('class="frame-card"'), 10)
            formal = json.loads((Path(td) / "01" / "01 Synthetic.json").read_text(encoding="utf-8"))
            self.assertEqual([len(segment["frames"]) for segment in formal["segments"]], [1, 2, 3, 4])
            self.assertEqual(formal["segments"][1]["frames"][0]["ocr"], "")
            for segment in formal["segments"]:
                for frame in segment["frames"]:
                    source_frame = fixture / frame["path"]
                    staged_frame = Path(td) / "01" / frame["path"]
                    self.assertTrue(source_frame.is_file())
                    self.assertTrue(staged_frame.is_file())
                    self.assertEqual(
                        hashlib.sha256(staged_frame.read_bytes()).hexdigest(),
                        hashlib.sha256(source_frame.read_bytes()).hexdigest(),
                    )
            from lecture_model import load_lecture, validate_lecture_schema
            invalid_path = fixture.parent / "invalid-schema.json"
            invalid = load_lecture(invalid_path)
            findings = validate_lecture_schema(invalid, invalid_path.parent)
            by_code = {item.code for item in findings}
            self.assertTrue({"frame_path", "frame_time", "frame_ocr_type"}.issubset(by_code))
            self.assertIn("/absolute/not-allowed.jpg", {item.path for item in findings if item.code == "frame_path"})
            self.assertIn("frames/out-of-range.jpg", {item.path for item in findings if item.code == "frame_time"})
```

- [ ] **Step 2: Run and verify RED**

Run: `python -m unittest tests.test_lecture_rebuild_pipeline.FixturePipelineTests -v`

Expected: FAIL because fixture and `run_fixture_pipeline` are absent.

- [ ] **Step 3: Generate tiny deterministic fixture and pipeline adapter**

Create the MP4 files once with PowerShell-compatible ffmpeg commands; commit only the resulting tiny media, not generated staging:

```powershell
ffmpeg -y -f lavfi -i "testsrc2=size=320x180:rate=1:duration=4" -pix_fmt yuv420p ".\tests\fixtures\lecture_rebuild\course\01 Synthetic.mp4"
ffmpeg -y -f lavfi -i "color=c=black:s=320x180:d=2:r=1" -pix_fmt yuv420p ".\tests\fixtures\lecture_rebuild\course\02 Failure.mp4"
Get-FileHash ".\tests\fixtures\lecture_rebuild\course\01 Synthetic.mp4" -Algorithm SHA256
Get-FileHash ".\tests\fixtures\lecture_rebuild\course\02 Failure.mp4" -Algorithm SHA256
```

`01 Synthetic.json` must contain four consecutive segments covering unchanged ranges 0–1、1–2、2–3、3–4 seconds, each with a focused title containing `Glioblastoma`, and the formal frame counts must be exactly 1、2、3、4；these are rendered by the production `render()` path, not created by probe JavaScript。The first selected frame in segment 2 has exact `"ocr": ""` so the successful pipeline proves empty OCR is preserved and rendered as the explicit fallback label。All ten referenced PNG files must exist and be browser-loadable。`01 Synthetic.srt` must contain a real cue spanning `00:00:00,500 --> 00:00:01,500` so Task 12 can prove that playback of the committed 4-second synthetic MP4 advances through the cue and adds `.on` from the video's actual `timeupdate` event。`02 Failure.json` must contain one segment whose candidate manifest has only black/duplicate frames, causing `no valid frame` and preserving lecture 01 success。

Create `tests/fixtures/lecture_rebuild/invalid-schema.json` with this exact synthetic content；it remains outside `course/`, so it cannot create a fourth lecture pair:

```json
{
  "title": "Invalid synthetic schema",
  "segments": [{
    "start_sec": 0.0,
    "end_sec": 4.0,
    "title": "Invalid frame validation fixture",
    "summary_zh": "僅供驗證",
    "takeaways_zh": ["A", "B", "C", "D"],
    "editorial_notes_zh": [],
    "frames": [
      {"time": 1.0, "ocr": "absolute", "path": "/absolute/not-allowed.jpg"},
      {"time": 9.0, "ocr": null, "path": "frames/out-of-range.jpg"}
    ]
  }]
}
```

Expected RED: fixture test fails until empty OCR survives the real fixture pipeline and `validate_lecture_schema()` reports the exact absolute-path, out-of-range-time and non-string-OCR findings shown above。

Implement `run_fixture_pipeline()` using injected pure functions, not RapidOCR or long video processing:

```python
def run_fixture_pipeline(fixture_root: Path, output_root: Path) -> CourseRunResult:
    pairs = pair_lectures(fixture_root)

    def fixture_runner(pair: LectureInputs, stage_root: Path, spec: StageSpec) -> None:
        stage_root.mkdir(parents=True, exist_ok=True)
        if spec.name == "extract":
            source = fixture_root.parent / f"{pair.lecture_id}.candidates.json"
            shutil.copy2(source, stage_root / "candidate_frames.json")
            for item in json.loads(source.read_text(encoding="utf-8"))["candidates"]:
                src = fixture_root / item["path"]
                dst = stage_root / item["path"]
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
            return
        if spec.name == "rewrite-apply":
            shutil.copy2(fixture_root.parent / f"{pair.lecture_id}.rewrite_results.json", stage_paths(pair, stage_root)["rewrite"])
            shutil.copy2(fixture_root.parent / f"{pair.lecture_id}.review_records.json", stage_paths(pair, stage_root)["review"])
        run_stage(pair, stage_root, spec)

    def rebuild_one(pair: LectureInputs, stage_root: Path, stages=STAGE_ORDER):
        return rebuild_lecture(pair, stage_root, stages=stages, stage_runner=fixture_runner)

    return rebuild_course(pairs, output_root, rebuild_one=rebuild_one)
```

- [ ] **Step 4: Run fixture integration**

Run:

```powershell
python -m unittest tests.test_lecture_rebuild_pipeline.FixturePipelineTests -v
```

Expected: lecture 01 completes with four production-rendered chapter grids containing exactly 1/2/3/4 cards（10 formal frames total）and the exact empty OCR value preserved；lecture 02 fails at curate；the external invalid-schema fixture produces exact `frame_path`, `frame_time`, `frame_ocr_type` assertions；command exits test PASS because isolation is expected。

- [ ] **Step 5: Commit**

```powershell
git add -- "tests/fixtures/lecture_rebuild" "tests/test_lecture_rebuild_pipeline.py" "skills/lecture-to-notes/scripts/rebuild_course.py"
git commit -m "test(lecture): add synthetic rebuild fixture"
```

---

### Task 12: Viewer Browser E2E 與 769/768 邊界

**Files:**
- Create: `tests/test_lecture_viewer_e2e.py`
- Modify: `skills/lecture-to-notes/scripts/build_lecture_viewer.py:probe dispatch used only by fixture E2E`
- Reuse: `tests/fixtures/lecture_rebuild/course/` and `run_fixture_pipeline()` from Task 11；E2E opens the actual temporary staging viewer and its staged `frames/` assets。

**Interfaces:**
- Consumes: `run_fixture_pipeline()` 每次測試 class setup 產生的真實 staging viewer HTML through `file://`；不得讀取手工維護的 `expected/*.html`。
- Verifies: browser `JSON.parse(textContent)` for both raw `application/json` payloads；chapter state, deep link, search labels/navigation, transcript/OCR details, modal and frame seek；production renderer/fixture 產生的四個實際 chapter grids 必須分別有 1/2/3/4 張可成功載入的 PNG。Async probe 逐 grid/card `scrollIntoView()`，等待每張 lazy image 的 `load`/`error`，再 `await image.decode()` 並檢查 `naturalWidth/naturalHeight`；之後由真實 DOM 計算 columns/gap/overflow/visibility，並以正式 document-level delegated handler 點開每張圖的 modal。Probe 不得建立替代 `.frame-grid`/`.frame-card`；no candidate images；>768 2-column and <=768 single-column；and the committed synthetic MP4's real `readyState`/`error`/`play()`/advancing `currentTime` plus transcript highlighting driven by an actual media `timeupdate`。

- [ ] **Step 1: Write headless browser probe**

```python
# tests/test_lecture_viewer_e2e.py
import html as html_lib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "lecture-to-notes" / "scripts"))

from rebuild_course import run_fixture_pipeline
BROWSERS = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
]


def browser_path():
    for path in BROWSERS:
        if path.exists():
            return path
    raise unittest.SkipTest("Chrome or Edge not installed")


PROBE_START = "__NR_PROBE_RESULT_START__"
PROBE_END = "__NR_PROBE_RESULT_END__"


def extract_probe_result(dumped_dom: str) -> dict:
    match = re.search(
        re.escape(PROBE_START) + r"(.*?)" + re.escape(PROBE_END),
        dumped_dom,
        re.DOTALL,
    )
    if match is None:
        raise AssertionError("probe result sentinel missing from dumped DOM")
    return json.loads(html_lib.unescape(match.group(1)))


class LectureViewerE2ETests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.browser = browser_path()
        cls.temp = tempfile.TemporaryDirectory()
        output_root = Path(cls.temp.name)
        fixture_root = ROOT / "tests" / "fixtures" / "lecture_rebuild" / "course"
        result = run_fixture_pipeline(fixture_root, output_root)
        if result.completed_lectures != ["01"]:
            raise AssertionError(f"fixture pipeline did not build lecture 01: {result.to_dict()}")
        cls.html = output_root / "01" / "01 Synthetic.viewer.html"
        if not cls.html.is_file():
            raise AssertionError(f"staged viewer missing: {cls.html}")

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def probe(self, html: Path, width: int, script: str):
        url = html.resolve().as_uri() + "?t=1.5&probe=" + script
        completed = subprocess.run([
            str(self.browser), "--headless=new", "--disable-gpu", "--allow-file-access-from-files",
            "--autoplay-policy=no-user-gesture-required", "--virtual-time-budget=8000",
            f"--window-size={width},900", "--dump-dom", url,
        ], check=True, capture_output=True, text=True, encoding="utf-8")
        return extract_probe_result(completed.stdout)

    def test_probe_extraction_tolerates_hidden_attribute_serialization(self):
        dumped = (
            '<pre class="diagnostic" id="probe-result" hidden="">'
            + PROBE_START + '{&quot;ok&quot;:true,&quot;count&quot;:4}' + PROBE_END
            + '</pre>'
        )
        self.assertEqual(extract_probe_result(dumped), {"ok": True, "count": 4})

    def test_769px_is_two_columns_and_768px_is_one_column(self):
        html = self.html
        wide = self.probe(html, 769, "layout")
        narrow = self.probe(html, 768, "layout")
        self.assertEqual(wide["columns"], 2)
        self.assertEqual(narrow["columns"], 1)
        self.assertFalse(wide["overflow"])
        self.assertFalse(narrow["overflow"])

    def test_formal_frames_only_modal_seek_search_and_details(self):
        html = self.html
        state = self.probe(html, 1024, "interactions")
        self.assertEqual(state["formalFrames"], 10)
        self.assertEqual(state["candidateFrames"], 0)
        self.assertTrue(state["modalOpened"])
        self.assertTrue(state["seekMatched"])
        self.assertTrue(set(state["searchTypes"]).issuperset({"title", "summary", "takeaway", "editorial", "transcript"}))
        self.assertTrue(state["transcriptOpened"])
        self.assertTrue(state["ocrOpened"])
        self.assertTrue(state["deepLinkActivatedChapter"])
        self.assertTrue(state["timeUpdateActivatedChapter"])
        self.assertTrue(state["transcriptSeekMatched"])
        self.assertTrue(state["searchNavigationMatched"])
        self.assertTrue(state["modalClosedByEscape"])
        self.assertTrue(state["emptyEditorialHidden"])
        self.assertTrue(state["jsonPayloadParsed"])
        self.assertEqual([item["count"] for item in state["frameGridResults"]], [1, 2, 3, 4])
        for item in state["frameGridResults"]:
            self.assertEqual(item["columns"], 2)
            self.assertEqual(item["gap"], 12)
            self.assertFalse(item["overflow"])
            self.assertTrue(item["visible"])
            self.assertTrue(item["imagesLoaded"])
            self.assertEqual(item["delegatedClicks"], item["count"])

    def test_real_synthetic_media_loads_plays_and_highlights_transcript_from_actual_time(self):
        html = self.html
        state = self.probe(html, 1024, "media")
        self.assertGreaterEqual(state["readyState"], 2)
        self.assertIsNone(state["mediaError"])
        self.assertTrue(state["playResolved"])
        self.assertGreater(state["endTime"], state["startTime"])
        self.assertTrue(state["actualTimeUpdateObserved"])
        self.assertTrue(state["transcriptHighlighted"])
        self.assertTrue(state["jsonPayloadParsed"])
```

The probe dispatch is a fixed three-value allowlist（`layout`, `interactions`, `media`）and never evaluates query text。The code above writes only computed fixture state between fixed text sentinels `__NR_PROBE_RESULT_START__` / `__NR_PROBE_RESULT_END__` inside hidden `#probe-result`; Python extracts by sentinel regex and HTML-unescapes the payload, so Chromium may serialize `hidden=""` or reorder attributes without breaking extraction。Without one of those exact probe values it performs no probe action。`media` must finish through the asynchronous Promise before `--virtual-time-budget=8000` expires；a `probeError` object is an explicit test failure, never a skip。

- [ ] **Step 2: Run and verify RED**

Run: `python -m unittest tests.test_lecture_viewer_e2e -v`

Expected: FAIL until expected fixture HTML, raw-JSON browser parsing, measured visible/clickable 1–4 grids, real synthetic media playback and actual-time transcript highlighting all exist。

- [ ] **Step 3: Use the production fixture pipeline and implement probe hook**

`setUpClass()` above must call `run_fixture_pipeline()` and open its temporary `01/01 Synthetic.viewer.html`; this guarantees HTML、MP4 relative URL and all `frames/...` URLs use the same production staging layout。Do not generate or commit a second golden viewer tree。

Add a fixed probe dispatch table in viewer JavaScript; never evaluate arbitrary query text:

```javascript
function writeProbe(value){
  let node=document.getElementById('probe-result');
  if(!node){node=document.createElement('pre');node.id='probe-result';node.hidden=true;document.body.appendChild(node);}
  node.textContent='__NR_PROBE_RESULT_START__'+JSON.stringify(value)+'__NR_PROBE_RESULT_END__';
}
function parseJsonPayloads(){
  return {
    snapshot:JSON.parse(document.getElementById('canonical-snapshot').textContent),
    search:JSON.parse(document.getElementById('search-data').textContent),
  };
}
function runLayoutProbe(){
  const grid=document.querySelector('.frame-grid');
  const columns=getComputedStyle(grid).gridTemplateColumns.split(' ').filter(Boolean).length;
  writeProbe({columns,overflow:document.documentElement.scrollWidth>innerWidth,jsonPayloadParsed:Boolean(parseJsonPayloads().snapshot)});
}
async function waitForImage(image){
  image.scrollIntoView({block:'center',inline:'nearest'});
  if(!image.complete){
    await new Promise((resolve,reject)=>{
      image.addEventListener('load',resolve,{once:true});
      image.addEventListener('error',()=>reject(new Error('frame image load failed: '+image.src)),{once:true});
    });
  }
  if(typeof image.decode==='function'){
    try{await image.decode();}catch(error){throw new Error('frame image decode failed: '+image.src);}
  }
  return image.naturalWidth>0&&image.naturalHeight>0;
}
async function measureFrameGrids(){
  const grids=[...document.querySelectorAll('.chapter .frame-grid')];
  const results=[];
  for(const grid of grids){
    grid.scrollIntoView({block:'center'});
    const cards=[...grid.querySelectorAll(':scope > .frame-card')];
    const loaded=[];
    for(const card of cards){
      const image=card.querySelector('img');
      loaded.push(Boolean(image)&&await waitForImage(image));
    }
    let delegatedClicks=0;
    for(const card of cards){
      card.click();
      const modal=document.getElementById('frame-modal');
      const modalImage=document.getElementById('modal-image');
      if(modal.open&&modalImage.src===new URL(card.dataset.fullSrc,document.baseURI).href){delegatedClicks+=1;}
      if(modal.open)modal.close();
    }
    const style=getComputedStyle(grid);const rect=grid.getBoundingClientRect();
    results.push({
      count:cards.length,
      columns:style.gridTemplateColumns.split(' ').filter(Boolean).length,
      gap:Number.parseFloat(style.columnGap),
      overflow:grid.scrollWidth>grid.clientWidth,
      visible:rect.width>0&&rect.height>0&&cards.every(card=>card.getClientRects().length===1),
      imagesLoaded:loaded.every(Boolean),
      delegatedClicks,
    });
  }
  return results;
}
async function runInteractionProbe(){
  const payloads=parseJsonPayloads();
  const deepLinkTarget=[...document.querySelectorAll('.chapter')].find(chapter=>Number(chapter.dataset.start)<=1.5&&1.5<Number(chapter.dataset.end));
  const initialDeepLinkActivatedChapter=Boolean(deepLinkTarget&&deepLinkTarget.classList.contains('on'));
  const first=document.querySelector('.frame-card');first.click();
  const modalOpened=document.getElementById('frame-modal').open;
  document.getElementById('modal-seek').click();
  const seekMatched=Math.abs(video.currentTime-Number(first.dataset.frameTime))<0.01;
  const transcript=document.querySelector('.transcript-details');transcript.open=true;
  const ocr=document.querySelector('.ocr-details');ocr.open=true;
  const cue=document.querySelector('.transcript-cue');if(cue)cue.click();
  const transcriptSeekMatched=!cue||Math.abs(video.currentTime-Number(cue.dataset.time))<0.01;
  video.currentTime=Number(document.querySelector('.chapter').dataset.start);video.dispatchEvent(new Event('timeupdate'));
  const timeUpdateActivatedChapter=Boolean(document.querySelector('.chapter.on'));
  const searchTypes=new Set(payloads.search.map(item=>item.kind));
  search('Glioblastoma');const searchHit=document.querySelector('.sr');if(searchHit)searchHit.click();
  const searchNavigationMatched=!searchHit||Math.abs(video.currentTime-Number(searchHit.dataset.t))<0.01;
  document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape'}));
  writeProbe({
    formalFrames:document.querySelectorAll('.frame-card').length,
    candidateFrames:document.querySelectorAll('[data-candidate-frame]').length,
    modalOpened,seekMatched,searchTypes:[...searchTypes],transcriptOpened:transcript.open,
    ocrOpened:ocr.open,deepLinkActivatedChapter:initialDeepLinkActivatedChapter,
    timeUpdateActivatedChapter,transcriptSeekMatched,searchNavigationMatched,
    modalClosedByEscape:!document.getElementById('frame-modal').open,
    emptyEditorialHidden:[...document.querySelectorAll('.chapter')].some(chapter=>!chapter.querySelector('.editorial-note')),
    frameGridResults:await measureFrameGrids(),jsonPayloadParsed:Array.isArray(payloads.snapshot)&&Array.isArray(payloads.search),
  });
}
async function runMediaProbe(){
  const payloads=parseJsonPayloads();
  if(video.readyState<2){
    await new Promise((resolve,reject)=>{
      video.addEventListener('loadeddata',resolve,{once:true});
      video.addEventListener('error',()=>reject(new Error('media load failed')),{once:true});
    });
  }
  video.currentTime=0.6;
  const startTime=video.currentTime;
  let actualTimeUpdateObserved=false;
  const advanced=new Promise(resolve=>{
    const onTime=()=>{if(video.currentTime>1.0){actualTimeUpdateObserved=true;video.removeEventListener('timeupdate',onTime);resolve();}};
    video.addEventListener('timeupdate',onTime);
    setTimeout(resolve,3000);
  });
  let playResolved=true;
  try{await video.play();}catch(error){playResolved=false;}
  await advanced;
  video.pause();
  writeProbe({
    readyState:video.readyState,
    mediaError:video.error?video.error.code:null,
    playResolved,
    startTime,
    endTime:video.currentTime,
    actualTimeUpdateObserved,
    transcriptHighlighted:Boolean(document.querySelector('.transcript-cue.on')),
    jsonPayloadParsed:Array.isArray(payloads.snapshot)&&Array.isArray(payloads.search),
  });
}
const probeName=new URLSearchParams(location.search).get('probe');
const probes={layout:runLayoutProbe,interactions:runInteractionProbe,media:runMediaProbe};
if(Object.prototype.hasOwnProperty.call(probes,probeName)){
  Promise.resolve(probes[probeName]()).catch(error=>writeProbe({probeError:String(error)}));
}
```

- [ ] **Step 4: Run E2E at both boundaries**

Run: `python -m unittest tests.test_lecture_viewer_e2e -v`

Expected: PASS with computed grid measurements for 1/2/3/4 cards, browser `JSON.parse()` success, no overflow at both boundaries, and real MP4 `readyState>=2`, `error=null`, resolved `play()`, advancing time and transcript `.on`。An explicit Skip is allowed only when neither supported browser exists；on the implementation machine a Skip is not final acceptance, so install/use Chrome or Edge and capture a real PASS before Task 15。

- [ ] **Step 5: Commit**

```powershell
git add -- "tests/test_lecture_viewer_e2e.py" "skills/lecture-to-notes/scripts/build_lecture_viewer.py"
git commit -m "test(lecture): cover responsive viewer interactions"
```

---

### Task 13: Skill Contract、正式重跑入口與 Sync

**Files:**
- Modify: `skills/lecture-to-notes/SKILL.md:workflow/schema/commands/safety sections`
- Modify: `skills/lecture-to-notes/scripts/rebuild_course.py:CLI parser/main()`

**Interfaces:**
- Formal local entry is two-phase: `--stages extract,curate,evidence` writes `awaiting_review`; after human review files exist, `--stages rewrite-apply,render,audit --resume-awaiting-review <course-run.json>` completes the same run without changing source times.
- Formal publish entry: same command plus `--publish --backup-root <path> --confirm-course-id 20150804-NR`; no publish without explicit confirmation and a matching `preflight.json` receipt whose roots/count/source hashes match, `ok=true`, `replace_probe_passed=true`, and bound `run_id`/`course_run_sha256` match the staged `course-run.json`。Lecture inventory contract is explicit via `--expected-lecture-count`（default 11；sample flow passes 3）；跨 live/staging probe 另需 `--probe-live-replace` opt-in。任何講次 audit `ok != true` 或 publish `result.ok == false` 都立即停止同一 invocation；該講不得建立 manifest/replace，後續講次與首頁保持不變。

- [ ] **Step 1: Add CLI contract test**

```python
# append to tests/test_lecture_rebuild_pipeline.py
class RebuildCliContractTests(unittest.TestCase):
    def test_publish_requires_confirmation_and_backup_root(self):
        from rebuild_course import parse_args
        with self.assertRaises(SystemExit):
            parse_args(["course", "--publish"])
        args = parse_args(["course", "--staging-root", "stage", "--publish", "--backup-root", "backup", "--confirm-course-id", "20150804-NR"])
        self.assertTrue(args.publish)
        self.assertEqual(args.expected_lecture_count, 11)
        sample = parse_args(["course", "--staging-root", "stage", "--expected-lecture-count", "3"])
        self.assertEqual(sample.expected_lecture_count, 3)
        with self.assertRaises(SystemExit):
            parse_args(["course", "--staging-root", "stage", "--probe-live-replace"])
        probe = parse_args(["course", "--staging-root", "stage", "--probe-live-replace", "--confirm-course-id", "20150804-NR"])
        self.assertTrue(probe.probe_live_replace)
        with self.assertRaises(SystemExit):
            parse_args(["course", "--staging-root", "stage", "--expected-lecture-count", "0"])
        with self.assertRaises(SystemExit):
            parse_args(["course", "--staging-root", "stage", "--stages", "publish-homepage"])
        for mixed in ("extract,publish", "audit,publish-homepage", "preflight,extract"):
            with self.subTest(stages=mixed), self.assertRaises(SystemExit):
                parse_args([
                    "course", "--staging-root", "stage", "--stages", mixed,
                    "--publish", "--backup-root", "backup", "--confirm-course-id", "20150804-NR",
                ])

    def test_stop_predicate_covers_recovery_required_or_not_rolled_back(self):
        from publish_transaction import PublishResult
        from rebuild_course import publication_requires_stop
        manifest = type("M", (), {"state": "recovery_required"})()
        self.assertTrue(publication_requires_stop(PublishResult(False, True, "rollback error"), manifest))
        manifest.state = "rolled_back"
        self.assertTrue(publication_requires_stop(PublishResult(False, False, "not rolled back"), manifest))
        self.assertTrue(publication_requires_stop(PublishResult(False, True, "fully rolled back"), manifest))
        self.assertFalse(publication_requires_stop(PublishResult(True, False, None), manifest))

    def test_representative_sample_contract_requires_one_unique_id_per_category(self):
        from rebuild_course import select_representative_samples
        def pair(lecture_id, title):
            return type("P", (), {
                "lecture_id": lecture_id,
                "mp4": Path(f"{lecture_id} {title}.mp4"),
                "json": Path(f"{lecture_id} {title}.json"),
            })()
        selected = select_representative_samples([
            pair("01", "Brain tumor"), pair("02", "Vascular"), pair("03", "Spine"),
        ])
        self.assertEqual([item.lecture_id for item in selected], ["01", "02", "03"])
        with self.assertRaisesRegex(ValueError, "exactly one Brain tumor"):
            select_representative_samples([
                pair("01", "Brain tumor"), pair("02", "Brain neoplasm"), pair("03", "Spine"),
            ])

    def test_publish_blocks_missing_probe_unbound_run_and_changed_source_or_run_hash(self):
        from rebuild_course import (
            LectureInputs, bind_preflight_to_run, preflight_receipt_payload,
            verify_preflight_receipt,
        )
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); course = root / "course"; stage = root / "stage"; backup = root / "backup"
            course.mkdir(); stage.mkdir(); backup.mkdir()
            paths = [course / name for name in ("01.mp4", "01.srt", "01.json")]
            for path in paths:
                path.write_bytes(b"source")
            pair = LectureInputs("01", *paths)
            args = type("Args", (), {
                "course_root": course, "staging_root": stage, "backup_root": backup,
                "expected_lecture_count": 1,
            })()
            receipt_path = stage / "preflight.json"
            run_path = stage / "course-run.json"
            with self.assertRaisesRegex(ValueError, "passing preflight receipt"):
                verify_preflight_receipt(args, [pair])
            receipt = preflight_receipt_payload(
                args, [pair], ok=True, findings=[], replace_probe_passed=False,
            )
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            run_path.write_text('{"run_id":"run-1","source_hashes":{}}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "probe-backed"):
                verify_preflight_receipt(args, [pair])
            receipt["replace_probe_passed"] = True
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "bound to the staged run"):
                verify_preflight_receipt(args, [pair])
            bind_preflight_to_run(args, run_path)
            verify_preflight_receipt(args, [pair])
            original_run = run_path.read_bytes()
            run_path.write_text('{"run_id":"run-2","source_hashes":{}}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "staged run changed"):
                verify_preflight_receipt(args, [pair])
            run_path.write_bytes(original_run)
            paths[1].write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "source inventory changed"):
                verify_preflight_receipt(args, [pair])

    def test_middle_lecture_audit_failure_stops_before_its_manifest_and_preserves_it_later_lectures_and_homepage(self):
        from publish_transaction import PublishResult
        from rebuild_course import LectureInputs, publish_staged_course
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); course = root / "course"; stage = root / "stage"; backup = root / "backup"
            course.mkdir(); stage.mkdir(); backup.mkdir()
            homepage = course / "課程首頁.html"; homepage.write_text("old-homepage", encoding="utf-8")
            homepage_bytes = homepage.read_bytes(); homepage_hash = hashlib.sha256(homepage_bytes).hexdigest()
            pairs = []
            original_live = {}
            for lecture_id, audit_ok in (("01", True), ("02", False), ("03", True)):
                lecture_stage = stage / lecture_id; lecture_stage.mkdir()
                source = course / f"{lecture_id}.json"; source.write_text(f"old-{lecture_id}", encoding="utf-8")
                original_live[lecture_id] = source.read_bytes()
                mp4 = course / f"{lecture_id}.mp4"; mp4.write_bytes(b"v")
                srt = course / f"{lecture_id}.srt"; srt.write_text("s", encoding="utf-8")
                (lecture_stage / f"{lecture_id}.audit.json").write_text(json.dumps({"ok": audit_ok}), encoding="utf-8")
                pairs.append(LectureInputs(lecture_id, mp4, srt, source))
            (stage / "course-run.json").write_text('{"run_id":"run-audit-stop"}', encoding="utf-8")
            args = type("Args", (), {"staging_root": stage, "course_root": course, "backup_root": backup})()
            built = []
            def fake_builder(run_id, lecture_id, *rest):
                built.append(lecture_id)
                return type("Manifest", (), {
                    "run_id": run_id, "lecture_id": lecture_id,
                    "manifest_path": str(backup / run_id / lecture_id / "transaction.json"),
                    "state": "prepared",
                })()
            exit_code = publish_staged_course(
                args, pairs, manifest_builder=fake_builder,
                publisher=lambda manifest: PublishResult(ok=True, rolled_back=False, error=None),
            )
            self.assertEqual(exit_code, 1)
            self.assertEqual(built, ["01"])
            self.assertFalse((backup / "run-audit-stop" / "02" / "transaction.json").exists())
            for lecture_id in ("02", "03"):
                self.assertEqual((course / f"{lecture_id}.json").read_bytes(), original_live[lecture_id])
            self.assertEqual(homepage.read_bytes(), homepage_bytes)
            self.assertEqual(hashlib.sha256(homepage.read_bytes()).hexdigest(), homepage_hash)

    def test_any_publish_failure_stops_remaining_publication_and_locks_homepage(self):
        from publish_transaction import PublishResult, _write_manifest, load_manifest
        from rebuild_course import LectureInputs, publish_staged_course
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); course = root / "course"; stage = root / "stage"; backup = root / "backup"
            course.mkdir(); stage.mkdir(); backup.mkdir()
            homepage = course / "課程首頁.html"
            homepage.write_text("old-homepage", encoding="utf-8")
            old_homepage_bytes = homepage.read_bytes()
            old_homepage_hash = hashlib.sha256(old_homepage_bytes).hexdigest()
            pairs = []
            for lecture_id in ("01", "02", "03"):
                lecture_stage = stage / lecture_id; lecture_stage.mkdir()
                source = course / f"{lecture_id}.json"; source.write_text("{}", encoding="utf-8")
                (course / f"{lecture_id}.mp4").write_bytes(b"v"); (course / f"{lecture_id}.srt").write_text("s", encoding="utf-8")
                (lecture_stage / f"{lecture_id}.json").write_text('{"segments":[]}', encoding="utf-8")
                (lecture_stage / f"{lecture_id}.audit.json").write_text('{"ok":true}', encoding="utf-8")
                pairs.append(LectureInputs(lecture_id, course / f"{lecture_id}.mp4", course / f"{lecture_id}.srt", source))
            (stage / "course-run.json").write_text('{"run_id":"run-stop"}', encoding="utf-8")
            args = type("Args", (), {"staging_root": stage, "course_root": course, "backup_root": backup})()
            called = []
            def fake_builder(run_id, lecture_id, *rest):
                called.append(lecture_id)
                path = backup / run_id / "lectures" / lecture_id / "transaction.json"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps({"run_id": run_id, "lecture_id": lecture_id, "manifest_path": str(path), "recovery_path": str(backup / "_recovery" / f"{run_id}-{lecture_id}.json"), "created_at": "x", "updated_at": "x", "state": "prepared", "entries": [], "rollback_errors": [], "persistence_errors": []}), encoding="utf-8")
                return load_manifest(path)
            def fake_publish(manifest):
                if manifest.lecture_id == "02":
                    manifest.state = "rolled_back"; _write_manifest(manifest)
                    return PublishResult(ok=False, rolled_back=True, error="injected but fully rolled back")
                manifest.state = "committed"; _write_manifest(manifest)
                return PublishResult(ok=True, rolled_back=False, error=None)
            exit_code = publish_staged_course(args, pairs, manifest_builder=fake_builder, publisher=fake_publish)
            self.assertEqual(exit_code, 1)
            self.assertEqual(called, ["01", "02"])
            self.assertEqual(homepage.read_bytes(), old_homepage_bytes)
            self.assertEqual(hashlib.sha256(homepage.read_bytes()).hexdigest(), old_homepage_hash)
            self.assertEqual((course / "03.json").read_text(encoding="utf-8"), "{}")
```

- [ ] **Step 2: Run and verify RED**

Run: `python -m unittest tests.test_lecture_rebuild_pipeline.RebuildCliContractTests -v`

Expected: FAIL until `parse_args()` enforces publish/expected-count/probe contracts, publish rejects a missing/stale/non-probed `preflight.json`, and `publish_staged_course()` stops immediately on every audit failure or failed lecture result（including a fully rolled-back failure）；audit-failed lecture must never build a manifest, later lectures remain untouched, and the integration assertion must show lecture 03 untouched and `課程首頁.html` bytes plus SHA-256 unchanged。

- [ ] **Step 3: Implement exact CLI validation and update SKILL.md**

```python
from lecture_audit import audit_course
from publish_transaction import (
    LectureManifest, PublishResult, build_manifest, load_manifest,
    publish_course_homepage, publish_lecture,
)


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("course_root", type=Path)
    parser.add_argument("--staging-root", type=Path, required=True)
    parser.add_argument("--stages", default="extract,curate,evidence")
    parser.add_argument("--expected-lecture-count", type=int, default=11)
    parser.add_argument("--probe-live-replace", action="store_true")
    parser.add_argument("--only")
    parser.add_argument("--resume-failed", type=Path)
    parser.add_argument("--resume-awaiting-review", type=Path)
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--backup-root", type=Path)
    parser.add_argument("--confirm-course-id")
    args = parser.parse_args(argv)
    stages = tuple(item.strip() for item in args.stages.split(",") if item.strip())
    allowed = set(STAGE_ORDER) | {"preflight", "publish", "publish-homepage"}
    if not stages or any(stage not in allowed for stage in stages):
        parser.error(f"--stages must use: {','.join(sorted(allowed))}")
    control_stages = {"preflight", "publish", "publish-homepage"}
    if any(stage in control_stages for stage in stages) and len(stages) != 1:
        parser.error("preflight, publish, and publish-homepage must be singleton stages")
    args.stage_list = stages
    if args.expected_lecture_count < 1:
        parser.error("--expected-lecture-count must be at least 1")
    if args.probe_live_replace and args.confirm_course_id != "20150804-NR":
        parser.error("--probe-live-replace requires --confirm-course-id 20150804-NR")
    if args.publish and (args.backup_root is None or args.confirm_course_id != "20150804-NR"):
        parser.error("--publish requires --backup-root and --confirm-course-id 20150804-NR")
    if any(stage in {"publish", "publish-homepage"} for stage in stages) and not args.publish:
        parser.error("publish stages require --publish")
    return args


def lecture_publish_paths(pair: LectureInputs, stage_root: Path) -> list[str]:
    paths = stage_paths(pair, stage_root)
    data = load_lecture(paths["formal_json"])
    relative = [pair.json.name, paths["viewer"].name, paths["pbf"].name, paths["v4"].name, paths["audit"].name]
    relative.extend(frame["path"] for segment in data["segments"] for frame in segment["frames"])
    return sorted(set(relative))


REPRESENTATIVE_PATTERNS = {
    "Brain tumor": re.compile(r"brain|tumou?r|腦.*腫瘤", re.IGNORECASE),
    "Vascular": re.compile(r"vascular|血管", re.IGNORECASE),
    "Spine": re.compile(r"spine|spinal|脊椎|脊髓", re.IGNORECASE),
}


def select_representative_samples(pairs: list[LectureInputs]) -> list[LectureInputs]:
    selected = []
    for category, pattern in REPRESENTATIVE_PATTERNS.items():
        matches = [pair for pair in pairs if pattern.search(f"{pair.mp4.name} {pair.json.name}")]
        if len(matches) != 1:
            raise ValueError(f"expected exactly one {category} lecture; matched {len(matches)}")
        selected.append(matches[0])
    if len({pair.lecture_id for pair in selected}) != 3:
        raise ValueError("representative categories must resolve to three unique lecture IDs")
    return selected


def preflight_receipt_payload(
    args,
    pairs: list[LectureInputs],
    ok: bool,
    findings: list[Finding],
    replace_probe_passed: bool,
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "ok": ok,
        "course_root": str(args.course_root.resolve()),
        "staging_root": str(args.staging_root.resolve()),
        "backup_root": str(args.backup_root.resolve()) if args.backup_root else None,
        "expected_lecture_count": args.expected_lecture_count,
        "replace_probe_passed": replace_probe_passed,
        "run_id": None,
        "course_run_sha256": None,
        "source_hashes": {pair.lecture_id: source_hash(pair) for pair in pairs},
        "pairs": [
            {"lecture_id": pair.lecture_id, "mp4": pair.mp4.name, "srt": pair.srt.name, "json": pair.json.name}
            for pair in pairs
        ],
        "findings": [
            {"severity": item.severity, "code": item.code, "message": item.message, "path": item.path}
            for item in findings
        ],
    }


def bind_preflight_to_run(args, course_run_path: Path) -> None:
    receipt_path = args.staging_root / "preflight.json"
    if not receipt_path.is_file():
        return
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("ok") is not True or receipt.get("replace_probe_passed") is not True:
        return
    course_run = json.loads(course_run_path.read_text(encoding="utf-8"))
    receipt["run_id"] = str(course_run["run_id"])
    receipt["course_run_sha256"] = hashlib.sha256(course_run_path.read_bytes()).hexdigest()
    write_json_atomic(receipt_path, receipt)


def verify_preflight_receipt(args, pairs: list[LectureInputs]) -> None:
    path = args.staging_root / "preflight.json"
    if not path.is_file():
        raise ValueError("publish requires a passing preflight receipt")
    receipt = json.loads(path.read_text(encoding="utf-8"))
    roots_match = (
        receipt.get("course_root") == str(args.course_root.resolve())
        and receipt.get("staging_root") == str(args.staging_root.resolve())
        and receipt.get("backup_root") == str(args.backup_root.resolve())
    )
    if (
        receipt.get("ok") is not True
        or receipt.get("replace_probe_passed") is not True
        or receipt.get("expected_lecture_count") != args.expected_lecture_count
        or not roots_match
    ):
        raise ValueError("publish requires a passing probe-backed preflight receipt for these roots and count")
    course_run_path = args.staging_root / "course-run.json"
    if not course_run_path.is_file() or not receipt.get("run_id") or not receipt.get("course_run_sha256"):
        raise ValueError("preflight receipt is not bound to the staged run")
    course_run = json.loads(course_run_path.read_text(encoding="utf-8"))
    if (
        receipt["run_id"] != str(course_run.get("run_id"))
        or receipt["course_run_sha256"] != hashlib.sha256(course_run_path.read_bytes()).hexdigest()
    ):
        raise ValueError("staged run changed after preflight binding")
    current = {pair.lecture_id: source_hash(pair) for pair in pairs}
    if receipt.get("source_hashes") != current:
        raise ValueError("source inventory changed after preflight")
    if course_run.get("source_hashes") not in ({}, current):
        raise ValueError("course-run source hashes do not match current inventory")


def publication_requires_stop(result: PublishResult, manifest: LectureManifest) -> bool:
    return not result.ok


def publish_staged_course(
    args,
    pairs: list[LectureInputs],
    manifest_builder=build_manifest,
    publisher=publish_lecture,
) -> int:
    course_run_path = args.staging_root / "course-run.json"
    course_run = json.loads(course_run_path.read_text(encoding="utf-8"))
    run_id = str(course_run["run_id"])
    failed = []
    processed_ids = []
    stopped_at = None
    for pair in pairs:
        processed_ids.append(pair.lecture_id)
        lecture_stage = args.staging_root / pair.lecture_id
        audit_path = stage_paths(pair, lecture_stage)["audit"]
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        if audit.get("ok") is not True:
            failed.append(pair.lecture_id)
            stopped_at = pair.lecture_id
            break
        manifest = manifest_builder(
            run_id, pair.lecture_id, args.course_root, lecture_stage, args.backup_root,
            lecture_publish_paths(pair, lecture_stage),
        )
        result = publisher(manifest)
        manifest_path = Path(manifest.manifest_path)
        saved = load_manifest(manifest_path) if manifest_path.is_file() else manifest
        if result.ok:
            continue
        failed.append(pair.lecture_id)
        if publication_requires_stop(result, saved):
            stopped_at = pair.lecture_id
            break
    if failed:
        untouched = [pair.lecture_id for pair in pairs if pair.lecture_id not in set(processed_ids)]
        print(f"[publish] failed={','.join(failed)} stopped_at={stopped_at or ''} untouched={','.join(untouched)} homepage=unchanged")
        return 1
    print(f"[publish] lectures={len(pairs)} homepage=unchanged")
    return 0


def publish_staged_homepage(args, pairs: list[LectureInputs]) -> int:
    if len(pairs) != 11:
        raise ValueError("homepage publish requires all 11 lectures")
    course_run = json.loads((args.staging_root / "course-run.json").read_text(encoding="utf-8"))
    run_id = str(course_run["run_id"])
    manifest_paths = [args.backup_root / run_id / "lectures" / pair.lecture_id / "transaction.json" for pair in pairs]
    staged_homepage = args.staging_root / "課程首頁.html"
    subprocess.run([
        sys.executable, str(SCRIPTS / "build_course_hub.py"), str(args.staging_root),
        "--title", "20150804 NR 神放複習", "--require-complete", "11", "-o", str(staged_homepage),
    ], check=True)
    report_paths = [stage_paths(pair, args.staging_root / pair.lecture_id)["audit"] for pair in pairs]
    viewer_names = [stage_paths(pair, args.staging_root / pair.lecture_id)["viewer"].name for pair in pairs]
    course_report = audit_course(report_paths, staged_homepage, viewer_names, expected_count=11)
    write_json_atomic(args.staging_root / "course.audit.json", course_report.to_dict())
    if not course_report.ok:
        print("[homepage] course audit failed; homepage=unchanged")
        return 1
    result = publish_course_homepage(
        run_id, staged_homepage, args.course_root / "課程首頁.html", args.backup_root,
        manifest_paths, course_report.to_dict(),
    )
    return 0 if result.ok else 1


def main(argv=None) -> int:
    args = parse_args(argv)
    pairs = pair_lectures(args.course_root)
    pairs = select_pairs(pairs, args.only, args.resume_failed, args.resume_awaiting_review)
    if args.stage_list == ("preflight",):
        result = run_preflight(
            args.course_root,
            staging_root=args.staging_root,
            backup_root=args.backup_root,
            expected_lecture_count=args.expected_lecture_count,
            sync_check=lambda: subprocess.run([sys.executable, str(ROOT / "sync_skills.py"), "--check"]).returncode,
            allow_replace_probe=args.probe_live_replace,
        )
        write_json_atomic(
            args.staging_root / "preflight.json",
            preflight_receipt_payload(
                args,
                result.pairs,
                ok=result.ok,
                findings=result.findings,
                replace_probe_passed=result.ok and args.probe_live_replace,
            ),
        )
        for finding in result.findings:
            print(f"[preflight] severity={finding.severity} code={finding.code} path={finding.path or ''}")
        return 0 if result.ok else 1
    if args.stage_list == ("publish",):
        verify_preflight_receipt(args, pairs)
        return publish_staged_course(args, pairs)
    if args.stage_list == ("publish-homepage",):
        verify_preflight_receipt(args, pairs)
        return publish_staged_homepage(args, pairs)
    result = rebuild_course(pairs, args.staging_root, stages=args.stage_list)
    if result.ok:
        bind_preflight_to_run(args, args.staging_root / "course-run.json")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

Update `SKILL.md` with exact schema, field rules, commands, manual-first rewrite, optional Claude mode, privacy gate, staging-only candidates, publish safety, cp950 progress, test commands and the prohibition on committing outputs. Include these exact execution examples:

```powershell
python ".\skills\lecture-to-notes\scripts\rebuild_course.py" "C:\local-fixture-course" --staging-root "C:\local-fixture-course\.staging" --stages "extract,curate,evidence"
python ".\skills\lecture-to-notes\scripts\rebuild_course.py" "C:\local-fixture-course" --staging-root "C:\local-fixture-course\.staging" --stages "rewrite-apply,render,audit" --resume-awaiting-review "C:\local-fixture-course\.staging\course-run.json"
python ".\skills\lecture-to-notes\scripts\rebuild_course.py" "C:\local-fixture-course" --staging-root "C:\local-fixture-course\.staging" --only "03" --resume-failed "C:\local-fixture-course\.staging\course-run.json"
```

Do not place the real NAS command in the routine examples; keep it only in Task 16 handoff.

- [ ] **Step 4: Run contracts, sync canonical skill and verify drift**

Run:

```powershell
python -m unittest tests.test_lecture_rebuild_pipeline.RebuildPreflightTests tests.test_lecture_rebuild_pipeline.RebuildCliContractTests -v
if ($?) { python ".\sync_skills.py" }
if ($?) { python ".\sync_skills.py" --check }
```

Expected: CLI contract、3-vs-11 inventory 與 publication-stop tests PASS；first sync command reports synchronized copies；`--check` exits 0。Derived copies remain ignored and are not staged.

- [ ] **Step 5: Commit**

```powershell
git add -- "skills/lecture-to-notes/SKILL.md" "skills/lecture-to-notes/scripts/rebuild_course.py" "tests/test_lecture_rebuild_pipeline.py"
git commit -m "docs(lecture): define canonical rebuild workflow"
```

---

### Task 14: Local Three-Lecture Sampling Gate（No NAS）

**Files:**
- No tracked file changes expected.
- Runtime outputs: operator-selected local staging outside Git only.

**Interfaces:**
- Consumes: locally copied/de-identified Brain tumor、Vascular、Spine lecture inputs, never direct NAS publish。
- Produces: one local `course-run.json` containing exactly three selected lecture IDs, plus three per-lecture audit JSON files, reviewer records and browser results outside repo。

- [ ] **Step 1: Obtain explicit permission for source access and define a non-Git local working root**

Use `C:\nr-rebuild-work\` only after confirming it exists or creating it with user permission. Do not copy source material into this repo.

- [ ] **Step 2: Run read-only sensitive-data and pairing preflight**

```powershell
python ".\skills\lecture-to-notes\scripts\rebuild_course.py" "C:\nr-rebuild-work\sample-input" --staging-root "C:\nr-rebuild-work\sample-staging" --expected-lecture-count 3 --stages "preflight"
$Preflight = Get-Content "C:\nr-rebuild-work\sample-staging\preflight.json" -Raw | ConvertFrom-Json
$Brain = @($Preflight.pairs | Where-Object { ($_.mp4 + ' ' + $_.json) -match '(?i)brain|tumou?r|腦.*腫瘤' })
$Vascular = @($Preflight.pairs | Where-Object { ($_.mp4 + ' ' + $_.json) -match '(?i)vascular|血管' })
$Spine = @($Preflight.pairs | Where-Object { ($_.mp4 + ' ' + $_.json) -match '(?i)spine|spinal|脊椎|脊髓' })
if ($Brain.Count -ne 1) { throw "Expected exactly one Brain tumor lecture; matched $($Brain.Count)." }
if ($Vascular.Count -ne 1) { throw "Expected exactly one Vascular lecture; matched $($Vascular.Count)." }
if ($Spine.Count -ne 1) { throw "Expected exactly one Spine lecture; matched $($Spine.Count)." }
$Samples = @($Brain[0], $Vascular[0], $Spine[0])
$UniqueIds = @($Samples.lecture_id | Sort-Object -Unique)
if ($UniqueIds.Count -ne 3) { throw "Brain tumor, Vascular, and Spine must resolve to three unique lecture IDs." }
$SampleIds = ($UniqueIds -join ',')
```

Expected PASS: exit 0；`$SampleIds` contains exactly three unique lecture IDs；dependencies and space checks PASS。The automated contract test invokes the same inventory with `expected_lecture_count=3` and passes, then with 11 and Expected FAIL code `lecture_count`。Any `sensitive_input` warning blocks external LLM mode for that lecture and requires manual/local-only rewrite.

- [ ] **Step 3: Run extract and curate in foreground**

```powershell
$Old = $env:PYTHONIOENCODING; $env:PYTHONIOENCODING = "cp950:strict"; python ".\skills\lecture-to-notes\scripts\rebuild_course.py" "C:\nr-rebuild-work\sample-input" --staging-root "C:\nr-rebuild-work\sample-staging" --expected-lecture-count 3 --stages "extract,curate,evidence" --only $SampleIds; $env:PYTHONIOENCODING = $Old
```

Expected: continuous cp950-safe progress; each chapter has 1–4 selected frames; all candidate files remain under staging and are absent from canonical JSON/viewer.

- [ ] **Step 4: Generate evidence packets and complete rewrite review**

For manual mode, reviewers edit only `rewrite_results.json` and `review_records.json` in the external staging root. Each record must confirm `source_faithful=true`, `case_details_verified=true`, `editorial_separated=true`, and match `packet_sha256`. If explicitly authorized to use Claude, first set credentials outside the repo and require the explicit flag:

```powershell
python ".\skills\lecture-to-notes\scripts\rewrite_lecture.py" "C:\nr-rebuild-work\sample-staging\Brain-tumor\lecture.json" --evidence "C:\nr-rebuild-work\sample-staging\Brain-tumor\evidence_packets.json" --rewrite "C:\nr-rebuild-work\sample-staging\Brain-tumor\rewrite_results.json" --review "C:\nr-rebuild-work\sample-staging\Brain-tumor\review_records.json" --provider claude --allow-external-llm --confirm-external-llm "TEXT-EVIDENCE-ONLY" -o "C:\nr-rebuild-work\sample-staging\Brain-tumor\rewritten.json"
```

Expected: candidate rewrite is generated but application stops pending human review; no image or original file is uploaded. If preflight finds sensitive data, expected result is non-zero with `external rewrite blocked by sensitive-data preflight`.

- [ ] **Step 5: Render, audit and browser-test all three samples**

```powershell
python ".\skills\lecture-to-notes\scripts\rebuild_course.py" "C:\nr-rebuild-work\sample-input" --staging-root "C:\nr-rebuild-work\sample-staging" --expected-lecture-count 3 --stages "rewrite-apply,render,audit" --only $SampleIds --resume-awaiting-review "C:\nr-rebuild-work\sample-staging\course-run.json"
python -m unittest tests.test_lecture_viewer_e2e -v
```

Expected: three audits `ok=true`; reviewers confirm terminology, no invented case detail, representative frames, OCR usefulness, viewer/PBF/V4/JSON equality, search/deep-link/transcript/seek behavior. Any failure returns to the earliest responsible canonical task; do not manually edit generated HTML.

- [ ] **Step 6: Record external evidence path, not content, in execution notes**

Execution report must list local audit/review paths and hashes only. Do not stage or commit local course content.

---

### Task 15: Full Automated Verification 與 Fresh-Context Review

**Files:**
- No new production files.
- Modify tests only if a real defect is found; use a new commit per fix and rerun the full gate.

**Interfaces:**
- Fresh verifier receives the approved spec, this plan, changed paths and commands, but not implementation-agent assumptions。

- [ ] **Step 1: Run all lecture unit and fixture tests**

```powershell
python -m unittest discover -s ".\tests" -p "test_lecture_*.py" -v
```

Expected: all tests PASS; browser tests produce real PASS on the implementation machine.

- [ ] **Step 2: Run cp950 strict gate**

```powershell
$Old = $env:PYTHONIOENCODING; $env:PYTHONIOENCODING = "cp950:strict"; python -m unittest tests.test_lecture_console_encoding tests.test_lecture_rebuild_pipeline tests.test_lecture_publish_transaction tests.test_lecture_audit -v; $env:PYTHONIOENCODING = $Old
```

Expected: PASS with no encoding exceptions.

- [ ] **Step 3: Run syntax, sync, diff and secret/output scans**

```powershell
python -m py_compile ".\skills\lecture-to-notes\scripts\lecture_model.py" ".\skills\lecture-to-notes\scripts\lecture_content_rules.py" ".\skills\lecture-to-notes\scripts\rewrite_evidence.py" ".\skills\lecture-to-notes\scripts\rewrite_lecture.py" ".\skills\lecture-to-notes\scripts\frame_curator.py" ".\skills\lecture-to-notes\scripts\render_v4_note.py" ".\skills\lecture-to-notes\scripts\lecture_audit.py" ".\skills\lecture-to-notes\scripts\rebuild_course.py" ".\skills\lecture-to-notes\scripts\publish_transaction.py"
python ".\sync_skills.py" --check
git diff --check
git status --short
```

Expected: all exit 0 except `git status` may show pre-existing unrelated user changes; no NAS/staging/output paths are staged.

- [ ] **Step 4: Dispatch fresh-context verifier**

Use a fresh verifier with this exact assignment:

```text
Read docs/superpowers/specs/2026-08-08-nr-viewer-rebuild-design.md and docs/superpowers/plans/2026-08-08-nr-viewer-rebuild.md. Inspect only the implementation commits and run representative lecture tests. Report each spec requirement as PASS/FAIL with file:symbol or command output evidence. Explicitly check schema, times unchanged, editorial separation, frame staging/1-4 rule, viewer 2x2/768px, transcript/OCR-only expansion, structured audit, V4/PBF/hub consistency, transaction rollback, cp950 output, privacy gate, skill sync, and that no NAS/sensitive outputs are tracked. Do not modify files.
```

Expected: no FAIL. Any FAIL returns to its owning task, receives a focused fix commit, and repeats Step 1–4.

- [ ] **Step 5: Create final implementation verification commit only if tracked verification artifacts changed**

Normally no commit is needed because Task 12 generates its staging viewer in `TemporaryDirectory` and has no tracked golden HTML。If a declared synthetic source fixture under `tests/fixtures/lecture_rebuild/course/` legitimately changed, stage only those exact fixture paths and commit `test(lecture): finalize rebuild verification`.

---

### Task 16: Exact NR 11-Lecture Execution Handoff、Publication 與 Rollback Runbook

**Files:**
- No Git-tracked changes.
- NAS runtime only after separate explicit authorization: `\\jieyu_nas\web\files\2015\08\20150804 NR 神放複習`.

**Interfaces:**
- Input course ID: `20150804-NR`.
- Transaction unit: one lecture's JSON, viewer, PBF, `.v4.md`, selected frame assets and audit report.
- Homepage transaction: independent and last, only after 11/11 lectures committed and course audit passes.

- [ ] **Step 1: Confirm execution authorization and freeze Git implementation revision**

Record `git rev-parse HEAD`, `python .\sync_skills.py --check`, and a clean staged index. Do not proceed if the user has not explicitly authorized NAS access and long-running processing.

- [ ] **Step 2: Set roots without embedding credentials**

```powershell
$Course = '\\jieyu_nas\web\files\2015\08\20150804 NR 神放複習'
$RunId = Get-Date -Format 'yyyyMMdd-HHmmss'
$Staging = Join-Path $Course ".rebuild-staging\$RunId"
$Backup = Join-Path $Course ".rebuild-backup"
```

Expected: both staging and backup are on the same UNC share as live files. Do not use `%TEMP%` or the repo as staging.

- [ ] **Step 3: Run opt-in UNC filesystem probe and course preflight**

Only with `--probe-live-replace`, preflight must create one uniquely named disposable probe directly under `$Course` and one under `$Staging`, test create/read/hash/cross-root replace-existing/cleanup, close all handles, and report that the live/staging share supports the required `os.replace()` path. Probe names start with `.nr-rebuild-*-probe-<uuid>.tmp` and can never collide with formal course filenames.

```powershell
python ".\skills\lecture-to-notes\scripts\rebuild_course.py" $Course --staging-root $Staging --backup-root $Backup --expected-lecture-count 11 --stages "preflight" --probe-live-replace --confirm-course-id "20150804-NR"
$Preflight = Get-Content (Join-Path $Staging 'preflight.json') -Raw | ConvertFrom-Json
$Brain = @($Preflight.pairs | Where-Object { ($_.mp4 + ' ' + $_.json) -match '(?i)brain|tumou?r|腦.*腫瘤' })
$Vascular = @($Preflight.pairs | Where-Object { ($_.mp4 + ' ' + $_.json) -match '(?i)vascular|血管' })
$Spine = @($Preflight.pairs | Where-Object { ($_.mp4 + ' ' + $_.json) -match '(?i)spine|spinal|脊椎|脊髓' })
if ($Brain.Count -ne 1) { throw "Expected exactly one Brain tumor lecture; matched $($Brain.Count)." }
if ($Vascular.Count -ne 1) { throw "Expected exactly one Vascular lecture; matched $($Vascular.Count)." }
if ($Spine.Count -ne 1) { throw "Expected exactly one Spine lecture; matched $($Spine.Count)." }
$UniqueIds = @(@($Brain[0].lecture_id, $Vascular[0].lecture_id, $Spine[0].lecture_id) | Sort-Object -Unique)
if ($UniqueIds.Count -ne 3) { throw "Representative categories must resolve to three unique lecture IDs." }
$SampleIds = ($UniqueIds -join ',')
```

Expected: 11 unique MP4/SRT/JSON pairs; first-lecture existing frames readable; extract/OCR/render/browser dependencies available; sufficient staging/backup space; sync check PASS; UNC replace probe PASS. Any failure stops before formal writes.

- [ ] **Step 4: Build and audit three samples without publish**

```powershell
python ".\skills\lecture-to-notes\scripts\rebuild_course.py" $Course --staging-root $Staging --stages "extract,curate,evidence" --only $SampleIds --confirm-course-id "20150804-NR"
```

Expected: human review and E2E gates from Task 14 PASS. Otherwise stop and fix canonical code; do not edit NAS viewer manually.

- [ ] **Step 5: Build all 11 lectures without publish**

```powershell
$Old = $env:PYTHONIOENCODING
$env:PYTHONIOENCODING = 'cp950:strict'
python ".\skills\lecture-to-notes\scripts\rebuild_course.py" $Course --staging-root $Staging --stages "extract,curate,evidence" --confirm-course-id "20150804-NR"
# Complete all 11 rewrite_results.json and review_records.json files, then:
python ".\skills\lecture-to-notes\scripts\rebuild_course.py" $Course --staging-root $Staging --stages "rewrite-apply,render,audit" --resume-awaiting-review (Join-Path $Staging 'course-run.json') --confirm-course-id "20150804-NR"
$Exit = $LASTEXITCODE
$env:PYTHONIOENCODING = $Old
if ($Exit -ne 0) { throw "NR rebuild failed with exit code $Exit" }
```

Expected: 11 lecture results; zero zero-frame chapters; every canonical time signature equals its source snapshot; every audit `ok=true`; course homepage is not yet changed.

- [ ] **Step 6: Review course-level consistency before publish**

Check 11 titles/terminology, JSON/viewer/PBF/V4 chapter counts/order/times/titles, all relative asset paths, viewer resource loads, and course homepage candidate links/status. Store the course audit under `$Staging`, not Git.

- [ ] **Step 7: Publish lectures one at a time**

```powershell
python ".\skills\lecture-to-notes\scripts\rebuild_course.py" $Course --staging-root $Staging --backup-root $Backup --expected-lecture-count 11 --stages "publish" --publish --confirm-course-id "20150804-NR"
```

Expected per lecture: manifest `prepared -> backed_up -> committed`; hashes verified。任何講次 `result.ok=False`（包含完整 rollback、`recovery_required` 或 `rolled_back=False`）都必須在當下停止同一 invocation，不呼叫任何後續講次的 manifest builder/publisher；未處理講次 live bytes 保持原 hash，staging/audit 不受影響，首頁維持舊 hash並禁止 Step 9。只有完整 rollback 且操作員另行判定安全時才可開始新的 publish invocation；不得在同一 invocation 繼續。Publish 前程式必須重新驗證 `$Staging\preflight.json` 為同一 live/staging/backup roots、11 講 source hashes 未變、`ok=true`、`replace_probe_passed=true`，且 receipt 的 `run_id`/`course_run_sha256` 與目前 `$Staging\course-run.json` 完全相符；缺少、未綁定或 stale receipt 時 Expected FAIL before manifest creation。

- [ ] **Step 8: Run post-publish 11-lecture smoke/E2E**

Verify all formal JSON/viewer/PBF/V4/assets and run browser smoke against file URLs. Expected: 11/11 pass, no mixed version according to manifest hashes, and homepage remains old until this gate passes.

- [ ] **Step 9: Publish homepage last as an independent single-file transaction**

Run only after Step 8 passes:

```powershell
python ".\skills\lecture-to-notes\scripts\rebuild_course.py" $Course --staging-root $Staging --backup-root $Backup --expected-lecture-count 11 --stages "publish-homepage" --publish --confirm-course-id "20150804-NR"
```

Expected: the publisher validates exactly 11 committed manifests from `$RunId`, rebuilds and audits the staged hub, backs up the old homepage, closes/fsyncs the sibling temporary file, and uses `os.replace()` for the final single-file switch. Homepage manifest state is `committed`; all links resolve to verified formal artifacts.

- [ ] **Step 10: Roll back one lecture when blocked after publication**

Use that lecture's transaction manifest; never restore only one derivative:

```powershell
python ".\skills\lecture-to-notes\scripts\publish_transaction.py" rollback --manifest (Join-Path $Backup "$RunId\lectures\01\transaction.json")
```

Expected: JSON, viewer, PBF, `.v4.md`, related selected frame assets and audit report all restore to recorded old hashes; then rerun cross-derived audit and viewer smoke. If rollback itself fails, preserve all backup/staging evidence, mark `recovery_required`, stop homepage publication, and report both original and rollback errors verbatim.

- [ ] **Step 11: Roll back homepage independently when necessary**

```powershell
python ".\skills\lecture-to-notes\scripts\publish_transaction.py" rollback --manifest (Join-Path $Backup "$RunId\course-homepage\transaction.json")
```

Expected: old homepage hash restored; lecture files remain unchanged.

- [ ] **Step 12: Retain evidence and delay cleanup**

Keep timestamped backup, staging manifests and audit reports until the new course has been manually stable for the agreed retention window. Cleanup must be a separate explicitly authorized operation; never delete backups during the rebuild command.

---

## References

Only official sources were used for API/library behavior. These points constrain implementation; they do not prove a third-party NAS/SMB appliance provides stronger guarantees than documented.

1. PySceneDetect documentation: https://www.scenedetect.com/docs/latest/
   - Required dependency contract is `scenedetect>=0.6.4,<0.8`; preflight reads installed distribution metadata and blocks anything outside this range. Pin/document the installed version and detector/backend settings in manifests.
2. PySceneDetect API: https://www.scenedetect.com/docs/latest/api.html
   - Scene detection returns `(start_time, end_time)` `FrameTimecode` pairs; candidate extraction must preserve explicit time values.
3. ContentDetector API: https://www.scenedetect.com/docs/latest/api/detectors.html
   - Threshold, minimum scene length, weights, kernel and filtering affect results; expose/persist them rather than relying on hidden defaults.
4. SceneManager API: https://www.scenedetect.com/docs/latest/api/scene_manager.html
   - `frame_skip` reduces accuracy; this plan fixes it to 0 and uses fixture characterization for boundaries.
5. FrameTimecode API: https://www.scenedetect.com/docs/latest/api/common.html
   - Display timecode and VFR frame numbering may be approximate; retain seconds and, when available, PTS/time-base metadata in staging manifests.
6. Python `os.replace()` and `fsync()`: https://docs.python.org/3/library/os.html#os.replace
   - `replace()` can replace an existing file; cross-filesystem operations may fail. A successful single rename/replace is not a multi-file transaction guarantee.
7. Python `tempfile`: https://docs.python.org/3/library/tempfile.html
   - Create temporary files in the target directory; Windows named temporary files and open handles have delete-sharing constraints.
8. Python `shutil`: https://docs.python.org/3/library/shutil.html
   - `move()` may fall back to copy-then-delete; `copytree()` is not transactional. Use `shutil` for backup/staging, never as the commit primitive.
9. Python `pathlib`: https://docs.python.org/3/library/pathlib.html
   - UNC shares are Windows drives; use absolute injected roots and never infer atomicity from path syntax alone.
10. Microsoft MoveFileExW: https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-movefileexw
    - Cross-volume move may become copy plus delete; SMB support does not promise NAS-wide transactional semantics.
11. Microsoft ReplaceFileW: https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-replacefilew
    - Replacement/backup volume and permissions matter; partial failure states require recovery testing.
12. pytest temporary paths: https://docs.pytest.org/en/stable/how-to/tmp_path.html
    - `tmp_path` is isolated per test, but this repo retains its established `unittest`/`TemporaryDirectory` idiom to avoid adding a runner dependency. Do not point `--basetemp` at shared NAS paths.
13. pytest monkeypatch: https://docs.pytest.org/en/stable/how-to/monkeypatch.html
    - Inspired the failure-injection boundary; this repo implements equivalent scoped injection via function parameters and `unittest.mock`.
14. pytest fixtures: https://docs.pytest.org/en/stable/how-to/fixtures.html
    - Teardown ordering informs one-state-change-per-fixture design; cleanup failure is tested separately.
15. pytest capture/logging: https://docs.pytest.org/en/stable/how-to/capture-stdout-stderr.html and https://docs.pytest.org/en/stable/how-to/logging.html
    - CLI progress/error assertions must preserve original failures and rollback outcomes; current implementation uses `unittest` stream capture where applicable.
16. Claude structured outputs: https://platform.claude.com/docs/en/build-with-claude/structured-outputs.md
    - Optional Claude rewrite uses the official SDK and `output_config.format` JSON schema, never assistant prefill or raw HTTP.
17. Claude vision/privacy boundary: https://platform.claude.com/docs/en/build-with-claude/vision.md
    - This plan does not upload lecture images; only preflight-approved text evidence may be sent, behind an explicit opt-in.
18. Anthropic Python SDK: https://github.com/anthropics/anthropic-sdk-python
    - Use `anthropic.Anthropic()` credential resolution, typed SDK errors/response blocks, and check `stop_reason` before consuming content.

## Implementation Execution Handoff

1. Create an isolated implementation worktree with `superpowers:using-git-worktrees` if the executor wants isolation; do not move or discard the current dirty working tree.
2. Execute Task 1–13 using `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans`; each task ends with its own tests and commit.
3. After Task 13, run Task 15 automated/fresh-context verification before any real course access.
4. Task 14 may run only with permission to use local/de-identified sample sources.
5. Task 16 may run only after a new explicit user authorization covering NAS access, long video processing, backups and publication.
6. Never push automatically. Never commit NAS/staging/backup/audit/rewrite content.

## Plan Self-Review Record

- Spec coverage: every design requirement maps to Task 1–16, including focused-title/schema/path/OCR/time gates, candidate/formal frames, raw-JSON viewer payloads, single render call chain, measured responsive layout, real media playback/transcript state, V4/PBF/homepage, structured audit, staging/backup/rollback/recovery evidence, progress, three-sample uniqueness, 11-lecture rollout, fresh verification and Git/NAS boundaries。
- 未完成內容掃描：禁用的未完成標記與模糊測試指示均為零；implementation steps 均含具體 test code、minimal implementation、PowerShell 5.1 RED/GREEN command 與 Expected FAIL/PASS。
- Type/signature consistency: `Finding` originates in `lecture_model.py`; content/evidence/audit modules reuse it；`normalize_lecture()` is the sole schema adapter；viewer flow is exactly `main() -> render(data, cues, title, video_rel, media_dir: Path) -> build_blocks(data, cues)`；`AuditReport.ok`, `CourseRunResult.ok`, `ProgressEvent` chapter fields, `run_preflight(expected_lecture_count, allow_replace_probe)` and manifest state names/CLI flags remain consistent across tasks。
- Fresh-review hardening: Task 1–2 cover generic-title rejection, >=250-Han valid content, real Windows/POSIX absolute paths, OCR type and malformed string/null/negative/nonfinite times as structured findings；Task 3 copies and hash-verifies all 72 legacy assets into staging before dedup/1–4 selection；Task 5/7 use one `kind/start` block/search schema, unambiguous `parse_srt_text(str)`/`load_srt(Path)`, and parseable raw JSON without HTML entity mutation；Task 8 covers derivative-JSON filtering, writable live root, installable dependency contract, opt-in cross-root probe, 3-vs-11 count and metadata gate；Task 9 covers exact cp950 chapter/failure progress plus full-content MP4/SRT/JSON identity；Task 10 preserves immutable staging across lecture/homepage retry and writes external recovery evidence when the transaction directory stays unwritable；Task 11–12 use one self-contained `course/frames/` source, production staging materialization/hash checks, actual 1/2/3/4 grids, delegated modal clicks and real MP4 playback；Task 13 rejects mixed control/build stages, binds preflight to source/run hashes, and stops before a middle audit-failed lecture manifest while preserving that lecture, later lectures and `課程首頁.html` bytes/hash；Task 14 enforces one unique Brain tumor, Vascular and Spine lecture in one three-lecture `course-run.json`。
- Scope discipline: no unrelated viewer refactor, no NR-specific long-term code path, no direct NAS edit in implementation tasks, and no rollout before explicit authorization.
