# Crosslink 鍵盤縮放、直式版面與批次錨點設計

## 目的

改善 Crosslink 在一般與直式螢幕上的閱片效率：游標位於影像時可用鍵盤 `+`／`-` 縮放；直式螢幕將多個 Sequence 影像改為上中下排列；三組 Sequence 對位完成後可按一次按鈕，同時建立 S1↔S2 與 S1↔S3 錨點。

## 鍵盤縮放

- 游標進入 viewport canvas 時記錄該 viewport，離開後清除。
- 游標位於影像時，主鍵盤 `+`、`-` 與數字鍵盤加減鍵控制該影像縮放。
- `+` 將 zoom 乘以 `1.1`；`-` 將 zoom 除以 `1.1`；結果限制在既有 `0.25×` 至 `12×` 範圍。
- 勾選「同步縮放／平移」時，使用既有 navigation sync 將 zoom 複製到其他 viewport；取消時只改變游標所在 viewport。
- `Shift+拖曳` 保留為平移，`Ctrl/Meta+滾輪` 保留為縮放，不改變既有右鍵拖曳 Intensity 與一般滾輪切片。
- 沒有 viewport 處於 hover 狀態時，`+`／`-` 不攔截瀏覽器或表單按鍵。
- 工具列說明補上「游標置於影像後按 +/-：縮放」，並明確保留「Shift+拖曳：平移」。

## 直式螢幕版面

- 只調整 Crosslink 的 `#axial-viewports`；MPR 網格維持既有響應式設計。
- 在 CSS `orientation: portrait` 條件下，active Sequence viewport 固定為單欄，因此三組 Sequence 依 S1、S2、S3 上中下排列。
- 每個 Crosslink 影像框在直式模式使用隨視窗寬度增加的高度，兼顧影像尺寸與頁面捲動；橫式螢幕維持目前並排顯示。
- 檔名列仍固定在各影像框正下方，且不影響單欄寬度。

## 一次新增全部 Sequence 錨點

- 新增按鈕改名為「新增全部序列錨點」。
- 兩組 Sequence 時，一次建立目前 `S1↔S2` 錨點。
- 三組 Sequence 時，一次建立目前 `S1↔S2` 與 `S1↔S3` 兩組錨點。
- 批次新增採原子操作：先對所有 active target 使用既有嚴格單調規則驗證；任一 target 發生重複 reference、重複 target 或交叉錨點時，所有 map 都保持原狀，並顯示失敗 Sequence 與原因。
- 全部驗證成功後才一次更新各 target map，並重新繪製 timeline 與 connector。
- 成功訊息列出本次建立的所有配對，例如 `已新增：S1 25 ↔ S2 28；S1 25 ↔ S3 27`。
- 目標選單標示改為「編輯目標」；「更新所選錨點」與「刪除所選錨點」維持個別操作，不改變既有 marker 選取方式。

## 測試與驗收

- 真實 headless Chromium 中，hover S2 後按 `+` 會增加 S2 zoom；同步開啟時 S1/S3 同步，關閉時只有 S2 改變。
- 沒有 hover viewport 時，鍵盤加減鍵不改變 zoom。
- 直式 viewport 中三個 Crosslink 影像形成三個不同的垂直 row，且每個影像使用完整欄寬；橫式仍可並排。
- 三組 Sequence 批次新增成功時，同時產生 S2 與 S3 map；其中一組無效時兩個 map 都不變。
- 兩組 Sequence 仍只建立 S2 map；個別更新與刪除維持既有行為。
- 既有影像匯入、檔名列、volume、crosslink、MPR、離線與 probe 測試全部維持通過。
