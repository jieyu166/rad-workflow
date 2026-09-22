# lecture2notes-vendoring Specification

## Purpose

TBD - created by archiving change 'adopt-lecture2notes-submodule'. Update Purpose after archive.

## Requirements

### Requirement: Pinned submodule

The repository SHALL include lecture2notes as a git submodule at `vendor/lecture2notes`, checked out at a release tag (v0.2.1 for this change). The submodule MUST NOT be placed under `skills/`, so that `sync_skills.py` does not enumerate it.

#### Scenario: Submodule is pinned to a tag

- **WHEN** `git submodule status` and `git -C vendor/lecture2notes describe --tags --exact-match` are run after a fresh clone with `--recurse-submodules`
- **THEN** the first lists `vendor/lecture2notes` and the second prints `v0.2.1`

#### Scenario: sync_skills ignores the submodule

- **WHEN** `python sync_skills.py --check` runs
- **THEN** its output does not mention lecture2notes and it exits 0


<!-- @trace
source: adopt-lecture2notes-submodule
updated: 2026-09-22
code:
  - ahk-scripts/usai-prompts/backup-spine-landmarks-20260922-114957/common.md
  - ahk-scripts/usai-prompts/backup-spine-landmarks-20260922-114957/spine.md
  - ahk-scripts/usai-prompts/backup-spine-research-20260922-122422/spine.md
  - ahk-scripts/usai-prompts/common.md
  - ahk-scripts/usai-prompts/spine.md
  - ahk-scripts/簡碼 jai.ahk
-->

---
### Requirement: Versioned personal overlay

The directory `skills-overlay/lecture2notes/` SHALL be the canonical source of the personal overlay and SHALL contain exactly these overlay files: `note.frontmatter.yaml`, `note.template.md`, `corrections.json`, `outputs.toml`, `privacy.toml`, plus a `README.md`. `outputs.toml` SHALL set profile to radiology, note.style to faithful, and pbf to true. `note.frontmatter.yaml` SHALL define the keys title, date, DateRev, aliases, noteVer, tags, subspecialty, tier, 消化層級, source, sourceType. `corrections.json` SHALL carry every entry of the legacy correction table: 179 deterministic entries (135 general plus 44 radiology) and 7 context-sensitive entries.

#### Scenario: Correction counts survive conversion

- **WHEN** the converted `corrections.json` is loaded
- **THEN** its deterministic section has 179 entries and its context-sensitive section has 7 entries, and every entry has a non-empty source value

##### Example: entry conversion

| Legacy section | Legacy entry | Overlay section | source |
| --- | --- | --- | --- |
| deterministic | heard "口拍的", correct "Copilot", source present | deterministic | unchanged |
| radiology | heard "空中馬來西亞", correct "chondromalacia", no source | deterministic | rad-workflow-legacy |
| context_sensitive | heard "以色列", correct "Excel" | context-sensitive | unchanged or rad-workflow-legacy |

#### Scenario: Overlay takes effect

- **WHEN** the overlay has been deployed and `l2n profile show --json` runs with no project overlay present
- **THEN** note.style is faithful, pbf is true, and profile is radiology, each with source user


<!-- @trace
source: adopt-lecture2notes-submodule
updated: 2026-09-22
code:
  - ahk-scripts/usai-prompts/backup-spine-landmarks-20260922-114957/common.md
  - ahk-scripts/usai-prompts/backup-spine-landmarks-20260922-114957/spine.md
  - ahk-scripts/usai-prompts/backup-spine-research-20260922-122422/spine.md
  - ahk-scripts/usai-prompts/common.md
  - ahk-scripts/usai-prompts/spine.md
  - ahk-scripts/簡碼 jai.ahk
-->

---
### Requirement: Deployment script

