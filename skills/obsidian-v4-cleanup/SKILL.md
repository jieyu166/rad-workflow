---
name: obsidian-v4-cleanup
description: 整理 Obsidian 放射科筆記的 V4 格式、引用或閱片 callout，製作 PDF 深讀筆記，或查核既有筆記的新知；不處理一般程式碼修正。
---

# Obsidian 放射科筆記

只執行使用者要求的任務；單純修引用不自動重做 YAML 或 PDF 深讀。編號保留既有引用，不補回已移出的 Task 4／6／7。

| 本次要求 | 按需讀取 |
|---|---|
| V4 YAML／筆記格式 | [Task 1](references/task1-v4.md) |
| 外部引用改成腳註 | [Task 2](references/task2-footnotes.md) |
| 閱片題目表格改 callout | [Task 3](references/task3-callouts.md) |
| PDF 論文或教科書章節深讀 | [Task 5](references/task5-pdf.md)，先跑 Step 0 兩層分流決定 L1／L3，保留來源覆蓋與 Canvas 驗證 |
| 既有醫學筆記現代新知查核 | [Task 8](references/task8-overview.md)，再讀其指定的查核規範 |
| 已授權的批次格式整理 | 相應 Task，加上 [批次整理與驗證](references/bulk-cleanup.md) |
| 影片、SRT 導航、課程首頁 | 使用 lecture-to-notes，不在本 skill 重複影片流程 |

讀取前先確認輸入與要交付的成果。明確的局部整理直接完成；來源不明或要求改變原意時，只詢問必要決策。保留原文內容、數值與臨床不確定性，格式整理不補入模型知識。

## Critical Safety Rules

一般整理保留以下內容；Task 5 另遵循 PDF 重建的歸檔與來源要求，Task 8 保留歷史層並分開呈現現代證據。

1. **Spaced Repetition comments**: `<!--SR:!2024-01-15,30,270-->` — do not touch these under any circumstance
2. **Image embeds**: `![[image.png]]` — preserve exactly during ordinary cleanup; validate before carrying into a Task 5 rebuild
3. **Embed references**: `![[other note#heading]]` — preserve exactly during ordinary cleanup; validate before carrying into a Task 5 rebuild
4. **Dataview queries**: ` ```dataview ... ``` ` blocks — preserve during ordinary cleanup; retain in Task 5 only when still applicable
5. **Existing wikilinks**: `[[any link]]` — never break them during ordinary cleanup; do not blindly copy stale or placeholder links into a Task 5 rebuild

---

## 完成條件

驗證本次改動的格式、引用與連結；未修改的層不重做。Tasks 1–3：YAML 有變動才驗證 YAML，引用有變動才核對腳註，callout 有變動才核對題目結構；共同保留規則始終適用。Task 5／8 使用各自參考文件的來源與歸檔驗證，不以字數或格式通過取代內容覆核。
