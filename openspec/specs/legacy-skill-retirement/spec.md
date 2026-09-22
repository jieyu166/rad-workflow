# legacy-skill-retirement Specification

## Purpose

TBD - created by archiving change 'adopt-lecture2notes-submodule'. Update Purpose after archive.

## Requirements

### Requirement: Legacy lecture skills leave version control

`skills/lecture-to-notes` and `skills/whisper-srt-zh` SHALL be removed from the repository with `git rm`, in a commit whose message records the last commit that contained them. `skills/obsidian-v4-cleanup` MUST remain tracked and unchanged by this change.

#### Scenario: Skills directory after retirement

- **WHEN** `git ls-files skills` is run after the retirement commit
- **THEN** no path begins with `skills/lecture-to-notes/` or `skills/whisper-srt-zh/`, and paths under `skills/obsidian-v4-cleanup/` are still listed

#### Scenario: Retirement is reversible

- **WHEN** the commit hash named in the retirement commit message is used with `git checkout <hash> -- skills/whisper-srt-zh`
- **THEN** the directory is restored with its scripts and references


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
### Requirement: Copies outside version control are moved, not deleted

Every copy of lecture-to-notes and whisper-srt-zh outside version control (user-level agent skill directories and the three generated project-level agent directories), and the two stale obsidian-v4-cleanup forks inside the Radiology vault (`.claude/skills/obsidian-v4-cleanup` and `tmp/skill-validate/obsidian-v4-cleanup`), SHALL be moved into `~/.claude/skills-retired-20260922/` under a subfolder that names the original location. No file outside version control SHALL be deleted without a copy existing in that folder. The junction `~/.claude/skills/obsidian-v4-cleanup` and its target `~/.agents/skills/obsidian-v4-cleanup` MUST NOT be moved or modified.

#### Scenario: A retired copy can be found

- **WHEN** the retirement step has finished
- **THEN** `~/.claude/skills-retired-20260922/` contains one subfolder per moved copy, each holding that copy's SKILL.md, and none of the original locations still contains a lecture-to-notes or whisper-srt-zh folder

#### Scenario: The live obsidian-v4-cleanup is untouched

- **WHEN** the sha256 of `~/.agents/skills/obsidian-v4-cleanup/SKILL.md` and of every file under its references folder is recorded before and after the retirement step
- **THEN** the two recordings are identical, and `~/.claude/skills/obsidian-v4-cleanup` is still a junction to it

#### Scenario: A locked file stops the move safely

- **WHEN** a file in a copy cannot be removed from its original location because it is locked
- **THEN** the step reports that path, leaves the original in place, keeps the already-made copy, and exits with a non-zero code


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
### Requirement: Worktrees are out of scope

This change MUST NOT remove, reset, or modify any directory under `.worktrees/` or `.claude/worktrees/`, nor delete any branch. The state of those worktrees at migration time SHALL be recorded in `skills-overlay/lecture2notes/README.md`.

#### Scenario: Worktrees unchanged

- **WHEN** `git worktree list` and `git branch --list` are recorded before and after the change
- **THEN** both recordings are identical


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
### Requirement: Guidance points to the new product

`CLAUDE.md` SHALL route lecture-to-notes work to the lecture2notes skill and the `l2n` command, list the deploy and check commands, and state that lecture2notes is not distributed by `sync_skills.py`. Each of the three historical documents that reference the retired script paths SHALL gain a single header line stating that those scripts were replaced by lecture2notes; their bodies MUST NOT be rewritten. `docs/PITFALLS.md` SHALL describe the symptom and fix for an uninitialised submodule.

#### Scenario: Routing table updated

- **WHEN** `CLAUDE.md` is searched for `lecture2notes`
- **THEN** the routing table has a row for lecture video to notes that names `deploy_lecture2notes.py`, and the project-specific body remains within its 60-line limit

#### Scenario: Historical documents carry a notice only

- **WHEN** the diff of the three historical documents is inspected
- **THEN** each shows exactly one added line near the top and no other change

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