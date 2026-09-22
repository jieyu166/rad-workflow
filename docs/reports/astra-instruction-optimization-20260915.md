> 註（2026-09-22）：本文引用的 skills/lecture-to-notes 與 skills/whisper-srt-zh 腳本已由 lecture2notes（vendor/lecture2notes）取代；內文保留作歷史紀錄。
# 指示、skills 與 USAI prompt 優化紀錄

日期：2026-09-15。依使用者核准的範圍修改。

依據：[OpenAI — Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)。採用精確觸發、按需載入、清楚的完成條件與依風險選用驗證流程；不把 prompt 縮短等同於模型品質提升。

## 已修改

- 全域 `C:/Users/jai16/.codex/AGENTS.md`：精簡跨專案規則，明確區分已授權的本機工作與外部副作用，減少重複確認及固定工作流。修改前備份為同目錄 `AGENTS.md.backup-20260915-131959`。
- 新增專案根目錄 `AGENTS.md`：記錄 AHK v1、隔離測試、USAI prompts 路由、skills 原始來源與病患資料界線。
- 14 個自有 skills 收窄 description；保留其餘原有 frontmatter。
- `obsidian-v4-cleanup` 入口由 777 行降為 36 行，細節移至按任務讀取的 references；PDF 深讀、新知查核、來源及品質 gate 保留。
- `lecture-to-notes` 入口由 280 行降為 41 行；轉錄、分段、截圖筆記、批次輸出分開載入。保留純音檔及手動截圖例外、來源優先序、本機 ASR 與程序完成檢查。
- `spectra-apply` 由 313 行降為 53 行；保留狀態查核、專案品質選項、任務完成紀錄與驗證，允許在既有授權內修復可恢復失敗。
- USAI 的 CXR、knee、foot/ankle prompts 移除無依據的預設陽性或過度確定結論；spine 移除重複錯誤清單，保留數字規則與全部六個範例。更新 USAI README。
- 25 個修改檔案同步至 `.agents/skills/`、`.claude/skills/`、`.opencode/skills/`。其他既有副本或第三方 plugin cache 未刪改。

## 驗證

- USAI 測試：`python -m unittest discover -s tests -p 'test_usai_*.py'`，指定 AHK v1 執行檔，11 項通過。
- 14 份 skill YAML 解析成功，除 description 外的 frontmatter 與修改前快照一致。
- 官方 `quick_validate.py`：5 份通過；9 份 Spectra 因既有 `compatibility`，以及其中兩份的 `disallowedTools` 欄位，被簡易驗證器拒絕。保留原欄位，未宣稱官方驗證全部通過。
- 三個副本的 75 個檔案 SHA-256 與原始來源一致。
- `ahk-scripts/prompts/` 的 4 個 GPT-5.4-mini prompt SHA-256 與修改前一致。
- 拆分後入口的 Markdown 文件連結存在；Task 5／8 原始主體保留。獨立檢查發現的純音檔例外與過時 Task 4 引用已修正。
- spine 六個完整範例及去重段落之前的數字規則與修改前一致。
- `git diff --check` 通過。

## 尚未證明

未呼叫真實模型 API、未操作院內 HIS／PACS，未對 Astra、Terra、Luna 進行醫療案例品質比較，也未實跑完整影片／PDF 管線。臨床閾值未重新查證或更新。

全域指示與 skill description 的新版本通常在新工作階段完整載入。本次保留其他任務的未提交修改，未 commit 或 push。
