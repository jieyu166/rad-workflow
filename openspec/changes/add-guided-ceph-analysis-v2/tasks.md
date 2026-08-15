## 1. 測試契約與單檔骨架

- [x] 1.1 依「可測試的 DOM 契約」先在 `tests/test_ceph_analysis.py` 建立 production HTML parser、Node VM `CephCore` harness 與 headless browser fixture，讓缺少必要 id、核心 script 或出現外部資源時測試先失敗；以 `python -m unittest tests.test_ceph_analysis -v` 驗證測試可執行且 failure message 可定位。
- [x] 1.2 依「單檔離線與記憶體狀態」建立 V2 page shell 與穩定 DOM ids，使 Offline image intake and privacy 的 no-external-assets、no-persistence 契約通過 parser 測試，並以 `test_offline_document_contract` 驗證沒有外部 src/href、fetch、XMLHttpRequest、WebSocket、localStorage 或 IndexedDB。

## 2. 影像工作區與互動狀態

- [x] 2.1 實作 Offline image intake and privacy 與 Safe in-memory lifecycle：paste、drop、file picker 能載入單張合規 PNG/JPG，錯誤輸入保留既有 study，換圖與離頁有明確確認；以 `test_image_intake_contract`、`test_invalid_image_preserves_state` 與 headless fixture 驗證。
- [x] 2.2 依「Canvas 座標與校正」實作 source/display transform，使 Landmark placement and editing 在 zoom/pan 後仍寫入相同 normalized source coordinates，並支援 place、move、delete、uncertain、undo/redo、arrow nudge；以 `test_coordinate_round_trip`、`test_landmark_history` 與 headless click fixture 驗證。
- [x] 2.3 實作 Diagnostic image controls 的 zoom、pan、invert、fit、reset，確保只改變顯示、不改變 landmark 或 measurement；以 `test_view_controls_preserve_geometry` 驗證。
- [x] 2.4 實作 Accessible responsive workspace，使 progress、current-step、canvas 與主要動作具鍵盤操作和可存取名稱，且 1440×900、1024×768 無水平頁面溢位；以 `test_accessibility_contract` 與 headless layout measurements 驗證。

## 3. 漸進式精靈、巡檢與校正

- [x] 3.1 依「漸進式精靈與相依性」實作 Progressive wizard stages：image → survey → calibration → S/N/A/B → optional skeletal/dental groups → report，核心缺點時列出依賴且 optional group 可整組跳過；以 `test_progressive_unlock_and_skip` 驗證。
- [x] 3.2 依「安全巡檢與無預設正常」實作 Six-area survey without default normal findings，六項初始 unassessed、批次 normal 必須明確確認且不得覆蓋 abnormal/limited；以 `test_survey_defaults_and_batch_action` 驗證。
- [x] 3.3 實作 Visible-ruler scale calibration 與 Calibrated manual distance measurements：兩刻度點與有限正 mm 建立 mmPerPixel，無效或跳過校正時禁止 mm，合規時允許具 label 的 raw distance；以 `test_scale_calibration_boundaries` 與 `test_manual_distance_requires_scale` 驗證。

## 4. 純函式量測核心

- [x] 4.1 依「純函式量測核心」實作 Deterministic core cephalometric measurements 與 Conservative sagittal classification，使 SNA、SNB、signed ANB 和 -0.1/0/4/4.1° boundaries 產生規格指定值與保守文字；以 Node VM `test_core_angle_fixture` 與 `test_anb_boundaries` 驗證。
- [x] 4.2 實作 Dependency-gated advanced angular measurements 與 Uncertainty propagation，使 SN-MP、PP-MP、U1-PP、L1-MP、interincisal 只在依賴完整時出現，且 uncertainty 只傳播至相關量測；以 `test_advanced_dependencies`、`test_dental_obtuse_convention` 與 `test_uncertainty_propagation` 驗證。

## 5. 報告產生與醫師編輯

- [x] 5.1 依「報告快照與保守用語」實作 Structured radiology report 與 Fixed clinical limitations，使報告包含五個固定 section、只引用顯式 survey/measurement/reference，未評估時 suppress 全影像陰性陳述，且永不由 lateral cephalogram 診斷 OSA；以 `test_report_sections`、`test_report_omits_unassessed_normality`、`test_no_osa_diagnosis` 與 golden-text review 驗證。
- [x] 5.2 實作 Editable report snapshot 與 Report copy fallback，使人工文字不被上游更新覆蓋、stale report 需確認才 regenerate，clipboard 失敗仍保留可選取文字；以 headless `test_report_snapshot_staleness` 與 `test_copy_fallback` 驗證。

## 6. 整體驗證與範圍稽核

- [x] 6.1 執行 `python -m unittest tests.test_ceph_analysis tests.test_index_navigation -v`、`git diff --check` 與 `spectra validate add-guided-ceph-analysis-v2`，確認所有自動化契約通過且 `index.html` 原有 `tool/ceph-analysis.html` 連結仍有效。
- [x] 6.2 以真實 lateral cephalometric PNG/JPG 在本機 HTTP fixture 完成 paste/file、六區巡檢、40 mm 校正、S/N/A/B、選做點、人工 report edit 與 copy 的端對端人工檢查，記錄 1440×900 與 1024×768 結果，並確認 `tool/ceph-analysis.html` 與 `tests/test_ceph_analysis.py` 之外沒有功能碼變更。

## 7. 英文報告輸出

- [x] 7.1 將 `buildReport` 的 system-generated technique、findings、analysis、impression 與 limitations 全部改為英文，同時逐字保留 physician-entered note 且不自動翻譯；以 `test_system_generated_report_is_english`、既有 missing/uncertainty/OSA/linear-measurement tests 與完整回歸驗證。

## 8. 門牙長軸教學

- [x] 8.1 在選做門牙組加入「一顆牙、兩個點、一條長軸」圖文教學，明確將 U1 對應 FDI 11/21、L1 對應 FDI 31/41，說明側位片左右重疊時應選可由切端連續追蹤至根尖的同一顆較唇側且輪廓清楚之中切牙，不得混用兩側牙影；無法可靠配對時標記不確定或跳過。先以 `test_incisor_axis_guidance_uses_fdi_and_same_tooth_pairing` 建立失敗契約，再執行完整 ceph 與 index navigation 回歸。
