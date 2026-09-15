# 腳本用法與工作流程

> 從 `radtracker/CLAUDE.md` 拆出。要跑某支腳本、或要走完整週報流程時讀這份。

## 專案結構
```
radtracker/
├── parse_csv.py               ← CSV 解析引擎（支援 ROC 日曆檔名自動偵測）
├── generate_report.py         ← 產出週報 JSON（支援 --csv/--xlsx/--mid 模式）
├── update_history.py          ← 自動更新 history.json
├── archive_week.py            ← 自動歸檔 output/ 至 W{nn}/
├── schedule_prompt.md         ← 排程規劃 prompt（含 GCal 同步規範）
├── claude.md                  ← 你正在讀的這份（固定規則）
├── weekly_review_prompt.md    ← 標準化週報 prompt（8個固定輸出區段）
├── week_input.yaml            ← 當前週使用者輸入
├── week_input_template.yaml   ← 使用者每週輸入模板（含 mid-week 欄位）
├── history.json               ← 歷史週報摘要（跨週趨勢）
├── csv_input/                 ← 所有 CSV 輸入（.gitignore）
│   ├── 202602.csv, 202603.csv ← 醫院月報表（YYYYMM.csv）
│   ├── 1150319_JL.csv         ← ROC 日曆格式（115MMDD_*.csv）
│   └── legacy/
│       └── radiology_tracker.xlsx
└── output/
    ├── W09/, W10/, W11/       ← 歷史週報歸檔
    └── (當前週產出)
```

---
## 工作流程

### CSV 模式（推薦）
```bash
# 1. 使用者填寫 week_input.yaml（8 個數字 + 備註）
# 2. CSV 放入 csv_input/ 目錄（ROC 日曆檔名如 1150319_JL.csv 可自動偵測週次）

# 3. 產出完整週報
python generate_report.py --csv csv_input/202603.csv --input week_input.yaml -o output/weekly_report.json

# 含永康院區值班資料
python generate_report.py --csv csv_input/202603.csv --yk csv_input/202603YK.csv --input week_input.yaml

# 4. 期中分析（需在 week_input.yaml 加 remaining.mid 欄位）
python generate_report.py --csv csv_input/1150319_JL.csv csv_input/1150319_YK.csv --input week_input.yaml --mid

# 5. 更新歷史記錄
python update_history.py output/weekly_report.json

# 6. 歸檔（週報完成後）
python archive_week.py
```

### priority_breakdown.py（2026-05-14 起新增）
依臨床優先 triage 分桶 P1-P4，輸出 SLA KPI。

```bash
# pending CSV 模式（即時 backlog 監控）— 需可匯出未完成單
python priority_breakdown.py --csv csv_input/{pending}.csv --pending --today YYYY-MM-DD --json output/priority_W{NN}.json

# completed CSV 模式（事後 TAT 回顧）
python priority_breakdown.py --csv csv_input/1150515_CL.csv --modality CT
```

### update_planned_with_actuals.py（2026-05-11 起新增）
週日覆盤時對比 schedule 計畫 vs 實際完成（日層級，by modality）。

```bash
python update_planned_with_actuals.py W{NN} --csv csv_input/{week_csv}.csv [--yk ...]
# 輸出 output/w{nn}_actuals.json — 含 GCal description 回填區塊
```

> 為何日層級：CSV report_time 為 batch sign-off（~60%）非實際讀片時間，slot-level 時間比對僅能 catch ~15%。日層級彙總 by modality 才誠實。

### xr_value.py（2026-05-27 新增，後改真實計時）
全模態報告單位時間產值（pt/hr）。回答「哪種報告最賺錢」。

```bash
# 建議餵多週/整月 CSV 累積足夠計時樣本
python xr_value.py --csv csv_input/115*_CL.csv --min-n 15 --json output/xr_value_{month}.json
```

→ 輸出供 weekly_report **Section 12** 引用。
- **計時法**：真實 CSV 簽發間隔（間隔 0=批次剔除、>30min=休息剔除、用中位數），非估算
- 全模態 + 子分類；**Spine 依 protocol 拆**（AP/Lat vs Flex/Ext vs 4view）
- 平均點值＝硬數據；計時樣本 n<15 標「⚠少」
- 典型結論（2026-05 大樣本）：Mammo 422 / Knee 409 最高；Chest 97（量大值低，佔量 30%）；CT/LDCT 88-109（中位 15-18min）
- 限制：report_time 僅到分 → 次分鐘讀片 floor 1min

