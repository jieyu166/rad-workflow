## Why

放射影像從系統匯出為 PNG/JPG 後會失去 DICOM 的序列、空間與 crosslink metadata，目前缺乏一個可完全離線整理 2–3 組影像、手動建立跨序列對應並進行基本 MPR 的本機工具。此功能可讓使用者在不重新取得 DICOM、也不將影像上傳網路的情況下，完成基本瀏覽、同步定位與重組。

## What Changes

- 新增完全離線、單一 HTML 的 PNG/JPG image-stack viewer，不修改既有超音波探頭模擬器。
- 支援一次匯入影像後，以自然排序、分界點、縮圖 timeline、逐張勾選與拖曳建立 2 或 3 個 sequence。
- 支援每個 sequence 的 slice spacing、正反序、0/90/180/270 度旋轉、左右與上下翻轉。
- 以 Sequence 1 為基準，讓 Sequence 2／3 分別建立多個 crosslink 錨點，並以可逆的分段線性映射同步瀏覽。
- 提供 axial 瀏覽、Intensity 調整、縮放、平移、反相、Fit/Reset，以及 COR、SAG 與三角度 Oblique MPR。
- 採寬螢幕優先的基準序列 2×2 MPR 配置，並為次要 sequence 顯示同步比較視窗。
- 以純 JavaScript、Canvas 2D 與 TypedArray 實作；不使用 CDN、遠端 API 或影像上傳。

## Capabilities

### New Capabilities

- `image-stack-import`: 本機 PNG/JPG 的離線匯入、自然排序、2–3 組 sequence 編排、幾何設定、驗證與記憶體防護。
- `sequence-crosslink`: 以 Sequence 1 為基準的多錨點 crosslink 建立、顯示、編輯、單調性驗證、內插、外推與反向換算。
- `image-stack-mpr`: 8-bit 灰階 volume 的 axial/COR/SAG/Oblique 重採樣、基本影像操作、寬螢幕 MPR 佈局與跨 sequence 同步。

### Modified Capabilities

(none)

## Impact

- Affected specs: `image-stack-import`, `sequence-crosslink`, `image-stack-mpr`
- Affected code:
  - New: `tool/image-stack-mpr.html`
  - New: `tests/test_image_stack_mpr.py`
  - Modified: (none)
  - Removed: (none)
- Dependencies: no runtime dependency and no network service; tests require the repository's existing Python and Node.js runtimes.
- Existing behavior: `tool/us-probe-ct-plane.html` remains unchanged and serves only as a reviewed reference for volume sampling concepts.
