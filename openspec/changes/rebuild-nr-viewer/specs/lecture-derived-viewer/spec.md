## ADDED Requirements

### Requirement: Derived outputs use canonical JSON as the sole content source
The viewer, PBF, `.v4.md`, course hub, search index, and audit snapshot SHALL derive chapter order, times, titles, summaries, takeaways, editorial notes, and formal frame references from normalized canonical JSON. No renderer SHALL maintain a second chapter-content source.

#### Scenario: Derived outputs are audited
- **WHEN** a rendered title, order, time, summary, takeaway, editorial note, or frame reference differs from canonical JSON
- **THEN** cross-derived audit returns a blocking mismatch finding

### Requirement: Viewer preserves core navigation and playback
The viewer SHALL retain MP4 playback, chapter navigation and active chapter state, shareable `?t=<seconds>` links, stable chapter hashes, synchronized transcript, and seek actions from chapters, transcript cues, OCR entries, frames, and search results.

#### Scenario: Deep link opens a chapter time
- **WHEN** the viewer loads with `?t=90.5` or a stable chapter hash
- **THEN** playback seeks to the mapped time and the matching chapter becomes active without changing chapter boundaries

### Requirement: Chapter presentation separates formal content
Each chapter SHALL render, in order, a focused title, one or two summary paragraphs, exactly four takeaways, a formal frame grid, a separately styled editorial section only when notes are non-empty, and expandable transcript and OCR details. Expandable areas SHALL NOT display candidate frames or frames absent from canonical `frames`.

#### Scenario: Editorial notes are empty
- **WHEN** a chapter has an empty `editorial_notes_zh` list
- **THEN** no empty editorial box or prompt text is rendered

### Requirement: Formal frame layout is responsive and interactive
At viewport widths greater than 768px, each chapter frame area SHALL use a two-column equal-cell grid; at widths less than or equal to 768px, it SHALL use one column. Existing one to four frames SHALL fill in reading order without empty placeholders, clipping important content, overlap, or horizontal overflow. Every thumbnail SHALL load, open a larger modal, and seek to its frame time.

#### Scenario: Responsive boundary
- **WHEN** the same production-rendered fixture viewer is measured at 769px and 768px
- **THEN** computed layout reports two columns at 769px, one column at 768px, and no horizontal overflow

#### Scenario: Partial frame count
- **WHEN** a chapter contains one, two, or three formal frames
- **THEN** only those frames are rendered and no blank grid cells or synthetic images appear

### Requirement: Search uses one typed semantic schema
The lecture viewer SHALL index title, summary, takeaway, editorial note, slide OCR, and transcript entries as objects containing `kind`, `label`, `start`, `end`, and `text`. The course hub SHALL use the same fields and SHALL add only `viewer`, `lecture_id`, and `lecture_number`. Search results SHALL display their source label and navigate to the correct chapter or time.

#### Scenario: Search across all content types
- **WHEN** a query matches a title, summary, takeaway, editorial note, OCR text, or transcript cue
- **THEN** each result identifies its source type and selecting it seeks to its exact indexed start time

### Requirement: Embedded JSON is raw, parseable, and script-close safe
Every `application/json` script SHALL contain raw `json.dumps` output with only the `</` sequence escaped as `<\/`; it SHALL NOT contain HTML entity escaping. The browser SHALL parse both canonical snapshot and search payload with `JSON.parse(element.textContent)` even when text contains `</script>`, ampersands, or quotes.

#### Scenario: Hostile text remains parseable
- **WHEN** a title or OCR value contains `</script><img>` and quoted text
- **THEN** the script element remains closed safely, contains no `</script` sequence in its payload, and `JSON.parse` reproduces the original value
