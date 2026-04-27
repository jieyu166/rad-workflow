# Rad Tracker

`radtracker/` 提供放射科 CSV 工作量解析、週報產生、切片/介入處置追蹤、
以及每月乳房攝影 BI-RADS 0 品質追蹤等本地工作流程工具。

多數腳本設計於院內或工作電腦本機執行；產出檔案可能含病歷號與報告全文，
請勿將任何含病人資料的檔案推送到 GitHub。

## 編碼規則

- 醫院 CSV 匯出檔為 CP950 編碼、Tab 分隔。
- AHK 相關檔案通常為 UTF-8 with BOM。
- Python、JSON、Markdown、YAML 預設使用 UTF-8。
- 編輯舊檔時請維持原本編碼。

## 目錄結構

| 路徑 | 用途 |
|---|---|
| `csv_input/` | 醫院系統匯出的 CSV 來源檔。 |
| `output/` | 產生的週報、排程、JSON 摘要、乳攝追蹤檔等。 |
| `week_input.yaml` | 當週週報輸入（含期初、期末剩餘量）。 |
| `week_input_template.yaml` | 新一週的輸入範本。 |
| `history.json` | 跨週累積的歷史摘要，供趨勢分析使用。 |
| `schedule_prompt.md` | 排程規劃 prompt 與 Google Calendar 同步規範。 |
| `weekly_review_prompt.md` | 週報 prompt（10 個固定區段）。 |
| `CLAUDE.md` | 工作流程細節與實作規則的補充說明。 |

## 主要腳本

| 腳本 | 用途 |
|---|---|
| `parse_csv.py` | 依 ISO 週次解析醫院 CSV，含模態分類、星期、工作點值與活躍時數推估。 |
| `generate_report.py` | 結合 CSV/XLSX 與 `week_input.yaml` 產出週報 JSON。 |
| `update_history.py` | 將週報或期中報告寫入 `history.json`。 |
| `archive_week.py` | 將當週 `output/` 內容移動到 `output/Wxx/`。 |
| `biopsy_tracker.py` | 從 CSV 追蹤切片/FNA/介入處置案件。 |
| `mammo_tracker.py` | 掃描每月乳房攝影篩檢案件，並計算 recall rate / PPV1 等指標。 |
| `mammo_report_fetcher.py` | 從院內網路抓取乳攝報告並維護 BI-RADS 0 追蹤清單。 |

## 週報流程

週末完整流程：

```powershell
python radtracker\generate_report.py --csv radtracker\csv_input\1150426_CL.csv --input radtracker\week_input.yaml -o radtracker\output\weekly_report.json
python radtracker\update_history.py radtracker\output\weekly_report.json
python radtracker\archive_week.py --week W17
```

期中分析（需在 `week_input.yaml` 加上 `remaining.mid` 欄位）：

```powershell
python radtracker\generate_report.py --csv radtracker\csv_input\1150423_CL.csv --input radtracker\week_input.yaml --mid -o radtracker\output\weekly_report_mid.json
```

延伸週末邊界（例如把下週一的報告也納入）：

```powershell
python radtracker\generate_report.py --csv radtracker\csv_input\202604.csv --input radtracker\week_input.yaml --extra-days 1
```

需要中介 CSV 摘要時，可單獨使用 `parse_csv.py`：

```powershell
python radtracker\parse_csv.py radtracker\csv_input\1150426_CL.csv --week 2026-W17 --output radtracker\output\w17_midweek.json
```

CSV 模式下，`generate_report.py` 會自動呼叫 `biopsy_tracker.get_biopsy_summary()`
並把 `biopsy_followup` 寫入週報 JSON，因此週報的「切片追蹤」區段不需另外執行。

## 週報輸入

新建一週請從 `week_input_template.yaml` 開始。

`week_input.yaml` 內容包含：

- 週次代號與日期範圍
- 期初剩餘量、期末剩餘量
- 預估閾值
- 自由備註或修正

請維持 UTF-8 編碼。

## 切片/FNA 追蹤

`biopsy_tracker.py` 會掃描 `csv_input/` 的所有 CSV 檔，依 `case_id` 分組
並判定切片/FNA/介入處置案件。`generate_report.py` 也會呼叫此模組，
將追蹤提醒併入週報。

報告醫師代號沿用：

```text
A80748
```

## 乳攝 BI-RADS 0 追蹤

乳攝追蹤分為兩階段：

