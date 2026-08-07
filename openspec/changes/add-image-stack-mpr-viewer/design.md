## Context

既有 `tool/us-probe-ct-plane.html` 已證明單頁 JavaScript 可把 PNG/JPG stack 轉成 volume，並以 CPU 三線性內插產生任意探頭切面；但該頁將單一 `VOL`、探頭狀態、Three.js 場景與 sonogram renderer 高度耦合，不適合直接增加 2–3 組 sequence、crosslink timeline 與傳統 MPR。新工具必須獨立存在，完全離線，從 `file://` 雙擊即可啟動，且不得把可能含醫療資訊的影像送出本機。

PNG/JPG 不含可靠的 DICOM Image Position、Image Orientation、Pixel Spacing 或 HU。工具因此只能建立使用者定義幾何的 8-bit pseudo-volume，並在比例未知時清楚標示限制。主要使用情境為數十至數百張 axial 匯出影像，以寬螢幕比較 2 或 3 組 sequence。

## Goals / Non-Goals

**Goals:**

- 提供完全離線、單一 HTML 的 2–3 組 PNG/JPG stack 匯入、整理與瀏覽。
- 以縮圖 timeline、分界線、逐張勾選與跨 lane 拖曳完成 sequence 編排。
- 以 Sequence 1 為基準建立可逆、多錨點、單調的 crosslink。
- 提供 AX/COR/SAG/Oblique MPR 與基本 Intensity、zoom、pan、invert、fit/reset 操作。
- 讓核心排序、座標轉換、crosslink 與 reslice 數學可由 Node VM 與合成 volume 測試。

**Non-Goals:**

- 不解析 DICOM、不宣稱具有 HU、不提供距離測量或診斷級幾何精度。
- 不做自動 registration、影像融合、segmentation、annotation、登入、雲端同步或資料上傳。
- 不修改 `tool/us-probe-ct-plane.html`，也不引入 Cornerstone、VTK、WebGL 3D texture 或外部 runtime dependency。
- 第一版不保存影像或工作階段；重新整理頁面後需重新匯入。

## Decisions

### 單一離線 HTML 與純 Canvas 2D

新增 `tool/image-stack-mpr.html`，所有 CSS、JavaScript、Worker source 與 UI 都內嵌於單一檔案。頁面不含 CDN、外部字型、遠端 API 或分析程式，並以 Content Security Policy 限制網路來源。Canvas 2D 負責 axial 與 MPR 輸出；若需要背景運算，Worker 由內嵌 source 建立 Blob URL。

選擇 CPU Canvas 2D 是因為輸入是 8-bit PNG/JPG pseudo-volume，資料量預期可由 typed arrays 管理，且 `file://` 相容性與可測試性優於 3D texture。WebGL 方案可提高持續旋轉幀率，但會引入 texture 尺寸、GPU memory 與瀏覽器差異，第一版不採用。

### 以 Uint8Array 建立正規化 sequence volume

每個 sequence 使用下列資料形狀：

```js
{
  id: 1 | 2 | 3,
  files: Array<{ id, name, file, included, thumbnailUrl, decodeError }>,
  data: Uint8Array,
  width: number,
  height: number,
  depth: number,
  pixelSpacingX: number,
  pixelSpacingY: number,
  sliceSpacing: number,
  order: "forward" | "reverse",
  rotation: 0 | 90 | 180 | 270,
  flipX: boolean,
  flipY: boolean
}
```

匯入檔以大小寫不敏感的自然數排序保持穩定順序。Sequence 數量只能為 2 或 3；使用者先拖曳分界點批次分組，再以 thumbnail lane 逐張改組或排除。每組影像依序解碼為 luminance `Uint8Array`，解碼完成即釋放完整 bitmap/object URL，只保留 volume 與小縮圖。方向設定透過 canonical-to-source 座標轉換套用，不重寫原始檔案。

`pixelSpacingX` 與 `pixelSpacingY` 未知時預設 1，`sliceSpacing` 預設 5 mm；比例未知時 MPR 必須顯示警示。建立前顯示估算的 grayscale volume bytes，總量達 512 MiB 時要求使用者再次確認。任何 sequence 少於 2 張、含解碼失敗或 canonical 尺寸不一致時不得建立該 volume，並保留編排狀態供修正。

### Sequence 1 基準的可逆 crosslink

每個次要 sequence 保存獨立 anchor list：

```js
{
  targetSequenceId: 2 | 3,
  anchors: Array<{ referenceIndex: number, targetIndex: number }>
}
```

Anchor 以 `referenceIndex` 排序，reference 與 target index 都必須嚴格遞增。0 個 anchor 時 sequence 獨立；1 個 anchor 使用固定 offset；2 個以上在鄰近 anchors 間做分段線性內插，範圍外沿最近 segment 外推後 clamp 到有效範圍。反向同步使用同一組 segment 交換自變數與應變數，不建立另一份可能漂移的 mapping。

Axial viewport 將 fractional position 四捨五入到最近原始 frame；MPR 保留 fractional coordinate 供三線性內插。Sequence 2／3 的操作先反向映射到 Sequence 1，再由 Sequence 1 映射到其他 sequence。Timeline anchor 可建立、選取、修改與刪除；非單調或重複 index 的 anchor 會被拒絕並顯示衝突。

### 低解析互動與完整解析重建

