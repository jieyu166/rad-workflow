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

放射科工作流程自動化工具集：`radtracker/`（週工作量與品質追蹤）、`ahk-scripts/`（RIS 報告範本，AutoHotkey v1）、`tool/`（GitHub Pages 網頁工具）、`skills/`（三家 AI 代理共用技能庫 canonical）。

## 路由表（按需讀取，不要憑記憶做）

| 情境 | 讀這個 |
|---|---|
| 指令/程式第一次失敗；要動編碼/Shell/OneDrive/AHK/xlsx | [docs/PITFALLS.md](docs/PITFALLS.md) — 陷阱表，先比對症狀再動手 |
| radtracker 週報全流程與欄位規則 | [radtracker/claude.md](radtracker/claude.md) |
| 派 subagent、選模型、驗證方式 | `~/.claude/playbooks/model-dispatch.md` |
| 不確定升級/完成/該不該問使用者 | `~/.claude/playbooks/judgment-rubrics.md` |
| 專案介紹/維護/roadmap/技術債（人看的） | GitHub Wiki: https://github.com/jieyu166/rad-workflow/wiki |

## 核心規則（違反即算錯）

1. 主控台輸出必須 cp950 相容（print 禁用 `→ ≥ ✓` 等 Unicode 符號）
2. 醫院 CSV = cp950 + Tab 分隔；AHK 檔 = utf-8-sig；寫回維持原編碼
3. `radtracker/output/biopsy_tracker_2026.xlsx` 含病患資料，嚴禁 commit；機密一律放環境變數或 `.env`
4. OneDrive 有遺失前例：**寫完立即 commit**（Stop hook 會警告未 commit 檔）
5. 預設報告醫師代號：A80748
6. 使用者介面文字 = 繁體中文台灣用語；程式碼與註解 = 英文
7. 共用技能只改 `skills/<name>/SKILL.md`，再跑 `python sync_skills.py` 散佈；各家資料夾（`.claude/skills/`、`.agents/skills/`、`.opencode/skills/`）是衍生 copy 已 gitignore，勿直接改、勿用 symlink；`--check` 驗 drift（不一致 exit 2）
8. 本檔只當索引：新增長內容一律寫到被引用檔（教訓→PITFALLS.md），不塞回這裡；Spectra 區塊外的本文上限 60 行

## 常用指令速查

```bash
# 週報（完整規則見 radtracker/claude.md；產出後用 weekly_review_prompt.md 生成 HTML）
cd radtracker && python generate_report.py --csv YYYYMM.csv --yk YYYYMMYK.csv --input week_input.yaml -o output/weekly_report.json

# 技能庫同步 / drift 檢查
python sync_skills.py
python sync_skills.py --check
```

Web 工具部署：push main 後由 GitHub Pages 自動發佈至 https://jieyu166.github.io/rad-workflow/
