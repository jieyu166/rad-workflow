## 1. 實機確認與測試資料

- [x] 1.1 實機確認 DICOM 欄位（Open Question）：在 PACS 開一位 mammo 病人，確認 DICOM 檔頭中 "Patient ID" 等於 8 碼病歷號、"Patient's Birth Date" 與 "Study Date" 標籤存在且為 YYYYMMDD；驗證方式：使用者回報三個標籤的實際格式（不貼真實值），結果記在本任務備註。
  - 備註（2026-10-06 使用者提供去識別樣本）：0010,0020 Patient ID 為 8 碼數字、0010,0030 Patient's Birth Date 為 YYYYMMDD、0010,0010 Patient's Name 為英文；0010,1000 Other Patient IDs 為身分證號，使用者決定不導入。0008,0020 Study Date 已確認存在且為 YYYYMMDD（Series／Acquisition／Content Date 同值），以 GetDICOMLineData 讀取 Study Date。
- [x] 1.2 建立去識別 fixture（Local batch validation against archived reports 的測試面）：從 radtracker/output 挑 6 份報告（category 0 單側、0 雙側、0 含 benign calcification、4、5、2）存成 tests/fixtures/mammo_form/*.txt，遮蔽 6 位以上數字、日期與人名，並為每份寫期望的 category 與 lesions JSON；驗證：grep 確認 fixture 內無 6 位以上連續數字，人工複查無人名。

## 2. 網頁 tool/mammo-suspicious-form.html

- [x] 2.1 重現附表四之五 A4 版面並實作 Manual edit and A4 print 與 Hardcoded hospital, blank physician and ID（Fixed header fields）：表頭（姓名、身分證 10 格、出生日期、攝影日期、醫院名稱「佳里奇美醫院」、放射科醫師空白）、Category 0/3/4(a/b/c)/5、病灶 1–9 項全部為可勾選元件；@media print 只印表單頁、每頁一張 A4；驗證：tests/test_mammo_suspicious_form.cjs 檢查列印媒體下按鈕隱藏、頁面標題文字存在、表頭預設值正確。
- [x] 2.2 實作 Import patient data from clipboard JSON（Clipboard JSON hand-off instead of URL parameters）：Ctrl+V 與「從剪貼簿匯入」按鈕呼叫 importPayload，僅接受 source "rad-workflow/mammo-form"，nameZh 空白時以 nameEn（^ 換空白）帶入並標示需人工修正；不讀網址、不寫任何瀏覽器儲存；驗證：.cjs 測試涵蓋有效 payload、純文字 "hello"、缺中文姓名三情境，並斷言 localStorage/sessionStorage 為空。
- [x] 2.3 實作 ROC date conversion（toRocDate）：支援 YYYYMMDD、YYYY.MM.DD、YYYY/MM/DD、YYYY-MM-DD，無法解析留空；驗證：.cjs 測試跑 spec 中 4 列範例表。
- [x] 2.4 實作 Deterministic BI-RADS category（Deterministic category, LLM only for lesions）：detectCategory 以 (?:BI-?RADS\s*)?category\s*:?\s*(\d)([abc])?(?![a-z]) 取第一個匹配（4 後接 A/B/C 時同時勾子分類），0/3/4/5 勾選，其他或無匹配顯示警告不勾選；驗證：.cjs 測試跑 spec 範例表 4 列並以 6 份 fixture 斷言 category。
- [x] 2.5 實作 LLM lesion parsing（Single prompt source shared by page and validator）：系統提示詞放在 MAMMO-PROMPT-START / MAMMO-PROMPT-END 標記之間，模型 id 與 tool/ldct-report.html 相同值；「AI 解析」缺金鑰不送出；回應經 schema 與 enum 白名單驗證後交 applyParsedData，失敗時顯示錯誤與原始回應且不改勾選；驗證：.cjs 測試以 page.route 攔截 generateContent 回傳 fixture JSON、非 JSON 字串、缺 lesions 三種回應，並測缺金鑰時無請求發出。
- [x] 2.6 實作 One form page per lesion（One page per lesion with editable pages）：renderPages 依 lesions 順序每個病灶一頁、共用表頭與 category，零病灶產生一頁，提供刪頁與新增空白頁；驗證：.cjs 測試以雙側 fixture 斷言 2 頁且第 1 頁勾 Mass Rt.、第 2 頁勾 Calcifications Lt.，以 benign calcification fixture 斷言只有 1 頁 Asymmetry Lt. Focal UOQ。
- [x] 2.7 根目錄 index.html 新增「乳篩疑似異常個案報告表」連結至 tool/mammo-suspicious-form.html；驗證：tests/test_index_navigation.py 新增連結斷言並通過。

## 3. AHK 擷取 ahk-scripts/Mammo.ahk

- [x] 3.1 實作 Pure AHK functions for JSON building：MammoFormEscapeJSON 依 RFC 8259 跳脫反斜線、雙引號、CR、LF、TAB 與其他控制字元，MammoFormBuildJSON 依 Clipboard JSON hand-off 的欄位順序輸出單一 JSON 物件；驗證：tests/test_mammo_form_capture.py 以 AHK_V1_EXE 執行切出的函式，Python json.loads 結果與原字串（含引號、反斜線、CRLF、TAB、中文）完全相等。
- [x] 3.2 實作 Suspicious-form button in the mammo GUI 與 Collect report and patient data（Reuse existing AHK DICOM and PACS helpers）：mammo; GUI 新增「疑陽表單」按鈕，流程先備份 ClipboardAll，讀 ThunderRT6TextBox14 與 ThunderRT6TextBox9，呼叫 ActivatePACSForLDCT、GetDICOMData（僅一次）、GetDICOMLineData、GetAccessionNumber、GetPACSPatientChineseName；驗證：tests/test_mammo_form_capture.py 以 stub 取代視窗函式，斷言 GetDICOMData 只被呼叫一次且既有「輸出」標籤未被執行；AHK 語法檢查（/iLib NUL）通過。
- [x] 3.3 實作 Abort on missing source or patient mismatch（Chart number cross-check between HIS and PACS）：報告空白、無 INFINITT PACS 視窗、病歷號非 8 碼、HIS 與 DICOM 病歷號不同時顯示繁中 MsgBox、還原剪貼簿、不啟動 Edge；成功時剪貼簿放 JSON 並以 Edge 開啟不帶 query/fragment 的網頁路徑；驗證：tests/test_mammo_form_capture.py 以 stub 涵蓋四種中止情境（斷言未呼叫 Run、剪貼簿還原）與成功情境（斷言 Run 的 URL 不含 ? 與 #）。

## 4. 驗證

- [x] 4.1 實作 Local batch validation against archived reports：radtracker/validate_mammo_form_llm.py 以標記擷取 HTML 內同一份 prompt，讀 GEMINI_API_KEY（.env 或環境變數，缺則 exit 2），對 category 0/3/4/5 報告逐份解析並顯示進度，主控台只輸出 cp950 相容字元，明細 CSV 寫入 radtracker/output/；驗證：以 --limit 3 執行成功並輸出 JSON 合法率、schema 合法率、lesion 數分布、左右側一致率。
- [ ] 4.2 全量批次驗證並調整 prompt：跑 202602–202606 全部疑陽報告，達成 JSON 與 schema 合法率 100%、category 0 報告 lesion ≥ 1 比例 ≥ 95%；驗證：結果數字記於本任務備註，抽 10 份由使用者人工核對勾選正確性。
  - 備註（2026-10-06 全量 202602–202606）：143 份；JSON 合法 143/143、schema 合法 143/143（嚴格，無 enum 被丟棄）；lesion 數 1:119、2:20、3:4；category 0 有 lesion 138/138；左右側一致 138/138。抽樣核對頁 radtracker/output/mammo_form_review_20261006.html（gitignored），待使用者核對。
  - 備註（2026-10-15 實際報告測試）：新抓 202607–202610 共 507 份，BI-RADS 0 55 份；逐份 QA 唯一錯誤型態為「只寫半球／邊界鐘點時位置留空」（10 份 11 頁）。提示詞改為半球與邊界鐘點填 One view only 後，需人工補位置 15→2（剩餘 2 份報告本身無位置）。回歸 202602–202610 共 198 份：JSON／schema 100%、category 0 有 lesion 193/193、左右側一致 192/192。
- [ ] 4.3 端到端實機測試：使用者在佳里工作站以真實病例從 mammo; 按「疑陽表單」到列印預覽；驗證：使用者確認表頭、民國日期、病灶勾選與 A4 版面正確，並以 python -m pytest -q tests/ 與 node tests/test_mammo_suspicious_form.cjs 全數通過作為合併前檢查。
