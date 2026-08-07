## 1. 離線頁面與測試骨架

- [x] 1.1 建立「單一離線 HTML 與純 Canvas 2D」頁面骨架與固定 id 的 pure-core script block，使 `tool/image-stack-mpr.html` 可由 `file://` 開啟且不載入任何外部資源；以 `test_offline_single_file_image_stack_import` 與 HTML external-URL scan 驗證 **Offline single-file image stack import**。
- [x] 1.2 建立 `tests/test_image_stack_mpr.py` 的 HTML parser 與 Node VM runner，使後續 pure functions 可在無 DOM 狀態執行；以 `test_core_script_is_extractable_and_executable` 驗證測試契約。

## 2. 匯入、分組與 volume

- [x] 2.1 實作 `naturalCompare()`、2/3 sequence selector、可拖曳 boundaries 與穩定 assignment，讓檔名自然排序並可快速切成 2 或 3 組；以 `test_natural_ordering_and_sequence_count` 驗證 **Natural ordering and sequence count**。
- [ ] 2.2 實作 thumbnail lanes、逐張 inclusion control 與跨 lane reassignment，使使用者可保留排序地改組或排除影像；以 `test_boundary_and_per_image_assignment` 與 Chrome drag/drop assertion 驗證 **Boundary and per-image assignment**。
- [x] 2.3 實作「以 Uint8Array 建立正規化 sequence volume」的 canonical coordinate mapping、forward/reverse order、0/90/180/270 rotation、horizontal/vertical flip 與 1×1×5 defaults，使所有視圖使用一致方向；以 `test_sequence_geometry_configuration` 的非方形 synthetic slice cases 驗證 **Sequence geometry configuration**。
- [x] 2.4 實作循序 PNG/JPEG decode、luminance conversion、canonical dimension check、failed-file state 與 minimum-depth gate，使錯誤檔名可見且 organizer state 不遺失；以 `test_decode_and_dimension_validation` 驗證 **Decode and dimension validation**。
- [x] 2.5 實作 volume byte estimate、512 MiB confirmation gate、decode resource release 與 allocation failure recovery，使大型資料集不會未提示地配置記憶體；以 `test_memory_aware_volume_construction` 的 threshold boundary cases 驗證 **Memory-aware volume construction**。

## 3. Crosslink 核心與 timeline

- [x] 3.1 實作「Sequence 1 基準的可逆 crosslink」資料形狀與 `mapReferenceToTarget()`、`mapTargetToReference()`，使 Sequence 2／3 各自維持 reference-based maps；以 `test_reference_based_crosslink_model` 驗證 **Reference-based crosslink model**。
- [x] 3.2 實作 `validateAnchor()` 的 unique-index 與 strict monotonic checks，使 duplicate 或 crossing candidate 不改變既有資料；以 `test_strictly_monotonic_anchor_validation` 驗證 **Strictly monotonic anchor validation**。
- [x] 3.3 實作 zero-anchor independence、one-anchor offset、multi-anchor interpolation、outer extrapolation 與 endpoint clamp，使所有 mapping boundary 明確；以 `test_piecewise_mapping_behavior` 與 concrete 7→39、27→63 examples 驗證 **Piecewise mapping behavior** 及 **Independent mode without anchors**。
- [x] 3.4 實作 secondary→reference→other-secondary 更新路徑並保留 fractional MPR position，使任一 sequence 都能成為同步來源；以 `test_reversible_synchronization` 驗證 **Reversible synchronization**。
- [ ] 3.5 實作 anchor add/select/edit/delete controls、timeline diamonds 與 connectors，使目前切片可建立可見且可管理的 anatomical correspondence；以 `test_anchor_creation_and_editing`, `test_timeline_crosslink_visualization` 與 Chrome pointer assertion 驗證 **Anchor creation and editing** 及 **Timeline crosslink visualization**。

## 4. MPR 重採樣引擎

- [x] 4.1 實作 `sampleTrilinear()` 的界內八點內插與界外 0 intensity，使所有重組共用單一取樣契約；以 2×2×2 center=35 case 的 `test_trilinear_intensity_sampling` 驗證 **Trilinear intensity sampling**。
- [x] 4.2 實作 AX/COR/SAG plane basis、spacing-aware aspect 與 orientation labels，使正交切面遵循 canonical x/y/z；以 synthetic x/y/z gradient 的 `test_standard_orthogonal_reslices` 驗證 **Standard orthogonal reslices**。
- [x] 4.3 實作 center+azimuth+tilt+roll plane basis、direct manipulation、numeric controls 與 reset，使任意切面保持 orthonormal basis；以 `test_arbitrary_oblique_reslice` 驗證 **Arbitrary oblique reslice**。
- [x] 4.4 實作 fractional crosslink center 傳遞，使 secondary MPR 不將 50.4 先 round 成 axial frame；以 `test_crosslinked_mpr_location` 驗證 **Crosslinked MPR location**。
- [x] 4.5 實作「低解析互動與完整解析重建」的 256-pixel preview、120 ms debounce、1024-pixel full render、generation cancellation 與 worker fallback，使連續旋轉保持回應且舊結果不覆寫新結果；以 fake timer/generation 的 `test_progressive_reslice_quality` 驗證 **Progressive reslice quality**。

## 5. 工作區與影像互動

- [ ] 5.1 實作 Crosslink 模式的 2–3 個 axial viewports、thumbnail timelines、wheel slice、Ctrl/Meta+wheel zoom、pan、crosshair、right-drag Intensity、Fit、Reset、Invert 與 sync toggles；以 `test_basic_image_interaction_bindings` 及 Chrome gestures 驗證 **Basic image interaction**。
- [ ] 5.2 實作「寬螢幕 Crosslink 與 MPR 工作區」：Sequence 1 大型 2×2 grid、Sequence 2／3 comparison regions、Crosslink/MPR shared state，以及 1400/900 CSS pixel responsive rules；以 1600px 與 800px screenshots/checks 驗證 **Responsive comparison workspace**。
- [x] 5.3 實作 default pixel spacing 使用時的 persistent positioning-only notice，且介面只使用 Intensity、不得使用 HU 或 DICOM Window Level；以 `test_unknown_geometry_warning_and_copy` 驗證 **Unknown geometry warning**。

## 6. 整體驗證

- [x] 6.1 執行 `python -m unittest discover -s tests -p test_image_stack_mpr.py -v`、既有 `test_us_probe_ct_plane.py`、HTML external-URL scan 與 `git diff --check`，確認新 viewer 核心測試通過、完全離線且既有 probe tool 行為未回歸。
- [ ] 6.2 以 Chrome `file://` 手動載入 2 組與 3 組 synthetic PNG stacks，逐項驗證匯入分組、方向校正、雙向 crosslink、AX/COR/SAG/Oblique、基本互動、寬窄 reflow 與重新整理後資料不持久化，並把結果記錄在 Spectra apply verification evidence。
