## Context

乳篩報告 BI-RADS 0/3/4/5 須另填國健署附表四之五（疑似異常個案報告表）。使用者的實際流程：在報告電腦打完 mammo 報告後先暫存，再到另一台電腦開啟同一份報告；此時那台電腦的 chk060 顯示報告、INFINITT PACS 也開著同一位病人。PACS DICOM 只有英文姓名，中文姓名要沿用 LDCT 工具的作法，從 PACS 視窗控制項擷取（CT.ahk 的 GetPACSPatientChineseName）。

既有可重用元件：

- tool/ldct-report.html：單檔 HTML、無 CDN、Gemini generateContent（金鑰在頁面輸入、不儲存）、@media print 列印。
- ahk-scripts/test.ahk：GetDICOMData（點 PACS 開 DICOM 檔頭視窗、會覆寫剪貼簿）、GetDICOMLineData、GetAccessionNumber。
- ahk-scripts/CT.ahk：GetPACSPatientChineseName、ActivatePACSForLDCT。
- ahk-scripts/d8888basic.ahk：CopyReportHIS 讀 ThunderRT6TextBox14。
- radtracker/output/mammo_YYYYMM_reports.json：2026/02–07 約 138 份 BI-RADS 0 與少數 4/5 報告（gitignored，含病歷號）。

## Goals / Non-Goals

**Goals:**

- 一鍵從 chk060＋PACS 收集資料，網頁自動帶入表頭並由 LLM 勾選病灶欄位，人工確認後列印 A4。
- 病人資料不經網址、不落地瀏覽器儲存。
- 以既有報告做本機批次驗證，量化 LLM 解析品質。

**Non-Goals:**

- 不自動上傳或送出表單至國健署系統。
- 不擷取身分證統一編號（PACS/DICOM 無此資料），不填放射科醫師（需蓋章）。
- 不改動 mammo; 既有報告輸出邏輯，不做 BI-RADS 0 追蹤（radtracker 已有）。
- 不支援 LLM 供應商切換；只用 Gemini。

## Decisions

### Clipboard JSON hand-off instead of URL parameters

AHK 把資料組成帶 source 標記的 JSON 放剪貼簿，網頁以貼上或按鈕匯入。替代方案「網址參數（同 LDCT）」會把姓名、病歷號、報告全文留在 Edge 瀏覽紀錄，且報告全文可能過長；故否決。source 標記讓網頁能拒絕誤貼的其他內容。

### Reuse existing AHK DICOM and PACS helpers

擷取流程直接呼叫 GetDICOMData、GetDICOMLineData、GetAccessionNumber、GetPACSPatientChineseName、ActivatePACSForLDCT，不另寫 PACS 點擊邏輯。Mammo.ahk 與 test.ahk、CT.ahk 同被簡碼 jai.ahk include，可直接呼叫。流程開頭以 ClipboardAll 備份剪貼簿，中止時還原。

### Pure AHK functions for JSON building

新增 MammoFormEscapeJSON(str) 與 MammoFormBuildJSON(fields) 兩個不依賴視窗的純函式，讓 Python 測試能切出函式單獨以 AHK_V1_EXE 執行，比照 tests/test_mammo_silicone.py 的作法。不依賴 US.ahk 的 EscapeJSONString，避免測試時要 include 大檔。

### Chart number cross-check between HIS and PACS

chk060 ThunderRT6TextBox9 前 8 碼與 DICOM Patient ID 的 8 碼必須一致才繼續；兩台電腦切換的流程最容易發生「PACS 停在上一位病人」，這是防止整張表單填錯人的主要防線。

### Deterministic category, LLM only for lesions

疑似異常結果的 Category 以正規式從報告的 "BI-RADS category N" 或 "Category 4C" 寫法取得（2026/02–07 共 1,470 份報告與既有分類 100% 一致，4A/4B/4C 字母同時決定 4 的子分類），不交給 LLM；LLM 只負責病灶欄位。分類是表單最關鍵欄位，用確定性規則可避免模型幻覺。

### One page per lesion with editable pages

表單規定「單側多處或兩側病灶以不同表單分開」，故 LLM 回傳 lesions 陣列，每個元素一頁；使用者可刪頁、加空白頁、手動改任何勾選。所有 enum 值不在白名單者丟棄而非猜測。

### Single prompt source shared by page and validator

系統提示詞放在 HTML 內以 MAMMO-PROMPT-START / MAMMO-PROMPT-END 註解包住的 template literal；本機批次驗證腳本以這兩個標記擷取同一份提示詞，避免兩份 prompt 漂移。模型 id 與 ldct-report.html 使用同一字串常數值。

### Hardcoded hospital, blank physician and ID

醫院名稱寫死「佳里奇美醫院」；放射科醫師與身分證欄位留空（使用者決定：醫師需蓋章）。

