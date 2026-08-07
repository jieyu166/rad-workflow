# Rad Workflow 陷阱表（踩雷教訓）

> 按需讀取：指令或程式**第一次失敗就先來這裡比對症狀**，命中照修法，不要自己發明繞法。
> 新教訓寫法見 `~/.claude/playbooks/maintenance-protocol.md`；每條格式 = 症狀 → 根因 → 修法（+日期）。

## 編碼（本專案第一大坑）

| 對象 | 編碼 | 修法 |
|---|---|---|
| 醫院匯出 CSV | cp950（Big5）、Tab 分隔 | Python 開檔 `encoding='cp950'`；別用 utf-8 硬讀 |
| AHK 腳本（.ahk） | utf-8-sig | 編輯後維持 utf-8-sig，存成 cp950 會亂碼 |
| 主控台輸出 | 需 cp950 相容 | print 禁用 `→ ≥ ≈ ✓` 等符號，用 `-> >= ~= OK` 代替，否則 UnicodeEncodeError |

## Windows / Shell

- **症狀**：PowerShell 報 `&&` parser error。根因：Windows PowerShell 5.1 無 pipeline chain。修法：`A; if ($?) { B }`。
- **症狀**：git bash 裡多行 commit message 寫不進去。根因：bash 不支援 PowerShell here-string `@'...'@`。修法：訊息寫到 `.git/CM.txt` 後 `git commit -F .git/CM.txt`。（2026-06）
- **症狀**：settings.json 的 hook command 跳脫寫到懷疑人生。修法：外部化成 `~/.claude/hooks/*.sh`，JSON 只放路徑。（2026-06）

## OneDrive（資料遺失風險）

- **症狀**：原始 .py 檔憑空消失。案例：slide-extractor 曾遺失 .py，靠 .pyc 字串重建。修法：**寫完立即 commit**；Stop hook `~/.claude/hooks/check-uncommitted.sh` 會警告未 commit 的 .py/.md/.html/.yaml/.ahk。（2026-05）
- **症狀**：symlink 失效或被上傳成實體檔。根因：OneDrive 不支援 symlink 語義。修法：用「canonical 目錄 + 複製腳本 + git」，見 `sync_skills.py`。
- **注意**：檔案找不到時勿先怪 OneDrive——曾有一次是使用者自行搬移。先問再修。（2026-06）
- **症狀**：讀 OneDrive 檔案得到大小正確但內容全 `0x00` 的假檔；或 `Copy-Item` 報 "cloud operation was not completed before the time-out"。根因：online-only 佔位檔（attributes 含 `RecallOnDataAccess` 0x400000），未 hydrate 就被讀走稀疏內容。修法：先 `attrib -U +P "<file>"` 釘選觸發下載，再輪詢重讀直到 bytes 非全零才採用（實測需 2 分鐘以上）。**檢查用**：`(Get-Item $f).Attributes.value__ -band 4194304`，非 0 即尚未下載。（2026-08）

## AHK

- **症狀**：`#include` 進來的檔案，頂層 `global X := "值"` 是空的、頂層函式呼叫沒被執行。根因：auto-execute 段在**遇到第一個熱鍵定義就結束**，而 `簡碼 jai.ahk` 的 include 群第一個就是 `test.ahk`（第 3、7 行即熱鍵），其後所有 include 的頂層程式碼都不會跑。修法：設定改寫成函式回傳值（無執行期賦值），需要在載入時執行的呼叫放到 `簡碼 jai.ahk` 的 **include 之前**。（2026-08）
- **症狀**：`Call to nonexistent function` 單獨執行子腳本時。根因：`hgh_capture.ahk` -> `test.ahk` -> `簡碼 jai.ahk`/`Xray.ahk` 相依連鎖，子腳本無法獨立跑。修法：一律從 `簡碼 jai.ahk` 進入。（2026-08）
- **症狀**：`ControlClick, %MyFunc()%, ...` 沒作用。根因：傳統參數的 `%...%` 只能包變數，不能包函式呼叫。修法：改用強制運算式 `ControlClick, % MyFunc(), ...`。（2026-08）
- **症狀**：載入即報 `A control's variable must be global or static. Specifically: vXXX`。根因：`Gui, Add, ..., vXXX` 寫在函式內，`vXXX` 被當成區域變數。修法：函式內加 `global XXX`（或 `static`）。（2026-08）
- **症狀**：腳本在家用機正常、醫院機路徑全錯。根因：硬編絕對路徑，但家用機是 `C:\Users\jai16\OneDrive\`、醫院機是 `D:\jai166\Onedrive\`。修法：用 `A_LineFile` 推導本檔位置（在 `#include` 的檔案裡回傳的是「本檔」路徑，不是主腳本），勿用 `A_ScriptDir`。（2026-08）

## Python

- **症狀**：`http.server` 服靜態檔，中文檔名 404。根因：`urlparse(path).path` 不會 percent-decode。修法：手動 `unquote()` 再對磁碟路徑。（2026-06）
- **症狀**：同一 response 內 Python 寫檔腳本 + Edit tool 改同一檔，結果互相覆蓋。修法：同檔操作序列化，最後一步後必 read-back 驗證。
- **症狀**：openpyxl 讀 `biopsy_tracker_2026.xlsx` 資料錯位。根因：合併儲存格。修法：補登避開 merged cells；更新後跑 `build_trends.py`。

## Radtracker 資料規則

- 模態比對：US 用 `US-`（不是 `US `）；BMD 用 `DENSITOM`（不是 `DENSITY`）
- 深夜時段 00:00–05:59 歸屬前一天
- 醫院檔名 `115MMDD_jie.csv`（民國年）→ 改名 `2026MM.csv`；每週歸檔 `output/W{nn}/`
- 正常週基準：XR 300–350、CT 20–25、US 50–70、Mammo 40–70（額外值班週不列入基準）
- `biopsy_tracker_2026.xlsx` 含病患資料，**嚴禁 commit**

## AHK

- `HotstringMenuV` 標準格式：每引數獨立一行、前綴 `,`、單行 ≤150 字元
- 跨模態通用縮寫放 `Abbr.ahk`（如 CA;、FR;），不放 CT.ahk
- 新 hotstring 提議前先比對所有 .ahk（含簡碼/選單）防 trigger 衝突；報告用 trigger 慣例帶 `;`
- Keylogger 分析：`cd ahk-scripts && python analyze_keylog.py logs/<file> -o out.json`（腳本在 `ahk-scripts/`，log 檔在 `logs/`；舊文件寫 `cd ahk-scripts/logs` 是錯的，2026-07 實測修正）；跨檔彙整用 `aggregate_raw.json` 模式

## GitHub / 部署

- Web 工具部署於 GitHub Pages：https://jieyu166.github.io/rad-workflow/ ，push main 即生效
- GitHub Wiki 的 `[[A|B]]` 語法 = 顯示文字在前、頁面名在後；wiki.git 首頁必須先從網頁建立，直接 push 回 "Repository not found"（2026-07）
- `radiologist_settings.ini` 為個人設定檔，不可含真實密碼/API Key；機密放環境變數或 .env
