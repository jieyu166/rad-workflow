## ADDED Requirements

### Requirement: Canonical lecture schema and normalization
The system SHALL normalize legacy lecture JSON into one canonical segment shape containing `start_sec`, `end_sec`, `title`, `summary_zh`, `takeaways_zh`, `editorial_notes_zh`, and `frames`. Each formal frame SHALL contain `time`, `ocr`, and a safe course-relative `path`; JSON writes SHALL use UTF-8 and atomic replacement.

#### Scenario: Legacy content is normalized without losing timing
- **WHEN** a lecture contains start/end aliases, legacy bullets, string frame paths, or legacy OCR maps
- **THEN** the normalized result uses only canonical fields and retains the exact original segment time signature

#### Scenario: Unsafe frame data is reported structurally
- **WHEN** a frame has an absolute or parent-traversing path, a non-finite or out-of-range time, a non-string OCR value, or a missing file
- **THEN** validation returns structured findings for every detected error without crashing on the first malformed frame

### Requirement: Chapter timing is immutable
Every rewrite, render, audit, and publication input SHALL preserve the source segment count and every exact start/end pair. A changed count or time SHALL be a hard failure before formal output or publication.

#### Scenario: A rewritten end time differs
- **WHEN** segment 3 changes from end time `120.0` to `120.1`
- **THEN** the system rejects the lecture and identifies segment 3 as the changed range

### Requirement: Focused Traditional Chinese content
Each segment SHALL have a title that identifies one diagnosis, finding, anatomy, or reading task; a `summary_zh` containing 250–600 Han characters in one or two paragraphs; exactly four non-empty distinct `takeaways_zh`; and a list-valued `editorial_notes_zh`. Content SHALL use Traditional Chinese Taiwan terminology and SHALL NOT contain Simplified Chinese-only characters, unfinished markers, template prompts, empty titles, generic chapter labels, or excessive verbatim transcript copying.

#### Scenario: Valid focused chapter content passes
- **WHEN** a segment has a focused medical title, a 250–600 character structured summary, four distinct takeaways, and valid editorial notes
- **THEN** content validation returns no error findings

#### Scenario: Invalid count and unfinished content fail
- **WHEN** a segment has three takeaways or contains an unfinished marker or template prompt
- **THEN** validation returns blocking findings for every violated rule

### Requirement: Speaker content and editorial knowledge remain separated
`summary_zh` and `takeaways_zh` SHALL contain only source-confirmed speaker content reorganized for clarity. General background, modern classification, extra differential diagnosis, or teaching guidance not explicitly stated by the speaker SHALL appear only in `editorial_notes_zh`. The system SHALL NOT invent patient history, imaging findings, diagnoses, or other case-specific facts.

#### Scenario: Review confirms source boundaries
- **WHEN** a rewrite is submitted for application
- **THEN** its review record confirms source faithfulness, case-detail verification, editorial separation, reviewer identity, and the matching evidence packet hash

### Requirement: Evidence-bound and privacy-gated rewrite
The system SHALL build one SHA-256-bound evidence packet per segment from transcript text, selected frame OCR, timing, and existing content. Manual reviewed import SHALL be the default rewrite provider. External LLM generation SHALL remain disabled unless the operator supplies the explicit allow flag, the exact confirmation string `TEXT-EVIDENCE-ONLY`, and a full outbound-payload sensitive-data scan returns clean; credentials SHALL come only from environment or official SDK resolution, images and original files SHALL NOT be uploaded, and generated candidates SHALL NOT be applied before human review.

#### Scenario: External generation lacks explicit permission
- **WHEN** an operator requests the external provider without the allow flag or exact confirmation string
- **THEN** the request fails before a network call

#### Scenario: Sensitive evidence blocks external generation
- **WHEN** the outbound packet contains a medical record number, birth date, phone number, national identifier, email, or another configured sensitive pattern
- **THEN** external generation is rejected and manual or local review remains available
