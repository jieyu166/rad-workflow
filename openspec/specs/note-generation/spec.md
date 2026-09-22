# note-generation Specification

## Purpose

TBD - created by archiving change 'productize-lecture-to-notes'. Update Purpose after archive.

## Requirements

### Requirement: Deterministic skeleton note rendered from canonical JSON

`l2n render <stem>.json` SHALL produce `<stem>.v4.md` using only data present in the canonical JSON and the active profile/overlay templates, without calling any language model. Rendering the same JSON with the same effective profile twice MUST produce byte-identical output.

The skeleton SHALL contain, in this order: frontmatter rendered from the effective `note.frontmatter.yaml` template; `# Evergreen Note` (first item of takeaways_zh in bold quotation marks); `# Summary` (every takeaways_zh item as a bullet); `# Note (layer 1-3)` with one `## <index>、<title>` section per segment; `### References`; `## 題目` (one placeholder question per segment title); `## 學習驗證`.

Each segment section SHALL contain, in order: the segment's `frame` as an Obsidian embed `![[<path>]]` when present; `summary_zh`; each `quotes_zh` item as a blockquote whose text is wrapped in 「」 followed by the timestamp in parentheses; each `bullets_zh` item as a bullet, prefixed with 「」 when kind is quote.

The References section SHALL contain a table of `corrections` (columns heard, correct, source), a list of `unverified_terms` each marked as "未寫入本文", and the `source` block (video, subtitle origin, engine, offset model when not null).

#### Scenario: Deterministic output

- **WHEN** `l2n render a.json` is run twice
- **THEN** the two resulting files have identical sha256

#### Scenario: Unverified terms never leak into the body

- **WHEN** unverified_terms contains "Schrodinger's lobe sign"
- **THEN** that string appears under References and does not appear under Note (layer 1-3)

#### Scenario: Missing frame is tolerated

- **WHEN** a segment has frame null
- **THEN** its section starts with summary_zh and no embed line is emitted


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
### Requirement: Style selection

`--style faithful|concise` SHALL control rendering: faithful emits every quotes_zh item; concise emits at most one quotes_zh item per segment (the earliest) and omits bullets whose kind is quote. When `--style` is absent the value SHALL come from the effective profile/overlay `outputs.toml` key `note.style`, defaulting to concise in the built-in generic profile.

#### Scenario: Concise trims quotes

- **WHEN** a segment has three quotes_zh items and `--style concise` is used
- **THEN** exactly one blockquote appears in that section


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
### Requirement: LLM expansion contract

The skill SHALL instruct the language model to expand the skeleton in place: it reads `<stem>.v4.md`, the transcript, the canonical JSON, and any official handout, and writes back a full note that keeps the section order and frontmatter of the skeleton. Expansion output MUST pass `l2n check note`. The CLI SHALL provide `l2n render --expand-prompt` which prints the exact expansion instruction bundle (guideline text plus the file paths to read) for use by any agent.

#### Scenario: Expansion preserves skeleton structure

- **WHEN** an agent expands a skeleton and the result is checked
- **THEN** `l2n check note` finds every mandatory section present in the mandated order and every frame embed target existing on disk


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
### Requirement: Frontmatter comes from templates, not code

The public generic profile's frontmatter template SHALL output only title, date, source, and tags. Any additional field (for example noteVer, DateRev, subspecialty, tier, Parent Link) MUST originate from a profile or overlay template file, never from package code.

#### Scenario: Generic profile frontmatter

- **WHEN** `l2n render a.json` runs with no overlay and the generic profile
- **THEN** the frontmatter contains exactly the keys title, date, source, tags

#### Scenario: Overlay adds fields

- **WHEN** a user overlay `note.frontmatter.yaml` adds noteVer, DateRev, and subspecialty
- **THEN** the rendered frontmatter contains those keys with the templated values and the package code is unchanged

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