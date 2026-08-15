## Context

現有 `tool/ceph-analysis.html` 是單檔靜態頁面，重心為牙科理論教學與十多項手動量測輸入。V2 的主要使用者是非牙科背景的放射科醫師，必須把負擔降到載入一張 lateral cephalometric image、完成全影像巡檢、依序標記最少四個核心 landmark，然後取得可編輯的放射科報告。頁面須在本機瀏覽器完全離線運作，且不得保存或傳送病患影像與資料。

## Goals / Non-Goals

**Goals:**

- 讓醫師透過單一路徑精靈完成影像載入、巡檢、比例尺校正、核心與選做 landmark。
- 完成 S、N、A、B 後立即提供 SNA、SNB、ANB 與保守的 sagittal skeletal relationship。
- 只有在相依點完整時才產生進階角度或校正後線性數值。
- 產生正式放射科架構、可編輯且可複製的報告，明確呈現未評估、限制與不確定性。
- 維持單檔離線工具，並以純函式與 production DOM fixture 建立可重複驗證。

**Non-Goals:**

- 不提供完整 orthodontic treatment planning、所有 Steiner／Tweed／Downs 分析或生長預測。
- 不由 lateral cephalogram 診斷 obstructive sleep apnea。
- 不處理 DICOM metadata、PACS、伺服器上傳、病患資料庫或跨工作階段保存。
- 不在缺少比例尺校正時推測 mm 數值。
- 不從影像水平軸自動推測 overjet 或 overbite。
- 不使用 AI 自動找 landmark；V2 保留醫師最終標點責任。

## Decisions

### 單檔離線與記憶體狀態

V2 直接取代 `tool/ceph-analysis.html`，保留既有首頁網址。HTML、CSS、JavaScript 與圖示全部內嵌，不載入字型、CDN 或其他網路資源。影像以 Blob/Object URL 或同等本機解碼方式存在記憶體；state 不寫入 localStorage、IndexedDB、cookie 或網路。載入另一張影像前必須確認清除目前巡檢、校正、landmark 與報告。替代方案是保留 V1 並新增第二網址，但會增加導航與維護負擔，且 Git 已提供回復歷史，因此不採用。

### 漸進式精靈與相依性

流程固定為影像、六區巡檢、比例尺校正、核心 landmark、選做進階、報告。巡檢未完成與比例尺跳過不阻擋角度報告，但必須在報告中明示。核心組 S、N、A、B 全部完成後才開放 cephalometric basic report。骨性垂直組 ANS、PNS、Go、Me 與牙齒組 U1 tip、U1 apex、L1 tip、L1 apex 可整組跳過；部分完成的組別不產生依賴該組完整資料的結論。替代方案是一次顯示所有點，但會重現 V1 的高認知負擔，因此不採用。

門牙組入口內嵌「一顆牙、兩個點、一條長軸」示意，不要求放射科醫師先理解牙科符號。U1 明示為上顎恆中切牙 FDI 11 或 21，L1 明示為下顎恆中切牙 FDI 31 或 41；不使用容易和美式 Universal numbering 混淆的 `#11/#21` 寫法。由於側位投影使左右牙影重疊，使用者應選擇較唇側且能由切端連續追蹤至根尖的清楚牙影，兩點必須來自同一顆牙；不能可靠配對時標記不確定或跳過，不混用兩側端點。

### Canvas 座標與校正

landmark 儲存為相對於原始影像的 normalized coordinates，格式為 x、y 均介於 0 與 1，另含 uncertain boolean。Canvas 的 zoom、pan、反相只改變顯示 transform；pointer position 必須反轉換為原始影像座標後才寫入 state。比例尺由兩個原始影像點與醫師輸入的已知 mm 間距計算，`mmPerPixel` 等於 `distanceMm` 除以兩點的 source-pixel Euclidean distance。兩點重合、距離少於 20 source pixels、非正數或非有限輸入均視為失敗並顯示可修正訊息。校正成功後可建立具 label 的兩點手動距離；距離只顯示 raw mm，不自動判讀正常或異常。替代方案是直接假設可見尺為 45 mm，但裁切與可見端點不固定，因此不採用。

