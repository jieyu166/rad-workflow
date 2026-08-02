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
| 11 | **exec_date** | **執行日期＝檢查實際施作日** (MM/DD/YYYY)；≠報告日（報告常晚 1–4 天）。看「檢查何時做／何時有片可讀」用此欄，非 col13 |
| 12 | exec_time | 執行時間 (HH:MM)＝檢查施作時間 |
| 13 | report_date | 報告日期 (MM/DD/YYYY) |
| 14 | report_time | 報告時間 (HH:MM) |
| 17 | reporter_id | 報告醫師 ID (預設 A80748) |
| 24 | work_points | 工作點值 |
| 28 | weighted_pts | 加權點值 |

> ⚠ **PII 欄位**：col2 姓名、col25 身份證號、col26 生日、col1 病歷號皆為病患識別資料 → CSV 一律 gitignore、輸出（含病歷號）勿 commit/外傳。

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
| **LDCT** | exam_name 含 `Low Dose CT` 或 `LDCT`，**或 order_code 開頭 `33904`** |
| Brain | exam_name 含 `Brain` 或 `Head`，且非顯影劑 order_code |
| Brain-C | exam_name 含 `Brain`/`Head` + order_code 含 33072 或 33090 |
| Neck/CTA | exam_name 含 `Neck`/`C-Spine`/`C Spine`，或開頭為 `CTA-` |
| Chest/Abd | 以上皆不符（預設） |

> **LDCT 註**：order_code 33904-* 系列（33904-3 / 33904-8 等）皆為低劑量肺癌篩檢 CT。多數 source=2(門診) 但臨床性質屬健檢，依新策略應歸 **P2 (10d SLA)**，見〈臨床優先 Triage 策略〉。

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

## 臨床優先 Triage 策略（2026-05-14 起採用）

當 backlog 超過單人合理上限（如 W20 XR 1158 件），改採**按臨床急迫性 triage**，**XR 絕對總量不再是主要指標**。

### 優先級定義

| 優先級 | 條件 | SLA | 策略 |
|---|---|---|---|
| **P1 急打** | source = 1(急診) **或** 3(住院) | ≤24hr | ASAP，同日完成 |
| **P2a 健檢 XR** | source = 4 | ≤10d | 10 天內 |
| **P2b LDCT** | exam=LDCT 或 order_code 開頭 `33904` | ≤10d | 每日搭配一般 CT 處理（LDCT 較快 ~5-7/hr） |
| **P3 門診新** | source = 2 且 age < 3d | ≤3d | 維持讀 |
| **P4 門診舊** | source = 2 且 age ≥ 3d | — | **可放棄** |

> 注意：CT 也適用 P1（急診/住院 CT）；US/Mammo 多為 source=2/4，依此規則自動歸類。

### 監控指標（取代「XR 期末總量」）

| 新 KPI | 警示閾值 |
|---|---|
| P1 急打 pending > 24hr | > 10 件 |
| P2 健檢/LDCT 超 10 天 | > 5 件 |
| P3 門診新單 pending | > 50 件 |
| CT/US/Mammo 週末剩餘 | > 10 件 |

### 工具

```bash
# 跑 priority breakdown（pending CSV 模式）
python priority_breakdown.py --csv csv_input/{pending}.csv --pending --today YYYY-MM-DD --json output/priority_{week}.json

# 完成 CSV 模式（回顧 TAT）
python priority_breakdown.py --csv csv_input/1150515_CL.csv
```

→ 輸出供 weekly_report **Section 11 Priority Triage Status** 引用（見 `weekly_review_prompt.md`）。

### 已知限制
- 需可匯出 **pending CSV**（含 order_date 但無 report_date 的開單）才能即時監控
- 若僅有 completed CSV，只能事後檢視 TAT，不能反映當前 backlog 健康度

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

#### 永康值班典型量（W19 2026-05-08 驗證）
| 模態 | 典型件數 | 備註 |
|---|---|---|
| XR 急打 | **50+ 件** | 含本院積壓 + 永康急診（W19 實際 133 件，極端值）|
| Brain CT | **5-10 件** | 預估 rate 7/hr |
| 一般 CT | 0-5 件 | |
| MR | 0-1 件 | |

排程 W{N}_schedule 時，永康值班週的 XR/CT new 量約：
- XR new ~580/週（vs 非值班 ~450/週）
- CT new ~44/週（vs 非值班 ~25/週，多出來自 Brain CT）

