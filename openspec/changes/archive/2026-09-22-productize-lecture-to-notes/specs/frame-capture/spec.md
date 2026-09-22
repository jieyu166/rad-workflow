## ADDED Requirements

### Requirement: Two capture modes with one manifest format

`l2n frames <video>` SHALL support `--mode scene` (default; PySceneDetect adaptive detector, falling back to the ffmpeg scene filter when PySceneDetect is not installed) and `--mode interval --every <seconds>` (fixed-interval sampling, default 45 seconds). Both modes SHALL write frames as `frames/<stem>-<MMSS>.png` (minutes zero-padded to at least two digits, seconds two digits) scaled to `--width` (default 1280), and a manifest `<stem>.frames.json` whose `frames` array contains objects with timestamp_sec, timestamp_display, frame (relative path), and sha256.

#### Scenario: Interval mode on a screen recording

- **WHEN** `l2n frames pacs.mp4 --mode interval --every 45` is run on a 6018-second video
- **THEN** 134 sample points are evaluated, the manifest lists every kept frame with its sha256, and the console prints the count of kept and deduplicated frames

#### Scenario: Scene mode fallback

- **WHEN** PySceneDetect is not importable
- **THEN** the command prints `[frames] scenedetect not installed, using ffmpeg scene filter` and still produces a manifest in the same format

### Requirement: Adjacent-duplicate suppression in interval mode

In interval mode the system SHALL compare each candidate to the previously kept frame as a 64x36 grayscale thumbnail and discard the candidate when the mean absolute difference is below `--diff-min` (default 4.0 on a 0 to 255 scale).

#### Scenario: Static screen is deduplicated

- **WHEN** ten consecutive samples show an unchanged screen
- **THEN** only the first is kept and the manifest count reflects nine discards

##### Example: threshold boundary

| Mean abs diff | Kept | Notes |
| ------------- | ---- | ----- |
| 3.99 | no | below default threshold |
| 4.00 | yes | threshold is inclusive |
| 25.3 | yes | clear change |

### Requirement: Frames are merged into the canonical JSON by time range

`l2n frames` SHALL, when `<stem>.json` exists, assign to each segment the manifest frames whose timestamp_sec falls in [start_sec, end_sec) as `frames`, set `frame` to the first of them, and when a segment has none, set `frame` to the latest earlier frame (or the first manifest frame if no earlier one exists) while leaving `frames` empty. The canonical JSON is rewritten atomically.

#### Scenario: Segment without its own frame

- **WHEN** segment 5 spans 1260 to 1440 seconds and the manifest has frames at 1254 and 1441 seconds
- **THEN** segment 5 has frames [] and frame equal to the 1254-second frame

### Requirement: Staged candidate curation

`l2n frames --stage` SHALL write candidates to `staging/frames/` instead of `frames/`, and `l2n frames --curate` SHALL promote candidates into `frames/` limited to `--max-per-segment` (default 4) per segment, verifying each file's sha256 against the staging manifest before copying, and writing `<stem>.curation.json` listing promoted and rejected candidates with reasons. The canonical JSON MUST reference only promoted frames.

#### Scenario: Hash mismatch blocks promotion

- **WHEN** a staged file's sha256 differs from its manifest entry
- **THEN** that candidate is rejected with reason `hash mismatch`, no file is copied for it, and the command exits 2 after processing the remaining candidates

### Requirement: OCR is cached and attached to frames

`l2n ocr <stem>.json` SHALL run RapidOCR on every referenced frame not already present in `<stem>.frames_ocr.json` (keyed by path with size and mtime fingerprint), store the text there, and write each segment's `frame_ocr` array in the canonical JSON. Missing rapidocr MUST exit 3.

#### Scenario: Cache hit skips OCR

- **WHEN** all 102 frames already have cache entries with matching fingerprints
- **THEN** the command prints `[ocr] 102 frames, 0 need OCR (102 cached)` and exits 0