### 純函式量測核心

內嵌 script `ceph-analysis-core` 暴露 `CephCore` 純函式，至少包含 `angleAt`、`angleBetweenLines`、`calibrateScale`、`computeMeasurements` 與 `buildReport`。SNA 為 angle S-N-A，SNB 為 angle S-N-B，ANB 為 SNA 減 SNB。ANB 使用 Steiner adult reference 2° ± 2°，以低於 0°、0° 至 4°、高於 4°分別產生傾向 Class III、I、II 的保守用語；SNA 與 SNB 同時顯示實測值與命名參考值。SN-MP 與 PP-MP 使用兩條無方向直線的較小夾角（0°–90°）；U1-PP、L1-MP 與 interincisal 採 cephalometric obtuse convention，定義為 180° 減去兩條無方向直線的較小夾角（結果 90°–180°），因此不受任一線段端點順序影響。進階平面角度及牙齒角度只有各自相依點完整時才回傳。未經驗證的 reference range 不得新增自動正常／異常分類，只顯示原始量測。

### 安全巡檢與無預設正常

survey state 固定包含 `imageQuality`、`sellaSkullBase`、`sinusesNasopharynx`、`tmj`、`jawsDentition`、`cervicalAirway` 六項；每項狀態為 `unassessed`、`normal`、`abnormal` 或 `limited`，另有 note。所有項目初始為 unassessed。可提供明確的批次按鈕，但只有醫師主動點擊並確認後才把 eligible unassessed items 設為 normal，且不得覆蓋 abnormal 或 limited。只要解剖區仍有 unassessed 或 limited，報告就不得產生涵蓋全影像的「無明顯額外異常」陳述。

### 報告快照與保守用語

`buildReport` 依當下 state 與 measurement snapshot 產生英文 Examination/Technique、Findings、Cephalometric Analysis、Impression、Limitations；所有系統產生的報告敘述均使用英文，但醫師輸入的 note 原文保留且不自動翻譯。報告只包含已完成的量測；未完成組別標為 not performed，不得套用正常結論。uncertain landmark 使相關量測及結論附上 approximate／review-required 提示。airway 只能描述可見軟組織與二維篩檢限制，不得輸出 OSA 診斷。產生後的文字是可編輯 snapshot；上游 state 改變時標示報告已過期，由醫師明確選擇重新產生，系統不得靜默覆蓋人工修改。

### 可測試的 DOM 契約

頁面為各關鍵控制提供穩定 id 與可存取名稱；純函式 script 與 app script 分離。Python HTML parser 檢查必要元素、外部資源、禁止的永久儲存與核心 script。Node VM 執行 CephCore 固定座標案例。Headless Chrome 或 Edge 使用 production HTML 注入 fixture，驗證影像載入、source/display 座標轉換、progressive unlock、跳過、undo/redo、鍵盤微調、stale report 與 1440×900、1024×768 版面。替代方案只做字串檢查，但不足以證明 Canvas 與實際 DOM 互動，因此不採用。

## Implementation Contract

**Behavior**

1. 使用者可用 clipboard paste、drag/drop 或 file picker 載入一張 PNG/JPG；無影像時 landmark 與報告動作保持停用。
2. 成功載入後，頁面顯示以影像為主、右側單一步驟說明與頂部進度。每次只要求一個 landmark，並支援確認、上一步、跳過選做組、undo/redo、zoom、pan、invert 與 arrow-key nudge。
3. 核心四點完成後，頁面顯示 SNA、SNB、ANB 與可產生基本報告狀態。進階結論只在各自相依點齊全時出現。
4. 報告忠實反映 survey、calibration、landmark completeness 與 uncertainty；任何 missing data 均不得被預設正常值取代。
5. 使用者可編輯與複製報告；上游資料改變時既有報告保留並顯示 stale warning。

**Interface / data shape**

