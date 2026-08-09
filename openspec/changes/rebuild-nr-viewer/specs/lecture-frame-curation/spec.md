## ADDED Requirements

### Requirement: Candidate frames exist only in staging
Scene extraction and OCR SHALL write candidate image assets and `candidate_frames.json` only under the lecture staging root. Candidate frames SHALL NOT be inserted into canonical JSON or displayed by the viewer until curation selects them into `segments[].frames`.

#### Scenario: Extraction completes
- **WHEN** scene detection extracts candidate images and OCR processes them
- **THEN** the staging manifest records detector settings, the installed PySceneDetect version, candidate time/path/OCR/quality fields, and canonical JSON remains unchanged

### Requirement: Supported deterministic scene extraction
The extractor SHALL use PySceneDetect `>=0.6.4,<0.8`, preserve scene times in seconds from `FrameTimecode`, set `frame_skip` to zero, record detector type, threshold and minimum scene length, and fail preflight when the installed version is outside the supported range.

#### Scenario: Unsupported dependency version
- **WHEN** preflight detects PySceneDetect `0.8.0`
- **THEN** it emits a blocking `scenedetect_version` finding before course processing

### Requirement: Legacy formal frames are materialized safely
Before first-lecture curation, all 72 existing formal frames SHALL be copied with metadata preservation into that lecture's staging tree, each copy SHALL match the source SHA-256, and the normalized legacy candidates SHALL be tagged `source="legacy-formal"`. Candidate merging SHALL deduplicate equal path/time pairs without dropping distinct legacy assets.

#### Scenario: First lecture legacy migration
- **WHEN** the first lecture exposes 72 readable formal frame paths
- **THEN** staging contains 72 hash-identical files and the deduplicated candidate pool contains all 72 legacy candidates

#### Scenario: Legacy copy is missing or changed
- **WHEN** a source frame is missing or its staged hash differs
- **THEN** curation fails before canonical output is written

### Requirement: Each chapter has one to four formal frames
The curator SHALL select one to four unique, readable, time-valid formal frames per segment using deterministic quality and duplicate filtering. Four frames SHALL be the target; one to three SHALL produce a visible audit warning; zero valid frames SHALL be a hard failure. Blank, severely blurred, unrelated, duplicate, or placeholder images SHALL NOT be used to satisfy the count.

#### Scenario: Four ranked frames are available
- **WHEN** a segment has more than four in-range valid candidates
- **THEN** the four highest-ranked unique frames are returned in chronological order

#### Scenario: No valid frame remains
- **WHEN** every candidate is out of range, black, unreadable, or duplicate-invalid
- **THEN** the segment fails with a `no valid frame` error and no formal JSON is produced for that lecture

### Requirement: Frame paths and boundary tolerance are auditable
Every formal frame time SHALL be within its segment bounds or within one generator-wide configured tolerance, and every path SHALL be viewer-resolvable, course-relative, and free of local absolute or NAS credential information. OCR failure SHALL preserve a visually useful frame with an empty OCR string and a structured audit note rather than fabricating text.

#### Scenario: A frame is within configured boundary tolerance
- **WHEN** a frame falls 0.20 seconds outside a segment and the configured tolerance is 0.25 seconds
- **THEN** time validation accepts the frame and records the tolerance in the staging or audit evidence