`sampleTrilinear(volume, x, y, z)` 是所有重組的單一取樣入口。AX/COR/SAG 使用固定正交 basis；Oblique 使用 center、azimuth、tilt、roll 產生兩個平面 basis vectors。輸出像素位置依 `pixelSpacingX`、`pixelSpacingY` 與 `sliceSpacing` 換算到 volume coordinates。

拖曳 crosshair、旋轉 Oblique 或連續 resize 時，每個 MPR viewport 以最大 256×256 的預覽解析度重建；輸入停止 120 ms 後，以實際 CSS pixel size 乘 device pixel ratio、最長邊上限 1024 pixels 重建。每次新操作以 generation token 取消舊結果，避免慢結果覆寫新狀態。

### 寬螢幕 Crosslink 與 MPR 工作區

Crosslink 模式上方並排 2–3 個大型 axial viewport，下方為對應 thumbnail timelines 與 anchor connectors。MPR 模式以 Sequence 1 的大型 2×2 AX/COR/SAG/Oblique grid 為主，右側為 Sequence 2／3 的同步比較視窗；窄螢幕改為上下排列。兩個模式共用同一 volumes、crosshair、crosslink maps 與 viewer state，不重新解碼影像。

滾輪換 slice，Ctrl/Meta+滾輪縮放，拖曳移動 crosshair 或 pan，右鍵拖曳調整 Intensity window，並提供 Fit、Reset、Invert。Zoom/pan 與 Intensity 可個別啟用跨 sequence 同步。UI 不使用 Window/Level 或 HU 字樣。

## Implementation Contract

**Behavior**

- 使用者雙擊 `tool/image-stack-mpr.html` 後，可在無網路環境載入本機 PNG/JPG，建立 2 或 3 個 sequence，並在 Crosslink 與 MPR 模式間切換而不重新匯入。
- Crosslink anchor 的新增、修改、刪除會立即更新同步位置；任何 viewport 都能成為滾動來源。
- MPR 依使用者提供的 spacing 與方向設定產生標準與任意切面；比例未知時持續顯示限制訊息。

**Interfaces and data**

- `naturalCompare(a, b)`：穩定、大小寫不敏感的自然排序 comparator。
- `assignByBoundaries(items, sequenceCount, boundaries)`：回傳每張影像的 sequence assignment，sequenceCount 僅接受 2 或 3。
- `mapReferenceToTarget(position, anchors, targetDepth)` 與 `mapTargetToReference(position, anchors, referenceDepth)`：實作 offset、piecewise interpolation、extrapolation 與 clamp。
- `validateAnchor(candidate, anchors)`：回傳 `{ valid, reason }`，拒絕 duplicate 或 non-monotonic mapping。
- `sampleTrilinear(volume, x, y, z)`：界內回傳 0–255 浮點 intensity；界外回傳 0。
- `reslicePlane(volume, plane, outputWidth, outputHeight)`：回傳 `Uint8ClampedArray` RGBA buffer；plane 包含 center、u、v 與 mm-per-pixel。
- 核心函式放在具固定 id 的純 JavaScript script block，測試可在不建立 DOM 或 Canvas 的 Node VM 中執行。

**Failure modes**

- 解碼失敗、尺寸不一致、sequence 張數不足、spacing 非正數、anchor 衝突與 allocation failure 都必須以檔名或 sequence id 顯示可行動的錯誤；不得靜默排除。
- Invalid spacing 恢復 pixel spacing 1、slice spacing 5 mm，並顯示比例未知警示。
- Worker 或低解析預覽不可用時退回主執行緒同步重建；工具仍須可瀏覽 axial frames。

**Acceptance criteria**

- Python HTML parser 驗證匯入、sequence、timeline、crosslink、MPR 與離線必要元素存在，且 HTML 不含外部 script/link/font/network URL。
- Node VM 驗證自然排序、2/3 組分界、方向座標、anchor mapping/inverse/validation 與 trilinear sampling。
- 合成 gradient volume 的 AX/COR/SAG/Oblique 測試產生預期像素與方向。
- Chrome 以 `file://` 實測 2 組與 3 組匯入、timeline 編排、雙向 crosslink、基本影像操作、寬螢幕 MPR 與窄螢幕 reflow。
- `tool/us-probe-ct-plane.html` 的內容與既有測試結果不變。

**Scope boundaries**

- 實作只新增獨立 viewer 與其測試，不修改其他工具或引入 runtime dependency。
- 輸出是定位與教學用途的 pseudo-volume viewer，不提供 DICOM conformance 或診斷級量測承諾。

## Risks / Trade-offs

- [大影像 stack 造成瀏覽器記憶體壓力] → 使用單通道 `Uint8Array`、循序解碼、釋放完整 bitmap、512 MiB 預警與 allocation failure recovery。
- [CPU Oblique MPR 在高 DPI 螢幕卡頓] → 互動期 256 pixels 預覽、120 ms debounce、1024 pixels 完整重建上限與 generation cancellation。
- [PNG/JPG 缺乏真實空間 metadata] → 預設 1×1×5 幾何、每組可手動修改、方向校正與持續比例未知警示。
- [錯誤 anchors 造成 sequence 折返] → canonical order 後要求雙軸嚴格單調，衝突時拒絕更新。
- [單一 HTML 變大且責任集中] → 以明確區段與純函式界面分隔 importer、volume、crosslink、reslicer、viewer 與 UI binding。

## Migration Plan

此功能為新增獨立檔案，沒有資料 migration。部署時新增 viewer 與測試；rollback 只需移除這兩個檔案，不影響既有工具。

## Open Questions

無；第一版範圍與互動規則已確認。
