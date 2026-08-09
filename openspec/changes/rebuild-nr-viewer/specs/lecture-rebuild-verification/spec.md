## ADDED Requirements

### Requirement: Preflight blocks unsafe course processing
Preflight SHALL verify readable and writable course roots, exact MP4/SRT/formal-JSON pairing, expected unique lecture count, first-lecture 72-frame availability, ffmpeg/ffprobe, RapidOCR, OpenCC, supported PySceneDetect, browser availability, staging and backup space, and canonical skill mirror equality. Formal course processing SHALL NOT start when a blocking finding exists.

#### Scenario: Pairing or dependency fails
- **WHEN** a lecture has duplicate MP4 files or ffmpeg is unavailable
- **THEN** preflight emits a structured blocking finding and does not write formal course output

### Requirement: Rebuild is staged, resumable, and failure-isolated
The orchestrator SHALL execute `extract`, `curate`, `evidence`, `rewrite-apply`, `render`, and `audit` in that order, split by mandatory human review. Each lecture SHALL use an independent staging directory. A lecture generation failure SHALL be recorded while remaining lectures continue generation; resume SHALL accept exact lecture IDs and SHALL reject changed MP4, SRT, or JSON full-content hashes.

#### Scenario: One lecture fails during curation
- **WHEN** lecture 01 has zero valid frames and lecture 02 is valid
- **THEN** the course run records lecture 01 as failed, continues lecture 02, and preserves the source hashes needed for exact resume

### Requirement: Progress and command output are cp950-safe
Every long-running foreground stage SHALL continuously emit progress containing lecture ID, stage, completed/total, percent, status, chapter completed/total, and failure summary. All literal and rendered console text SHALL encode with cp950 strict and SHALL NOT use unsupported Unicode arrows, check marks, or mathematical symbols.

#### Scenario: Chapter failure is reported
- **WHEN** chapter 8 of 12 fails during curation
- **THEN** the emitted event includes chapter completion counters and the original exception type/message in cp950-encodable text

### Requirement: Audit is structured and fail-stop
Per-lecture audit SHALL report lecture ID, stage, findings with severity/code/message/segment/path, input hashes, warning and error counts, and optional browser results. Zero formal frames, changed time, invalid content, missing assets, derivative mismatch, failed browser functionality, or source-boundary failure SHALL make `ok=false`. Fewer than four but at least one valid frame SHALL remain `ok=true` with `frame_below_target` warning.

#### Scenario: Derived mismatch and zero frame coexist
- **WHEN** a lecture has a zero-frame chapter and a `.v4.md` title mismatch
- **THEN** one audit run records both blocking findings and returns non-zero status

### Requirement: TDD fixture and browser E2E cover boundary behavior
Implementation SHALL use RED/GREEN tests for schema, content, rewrite, frame curation, renderers, audit, preflight, orchestration, publication, and console encoding. A self-contained non-sensitive fixture SHALL cover formal frame counts 1, 2, 3, and 4, empty OCR, invalid paths/times/types, and an isolated zero-frame failure. Headless Chrome or Edge SHALL open the production staging viewer and verify raw JSON parsing, lazy image load/decode, computed 769/768 layout, modal/seek/search/details/deep links, actual synthetic MP4 playback, `timeupdate`, and transcript highlighting.

#### Scenario: Fixture pipeline runs
- **WHEN** the deterministic fixture pipeline builds two synthetic lectures
- **THEN** lecture 01 completes with frame counts `[1,2,3,4]`, lecture 02 fails independently at zero-frame curation, and no clinical identifiers or official NR content are present

### Requirement: Representative and full-course gates precede publication
After automated tests, a fresh-context verifier SHALL read back the approved artifacts and run representative tests. Real Brain tumor, Vascular, and Spine sampling SHALL select exactly one unique lecture per category and SHALL require separate source-access permission. Full 11-lecture processing SHALL require separate NAS authorization, 11 passing lecture audits, zero zero-frame chapters, consistent terminology and derivatives, and passing browser checks before publication.

#### Scenario: Sample categories are ambiguous
- **WHEN** the local inventory resolves Brain tumor to two lectures or resolves two categories to the same lecture ID
- **THEN** sampling fails before extract and reports the category conflict
