# Radiology Tracker — Claude Code 專案指南

## 你是誰
你是一位放射科醫師（Jieyu）的工作追蹤助手。你的核心任務是：
1. 解析工作回報資料（CSV 為主，xlsx 為 Legacy）
2. 產出標準化週報
3. 提供排程建議
4. 排程同步至 Google Calendar

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

## 資料來源

### CSV 模式（主要，推薦）
醫院放射科資訊系統匯出的月報表，自動解析工作量。

- **編碼**：cp950 (Big5)
- **分隔**：Tab (TSV)
- **檔案**：
  - `YYYYMM.csv` — 佳里院區（主要工作地點）
  - `YYYYMMYK.csv` — 永康院區（值班 Brain/Neck CT、MR）
  - 兩份 CSV 格式完全相同，可合併處理

#### CSV 欄位對照（0-indexed）
| 欄位索引 | 名稱 | 說明 |
|----------|------|------|
| 0 | case_id | 案號（同一檢查單號可含多筆 rows） |
| 1 | chart_no | 病歷號 |
| 3 | order_date | 開單日 (MM/DD/YYYY) |
| 4 | source | 來源代碼：1=急診, 2=門診, 3=住院, 4=健檢 |
| 5 | dept | 科別代碼 (S101, S103 等) |
| 6 | order_code | 醫令代碼（用於 CT 子分類） |
| 7 | qty | 次數 |
| 8 | exam_name | 項目名稱（用於模態分類） |
| 13 | report_date | 報告日期 (MM/DD/YYYY) |
| 14 | report_time | 報告時間 (HH:MM) |
| 17 | reporter_id | 報告醫師 ID (預設 A80748) |
| 24 | work_points | 工作點值 |
| 28 | weighted_pts | 加權點值 |

#### case_id 分組邏輯
- 同一 case_id 的多筆 rows = 1 份邏輯案件
- 例：case_id 800972090092142 含 8 rows（4 種 XR × 2 views）= 1 份困難 XR
- 計數單位：1 case_id = 1 份（與 xlsx 手動計數一致，已驗證）

#### 排除規則
- `exam_name` 含 "Contrast" 且 `work_points` = 0 → 藥品計費行，排除

#### 來源代碼與急打判定
| 代碼 | 來源 | 急打 |
|------|------|------|
| 1 | 急診 | **是** |
| 2 | 門診 | 否 |
| 3 | 住院 | **是** |
| 4 | 健檢 | 否 |

> 急打判定**僅依來源代碼**，與院區無關。佳里、永康院區皆可能有急打。

### XLSX 模式（Legacy）
手動逐筆輸入，保留向後相容。詳見下方「資料格式規範 > tracker.xlsx」。

---

## 模態分類規則（CSV 自動判定）

### 主分類（依 exam_name）
| 模態 | 判定條件 |
|------|----------|
| CT | 開頭為 `CT-` 或 `CTA-`；含 `Low Dose CT` / `LDCT` / `HRCT` |
| US | 開頭為 `US-` |
| Mammo | 含 `Mammography` |
| MR | 開頭為 `MR` 或含 `MRI` |
| BMD | 含 `Bone densitometry` |
| IVP | 含 `I.V.P.` 或 `IVP` |
| XR | 以上皆不符者（預設） |

### CT 子分類
| 子類別 | 判定條件 |
|--------|----------|
| Brain | exam_name 含 `Brain` 或 `Head`，且非顯影劑 order_code |
| Brain-C | exam_name 含 `Brain`/`Head` + order_code 含 33072 或 33090 |
| Neck/CTA | exam_name 含 `Neck`/`C-Spine`/`C Spine`，或開頭為 `CTA-` |
| Chest/Abd | 以上皆不符（預設） |

### US 子分類
| 子類別 | 判定條件 |
|--------|----------|
| 困難 | Breast, Prostate, Extremity, Lower Extremity A./V., Scrotum, Parotid Gland, Other |
| 一般 | 以上皆不符（預設） |

### XR 難度分類
| 難度 | 條件 |
|------|------|
| 急打 | 來源 = 1（急診）或 3（住院） |
| 困難 | 非急打，unique exam_name 種類 >= 3 |
| 中等 | 非急打，unique exam_name 種類 = 2 |
| 普通 | 非急打，unique exam_name 種類 = 1 |

---

## 時間推估方法（CSV 模式）

CSV 無法精確測量每筆報告的花費時間（61.4% 為批次簽發同一時間戳記）。
採用**每日粗估**方式：

1. **深夜歸屬**：00:00-05:59 的報告歸屬前一工作日
2. **排序**：將當日所有報告時間戳排序
3. **Session 切割**：相鄰報告間隔 > 30 分鐘 → 視為不同 session
4. **活躍時數**：各 session 首尾時間差加總
5. **最低保障**：至少 0.5 分鐘 × 報告數
6. **標記**：所有時間數據標記為 `(estimated)`

### 已知限制
- 值班日批次簽發率 ~76%，時間推估不準確
- 跨日批次簽發（如週六工作→週日簽發）會導致日期歸屬偏差
- 跨月報告若不在當月 CSV 中會遺失（如 2/28 工作→3/1 簽發，3/1 不在 202602.csv）

