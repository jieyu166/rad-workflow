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

- **症狀**：repo 根目錄冒出 `pyvenv.cfg`、`Lib/`、`Include/`，`scripts/` 混入 `python.exe`／`pip.exe`，`.gitignore` 只剩 `*`，`git add` 說全部被忽略、`spectra task done` 顯示成功但 tasks.md 沒勾。根因：subagent 的 Bash cwd 每次呼叫後會重設回本 repo，agent 以相對路徑或空變數執行 `python -m venv`，venv 建在 repo 根目錄；venv 會寫一份內容為 `*` 的 `.gitignore` 蓋掉原檔。修法：`git checkout -- .gitignore`，逐檔刪 venv 殘留（`scripts/` 內只刪未追蹤的 venv 檔）；交辦 prompt 一律給**絕對路徑**的 venv 位置並要求建立前 `pwd`。（2026-09）
- **症狀**：`l2n frames --mode scene` 跑十分鐘只留 1 張（00:00:00），log 滿是 `Frame at … has incorrect size and cannot be processed: decoded size = (2448, 1226), expected = (2448, 1338). Video may be corrupt.`。根因：螢幕錄影／直播存檔的解析度中途會變（分享畫面切換），PySceneDetect 以第一張為準、其後全部丟棄。修法：先 `ffprobe -show_entries stream=width,height` 或看 log，改 `l2n frames --mode interval --every 45 --force`；`--force` 只覆蓋 frames.json，不動其他產物。（2026-10）
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
- **症狀**：Win+X（複製舊報告）、`cxr2;`、`spine2;` 等所有經 `ActivateHISLight()` 輸出的功能，按鍵都打進原本的視窗（GUI 或 PACS），chk060 叫不到前景。根因：非程式碼問題（當晚 AHK 改動未觸及該路徑；chk060 無法以系統管理員執行，排除權限）；重開程式後即恢復。修法：**先重開 chk060／AHK 再查程式**，不要先改 `ActivateHISLight`。若重開無效，在 `ActivateHISLight` 記錄 WinActivate 前後的作用中程式與 chk060 視窗清單（只記類別、不記標題，標題含病人姓名）。（2026-10）

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
- **症狀**：腹超 impression→finding 常漏 inguinal hernia、pleural effusion、ascites（重跑 573 例：pleural 約一半消失）。根因：`US.ahk` 注入的 `conditionalOutput` 寫「Do NOT output: … Others …」，蓋過 `us_abd.md` 的「必須建立 Others」；只改 md 壓不住，要拿掉 AHK 端那個字。另外帶保留語氣的發現（Suspect/Probably X）會被整條刪掉，md 要明寫「去掉保留語氣、保留發現本身」。驗證方式：依申請單號從 `demo_diff.asp` 抓舊報告，用同模型重跑 impression 再比對；報告內文只放 scratchpad，不進 repo。gpt-5.4-mini 不能設 temperature，同一 prompt 兩次結果會不同，比較至少要 150 例以上。大批重跑會用掉 OpenAI 額度（`insufficient_quota`），額度一歸零 US.ahk 也會跟著失效。（2026-10）
- **症狀**：不打藥的胸部 CT，AI 產生的 METHOD 行寫成「有打藥」（重跑 48 例中 mini 有 8 例、Terra 有 16 例），不打藥的註記句也常漏掉。根因：`ct_chest.md` 有一條「沒給 METHOD 就用打藥版」的備用規則，範例輸出又把打藥的 METHOD 寫死，模型就照抄了。修法：固定不變的框架行不要交給模型產生，改由 `US.ahk` 的 `I2F_FixCTScaffold` 依 GUI 的選擇覆寫，測試在 `tests/test_ct_scaffold.py`；prompt 裡不要留會跟呼叫端代入值衝突的備用規則。（2026-10）
- Keylogger 分析：`cd ahk-scripts && python analyze_keylog.py logs/<file> -o out.json`（腳本在 `ahk-scripts/`，log 檔在 `logs/`；舊文件寫 `cd ahk-scripts/logs` 是錯的，2026-07 實測修正）；跨檔彙整用 `aggregate_raw.json` 模式

## GitHub / 部署

- Web 工具部署於 GitHub Pages：https://jieyu166.github.io/rad-workflow/ ，push main 即生效
- GitHub Wiki 的 `[[A|B]]` 語法 = 顯示文字在前、頁面名在後；wiki.git 首頁必須先從網頁建立，直接 push 回 "Repository not found"（2026-07）
- `radiologist_settings.ini` 為個人設定檔，不可含真實密碼/API Key；機密放環境變數或 .env
- **症狀**：`deploy_lecture2notes.py` 印 `run: git submodule update --init vendor/lecture2notes` 並 exit 2。根因：clone 時未帶 `--recurse-submodules` 或 submodule 未初始化。修法：照印出的指令執行後重跑。（2026-09）