### attendance_draft.py（出勤補登草稿，2026-07-23 新增）

從報告時間戳推算每日簽到/簽退草稿，供**人工**輸入「主治醫師刷卡補登作業」網頁。→ 週報 **區段十三**。

```bash
python attendance_draft.py --csv csv_input/{week_csv}.csv \
  --json output/attendance_W{NN}.json --out-csv output/attendance_W{NN}.csv
```

**工作段模型（2026-07-23 使用者定義）**：
- **深夜視為前一天延續**：`00:00–05:00`（`--night-cutoff 5`）的簽發歸**前一個工作日** → 該日簽退跨日
- **收工通常不超過 04:00、早上最早 06:00 開始** → cutoff 取 05:00 落在兩者之間
- **簽到不早於 06:00**（`--earliest-start`）；即使最早報告 06:30 減緩衝也夾在 06:00

其他：
- **算法**：篩 `reporter_id`(col17) → `report_date`(col13)+`report_time`(col14) 組 datetime → 依**工作日**分組 → 最早−45min＝簽到、最晚+20min＝簽退（`--checkin-buffer`/`--checkout-buffer` 可調）
- 實例（W29/W30）：07/19(日) 21:59→07/20 02:14 ⇒ 簽到 21:14、**簽退 07/20 02:34**；07/20(一) 自身則乾淨為 09:07–13:47
- 自動標記：`簽退跨日` / `深夜N筆` / `簽到偏晚需確認`(簽到≥12:00) / `簽到夾到06:00` / `假日` / `僅1筆`
- ⚠ **已知限制**：只反映「簽報告」時間。當天若上午做臨床/開會/處置而未簽報告，簽到會被低估 → 標「簽到偏晚需確認」由人工補正
- 件數依 case_id 去重；輸出 console 表格 + JSON + CSV(utf-8-sig)
- ⚠ **僅產草稿表，不碰網頁、不自動提交**；補登頁 `#DDL_date`/`#txt_HHMM`/`#btnSubmit`，逐筆送出、系統依打卡狀態自動判簽到/簽退；**跨日簽退直接用它自己的日期送出**
- 註：`exec_date`/`exec_time`(col11/12) 未使用（檢查施作時間≠醫師工作時間）

### build_trends.py（每月一次）
多週趨勢視覺化：週新增量、週點值、週完成、GitHub 強度熱力圖、Backlog 趨勢、**切片 QC（Thyroid ND 月趨勢 / Breast PPV / B3 追蹤）**、**區段九 時段效率（每整點 0–23 熱力圖 + 平日 cases/hr 折線，2026-06-23 起，呼叫 tod_efficiency.py）**。

```bash
python build_trends.py
# 輸出 output/trends.html — 拿來看 4 週 backlog 走勢、切片 QC、時段效率、和主任談話的數據
```

### tod_efficiency.py（時段效率分析，2026-06-23 新增）
全期「每整點 0–23」報告產出效率，回答「一天哪個時段效率最高/最低」。
- **計時法**：完成時間戳（report_date+report_time，精度到分）；00:00-05:59 歸前一工作日（深夜桶）；有效工時＝相鄰簽發間隔加總（單一間隔 >20min 截斷為 20，濾掉午休/被打斷的長空檔）；cases/hr＝件數÷有效工時；中位間隔為輔；中斷率＝間隔 >20min 佔比；依 case_id 去重
- **已知限制**：report_time 僅到分→中位間隔地板 1min；批次簽發（間隔 0）時段 cases/hr 偏高（如週末值班 XR），須對照件數與主要模態判讀
- **典型結論（2026-08-10 更新，n=13,720，2026-03-16~08-09）**：**真尖峰是 12–14 時（24–25 c/hr）**，14 時 25.2 最高（n1150）、12 時 25.0、13 時 24.0；15 時樣本最大（n1507, 23.9）＝最常工作的時段；晚間 19 時掉到 19.3、21 時 19.5，深夜 0–2 時最低（17–18）。
  - ⚠ 中斷率全日皆 6–11%，差異不大 → **效率落差來自時段本身，不是被打斷**
  - 舊結論「午後 13-17 最高／平日最熱 15 點」已由更大樣本取代：範圍應收斂為 **12–14 時**
