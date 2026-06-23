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
- OneDrive 同步資料夾的程式碼有遺失風險（slide-extractor 曾遺失 .py，靠 .pyc 重建）→ 寫完立即 commit；`~/.claude/hooks/check-uncommitted.sh` Stop hook 會自動警告未 commit 的 .py/.md/.html/.yaml/.ahk 等
- Python `http.server` 服務靜態檔時，`urlparse(path).path` **不會** percent-decode → 中文檔名需手動 `unquote()` 才能命中磁碟
- git bash 不支援 PowerShell here-string `@'...'@`；多行 commit message 寫到 `.git/CM.txt` 後 `git commit -F .git/CM.txt`
- Claude Code settings.json 的 hook command 若需 shell 跳脫，外部化成 `~/.claude/hooks/*.sh` 避免 JSON 跳脫地獄
- Python 寫檔腳本 + Edit tool 同時操作同一檔案 → 後執行者覆蓋前者；同一 response 內操作相同檔案後必須驗證結果

## 共用技能庫（Claude Code / OpenAI Codex / OpenCode）
三家 AI 代理共用同一份技能，**單一真實來源在 `skills/`**（進版控 → GitHub 多機同步）。
- **編輯只改 `skills/<name>/SKILL.md`**，然後跑 `python sync_skills.py` 散佈到各家資料夾
- 各家路徑（皆為 sync 產生的衍生 copy，已 gitignore）：
  - Claude Code → `.claude/skills/`
  - OpenAI Codex → `.agents/skills/`（複數 s）
  - OpenCode → `.opencode/skills/`（OpenCode 亦原生讀 `.claude/skills/` 與 `.agents/skills/`）
- **不用 symlink**：專案在 OneDrive，symlink 會被當實體檔上傳而失效 → 改用「canonical + 複製腳本 + Git」
- `python sync_skills.py --check` 檢查各家是否與 canonical 一致（drift 時 exit 2）
- frontmatter 走最大公因數（`name` + `description`）；Claude 專屬欄位三家共用時不要用

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
- `Abbr.ahk` — Abbreviation expansion（含跨模態通用縮寫，如 CA;、FR; 等；CA; 在此而非 CT.ahk）
- `radiologist_settings.ini` — Personal settings (never commit secrets)
- AHK 檔案編碼：`utf-8-sig`（非 cp950）
- `HotstringMenuV` 標準格式：每引數獨立一行、前綴 `,`，單行 ≤ 150 字元
- Keylogger 分析：`cd ahk-scripts/logs && python analyze_keylog.py <file> -o out.json`；跨多檔彙整用 `aggregate_raw.json` 模式

### Web Tools
Located in `tool/`. Deployed via GitHub Pages at:
https://jieyu166.github.io/rad-workflow/
