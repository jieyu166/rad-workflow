# derived-outputs Specification

## Purpose

TBD - created by archiving change 'productize-lecture-to-notes'. Update Purpose after archive.

## Requirements

### Requirement: Viewer is generated from canonical JSON v2

`l2n viewer <stem>.json` SHALL produce a single self-contained `<stem>.viewer.html` that references the video, frames, and subtitle by relative path and embeds the segment data from the canonical JSON. The viewer MUST render three layers (summary, transcript, frames), highlight the current segment and transcript cue during playback, jump playback when a segment card, transcript line, or frame is clicked, support a `?t=<seconds>` deep link, and provide cross-layer text search. Bullet items with a non-null `t` SHALL use that time; items with null `t` SHALL display an interpolated estimate marked with a tilde.

#### Scenario: Deep link

- **WHEN** the viewer is opened with `?t=1234`
- **THEN** playback seeks to 1234 seconds and the segment containing that time is highlighted

#### Scenario: Timed bullet

- **WHEN** a bullet has t = 812.5
- **THEN** clicking it seeks to 812.5 seconds and no tilde is shown for that bullet


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
### Requirement: PotPlayer chapter file is opt-in via outputs configuration

`l2n pbf <stem>.json` SHALL write `<stem>.pbf` with one chapter per segment (millisecond offsets, segment titles) using the video's stem so PotPlayer auto-loads it. The `run` command SHALL invoke pbf only when the effective `outputs.toml` sets `pbf = true`; the built-in generic profile SHALL set it to false.

#### Scenario: Generic profile skips pbf

- **WHEN** `l2n run video.mp4 --lang zh` runs with no overlay
- **THEN** no `.pbf` file is created and the stage list printed does not include pbf

#### Scenario: Overlay enables pbf

- **WHEN** the user overlay sets pbf = true
- **THEN** `l2n run` creates `<stem>.pbf` with a chapter count equal to the segment count


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
### Requirement: Course hub with cross-lecture search

`l2n hub <folder>` SHALL scan the folder for canonical JSON v2 documents and produce `課程首頁.html` containing one card per lecture (speaker, topic, duration, segment count, frame count, thumbnail, one-line summary) and a search index built from segment titles, takeaways, bullet text, quote text, and frame OCR text. Search results MUST link to the lecture viewer with `?t=` set to the matching segment's start. Cards SHALL be ordered by the pair (no, stem) compared as strings.

#### Scenario: OCR text is searchable

- **WHEN** a frame's OCR text contains "Haglund" and no transcript or bullet does
- **THEN** searching "Haglund" in the hub returns that lecture and segment


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
### Requirement: Card overrides via _titles.json

When `<folder>/_titles.json` exists, `l2n hub` SHALL read a mapping from stem to an object with optional no, speaker, and topic, and use those values on the card and for ordering instead of values derived from the JSON. Stems absent from the mapping keep derived values.

#### Scenario: Override applies

- **WHEN** _titles.json maps "20220925 MRI C1 wrist" to no "3" and topic "腕關節（上）"
- **THEN** that card shows the topic text "腕關節（上）" and sorts as the third card


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
### Requirement: Hub link integrity

`l2n hub` SHALL verify after writing that every relative href it emitted resolves to an existing file after percent-decoding, and SHALL report any missing target as an error with exit 2.

#### Scenario: Missing viewer

- **WHEN** a lecture JSON exists but its `.viewer.html` does not
- **THEN** the hub reports the missing file and exits 2

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