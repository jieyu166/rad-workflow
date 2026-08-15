## Why

現有 Cephalometric Analysis 頁面以牙科教學與大量手動數值輸入為主，對非牙科背景的放射科醫師造成過高認知與操作負擔。需要把流程改成以影像為中心的漸進式精靈，讓醫師完成最少四個核心 landmark 後即可產生保守、可編輯且具完整巡檢脈絡的放射科報告。

## What Changes

- 以 V2 漸進式精靈取代現有手動表單流程，支援貼上、拖放或選擇單張 lateral cephalometric PNG/JPG。
- 提供影像縮放、平移、反相、復原／重做、鍵盤微調與逐點說明。
- 加入影像品質與全影像六區巡檢 checklist，所有項目預設尚未評估。
- 加入兩刻度點比例尺校正；未校正時只允許角度量測，不產生 mm 數值。
- 以 S、N、A、B 為核心必做點，完成後計算 SNA、SNB、ANB 並開放基本報告。
- 將 ANS、PNS、Go、Me 與上下門牙切端／根尖分成可整組跳過的進階階段；只產生相依點完整的量測。
- 依已完成的巡檢與量測組裝正式放射科格式報告，保留可編輯與複製能力，並清楚列出未評估項目與固定限制。
- 維持單檔、完全離線架構；影像、病人資料、landmark 與報告只存在當次瀏覽器記憶體，不使用外部資源或永久儲存。

## Capabilities

### New Capabilities

- `guided-cephalometric-workflow`: 涵蓋離線影像輸入、全影像巡檢、比例尺校正、漸進式 landmark 標記及安全的互動狀態管理。
- `cephalometric-report-generation`: 涵蓋具相依性檢查的角度／線性量測、保守判讀與正式放射科報告組裝。

### Modified Capabilities

（無）

## Impact

- Affected specs: guided-cephalometric-workflow, cephalometric-report-generation
- Affected code:
  - Modified: tool/ceph-analysis.html
  - New: tests/test_ceph_analysis.py
  - New: docs/superpowers/specs/2026-08-13-ceph-analysis-v2-design.md
  - Removed: none
- External dependencies: none
- Network behavior: no requests or uploads
