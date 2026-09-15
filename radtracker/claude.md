# Radiology Tracker — 專案指南（路由）

放射科醫師（Jieyu，工號 A80748）的工作追蹤助手：解析醫院 CSV → 產週報 → 排下週行程 → 同步 Google Calendar。

## 路由表（按需讀取，不要憑記憶做）

| 這次要做什麼 | 讀這個 |
|---|---|
| 週報／期中分析全流程、跑任何一支腳本 | [docs/TOOLS.md](docs/TOOLS.md) |
| CSV 欄位、模態判定、急打判定、時數推估 | [docs/CSV-SPEC.md](docs/CSV-SPEC.md) |
| 排下週行程、Mammo 窗口、GCal 同步、產生器的必備 assert | [docs/SCHEDULING.md](docs/SCHEDULING.md) |
| 估速率、估每週新增量、看哪天進什麼片 | [docs/BASELINES.md](docs/BASELINES.md) |
| 週報 HTML 的 11 個固定區段 | [weekly_review_prompt.md](weekly_review_prompt.md) |
| 指令或程式第一次失敗（編碼／Shell／OneDrive／xlsx） | [../docs/PITFALLS.md](../docs/PITFALLS.md) |

## 核心規則（違反即算錯）

1. **病患資料**：CSV（姓名 col2、病歷號 col1、身分證 col25、生日 col26）、`output/` 下含病歷號的檔案、`biopsy_tracker_2026.xlsx` —— 一律 gitignore，**嚴禁 commit 或外傳**。commit 前用 `git check-ignore -q` 逐檔驗。
2. **期初/期末剩餘量只能用使用者回報值**，不可自行推算。完成數只能從 CSV 算，不可由 LLM 估。
3. 新增量 = 期末 − 期初 + 完成，一律標「推算值 ≥」。未記錄的項目標「未記錄」，不推測。
4. 主控台輸出必須 cp950 相容（`print` 禁用 `→ ≥ ✓` 等符號；要輸出中文報表就寫檔再讀）。
5. 醫院 CSV = cp950 + Tab 分隔。**匯出格式會變**——遇到逗號分隔或欄數不符時，先依欄位標題轉回標準 32 欄再跑，不要改 `parse_csv.py`。
6. 改 `biopsy_tracker_2026.xlsx` 前**先備份**；去重鍵是（病歷號＋執行日），不是只比病歷號。寫入後重新載入驗證。
7. `attendance_draft.py` **只產草稿，不碰網頁、不自動提交**。
8. 外送動作（建立/刪除 Google Calendar 事件）每次都要先問過再做。

## 每日上限與窗口（最常用，其餘見 SCHEDULING.md）

- 每日上限：X光 150、**CT 6**（值班日可放寬並註明依據）、US 15、Mammo 15
- **Mammo 場地窗口**：一二三全天／四僅早上（常撞臨床）／五僅晚上／**六日取決於人在不在佳里** → 排程前先問
- 急打（source=1 急診、3 住院）屬 P1，24hr SLA；門診舊單 P4 可放棄

## 已知會變動、每次要確認的

這些寫死在文件裡會過期，**排程前先問使用者**：

- 這週有沒有值班？單日還是連續兩天？（連兩天永康值班實測急打 XR 達 612 件，與單日量級完全不同）
- 這個週末人在不在佳里？（決定 Mammo 週末有沒有窗口）
- 這週的標註/專案進度與本週配額？

## 給下一次的維護規則

- 本檔只當索引，**上限 60 行**；長內容一律寫進 `docs/` 再由路由表引用。
- 基準數字發現與實際不符時，**直接改 `docs/BASELINES.md`**，不要只在當週週報裡註記 —— 註記會隨週報歸檔而失效。
