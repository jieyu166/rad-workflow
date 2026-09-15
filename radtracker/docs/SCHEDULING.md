# 排程規則與 Google Calendar 同步

> 從 `radtracker/CLAUDE.md` 與 `schedule_prompt.md` 合併。規劃下週行程時讀這份。

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

#### 永康值班典型量 —— **平日值班與假日值班是兩個量級，不可混用**

依 `exec_date` 實算（2026-03 ~ 09，值班日當天的急打 XR）：

| 值班型態 | 當日急打 XR | 實測範圍 | 樣本 |
|---|---|---|---|
| **平日值班**（多為週三，偶爾週五） | **~105 件** | 83–200 | 20 天 |
| **假日值班 · 週六** | **~175 件** | 169–182 | 2 天 |
| **假日值班 · 週日** | **~320 件** | 309–336 | 2 天 |

> 原文件寫「50+ 件」是平日值班的下限，作為排程數字低估了一倍 ——
> 平日值班請用 **~105**，離群可到 200（如 2026-07-08 的 197、2026-03-18 的 173）。

**連續兩天假日值班** = 六 ~175 ＋ 日 ~320 ≈ **500 件急打**，兩次實測高度一致
（W25 06/20–21 共 491、W37 09/12–13 共 505）。這種週的特徵：

- XR 週新增衝到 850–950；週末兩天就佔全週件數 60–66%、投入 13–18hr
- **平日產能會被排擠到剩 50–60%** —— 別在同一週再壓 Mammo 主力或專案時段
- 週末急打幾乎純 P1（急診＋住院 >97%，門診健檢 <3%）→ 不能延後
- 值班日 XR 批次簽發，速率可用 45/hr（非平日的 35）

其他模態（平日與假日值班相近）：

| 模態 | 當日件數 | 備註 |
|---|---|---|
| Brain CT | 5–10 件 | rate 8–10/hr，較快 |
| 一般 CT | 0–5 件 | |
| MR | 0–1 件 | |

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

> 🔴 **週六上班週的新增量（2026-08-10 確認）**：週六到佳里上班時，當天會新增 **Mammo 15–20 件 + US ~12 件**。US 當日可消化。
>
> **週末 Mammo 取決於「人在不在佳里」**：
> - 一般週末不在佳里 → 零窗口，週六新增的 Mammo 必然留到下週一（期末 ~17 件地板）
> - **若週末留在佳里處理 Mammo（如 W33）→ 週末窗口打開**，當週 Mammo 可望清零
> ⇒ 排程前先確認「這個週末人在哪裡」，再決定 Mammo 要不要排週末。

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

---

## 規劃步驟（原 schedule_prompt.md）

### 輸入
1. `output/weekly_report.json` — 取得 backlog 數據
2. `week_input.yaml` — 期初/期末剩餘量、值班日、上課日
3. **使用者口頭補充 —— 優先於所有預設規則**

### 輸出（三項全部必須，且必須同時更新）
1. `output/w{nn}_schedule.json`
2. `output/w{nn}_schedule.html`
3. Google Calendar 事件（primary，📋 前綴）

### Step 1: 計算 Backlog 與目標
- 期初剩餘 = 上週期末（或使用者提供）
- 預計新增 = 歷史平均或使用者估計
- 目標完成 = 依可用時數 × 速率推算
- 預估期末 = 期初 + 新增 − 完成

### Step 2: 確認每日可用時段
- 讀 `week_input.yaml` 的 duty_day / class_day / class_time
- **使用者規劃時的補充覆寫所有預設**

### Step 3: 分配模態至時段
- **Mammo 最優先**：窗口最窄（見上方場地規則），先卡位再排其他
- **標註/專案時段排在當日第一個工作時段**（W36 排在報告後只做 22%，W37 排最前做到 93%）
- US/CT 次之（耗時長、速率慢）
- XR 填充剩餘時段（速率快、彈性大）
- 連續同模態 > 2hr 需休息

### 混合速率（估整段時間時用，子分類速率見 docs/BASELINES.md）
| 模態 | 混合速率 | 備註 |
|------|------|------|
| XR 混合 | ~42–46 份/hr | 含普通+急打+中等 |
| US 混合 | ~12 份/hr | 含一般+困難 |

### 排程產生器的必備驗證（依歷次踩雷累積）
寫 `gen_w{nn}.py` 時務必 assert：
- 每日 US ≤ 15；CT ≤ 6（值班日可放寬，需在程式內註明依據）
- Mammo 只排在有場地的日子；**累積讀取量 ≤ 累積到片量**（不能讀還沒到的片）
- 專案/標註時段容量：`10 分準備 + 8 分 × 份數 ≤ 時段分鐘數`
- 有標註的日子，第一個 report/project slot 必須是 project
- 同日時段不重疊；`期初 + 新增 − 消化 == 預測期末` 且不為負
