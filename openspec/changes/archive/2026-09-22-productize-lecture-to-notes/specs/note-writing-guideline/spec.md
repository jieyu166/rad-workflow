## ADDED Requirements

### Requirement: The guideline is a shipped, versioned document

The repository SHALL contain `docs/note-writing-guideline.md`, and the skill's `references/note-writing.md` SHALL reference it. The guideline MUST contain two clearly separated parts: "LLM 必須遵守" (rules for the model) and "機器可檢查" (rules enforced by `l2n check note`). The guideline SHALL carry a version string that `l2n check note` prints in its report.

#### Scenario: Guideline is discoverable from the skill

- **WHEN** an agent follows the skill's routing table for the task "寫筆記"
- **THEN** it is directed to the note-writing reference, which in turn names the guideline document and its version

### Requirement: Source precedence and evidence rules for the model

The "LLM 必須遵守" part SHALL state, at minimum, these rules in this order of precedence: official handout, then slide or screen frames viewed by eye, then transcript, then OCR text; OCR text is used only to decide which frame to open and MUST NOT be copied into the note. Every fact, number, and term in the note MUST be traceable to one of these sources. Terms that cannot be verified against any source MUST be listed in `unverified_terms` and described in References as not written into the body; they MUST NOT appear in the Note body.

#### Scenario: Unverifiable sign name

- **WHEN** the transcript renders a term as "Schrodinger's lobe sign" and neither handout nor frames confirm it
- **THEN** the note lists the term under References with the annotation that it is unverified and omitted from the body, and the body uses only the confirmed descriptive phrase

### Requirement: Quotation and synthesis rules for the model

The guideline SHALL require that speaker statements reproduced verbatim are wrapped in 「」 and, in faithful style, that each Note section contains at least one such quotation. It SHALL forbid pasting transcript sentences as bullets without synthesis. It SHALL require that a speaker's explicit statements of uncertainty or inability ("我沒辦法回答", "我現在沒辦法解釋") are recorded as such and never replaced by the model's own answer. It SHALL require that ASR errors are corrected in the body and enumerated in the References correction table with heard, correct, and source.

#### Scenario: Speaker declines to answer

- **WHEN** the transcript contains the speaker saying they have no experience with a question
- **THEN** the note records that the speaker declined, and does not supply an answer in the speaker's voice

### Requirement: Privacy rules for the model

The guideline SHALL require that names of attendees, patients, and other private individuals appearing in the transcript are not written into the note or the canonical JSON; roles (for example "與會醫師", "57 歲女性") replace them. The guideline SHALL require that the speaker's name is taken from the filename, handout, or on-screen badge, never from the transcript alone.

#### Scenario: Patient name in transcript

- **WHEN** a presenter reads a patient's full name aloud
- **THEN** the note contains only age, sex, and clinically relevant descriptors, and `l2n check note` finds no match for the configured personal-name patterns

### Requirement: Machine-checkable rules

`l2n check note <stem>.json --note <stem>.v4.md` SHALL enforce:
- R1 (error): every mandatory section exists in the mandated order.
- R2 (error): every `![[...]]` embed in the note resolves to an existing file relative to the note.
- R3 (error): every item in `unverified_terms` appears under References and does not appear under Note (layer 1-3).
- R4 (error): the References correction table exists and every row has non-empty heard and correct cells.
- R5 (warning, error when the profile sets `guideline.transcript_paste = "error"`): no line under Note (layer 1-3) contains a run of 40 or more characters (after removing whitespace and punctuation) that also appears in the transcript, unless that line is a blockquote or wrapped in 「」.
- R6 (error in faithful style, skipped in concise): every segment section contains at least one line wrapped in 「」 or formatted as a blockquote.
- R7 (error): no line matches a pattern listed in the effective `privacy.toml`.
The check SHALL print one line per finding with rule id, severity, and location, then a summary with counts, and exit 0 when no errors and no warnings, 1 when only warnings, 2 when any error.

#### Scenario: Transcript paste detected

- **WHEN** a Note bullet reproduces 58 consecutive characters of the transcript without 「」
- **THEN** the check reports R5 with the section title and the first 20 characters, and the exit code is 1 under the generic profile

##### Example: R5 boundary

| Pasted run length (chars, normalized) | Marked as quote | Result |
| ------------------------------------- | --------------- | ------ |
| 39 | no | pass |
| 40 | no | R5 finding |
| 120 | yes (「」) | pass |
| 120 | yes (blockquote) | pass |

#### Scenario: Reference example of a failing note

- **WHEN** the guideline's appendix example (a de-identified finance-lecture note whose Summary bullets are raw transcript sentences with uncorrected ASR errors and a truncated Evergreen quote) is checked
- **THEN** the check reports at least one R5 finding and one R4 finding, demonstrating the failure mode the guideline exists to prevent