### Local batch validation against archived reports

radtracker/validate_mammo_form_llm.py 讀 radtracker/output/mammo_*_reports.json 中 category 0/3/4/5 的報告，從 .env 或環境變數 GEMINI_API_KEY 取金鑰，逐份呼叫 Gemini，輸出：JSON 合法率、schema 合法率、每份 lesion 數、與報告文字中左右側關鍵字的一致率；明細 CSV 寫到 radtracker/output/（gitignored）。主控台輸出只用 cp950 相容字元並顯示進度。測試 fixture 另以去識別的報告全文存於 tests/fixtures/mammo_form/（遮蔽 6 位以上數字與日期、人名）。

## Implementation Contract

**Behavior**

- mammo; GUI 出現「疑陽表單」按鈕。按下後：讀 chk060 報告與病歷號 → 啟用 PACS 視窗 → 讀 DICOM 一次 → 讀中文姓名 → 檢查病歷號一致 → JSON 放剪貼簿 → Edge 開 tool/mammo-suspicious-form.html（無 query）。
- 網頁：Ctrl+V 或「從剪貼簿匯入」帶入表頭與報告；Category 立即由正規式勾選；按「AI 解析」後依病灶產生多頁；按「列印」輸出 A4 表單頁。

**Interface / data shape**

- 剪貼簿 JSON：source "rad-workflow/mammo-form"、version "1"、chartNo、nameZh、nameEn、birthDate、studyDate（YYYYMMDD）、accession、reportText，全為字串。
- LLM 回傳 schema 與 enum 白名單依 mammo-suspicious-form spec。
- 網頁全域函式（供測試以 page.evaluate 呼叫）：importPayload(obj)、toRocDate(str)、detectCategory(text)、applyParsedData(obj)、renderPages()。
- AHK 純函式：MammoFormEscapeJSON(str)、MammoFormBuildJSON(fields)。
- 驗證腳本 CLI：python radtracker/validate_mammo_form_llm.py --months 202602-202606 [--limit N]。

**Failure modes**

- AHK：報告空白、無 PACS 視窗、病歷號非 8 碼、HIS/PACS 病歷號不一致 → 繁中 MsgBox、還原剪貼簿、不開 Edge。中文姓名讀不到不中止，交由網頁標示。
- 網頁：非本工具 JSON、LLM 非 JSON、schema 不符、缺金鑰、網路錯誤 → 顯示繁中錯誤訊息，既有勾選不變；LLM 原始回應可複製。
- 驗證腳本：缺金鑰時以 exit 2 結束並提示設定 GEMINI_API_KEY。

**Acceptance criteria**

- node tests/test_mammo_suspicious_form.cjs 全數 PASS（網路全擋，LLM 以 fixture JSON 經 applyParsedData 注入）。
- python -m pytest -q tests/ 全數通過，含新增 tests/test_mammo_form_capture.py 與 index 連結測試。
- 本機批次驗證：JSON 合法率與 schema 合法率皆 100%，category 0 報告 lesion 數 ≥ 1 的比例 ≥ 95%；結果貼回 tasks 備註。
- 實機一次：使用者在佳里工作站以真實病例按鈕到列印預覽，確認版面與帶入資料正確。

**Scope boundaries**

- In：Mammo.ahk 按鈕與兩個純函式、新網頁、index.html 連結、三類測試、驗證腳本。
- Out：修改 test.ahk / CT.ahk 既有函式行為、身分證號擷取、表單電子送出、其他 LLM 供應商。

## Risks / Trade-offs

- [GetDICOMData 依賴 PACS 介面座標，第二台電腦位置設定（varWhere）不同可能點錯] → 沿用 LDCT 已在用的同一套路徑；失敗時病歷號檢查會擋下。
- [DICOM 出生日期欄位名稱 "Patient's Birth Date" 尚未實機確認] → 實作時先以 test3.ahk 類探測確認；讀不到則留空、網頁可手填。
- [中文姓名擷取誤抓到醫師或其他中文字] → 沿用 IsExcludedChineseName 過濾；網頁顯示供人工核對。
- [LLM 把良性發現列為病灶，或漏列] → prompt 明確排除 benign；每頁可刪；批次驗證量化。
- [報告全文送至 Gemini 屬外部服務] → 不送姓名、病歷號、日期，只送報告文字；與 LDCT 工具相同的既有做法。
- [剪貼簿內容被其他程式覆寫] → 網頁驗證 source 標記，誤貼時拒絕。

## Open Questions

- 已解決（2026-10-06）：DICOM Patient ID 為 8 碼病歷號、Patient's Birth Date 為 YYYYMMDD。Other Patient IDs（0010,1000）為身分證號，依使用者決定不讀取、不導入。
- 無其他未決問題。
