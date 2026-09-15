---
name: spectra-apply
description: 實作或繼續既有 Spectra change 的任務；不套用到一般未使用 Spectra 的修改。
license: MIT
compatibility: Requires spectra CLI.
metadata:
  author: spectra
  version: "1.0"
  generatedBy: "Spectra"
---

# 實作既有 Spectra change

完成已授權 change 的待辦、受影響驗證與進度紀錄。tasks 檔的 checkbox 是唯一任務進度來源；不用另一套 tracker 重複紀錄。使用 CLI 回傳的檔案位置與 schema，不臆測固定路徑。

## 選取與狀態

1. 有 change 名稱就使用；可從目前對話唯一推定時直接使用。否則執行 `spectra list --json` 與 `spectra list --parked --json`，唯一 active change 可自動選取，多個候選才詢問。
2. 簡短告知選用的 change。執行 `spectra status --change "<name>" --json`，另查 parked list；status 成功不代表未 parked。
3. 若 parked 且使用者已明確要求繼續此 change，可執行 `spectra unpark "<name>"`；沒有繼續授權則詢問。之後重新讀狀態。
4. 執行 `spectra in-progress add "<name>"`，再執行 `spectra instructions apply --change "<name>" --json`。

CLI 不存在時先查專案文件中的安裝／執行位置；無法取得則回報具體阻礙，不假造狀態。單次命令失敗先確認 cwd、參數及可恢復原因；兩次同方法失敗後改變方法。仍無法取得可靠狀態時停止相依操作。

## Preflight 與品質

- `state: blocked`：依缺少的 artifacts 說明阻礙，必要時使用 spectra-propose；`all_done`：核對完成狀態後回報，不再實作。
- `preflight: clean` 繼續；warning 簡述後繼續；critical 檢查缺少的實際檔案，不略過必要輸入。能在原授權內修復者先修復，需變更需求或跳過規格時才請使用者決定。
- 執行 `spectra analyze <change-name> --json`。warning／suggestion 可持續處理；critical 先處理確定的矛盾或缺漏，無法判定需求時詢問，不自行略過。
- 根據 `contextFiles` 讀取本次待辦所需的設計、spec 與 tasks；先前已讀且未變的部分不用每個 task 重讀。上下文不足或檔案變更時重新查閱相應段落。

## 專案選項

讀取專案的 `.spectra.yaml`（若有）：

- `tdd: true`：用 `spectra instructions --skill tdd` 取得流程，以重現問題或規格範例的失敗測試開始。
- `audit: true`：用 `spectra instructions --skill audit` 核對危險預設、空值、型別混淆與靜默失敗；不因此自動啟動獨立三代理稽核。
- `parallel_tasks: true` 且連續待辦標 `[P]`：有可用且獲准的代理能力時，平行處理真正獨立的工作。資料相依或修改區域重疊則循序；無代理能力時循序完成。

## 執行與驗證

- 先查看相鄰程式與可重用工具，按 task 的實際要求修改，保留無關變更。
- 規格內的 GIVEN／WHEN／THEN 與範例表格作為驗證案例；有具體風險時可補邊界案例，不任意替換已約定的值。
- TBD／TODO 若造成需求不明，先釐清該處；可在既有設計內確定的細節直接補足。
- 可恢復的實作／測試失敗在授權範圍內繼續修正。遇到真正缺少輸入、權限、外部狀態或需變更設計的決策，才停止相依工作並說明。
- 核對 task 的每項要求與受影響測試後，執行 `spectra task done --change "<name>" <task-id>`，讓 CLI 更新 checkbox 並記錄相關檔案；未完成的項目不得勾選。
- 持續完成後續待辦；短暫回報進度不代表任務結束。

## 交付

再執行 `spectra instructions apply --change "<name>" --json`，確認 `all_done`；若還有本次範圍內待辦，繼續處理。回報 N/M、驗證與未解阻礙。封存、commit、推送及發布依使用者授權另外執行，不由 `all_done` 推定。

需要詢問時使用目前環境可用的提問工具；若沒有就用簡短文字。不依賴 Claude 專用工具名稱，也不對同一授權重複詢問。