- 三處使用：
  ```bash
  python tod_efficiency.py            # 單獨重產 output/tod_efficiency.html（全 115*_CL/YK 去重）
  # build_trends.py 自動呼叫 → trends.html 區段九（月熱力圖 + 平日折線）
  # generate_report.py 自動寫 hourly_weekday 進 weekly_report.json → 週報區段五-b 折線圖
  ```

### parse_csv.py 單獨使用
```bash
# 自動偵測 ROC 日曆檔名的週次（--week 可省略）
python parse_csv.py csv_input/1150319_JL.csv csv_input/1150319_YK.csv -o output/parsed.json

# 明確指定週次
python parse_csv.py csv_input/202603.csv --week 2026-W12 -o output/parsed.json
```

### [Legacy] XLSX 模式
```bash
python generate_report.py --xlsx csv_input/legacy/radiology_tracker.xlsx --input week_input.md
```

### 資料解析注意事項
- **CSV 模式**：模態/難度/子分類全部由 `parse_csv.py` 自動判定
- **case_id 分組**：已驗證與 xlsx 手動計數一致（W09 Mon/Tue/Fri XR 完全吻合）
- **openpyxl 操作 biopsy_tracker_2026.xlsx**：`insert_rows()` 不會位移 merged cells，遇 merged 範圍要先 `ws.unmerge_cells(...)` 再插入，否則新行的 B-F 欄位會被併入 A 欄
- BMD 不計入主要追蹤模態（X光/CT/US/Mammo 為四大追蹤模態）
- CSV 模式無法追蹤非報告活動（臨床/雜務/交通），僅記錄報告工作
- CSV 模式提供工作點值（work_points），xlsx 模式不提供
- [Legacy] xlsx 模態欄位不一致：子類別可能在「子類別」或「難度」欄位，需合併判斷
- [Legacy] other/雜務/臨床 的時間計入非報告時間，不計入報告效率

### 週日覆盤 SOP（2026-05-14 標準化）

每週日 21:00 GCal 已有 recurring 週覆盤 event。順序：

1. **跑 weekly report**
   ```bash
   /weekly-report   # 或 python generate_report.py + 產 HTML
   ```
2. **產出計畫 vs 實際對比**
   ```bash
   python update_planned_with_actuals.py W{NN} --csv csv_input/{latest_CL}.csv [--yk ...]
   ```
3. **（若有 pending CSV）跑 priority triage**
   ```bash
   python priority_breakdown.py --csv csv_input/{pending}.csv --pending --json output/priority_W{NN}.json
   ```
3b. **跑 XR 部位別產值（Section 12）**
   ```bash
   python xr_value.py --csv csv_input/{week_csv}.csv --json output/xr_value_W{NN}.json
   ```
3c. **跑出勤補登草稿（Section 13）**
   ```bash
   python attendance_draft.py --csv csv_input/{week_csv}.csv \
     --json output/attendance_W{NN}.json --out-csv output/attendance_W{NN}.csv
   ```
4. **填 GCal 週覆盤 event template**（成長/生活/工作三帳戶）
5. **歸檔**
   ```bash
   python update_history.py output/weekly_report.json
   python archive_week.py
   ```
6. **每月一次跑 trends**
   ```bash
   python build_trends.py
   ```

### 錯誤處理
- 遺失 week_input → 提示使用者補充期初/期末剩餘量
- CSV 無資料 → 確認檔案路徑、編碼（cp950）、reporter_id
- 跨月邊界遺失（如月底工作→次月簽發）→ 標記已知限制，不視為 bug
- 值班日計數偏低（批次簽發）→ 在報告中標註 `(estimated)`

---
## 週報品質標準

### 通用規則
- 期初/期末剩餘量必須使用使用者回報值，不可自行推算
- 新增量 = 期末 - 期初 + 完成（標記為「推算值 >=」）
- 未記錄的項目（交通、休息等）標註「未記錄」，不可推測

### CSV 模式
- 完成數量從 CSV 解析計算，不可由 LLM 推算
- 效率以每日粗估呈現（cases/active_hr），標記 `(estimated)`
- 子分類效率只顯示數量和基準，不計算實測速率（無精確時間）
- 工作點值為額外指標，從 CSV work_points 欄位加總
- 值班日數據可能因批次簽發而低估，需在報告中說明

### [Legacy] XLSX 模式
- 所有數字必須從 xlsx 計算而來，不可由 LLM 推算
- 效率 = 完成數量 / (花費時間/60)，精確到小數點一位
- 每日完成合計必須與追蹤表完成數一致（一致性檢查）

---
