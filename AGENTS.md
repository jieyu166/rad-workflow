# rad-workflow-main 專案指示

## 路由與修改範圍

- 先看 Git 狀態；本專案常有跨任務未提交變更，只處理本次明確相關檔案。
- AHK 使用 **AutoHotkey v1**。主入口為 `ahk-scripts/簡碼 jai.ahk`，會 include 部位模組、`test.ahk` 與 `hgh-bowel/hgh_capture.ahk`。
- `US.ahk` 的 USAIGUI prompts 位於 `ahk-scripts/usai-prompts/`，每次分析按共用規則、部位與影像模式組合。
- `ahk-scripts/prompts/` 供另一個 GPT-5.4-mini 程式 AI_FindOpen 使用；除非使用者明確要求修改該流程，不更動此目錄。
- skills 原始來源為 `skills/`；`.agents/skills/`、`.claude/skills/`、`.opencode/skills/` 是同步副本。修改原始來源後再同步，不直接編輯副本或第三方 plugin cache。
- 單檔網頁工具依本次用途查看 `tool/` 的相關檔案，不要求讀取整個工具目錄。

## 驗證

- AHK 載入檢查使用 v1 的 `/ErrorStdOut /iLib <暫存輸出> <主程式>`，工作目錄設為 `ahk-scripts/`；不要為了語法檢查直接啟動完整主程式。
- AHK 隔離測試由 `AHK_V1_EXE` 指定 v1 執行檔。只執行本次相關測試，例如 `test_usai_*.py`、`test_mammo_silicone.py`、`test_hgh_image.py`、`test_cxr_ai_hotkey.py`；先看測試的外部副作用再執行。
- LDCT 變更查看並執行 `tests/test_ldct_report.cjs`。其他測試依模組 README。
- 使用假資料且無正式系統存取的測試，可自主修正本次造成的失敗。真實 HIS／PACS 按鍵、報告寫入與病患資料上傳需對應明確授權；隔離測試通過不能代表院內 E2E 通過。
- prompt 的檔案／路由測試與模型判讀品質評測分開回報。USAI 同時支援 Astra、Terra、Luna，不能只憑 prompt 變短宣稱三者品質改善。

## 資料與完成條件

- 不讀取或回顯金鑰、登入資訊或病患資料來做範例。`hgh-bowel/work/`、機密 INI 與其他既有忽略項目不進版控。
- 保留醫師提供的報告文字、臨床閾值與不確定性；格式調整不等於臨床準則更新，新增醫學結論需另行查證。
- 每次任務完成到相關程式／文件修改、必要驗證與成果回報。沒有對外發布授權時停在本機可審閱結果。