### Mammo 場地/可讀時段（2026-08-03 更新，取代舊規則）
| 日 | Mammo 可讀時段 |
|---|---|
| 一、二、三 | **全天**（主力窗口）|
| 四 | 僅早上 |
| 五 | 晚上 |
| 六、日 | **通常不可用**（場地限制，W31 實證：週六/日各只做 1–2 件）|

> ⚠ 舊規則（一/六 18:00 後、五 21:00 後）已**淘汰**。
> **排程鐵則**：Mammo 幾乎只能靠**一~三白天**消化 —— 週四僅早上、週五僅晚上、**週末視同零產能窗口**。
> 推論：若每週新增 ~56–65 件，就必須在一~三三天內排 **每天 20–30 件**才不會滾動累積；把 Mammo 排在週末等於必然遞延（W31 教訓：期末 29 件全數順延至下週一）。

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
| **LDCT** | ct-ldct | **5-7份/hr** | — | 屬 P2 健檢 SLA 10d；建議每日搭配一般 CT 1-2 件 |

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

### 週新增量 baseline（2026-05 觀察）

排程預測 backlog 期末時使用，**新增量集中於 Mon-Fri，週末/假日通常無新單（除急診外）**。

| 模態 | 非值班週 new | 值班週 new | 母親節 surge |
|---|---|---|---|
| XR | ~450 | ~580 | 同 |
| CT | ~25 | ~44 | 同 |
| US | ~70（週二 surge） | 同 | 同 |
| Mammo | **~90**（2026-05 下旬上修，原估 46）| 同 | **+120**（一/二/五 集中）|
| IVP | ~5-7 | 同 | 同 |

> **Mammo 新增量上修註（2026-05-25）**：W22 起 user 回報 Mammo 每週新增約 90 件（遠高於先前估的 46）。單週完成 ~115 件僅能淨減 ~25，**Mammo backlog 難在單週清空**，需連續數週每週完成 >90 才能壓低。→ **改善（2026-07-20）**：Mammo 可讀時段其實是一~三全天+四早上+五晚（見〈Mammo 場地/可讀時段〉），比舊認知寬很多，一~三白天應多排 Mammo，別再視為只能週末晚。

⚠ **週末/假日 plan 折扣**：歷史教訓（W19 母親節 5/10 計畫 164 件、實際 4 件），週末/假日工作量**以「平日同類 × 50% 」估算**，避免 over-commit。

### 檢查執行日（col11）weekday 分佈（2026-07-20 分析，近 6 週中位數）

**用途**：`exec_date`(col11) = 檢查何時做 = 何時有片可讀。此表看「各模態片子哪天進來」，比 order_date 更貼近可讀時點。排程新增量時參考。

| 星期 | XR | CT | US | Mammo | IVP | BMD |
|---|---|---|---|---|---|---|
| 一 | ~98 | 0 | 0 | ~16 | 0 | ~7 |
| 二 | ~123 | 0 | **~65** | ~23 | 0 | ~5 |
| 三 | ~102 | ~5 | 0 | 0 | ~4 | 0 |
| 四 | **~2** | ~11 | 0 | 0 | 0 | 0 |
| 五 | ~21 | ~11 | 0 | ~10 | 0 | 0 |
| 六 | ~44（變異大 4–187） | 0 | 0 | 0 | 0 | 0 |
| 日 | ~0（06/21 有 309 為離群，健檢/急診批次） | 0 | 0 | 0 | 0 | 0 |

重點（排程用）：
- **US 只有週二**（~65），其他天幾乎 0 → US backlog 主要週二一次進來
- **週四幾乎不做 XR**（中位 2）→ 週四是 **CT 日**（~11）；非值班週週四別排大量 XR
- **XR 執行集中 一/二/三**（~100-123），四/五低、六變異大、日近 0 → 週末執行少，故**週一開工可讀 XR backlog 薄**（週末做的少）；週一做的 XR 多當天/隔天才讀完
- **CT 做在 三/四/五**（~5/11/11）；**Mammo 做在 一/二/五**（~16/23/10）；**IVP 週三**；**BMD 一/二**
- 註：exec_date ≠ report_date（報告常晚 1–4 天）；值班/佳里加班日會額外墊高當日執行量，非常態

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
- **典型結論（2026-03~06，n≈8400）**：午後 13-17 最高（18.1 c/hr、中斷率 7% 全日最低）；晚間 19-23 最低（15.7）；平日最熱在 15 點（19.9）；「下午不被打斷」勝「晚餐後」
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
