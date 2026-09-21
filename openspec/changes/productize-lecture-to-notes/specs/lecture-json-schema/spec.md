## ADDED Requirements

### Requirement: Versioned canonical lecture JSON

The canonical lecture document SHALL be a JSON object whose top level contains: `schema_version` (the string "2.0"), `stem`, `title`, `duration_sec` (number), `source` (object with video, subtitle.path, subtitle.origin in {asr, official}, subtitle.engine, subtitle.lang, subtitle.offset_model as object {a, b} or null), `profile` (string), `overall_summary_zh` (100 to 500 characters), `takeaways_zh` (6 to 12 strings), `segments` (array), `corrections` (array of objects with heard, correct, source), `unverified_terms` (array of strings), and optional `ocr_meta`.

Each element of `segments` SHALL contain: `index` (integer, starting at 1, consecutive), `start_sec`, `end_sec` (numbers; each segment's end_sec equals the next segment's start_sec; the last end_sec equals floor(duration_sec)), `start_time`, `end_time` (HH:MM:SS strings consistent with the seconds), `title`, `summary_zh`, `bullets_zh` (array of objects with text (required), t (number or null), kind in {synthesis, quote}), `quotes_zh` (array of objects with text and t), `frame` (string or null), `frames` (array of strings), `frame_ocr` (array of objects with frame and text), `editorial_notes_zh` (array of strings).

#### Scenario: Valid document passes

- **WHEN** `l2n check json lecture.json` is run on a document satisfying every rule above
- **THEN** the command prints `[json] ok` and exits 0

#### Scenario: Structural violations are errors

- **WHEN** a document has segments whose index sequence is 1, 2, 4 or whose end_sec of segment 2 differs from start_sec of segment 3
- **THEN** `l2n check json` lists each violation with the segment index and exits 2

##### Example: boundary checks

| Input | Expected | Notes |
| ----- | -------- | ----- |
| overall_summary_zh of 99 characters | error: overall_summary_zh length 99 < 100 | lower bound |
| overall_summary_zh of 500 characters | ok | inclusive upper bound |
| takeaways_zh with 13 items | error: takeaways_zh count 13 > 12 | upper bound |
| bullets_zh item is a bare string | error: segment N bullets_zh[i] is not an object (legacy?) | v2 requires objects |
| start_time "01:02:03" with start_sec 3722 | error: start_time mismatch | 01:02:03 is 3723 |

### Requirement: Legacy documents are migrated, not silently accepted

A document without `schema_version` SHALL be treated as legacy 1.x. `l2n check json` SHALL refuse it with the message `legacy schema detected; run: l2n migrate <file>` and exit 2. `l2n migrate <file>` SHALL rewrite it in place as 2.0, keeping a copy at `<file>.bak`, applying these conversions: string bullets become {text, t: null, kind: "synthesis"}; missing quotes_zh, editorial_notes_zh, corrections, unverified_terms become empty arrays; missing source becomes {video: "<stem>.mp4", subtitle: {path: "<stem>.srt", origin: "asr", engine: null, lang: null, offset_model: null}}; missing profile becomes "generic"; missing title becomes stem.

#### Scenario: Migration round trip

- **WHEN** `l2n migrate old.json` is run on a legacy document with 41 segments and string bullets
- **THEN** old.json.bak equals the original bytes, old.json has schema_version "2.0", every bullet is an object with kind "synthesis", segment count remains 41, and `l2n check json old.json` exits 0

### Requirement: Atomic UTF-8 writes without BOM

Every write of a canonical JSON document SHALL serialize as UTF-8 without byte order mark, with two-space indentation and non-ASCII characters unescaped, to a temporary file in the same directory, then replace the target by rename.

#### Scenario: Interrupted write leaves the original intact

- **WHEN** the process is killed after the temporary file is partially written
- **THEN** the original target file is unchanged and parses successfully

#### Scenario: No BOM

- **WHEN** any canonical JSON is written
- **THEN** the first three bytes of the file are not EF BB BF
