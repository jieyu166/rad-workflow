# stage-acceptance Specification

## Purpose

TBD - created by archiving change 'productize-lecture-to-notes'. Update Purpose after archive.

## Requirements

### Requirement: Per-stage acceptance checks

`l2n check <stage> <target>` SHALL implement four stages:
- `transcribe <stem>.srt`: SRT parses; cue numbers are consecutive from 1; every cue end is later than its start; times are monotonic; `<stem>.raw.srt` exists when `<stem>.corrections.json` exists; hallucination-loop warning as defined in transcription-engines.
- `frames <stem>.frames.json`: every listed frame file exists and its sha256 matches; timestamps are strictly increasing; frame count is at least 1.
- `json <stem>.json`: the canonical JSON v2 rules in lecture-json-schema; every segment has a non-null frame; every referenced frame path exists.
- `note <stem>.json --note <stem>.v4.md`: the machine-checkable rules R1 to R7 in note-writing-guideline.
Each check SHALL print one line per finding as `<severity> <rule-or-field> <location>: <message>`, then `<stage>: N errors, M warnings`, and exit 0 (clean), 1 (warnings only), or 2 (any error).

#### Scenario: Frame hash drift

- **WHEN** a frame file was regenerated after the manifest was written and its sha256 no longer matches
- **THEN** `l2n check frames` reports `error sha256 frames/x-0512.png: manifest 3f2a.. actual 91cc..` and exits 2

#### Scenario: Clean pipeline

- **WHEN** all four checks are run on outputs produced by `l2n run` on the test fixture
- **THEN** every check exits 0


<!-- @trace
source: productize-lecture-to-notes
updated: 2026-09-22
code:
  - ahk-scripts/usai-prompts/backup-spine-landmarks-20260922-114957/common.md
  - ahk-scripts/usai-prompts/spine.md
  - ahk-scripts/usai-prompts/common.md
  - ahk-scripts/usai-prompts/backup-spine-landmarks-20260922-114957/spine.md
  - ahk-scripts/簡碼 jai.ahk
  - ahk-scripts/usai-prompts/backup-spine-research-20260922-122422/spine.md
-->

---
### Requirement: Structured audit report

`l2n check --all <stem> --report <path>` SHALL run every applicable stage check and write a JSON report containing guideline_version, per-stage arrays of findings (severity, rule, location, message), and a summary object with total errors and warnings. The exit code SHALL be the maximum of the individual stage exit codes.

#### Scenario: Report is machine-readable

- **WHEN** the report is written
- **THEN** it parses as JSON and `summary.errors` equals the count of findings whose severity is error


<!-- @trace
source: productize-lecture-to-notes
updated: 2026-09-22
code:
  - ahk-scripts/usai-prompts/backup-spine-landmarks-20260922-114957/common.md
  - ahk-scripts/usai-prompts/spine.md
  - ahk-scripts/usai-prompts/common.md
  - ahk-scripts/usai-prompts/backup-spine-landmarks-20260922-114957/spine.md
  - ahk-scripts/簡碼 jai.ahk
  - ahk-scripts/usai-prompts/backup-spine-research-20260922-122422/spine.md
-->

---
### Requirement: Rebuild preflight is read-only

`l2n hub --preflight <folder>` and `l2n viewer --preflight <stem>.json` SHALL list every file that a real run would create or overwrite, with an indicator of whether it currently exists, and MUST NOT write anything. Exit code is 0 when the listing succeeds.

#### Scenario: Preflight touches nothing

- **WHEN** preflight is run and the folder's file list and mtimes are recorded before and after
- **THEN** the two recordings are identical


<!-- @trace
source: productize-lecture-to-notes
updated: 2026-09-22
code:
  - ahk-scripts/usai-prompts/backup-spine-landmarks-20260922-114957/common.md
  - ahk-scripts/usai-prompts/spine.md
  - ahk-scripts/usai-prompts/common.md
  - ahk-scripts/usai-prompts/backup-spine-landmarks-20260922-114957/spine.md
  - ahk-scripts/簡碼 jai.ahk
  - ahk-scripts/usai-prompts/backup-spine-research-20260922-122422/spine.md
-->

---
### Requirement: Transactional publication with rollback

`l2n publish <stem> --dest <dir>` SHALL copy a lecture's derivative set (viewer, pbf when enabled, note, frames directory, canonical JSON, subtitle) into the destination as one transaction: write a manifest listing each source path, destination path, and sha256; move any existing destination file to a timestamped backup directory beside the destination; copy all files to temporary names in the destination directory; verify each copy's sha256; rename all temporary names to final names; on any failure before completion, restore every backed-up file and remove every temporary file, then exit 2 with the failing path. Destination and source MUST be on the same filesystem; otherwise the command refuses with exit 2 before copying.

#### Scenario: Mid-copy failure rolls back

- **WHEN** the third of six files fails its sha256 verification
- **THEN** the destination contains exactly the files it had before the command, the backup directory is removed, and the command exits 2 naming the failed file

#### Scenario: Successful publication records a manifest

- **WHEN** all files are copied and verified
- **THEN** `<dest>/<stem>.publish.json` lists every file with its sha256 and the backup directory path (or null when nothing was replaced)

<!-- @trace
source: productize-lecture-to-notes
updated: 2026-09-22
code:
  - ahk-scripts/usai-prompts/backup-spine-landmarks-20260922-114957/common.md
  - ahk-scripts/usai-prompts/spine.md
  - ahk-scripts/usai-prompts/common.md
  - ahk-scripts/usai-prompts/backup-spine-landmarks-20260922-114957/spine.md
  - ahk-scripts/簡碼 jai.ahk
  - ahk-scripts/usai-prompts/backup-spine-research-20260922-122422/spine.md
-->