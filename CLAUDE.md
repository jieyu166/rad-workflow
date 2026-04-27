<!-- SPECTRA:START v1.0.2 -->

# Spectra Instructions

This project uses Spectra for Spec-Driven Development(SDD). Specs live in `openspec/specs/`, change proposals in `openspec/changes/`.

## Use `/spectra-*` skills when:

- A discussion needs structure before coding → `/spectra-discuss`
- User wants to plan, propose, or design a change → `/spectra-propose`
- Tasks are ready to implement → `/spectra-apply`
- There's an in-progress change to continue → `/spectra-ingest`
- User asks about specs or how something works → `/spectra-ask`
- Implementation is done → `/spectra-archive`
- Commit only files related to a specific change → `/spectra-commit`

## Workflow

discuss? → propose → apply ⇄ ingest → archive

- `discuss` is optional — skip if requirements are clear
- Requirements change mid-work? Plan mode → `ingest` → resume `apply`

## Parked Changes

Changes can be parked（暫存）— temporarily moved out of `openspec/changes/`. Parked changes won't appear in `spectra list` but can be found with `spectra list --parked`. To restore: `spectra unpark <name>`. The `/spectra-apply` and `/spectra-ingest` skills handle parked changes automatically.

<!-- SPECTRA:END -->

# Rad Workflow — Claude Code Project Guide

## Project Overview
Radiology workflow automation toolkit for Dr. Jieyu, containing:
- **radtracker/** — Weekly workload tracking & report generation (CSV-based)
- **ahk-scripts/** — AutoHotkey report templates for radiology RIS
- **tool/** — Web-based radiology report helpers (GitHub Pages)

## Key Rules
- All console output must be cp950-compatible (no Unicode symbols like >=, ~=, ->)
- CSV files are cp950 (Big5) encoded, Tab-separated
- Default reporter ID: A80748
- Language preference: Traditional Chinese for user-facing content, English for code/comments

## Quick Reference

### Radtracker Weekly Report
See `radtracker/claude.md` for full rules. Core workflow:
```bash
cd radtracker
python generate_report.py --csv YYYYMM.csv --yk YYYYMMYK.csv --input week_input.yaml -o output/weekly_report.json
```
Then use `weekly_review_prompt.md` to generate HTML from the JSON.

### AHK Scripts
Located in `ahk-scripts/`. Modality-specific report templates:
- `CT.ahk`, `US.ahk`, `Xray.ahk`, `Mammo.ahk`, `IR.ahk` — Report hotstrings
- `Abbr.ahk` — Abbreviation expansion
- `radiologist_settings.ini` — Personal settings (never commit secrets)

### Web Tools
Located in `tool/`. Deployed via GitHub Pages at:
https://jieyu166.github.io/rad-workflow/
