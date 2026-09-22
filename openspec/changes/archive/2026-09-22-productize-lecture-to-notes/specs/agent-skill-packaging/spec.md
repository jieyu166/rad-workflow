## ADDED Requirements

### Requirement: Single routed skill

The repository SHALL contain `skill/SKILL.md` with frontmatter `name: lecture2notes` and a description that names transcription, segmentation, frames, notes, viewer, and course hub. Its body SHALL be a routing table mapping the requested work to exactly one of six reference files under `skill/references/`: transcription.md, segmentation.md, frames-and-notes.md, note-writing.md, outputs-and-batch.md, profiles-and-overlay.md. SKILL.md MUST retain the six HARD RULES (language confirmed before transcription with no default; transcript never auto-rewritten without raw and corrections sidecars; source precedence handout, frames, transcript, OCR with OCR never copied into notes; frame extraction completes before dependent stages with tracked progress; in-house or patient material transcribed locally only; Traditional Chinese Taiwan wording with technical terms kept in English) and a completion-conditions section that requires running `l2n check` on every produced artifact. SKILL.md body MUST be at most 80 lines; detail lives in references.

#### Scenario: Routing covers every stage

- **WHEN** the routing table is read
- **THEN** each of the CLI stages transcribe, calibrate-subs, frames, ocr, scaffold, render, viewer, pbf, hub, check is mentioned by at least one row

#### Scenario: Skill and CLI agree on division of labor

- **WHEN** segmentation.md is read
- **THEN** it states that segment boundaries, titles, summaries, and takeaways are produced by the language model into canonical JSON v2 via `l2n scaffold` output, and that every mechanical stage is delegated to the corresponding `l2n` subcommand rather than reimplemented in prose

### Requirement: Three-target installer

`install.py` (also exposed as `l2n install-skill`) SHALL copy the `skill/` directory to a target directory chosen by `--target claude` (`~/.claude/skills/lecture2notes`), `--target codex` (`~/.agents/skills/lecture2notes`), or `--target opencode` (`~/.config/opencode/skills/lecture2notes`); `--dest <path>` SHALL override the directory; `--all` SHALL install to all three. Installation MUST copy files (no symbolic links), MUST NOT delete or overwrite any of the overlay file names listed in profiles-and-overlay that already exist in the target, and SHALL write `<target>/.installed.json` with version, source_sha256 (hash of the concatenated sorted skill file contents), installed_at (ISO 8601), and target.

#### Scenario: Install to all targets

- **WHEN** `l2n install-skill --all` runs on a machine with a home directory
- **THEN** all three target directories contain SKILL.md and the six reference files, each contains .installed.json, and the command prints the three paths

#### Scenario: Existing overlay is preserved

- **WHEN** the codex target already contains `corrections.json` authored by the user
- **THEN** after installation that file's bytes are unchanged

### Requirement: Drift check

`l2n install-skill --check [--target ...|--all]` SHALL recompute the source hash of the packaged skill and compare it with each target's installed content hash (recomputed from the target files, not read from .installed.json). Targets that match print `[ok] <path>`; targets that differ print `[drift] <path>` followed by one line per differing or missing file. The exit code SHALL be 0 when all checked targets match and 2 otherwise.

#### Scenario: Edited target is detected

- **WHEN** one line of `~/.claude/skills/lecture2notes/SKILL.md` is edited after installation
- **THEN** `l2n install-skill --check --all` prints `[drift]` for the claude target naming SKILL.md and exits 2

#### Scenario: Missing target

- **WHEN** the opencode target directory does not exist
- **THEN** `--check --all` prints `[drift] <path>: not installed` and exits 2

### Requirement: README states scope and privacy boundary

The repository README SHALL contain a section stating that ASR runs locally and uploads nothing, that language-model expansion sends transcript text to whichever model provider the agent uses and is therefore outside the local boundary, that Windows is the primary supported platform with Linux and macOS best-effort, and that the license is MIT. The README SHALL list the four engines with their local and GPU characteristics.

#### Scenario: Privacy section present

- **WHEN** README.md is searched for the heading containing "隱私" or "Privacy"
- **THEN** a section exists that mentions both local ASR and the language-model provider boundary
