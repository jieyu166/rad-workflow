# Crosslink 目前切片檔名顯示設計

## 目的

在 Crosslink 的每個 Sequence axial viewport 正下方顯示目前切片的原始 PNG/JPG 檔名，讓使用者在同步捲動與建立錨點時能直接核對來源檔案。

## 顯示規則

- 每個 Crosslink axial viewport 各有一列檔名，固定屬於該 Sequence。
- 顯示格式為 `檔案：<原始檔名>`，例如 `檔案：0045.jpg`。
- 顯示的檔名必須對應目前畫面採用的整數 axial slice；fractional crosslink 位置以畫面既有的四捨五入切片為準。
- 滾輪切片、crosslink 同步、切片順序正向／反向以及重新建立 volumes 後，檔名都必須隨畫面更新。
- 排除或解碼失敗的影像不會納入 volume，因此不得出現在目前切片檔名對照中。
- 長檔名使用單行省略；元素的 `title` 保留完整檔名。

## 資料對應

建立 volume 時，同步建立以 canonical z index 為索引的 `sliceNames`。每個 canonical index 先透過現有 `canonicalToSource()` 取得來源切片，再保存該來源項目的 `name`。這使正向／反向排序與既有 volume voxel 順序使用完全相同的映射。

渲染 Crosslink axial viewport 時，將目前位置四捨五入並限制在合法深度後，以該 index 讀取 `volume.sliceNames`。檔名列與 HUD 在同一次 render 更新，避免兩者顯示不同切片。

## 版面範圍

檔名列位於影像框外、正下方，不覆蓋影像。MPR 的 AX/COR/SAG/Oblique viewport 不顯示檔名，因為重組與內插切面不一定對應唯一來源檔案。

## 驗收

- 三個 Sequence 的 Crosslink viewport 分別顯示自己的目前檔名。
- 切換 slice 或 crosslink 同步後，檔名與 HUD slice number 同步更新。
- 反向排序後，第一個 canonical slice 顯示原來源序列最後一張的檔名。
- 檔名列不遮住 canvas，長檔名不撐破 viewport 欄寬。
- 既有 organizer、volume、crosslink、MPR、離線與 probe 測試維持通過。