`deploy_lecture2notes.py` at the repository root SHALL, when run without flags, verify that the submodule is initialised, install the submodule package in editable mode with the running interpreter, run `l2n install-skill --all`, copy the five overlay files into the `.lecture2notes` directory of the user's home, and print the effective note.style, pbf and profile values with their source layers. It SHALL print one ASCII progress line per step and MUST NOT print characters outside cp950. With `--home <path>` it SHALL use that path as the home directory for every step.

#### Scenario: Uninitialised submodule

- **WHEN** `vendor/lecture2notes` contains no files and the script runs
- **THEN** it prints `run: git submodule update --init vendor/lecture2notes`, performs no installation, and exits 2

#### Scenario: Successful deployment into a temporary home

- **WHEN** the script runs with `--home <tmp>` and a stub `l2n` on PATH that records its arguments
- **THEN** the stub was called with `install-skill --all` after the editable install step, `<tmp>/.lecture2notes/` contains the five overlay files byte-identical to the sources, and the exit code is 0


<!-- @trace
source: adopt-lecture2notes-submodule
updated: 2026-09-22
code:
  - ahk-scripts/usai-prompts/backup-spine-landmarks-20260922-114957/common.md
  - ahk-scripts/usai-prompts/backup-spine-landmarks-20260922-114957/spine.md
  - ahk-scripts/usai-prompts/backup-spine-research-20260922-122422/spine.md
  - ahk-scripts/usai-prompts/common.md
  - ahk-scripts/usai-prompts/spine.md
  - ahk-scripts/簡碼 jai.ahk
-->

---
### Requirement: Drift check

`python deploy_lecture2notes.py --check` SHALL write nothing. It SHALL run `l2n install-skill --check --all` and compare each overlay source file with its deployed copy by sha256. It SHALL exit 0 when the skill check exits 0 and every overlay file matches, exit 2 when any skill target or overlay file differs or is missing (naming each), and exit 3 with an installation hint when `l2n` is not on PATH.

#### Scenario: Edited overlay copy

- **WHEN** one byte of `<home>/.lecture2notes/outputs.toml` is changed after deployment
- **THEN** `--check` prints a line naming `outputs.toml` and exits 2

#### Scenario: l2n missing

- **WHEN** `l2n` cannot be found on PATH
- **THEN** `--check` prints an installation hint that mentions `deploy_lecture2notes.py` and exits 3


<!-- @trace
source: adopt-lecture2notes-submodule
updated: 2026-09-22
code:
  - ahk-scripts/usai-prompts/backup-spine-landmarks-20260922-114957/common.md
  - ahk-scripts/usai-prompts/backup-spine-landmarks-20260922-114957/spine.md
  - ahk-scripts/usai-prompts/backup-spine-research-20260922-122422/spine.md
  - ahk-scripts/usai-prompts/common.md
  - ahk-scripts/usai-prompts/spine.md
  - ahk-scripts/簡碼 jai.ahk
-->

---
### Requirement: Post-migration verification run

After deployment, the CC BY fixture clip shipped inside the submodule SHALL be processed end to end in a directory outside the repository, and the result SHALL be recorded in `skills-overlay/lecture2notes/README.md`: the rendered note's frontmatter contains noteVer and 消化層級, the note carries the faithful style marker, and `l2n profile show` reports the overlay layers as user.

#### Scenario: Verification is recorded

- **WHEN** `skills-overlay/lecture2notes/README.md` is read
- **THEN** it contains a section titled 部署驗證 with the date, the lecture2notes version, and the four observed results

<!-- @trace
source: adopt-lecture2notes-submodule
updated: 2026-09-22
code:
  - ahk-scripts/usai-prompts/backup-spine-landmarks-20260922-114957/common.md
  - ahk-scripts/usai-prompts/backup-spine-landmarks-20260922-114957/spine.md
  - ahk-scripts/usai-prompts/backup-spine-research-20260922-122422/spine.md
  - ahk-scripts/usai-prompts/common.md
  - ahk-scripts/usai-prompts/spine.md
  - ahk-scripts/簡碼 jai.ahk
-->