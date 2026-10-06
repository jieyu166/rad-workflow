## Why

乳篩報告判為 BI-RADS 0（或 3/4/5）時，須另填國健署「附表四之五 婦女乳房 X 光攝影檢查服務之篩檢疑似異常個案報告表」。目前要手抄姓名、病歷號、出生與攝影日期（民國年），再對照報告逐項勾選病灶欄位，費時又容易抄錯；LDCT 已有 tool/ldct-report.html 的「AHK 擷取＋LLM 解析＋列印」模式可以仿照。

## What Changes

- 新增網頁工具 tool/mammo-suspicious-form.html：重現附表四之五版面（A4 可列印），從剪貼簿 JSON 匯入病人資料與報告全文，呼叫 Gemini 解析報告後自動勾選「疑似異常結果」與「病灶勾選」1–9 項；每一處病灶各產生一頁表單（符合表單「單側多處或兩側病灶分開表單」規定），使用者可在列印前手動修改任何勾選。
- 醫院名稱固定為「佳里奇美醫院」；放射科醫師欄留空供蓋章；身分證統一編號留空供手填。
- 出生日期、攝影日期自動轉為民國年月日。
- 在 Mammo.ahk 的 mammo; GUI 新增「疑陽表單」按鈕：讀取 chk060 報告（ThunderRT6TextBox14）與病歷號（ThunderRT6TextBox9）、PACS DICOM（出生日期、攝影日期、Patient ID）、PACS 視窗中文姓名，組成 JSON 放入剪貼簿並以 Edge 開啟網頁；chk060 與 DICOM 病歷號不一致時警告並中止。
- 根目錄 index.html 新增工具連結。
- 新增測試：網頁 Playwright 測試（去識別 fixture）、AHK JSON 組裝單元測試；另提供本機批次驗證腳本，以 radtracker/output 既有 mammo 報告驗證 LLM 解析（不進 git）。

## Capabilities

### New Capabilities

- `mammo-suspicious-form`: 疑似異常個案報告表網頁——剪貼簿 JSON 匯入、LLM 報告解析、病灶分頁、民國日期轉換、A4 列印版面。
- `mammo-form-capture`: AHK 端資料擷取——從 chk060 與 INFINITT PACS 收集報告與病人資料、病歷號一致性檢查、剪貼簿 JSON 交接並開啟網頁。

### Modified Capabilities

(none)

## Impact

- Affected specs: mammo-suspicious-form（新）、mammo-form-capture（新）
- Affected code:
  - New: tool/mammo-suspicious-form.html, tests/test_mammo_suspicious_form.cjs, tests/test_mammo_form_capture.py, tests/fixtures/mammo_form/, radtracker/validate_mammo_form_llm.py
  - Modified: ahk-scripts/Mammo.ahk, index.html, tests/test_index_navigation.py
  - Removed: (none)
- 依賴：Gemini API（金鑰沿用 LDCT 作法，於頁面手動貼上，可用 XButton1 選單複製）；Edge（Playwright channel msedge）。
- PII：剪貼簿與網頁只在本機處理；不使用網址參數傳遞病人資料；radtracker/output 原始報告不進 git，fixture 必須去識別。