---

## 固定工作規則

### 每日目標
- X光：100-150 份/日（上限 150）
- CT：6 份/日（上限 8）
- US：15 份/日
- Mammo：15 份/日
- 讀書：每兩天 2 小時

### 可用時間
- 週一：全天可用（~8hr）
- 週二：白天另有工作，下午+晚間可用
- 週三：白天另有工作，下午+晚間可用
- 週四：白天另有工作（臨床），下午+晚間可用；通常值班日
- 週五：上午可用（~4hr），下午上課；部分週五 21:00 後可排 Mammo
- 週六：全天可能上課；18:00 後可排 Mammo
- 週日：午後可用（~4hr）

### 值班規則
- 通常週三或週四值班
- 值班 X光+CT 需當日處理
- 值班期間會有額外急診 CT/X光

### Mammo 場地限制
- 週一、週六：18:00 後可排
- 週五：21:00 後可排
- 其他時間需確認場地可用性

---

## 模態代碼表與基準速率

### X光
| 子類別 | 代碼 | 基準速率 | 最新實測 | 建議更新 |
|--------|------|----------|----------|----------|
| 普通 | xr | 35份/hr | 60.2份/hr (2/23-3/1) | → 50份/hr |
| 急打 | xr-u | 25份/hr | 37.5份/hr (2/23-3/1) | → 35份/hr |
| 中等 | xr-m | 30份/hr | 33.9份/hr | 維持 30份/hr |
| 困難 | xr-h | 20份/hr | 12.0份/hr (n=5) | 維持 20份/hr（樣本小） |

### CT
| 子類別 | 代碼 | 基準速率 | 最新實測 |
|--------|------|----------|----------|
| Chest/Abdomen | ct | 3.5份/hr | 3.2份/hr |
| Brain (non-contrast) | ct-br | 7份/hr | 10.0份/hr |
| Neck/CTA | ct-nk | 3.5份/hr | 2.8份/hr |
| Brain contrast | ct-brc | 3份/hr | — |

### US
| 子類別 | 代碼 | 基準速率 | 最新實測 | 建議更新 |
|--------|------|----------|----------|----------|
| 一般 | us | 10份/hr | 18.2份/hr | → 18份/hr |
| 困難 | us-h | 4份/hr | 5.0份/hr | 維持 4份/hr |

### 其他
| 模態 | 代碼 | 基準速率 | 最新實測 |
|------|------|----------|----------|
| Mammo | mm | 17份/hr | 23.8份/hr → 建議 22份/hr |
| MR | mr | 2份/hr | 2.0份/hr |
| IVP | ivp | 12份/hr | — |
| BMD | bmd | 60份/hr | ~49份/hr |

---

## 資料格式規範

### week_input.yaml 模板（推薦，CSV 模式用）
```yaml
week: "2026-W09"
date_range: "02/23 ~ 03/01"

remaining:
  start: {XR: 617, CT: 16, US: 9, Mammo: 76}
  end:   {XR: 464, CT: 15, US: 42, Mammo: 22}

duty_day: "三"
class_day: "五"
class_time: "13:00~17:00"
notes:
  - "週三值班"
study: []
```
> 使用者每週只需填寫 8 個數字（4 模態 x 期初/期末）+ 選填備註

### [Legacy] tracker.xlsx 欄位（每日工作紀錄 sheet）
| 欄位 | 類型 | 說明 |
|------|------|------|
| 日期 | date | YYYY/MM/DD |
| 星期 | text | 一~日 |
| 時間戳記 | time | HH:MM |
| 模態 | text | xr/ct/us/mm/mr/bmd/other |
| 子類別 | text | Chest/Abd, Brain, Mammo, 一般, 困難 等 |
| 難度 | text | 普通/急打/中等/困難（主要用於 X光） |
| 完成數量 | number | |
| 花費時間(分) | number | |
| 速率(份/hr) | number | 公式自動計算 |
| 備註 | text | 值班/臨床/雜務 等 |

### 深夜歸屬規則
凌晨 00:00-05:59 的記錄歸屬前一個工作日。CSV 模式由 `get_work_date()` 自動處理；xlsx 模式依星期欄位已標記。