1. 從 CSV 掃描每月篩檢乳攝案件。
2. 由院內網路抓取報告全文，解析 BI-RADS 分類。

```powershell
python radtracker\mammo_tracker.py --month 2026-04
python radtracker\mammo_report_fetcher.py --month 2026-04
python radtracker\mammo_tracker.py --month 2026-04 --stats
python radtracker\mammo_report_fetcher.py --list-birads0
```

抓取報告需在院內網路（含院內 Wi-Fi）下執行。為避免影響白天臨床工作，
fetcher 僅於每日 21:00–03:00 之間運作。

### 乳攝產出檔案

| 檔案 | 用途 |
|---|---|
| `output/mammo_YYYYMM_cases.json` | 當月 order_code=91 的乳攝篩檢案件清單。 |
| `output/mammo_YYYYMM_reports.json` | 抓取到的報告全文與 BI-RADS 解析結果。 |
| `output/mammo_YYYYMM_metrics.json` | （選用）當月各項指標統計。 |
| `output/mammo_birads0.json` | 累積的 BI-RADS 0 追蹤清單。 |

### 手動追蹤欄位

完成臨床追蹤後，請手動編輯 `output/mammo_birads0.json`。

下列為自動產生欄位，請勿修改：

- `case_id`
- `chart_no`
- `report_date`
- `recall_month`
- `followup_due`

下列為手動欄位：

| 欄位 | 可選值 | 意義 |
|---|---|---|
| `status` | `pending`、`resolved` | 是否已有最終結果。 |
| `outcome` | `null`、`benign`、`malignant`、`inadequate`、`lost_to_followup` | 最終回招結果，供 PPV1 統計。 |
| `notes` | 自由文字 | 臨床備註或追蹤計畫。 |

仍在追蹤中時請使用：

```json
{
  "status": "pending",
  "outcome": null,
  "notes": "US BI-RADS 3, 6 個月後追蹤"
}
```

僅當案件可從待追蹤清單移除時，才使用 `resolved + outcome`：

```json
{
  "status": "resolved",
  "outcome": "benign",
  "notes": "追蹤超音波為良性"
}
```

`inadequate` 與 `lost_to_followup` 計為已結案但非惡性。若仍需後續追蹤，
請保持 `pending + outcome: null` 並於 `notes` 說明計畫。

## 統計指標

目前乳攝指標包含：

- 當月乳攝篩檢總案件數
- BI-RADS 0 案件數
- recall rate（回招率）
- 已結案數
- 惡性數
- PPV1
- 待追蹤數

執行：

```powershell
python radtracker\mammo_tracker.py --month 2026-04 --stats --output radtracker\output\mammo_202604_metrics.json
```

## 歷史檔與歸檔

`update_history.py` 將週報（或期中報告）摘要寫入 `history.json`，
週報 prompt 會用此檔做跨週趨勢分析。歸檔則由 `archive_week.py`
將當週 `output/` 內容移到 `output/W{nn}/`，保持工作目錄整潔。

```powershell
python radtracker\update_history.py radtracker\output\weekly_report.json
python radtracker\archive_week.py --week W17
```

## 排程規劃

`schedule_prompt.md` 描述每週排程規劃流程，產出三項：

1. `output/w{nn}_schedule.json` — 結構化排程資料
2. `output/w{nn}_schedule.html` — 視覺化排程
3. Google Calendar 事件（同步至 `primary` 日曆，📋 前綴）

「實際完成」日曆
（`4nqk94mmpmctc9fu49ps673484@group.calendar.google.com`，✅ 前綴）為獨立日曆，
由週報 prompt 在「三帳戶回顧」區段查詢使用。

## 不可 commit 的檔案

下列含病人資料的檔案請勿推送到 GitHub：

- `csv_input/*.csv`
- `output/mammo_*_reports.json`
- `output/mammo_birads0.json`
- 手動匯出的報告純文字檔（如 `*.txt`）
- 任何含病歷號、報告全文或病人識別資料的檔案

原始程式碼、prompt、範本、README 等檔案經審視後可正常 commit。

## 常用檢查

編譯檢查 Python 腳本：

```powershell
python -m py_compile radtracker\parse_csv.py radtracker\generate_report.py radtracker\biopsy_tracker.py radtracker\mammo_tracker.py radtracker\mammo_report_fetcher.py
```

PowerShell 顯示中文亂碼時，可在當前 session 切換至 UTF-8：

```powershell
chcp 65001
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new()
$OutputEncoding = [System.Text.UTF8Encoding]::new()
```
