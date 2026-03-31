# 排程規劃 Prompt

## 使用時機
每週排程規劃時，參考此 prompt 結合 weekly_report.json 產出排程。

## 輸入
1. `output/weekly_report.json` — 本週（或上週）工作報告，取得 backlog 數據
2. `week_input.yaml` — 使用者填寫的期初/期末剩餘量、值班日、上課日
3. 使用者口頭補充 — **優先於所有預設規則**

## 輸出（三項全部必須）
1. `output/w{nn}_schedule.json` — 結構化排程
2. `output/w{nn}_schedule.html` — 視覺化排程
3. Google Calendar 事件 — 同步至 primary 日曆

## 規劃步驟

### Step 1: 計算 Backlog 與目標
- 期初剩餘 = 上週期末（或使用者提供）
- 預計新增 = 歷史平均或使用者估計
- 目標完成 = 依可用時數 x 速率推算
- 預估期末 = 期初 + 新增 - 完成

### Step 2: 確認每日可用時段
- 讀取 week_input.yaml 的 duty_day, class_day, class_time
- 套用使用者補充的特殊安排
- **使用者規劃時的補充覆寫所有預設**

### Step 3: 分配模態至時段
- US/CT 優先排（耗時長、速率慢）
- XR 填充剩餘時段（速率快、彈性大）
- Mammo 依場地限制排入可用時段
- 連續同模態 > 2hr 需休息

### Step 4: 產出 JSON + HTML
- JSON 格式見 CLAUDE.md「Schedule JSON 格式」
- HTML 格式見 w14_schedule.html 為範本

### Step 5: 同步 Google Calendar
- 讀取 JSON 中 `daily[].slots[]` 的 report 類型
- 每個 report slot 建立一個 Google Calendar 事件
- 事件格式：`📋 [模態] 預計 x[件數]`
- Color: XR=9, CT=11, US=10, Mammo=5
- Calendar: primary
- sendUpdates: none
- 建立後將 event ID 寫回 JSON 的 `gcal.synced_event_ids`

## 修改排程
當使用者要求修改排程時：
1. 讀取現有 `w{nn}_schedule.json`
2. 刪除 `gcal.synced_event_ids` 中的所有 Google Calendar 事件
3. 修改 slots
4. 重新建立 Google Calendar 事件
5. 更新 JSON（含新 event IDs）+ HTML

## Google Calendar 事件 Description 模板
```
目標：[模態] [件數]份（[子分類/備註]）
速率：[rate]份/hr
預估耗時：[hours]hr

[特殊備註]
Backlog: 期初 [start] → 目標消化 [target] 份，期末 [end]
```

## 速率參考
| 模態 | 速率 | 備註 |
|------|------|------|
| XR 混合 | ~42份/hr | 含普通+急打+中等 |
| XR 急打 | 35份/hr | 急診/住院 |
| XR 普通 | 50份/hr | 門診/健檢 |
| CT Chest/Abd | 3.5份/hr | |
| US 混合 | ~12份/hr | 含一般+困難 |
| US 一般 | 18份/hr | |
| US 困難 | 4份/hr | |
| Mammo | 22份/hr | |
| BMD | 60份/hr | |