### [Legacy] week_input.md 模板（xlsx 模式用）
```markdown
# 本週條件
- 日期範圍：MM/DD(一) ~ MM/DD(日)
- 期初剩餘：X光 ___份(中等困難___), CT ___份, US ___份, Mammo ___份
- 期末剩餘：X光 ___份(中等困難___), CT ___份, US ___份, Mammo ___份
- 值班日：週___
- 上課日：週___ (時段 ___:___~___:___)
- 特殊不可用時段：

# 讀書紀錄
- (日期) (時數) (主題)

# 其他備註
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
- BMD 不計入主要追蹤模態（X光/CT/US/Mammo 為四大追蹤模態）
- CSV 模式無法追蹤非報告活動（臨床/雜務/交通），僅記錄報告工作
- CSV 模式提供工作點值（work_points），xlsx 模式不提供
- [Legacy] xlsx 模態欄位不一致：子類別可能在「子類別」或「難度」欄位，需合併判斷
- [Legacy] other/雜務/臨床 的時間計入非報告時間，不計入報告效率

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

## 排程規劃 & Google Calendar 同步

### 概述
每週排程規劃產出三項：
1. `output/w{nn}_schedule.json` — 結構化排程資料（必須）
2. `output/w{nn}_schedule.html` — 視覺化排程（必須）
3. **Google Calendar 事件** — 同步至 primary 日曆（必須）

**重要：排程建立或修改時，必須同時更新三者。**

### Schedule JSON 格式
```json
{
  "week": "2026-W14",
  "date_range": "03/31~04/05",
  "days": 6,
  "notes": ["特殊備註"],
  "backlog": {
    "X光": {"start": 632, "forecast_added": 200, "target_completed": 480, "forecast_end": 352}
  },
  "totals": {
    "cases": 643, "hours": 27, "report_hours": 24,
    "by_modality": {"X光": 480, "CT": 18, "US": 75, "Mammo": 70}
  },
  "daily": [
    {
      "date": "2026-03-31",
      "day": "二",
      "tags": ["normal"],
      "total_cases": 93,
      "active_hr": 4.75,
      "slots": [
        {"start": "13:00", "end": "15:00", "type": "report", "modality": "US", "count": 25, "rate": 12, "colorId": "10", "note": "US 優先"},
        {"start": "09:00", "end": "12:00", "type": "clinical", "label": "臨床"},
        {"start": "12:00", "end": "13:00", "type": "break", "label": "午餐"}
      ]
    }
  ],
  "gcal": {
    "calendar_id": "primary",
    "event_prefix": "📋",
    "color_map": {"XR": "9", "CT": "11", "US": "10", "Mammo": "5"},
    "synced_event_ids": ["event_id_1", "event_id_2"]
  }
}
```

### Slot 類型
| type | 說明 | 必要欄位 |
|------|------|----------|
| `report` | 報告工作 | modality, count, rate, colorId |
| `clinical` | 臨床/其他工作 | label |
| `break` | 休息/午餐 | label |

### Google Calendar 同步規則

#### 日曆配置
| 用途 | Calendar ID | 備註 |
|------|-------------|------|
| 預計行程（排程） | `primary` (jieyu166@gmail.com) | 📋 前綴 |
| 實際完成（回顧） | `4nqk94mmpmctc9fu49ps673484@group.calendar.google.com` | ✅ 前綴 |

#### 事件格式
- **Title**: `📋 [模態] 預計 x[件數]`
  - 範例：`📋 [XR] 預計 x100（急打）`, `📋 [Mammo] 預計 x20`
- **Color**: XR=9(Blueberry), CT=11(Tomato), US=10(Basil), Mammo=5(Banana)
- **Description** 須包含：
  ```
  目標：[模態] [件數]份（[子分類]）
  速率：[rate]份/hr
  預估耗時：[hours]hr

  [備註]
  Backlog: 期初 [start] → 目標消化 [target] 份
  ```
- **sendUpdates**: `"none"`（不發通知）
- **timeZone**: `"Asia/Taipei"`

#### 建立流程
1. 從 schedule JSON 的 `daily[].slots[]` 中篩選 `type === "report"` 的 slot
2. 每個 report slot → 1 個 Google Calendar 事件
3. 建立後，將 event ID 寫入 `gcal.synced_event_ids`
4. 更新 schedule JSON 檔案

#### 修改流程
1. 讀取 schedule JSON 的 `gcal.synced_event_ids`
2. 刪除所有已同步的事件
3. 依據修改後的 slots 重新建立事件
4. 更新 `synced_event_ids` 為新的 event ID 清單

#### 刪除流程
1. 讀取 `gcal.synced_event_ids`
2. 逐一刪除事件
3. 清空 `synced_event_ids` 陣列

### 排程規劃規則（由使用者每週補充修正）

#### 基礎約束
- 每日目標上限：X光 150, CT 8, US 15, Mammo 15
- 連續同模態 > 2hr 需安排休息
- 使用者指定的臨床/上課/值班時段不可排報告

#### 每日可用時段（預設，使用者可覆寫）
| 日 | 預設可用 | 備註 |
|----|----------|------|
| 一 | 全天 ~8hr | 目前也工作，需使用者確認 |
| 二 | 下午+晚間 ~4hr | 上午臨床 |
| 三 | 下午+晚間 ~4hr | 上午另有工作；通常值班 |
| 四 | 下午+晚間 ~4hr | 上午臨床 |
| 五 | 上午 ~4hr | 下午上課 |
| 六 | 彈性 | Mammo 18:00 後 |
| 日 | 午後 ~4hr | |

#### 重要
- **每週工作狀況不同，以使用者規劃時的補充為主**
- 使用者提供的 schedule HTML 或口頭修正優先於預設規則
- 修改排程時必須同步更新 JSON + HTML + Google Calendar 三者
