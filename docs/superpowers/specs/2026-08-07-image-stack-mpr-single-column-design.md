# Image Stack MPR 單欄全寬版面設計

## 目的

取消載入／Sequence 編排與閱片工作區的左右分欄。頁面改成由上而下捲動，讓約 100 張 PNG/JPG 的 Sequence 時間軸使用完整視窗寬度，並避免分界拉桿越過容器後被遮住。

## 版面

頁面依序排列：標題列、載入與分組、Sequence 編排、Crosslink／MPR 模式與閱片內容。`.body` 永遠使用單欄；`.sidebar` 與 `.main` 都參與頁面垂直流，不建立各自的內部垂直捲軸。

每個 Sequence lane 佔滿可用寬度。縮圖維持單列時間軸，超過寬度時只在該列橫向捲動，不將約 100 張影像換行成多列。分界列保留「標籤／拉桿／數值」三欄，拉桿欄使用可收縮的 `minmax(0, 1fr)`，拉桿本身不得超過其 grid track。

## 不變範圍

不修改影像匯入、Sequence 指派、volume 建立、crosslink anchor、重組、Canvas 互動或離線處理邏輯；`tool/us-probe-ct-plane.html` 亦不變。

## 驗收

- 在桌面寬度中，載入／編排區位於 Crosslink／MPR 上方，而非左側。
- setup 與 viewer 使用相同的全寬內容區。
- 100 張縮圖保持單列，時間軸可橫向捲動。
- 分界拉桿位於 Sequence 編排卡片內並填滿中間可用欄寬。
- 既有 viewer 與 probe 自動測試全部通過，HTML 仍無外部資源。