- point: `{ x: number, y: number, uncertain: boolean }`，x/y 為 normalized source-image coordinates。
- survey item: `{ status: "unassessed" | "normal" | "abnormal" | "limited", note: string }`。
- calibration: `{ pointA, pointB, distanceMm, mmPerPixel }`；失敗或跳過時 mmPerPixel 為 null。
- manual distance: `{ label, pointA, pointB, valueMm }`；只在有效 calibration 下存在。
- measurement: `{ key, value, unit, dependencies, uncertain }`；不滿足 dependencies 時該 measurement 不存在。
- `CephCore` 為可在 Node VM 與瀏覽器執行、不依賴 DOM 的命名空間。
- 報告輸出為 UTF-8 plain text，可在頁面 textarea 編輯。

**Failure modes**

- 非 PNG/JPG、無法解碼、超過 50 MiB 或任一邊超過 16384 pixels 的影像會被拒絕，既有 state 不被清除，並顯示具體錯誤。
- calibration distance 必須是有限正數，兩點 source-pixel 距離至少 20 pixels；不符合時不建立 mmPerPixel。
- 核心點不足時，產生 basic cephalometric report 動作保持停用並列出缺少點。
- clipboard API 或 copy API 不可用時，paste event、file picker 與可手動選取的 report textarea 仍可運作。
- 瀏覽器重新整理或關閉時，若 state 已變更則觸發標準 beforeunload 提醒；工具不宣稱可復原資料。

**Acceptance criteria**

- `python -m unittest tests.test_ceph_analysis tests.test_index_navigation -v` 全部通過。
- 固定 source coordinates 證明 SNA、SNB、ANB、plane angles 與 mmPerPixel 在容許誤差內。
- 測試證明 missing、skipped、uncertain、unassessed、limited 與 uncalibrated 狀態產生指定的保守輸出。
- Headless browser fixture 證明 zoom/pan 後落點仍對應相同 source coordinate，且報告人工文字不被上游變更覆蓋。
- HTML parser 證明沒有外部 src/href、fetch、XMLHttpRequest、WebSocket、localStorage 或 IndexedDB。
- `git diff --check` 通過，且首頁原有 `tool/ceph-analysis.html` 連結仍有效。

**Scope boundaries**

本變更只修改 cephalometric 單頁工具並新增其專屬測試與規格。首頁路徑不變，其他 tool、radtracker、AHK、影像 viewer、NAS 與發布流程不在範圍內。

## Risks / Trade-offs

- [Risk] 手動 landmark 仍有 observer variability → 每點顯示定義與辨識提示，提供放大微調、uncertain 標記及報告限制。
- [Risk] 2D cephalogram 的 positioning 與 magnification 影響量測 → 使用 source coordinates、明示二維限制，線性數值須經可見尺校正。
- [Risk] 固定成人 reference 不適用所有年齡與族群 → 只對命名的 Steiner core reference 產生保守傾向，保留 raw values 與限制文字。
- [Risk] 單檔 HTML 體積較大 → 以明確 core/app 分層與測試契約維持可維護性，不引入 build dependency。
- [Risk] 使用者誤把未完成巡檢視為正常 → 預設 unassessed，報告 suppress 全影像正常陳述並列出未評估區域。
- [Risk] 瀏覽器記憶體資料在關閉後消失 → 顯示明確隱私與暫存提示，提供 copy workflow 與 beforeunload warning。

## Migration Plan

1. 在隔離 branch 以 V2 內容取代 `tool/ceph-analysis.html`，新增 `tests/test_ceph_analysis.py`。
2. 執行純函式、HTML、headless browser、首頁導航與 diff 檢查。
3. 以同一路徑人工驗收貼圖、標點、報告與 copy 流程。
4. 整合後既有首頁連結自動導向 V2，無資料 migration。
5. 若驗收失敗，以 Git 回復 `tool/ceph-analysis.html` 與專屬測試；不影響其他工具或資料。

## Open Questions

四段設計審查已確認臨床定位、校正方式、漸進式 landmark、報告結構與同一路徑取代 V1；本次變更沒有待決的必要產品問題。
