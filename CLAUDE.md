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
