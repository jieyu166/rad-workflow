# CSV 規格與解析規則

> 從 `radtracker/CLAUDE.md` 拆出。看「欄位在哪、模態怎麼判、時數怎麼估」時讀這份。

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
- 例：某 case_id 含 8 rows（4 種 XR × 2 views）= 1 份困難 XR
- ⚠ **case_id 的前 8 碼就是病歷號**（結構：`{8 碼病歷號}{7 碼流水}`）→ **case_id 視同 PII**，
  文件與範例一律不寫真實值，需要示意時用 `{chart_no}0177142` 這種佔位寫法
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
