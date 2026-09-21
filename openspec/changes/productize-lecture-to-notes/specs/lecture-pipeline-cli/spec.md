## ADDED Requirements

### Requirement: Installable package with a single console entry point

The system SHALL be distributed as a Python package named lecture2notes that installs a console script `l2n`. The package MUST declare all mandatory Python dependencies in `pyproject.toml`; optional engines MUST be declared as extras (`[breeze]`, `[qwen]`, `[whispercpp]`, `[scene]`). `l2n --help` MUST list every subcommand.

#### Scenario: Fresh install exposes the CLI

- **WHEN** a user runs `pip install lecture2notes` in a clean virtual environment and then `l2n --help`
- **THEN** the command exits 0 and lists the subcommands transcribe, calibrate-subs, frames, ocr, scaffold, render, viewer, pbf, hub, check, migrate, run, publish, convert-model, profile, install-skill

#### Scenario: Missing external dependency is reported, never silently degraded

- **WHEN** a subcommand requires an external tool or model that is absent (ffmpeg, rapidocr, a CT2 model directory, the qwen-asr package)
- **THEN** the command prints the missing item and the exact install instruction, produces no output files, and exits 3

### Requirement: Stage subcommands are idempotent and resumable

Each stage subcommand SHALL detect its own existing output for the given stem and skip work unless `--force` is given. `l2n run` SHALL execute the mechanical stages in order transcribe, frames, ocr, scaffold, render, viewer and MUST stop at the first stage whose acceptance check reports an error.

#### Scenario: Re-running a completed stage is a no-op

- **WHEN** `l2n frames video.mp4` is run and `video.frames.json` already exists with all referenced frame files present
- **THEN** the command prints `[frames] skip (exists)` and exits 0 without rewriting any file

#### Scenario: run halts on stage error

- **WHEN** `l2n run video.mp4 --lang zh` reaches a stage whose check reports an error
- **THEN** the command prints `[<stage>] error: <reason>`, does not start later stages, and exits 2

#### Scenario: run continues on stage warning

- **WHEN** a stage check reports only warnings
- **THEN** `l2n run` prints the warnings, continues to the next stage, and the final exit code is 1

### Requirement: Console output is cp950-safe and shows progress

All console output SHALL use only ASCII marker characters (for example `[ok]`, `[warn]`, `[error]`, `->`) and MUST NOT emit the characters `→`, `≥`, `✓`, `✗`. Any stage that runs longer than 10 seconds SHALL print a progress line at least every 5 seconds containing completed count, total count, elapsed seconds, and estimated remaining seconds. `--quiet` SHALL suppress progress lines; `--json-progress` SHALL emit one JSON object per progress event on stdout.

#### Scenario: Output survives a cp950 console

- **WHEN** any subcommand is executed with the environment variable PYTHONIOENCODING set to cp950
- **THEN** the command completes without raising UnicodeEncodeError

#### Scenario: JSON progress events

- **WHEN** `l2n transcribe video.mp4 --lang zh --json-progress` runs
- **THEN** stdout contains lines that each parse as a JSON object with keys stage, done, total, elapsed_sec, eta_sec

### Requirement: Language is mandatory for transcription

`l2n transcribe` and `l2n run` SHALL require `--lang` with one of zh, en, ja, auto. There MUST be no default value.

#### Scenario: Missing language aborts before any work

- **WHEN** `l2n transcribe video.mp4` is run without `--lang`
- **THEN** the command prints `--lang is required (zh|en|ja|auto)`, creates no files, and exits 2
