# Rad Workflow

放射科工作流程自動化工具集，包含 AutoHotkey 腳本與網頁工具。

- `vendor/lecture2notes`（submodule，講座管線產品）
- `skills-overlay/lecture2notes/`（個人 overlay）

## Web Tools

透過 GitHub Pages 直接使用：https://jieyu166.github.io/rad-workflow/

| 工具 | 說明 |
|---|---|
| [椎間孔狹窄報告輔助工具](https://jieyu166.github.io/rad-workflow/tool/spinal-foramen.html) | Spinal foraminal stenosis 報告產生器 |
| [DVT報告輔助工具](https://jieyu166.github.io/rad-workflow/tool/usdvt.html) | 雙側多種狀況可用點選方式產生報告 |
| [Cephalometric Analysis](https://jieyu166.github.io/rad-workflow/tool/ceph-analysis.html) | Cephalometric Analysis 教學&報告產生器 |
| [影片字幕播放器](https://jieyu166.github.io/rad-workflow/tool/jsonvideo.htm) | 影片播放器 + Recap 章節跳轉 |
| [字幕對齊工具](https://jieyu166.github.io/rad-workflow/tool/video-player-with-2subtitles.html) | 雙字幕影片播放與對齊 |
| [LDCT 報告輔助工具](https://jieyu166.github.io/rad-workflow/tool/ldct-report.html) | LDCT 肺癌篩檢報告產生器 |
| [探頭切面模擬器](https://jieyu166.github.io/rad-workflow/tool/us-probe-ct-plane.html) | 超音波探頭擺位 → 對應的 CT 重組切面（可載入 DICOM） |
| [Rad Tracker](https://jieyu166.github.io/rad-workflow/tool/exam_clock_input.html) | 檢查時間記錄追蹤工具 |
| [台鐵時刻表](https://jieyu166.github.io/rad-workflow/tool/timetable.html) | 西部幹線平日時刻表（高雄–新營，含沙崙支線） |
| [2026 下半年舊戶卡片回饋查詢](tool/card-rewards.html) | 既有持卡人／既有帳戶的 2026-08-01 至 12-31 離線回饋快照；查證基準日 2026-08-18，非即時銀行資料 |


## LDCT 報告工具

以瀏覽器開啟 `tool/ldct-report.html`。No lung nodule、Benign features、Insignificant 與 Juxtapleural 為獨立勾選項，可疑結節可另行勾選及編輯。

AI Parse 需要 Anthropic API Key（Claude）與網路，會將輸入的 Impression 傳送至 Anthropic Claude API；人工編輯與產生報告不需 API。金鑰只在頁面欄位中使用，不寫入網址或瀏覽器儲存空間；AHK 的 XButton1 選單「複製 Claude API Key」可從 `radiologist_settings.ini` 的 `APIKey3` 複製。AI 解析 insignificant nodules 時只填 SE，IM 留白，避免只列出部分影像；醫師可手動填入完整 IM 清單，例如 `4,55`。解析結果仍須人工覆核，PDF 通知單僅支援 Category 1–2。

回歸測試需要 Node.js、Playwright 套件與 Microsoft Edge：

```powershell
npm install --no-save --package-lock=false playwright
node tests/test_ldct_report.cjs
```

測試以合成資料在 headless Edge 執行，Claude 回應由測試替代，不使用真實 API Key 或傳送病患資料；不涵蓋真實 Claude 判讀品質、系統列印對話框或完整臨床規則驗證。

## AHK Scripts

`ahk-scripts/` 目錄下的 AutoHotkey 腳本，用於放射科報告自動化。

| 腳本 | 說明 |
|---|---|
| `CT.ahk` | CT 報告範本與快捷鍵 |
| `US.ahk` | 超音波報告（含 AI 輔助） |
| `Xray.ahk` | X 光報告範本 |
| `Mammo.ahk` | 乳房攝影報告 |
| `IR.ahk` | 介入放射報告 |
| `Abbr.ahk` | 縮寫快捷輸入 |
| `HotstringMenu.ahk` | Hotstring 選單 |
| `簡碼 jai.ahk` | 簡碼輸入（含 AI 設定） |
| `d8888basic.ahk` | 基礎設定 |
| `Gdip.ahk` | GDI+ 圖形庫 |
| `AHKClock - 2.ahk` | 桌面時鐘 |
| `test.ahk` / `test2m.ahk` | 測試用腳本 |

### usaigui 影像分析

`ahk-scripts/US.ahk` 的 `usaigui` 可選 `gpt-6-astra`（預設）、`gpt-5.6-terra` 或 `gpt-5.6-luna`。檢查部位與模型分開選擇，移除原本部位名稱中的 Thinking；Responses API 統一設定 `reasoning.effort: medium`。影像 prompt 放在獨立的 [ahk-scripts/usai-prompts](ahk-scripts/usai-prompts/README.md)，與 `ahk-scripts/prompts` 的 Impression → Findings 功能分開。更新 AHK 後需重載一次；之後編輯 UTF-8 Markdown 檔，每次分析都會重新讀取，無需重載。缺檔或空檔時停止分析並顯示檔案路徑。

模型路由測試需 Python 與 AutoHotkey v1.1；以隱藏 GUI 實跑選單及 JSON 建構，攔截網路 worker，不呼叫 API：

```powershell
$env:AHK_V1_EXE = 'C:\path\to\AutoHotkeyU64.exe'
python -m unittest discover -s tests -p "test_usai_*.py"
```

測試不代表真實 API 存取權、醫療影像分析品質或院內 HIS 完整操作已驗證。

### AI_FindOpen（Impression → Findings）模型選擇

`US.ahk` 的 AI_FindOpen 依情境選模型（2026-10-29 起）：

| 情境 | 模型 | API 金鑰（`radiologist_settings.ini`） |
|---|---|---|
| 腹超、TRUS | `claude-sonnet-5-5`（thinking `between_tools`、effort `low`、拒答 fallback） | `APIKey3` |
| IVP、CT-Chest | `gpt-5.6-terra`（`reasoning_effort: none`） | `APIKey` |
| Scrotum | `gpt-5.4-mini`（`reasoning_effort: none`） | `APIKey` |

CT 的 METHOD 行、打藥 contrast note 與不打藥註記由 `I2F_FixCTScaffold` 依 GUI radio button 覆寫，不交給模型；模型多加的 `<<END>>` 等標記行由 `I2F_StripTags` 刪除。

#### 測試方法

- **資料**：`radtracker/csv_input` 中 A80748 簽出的報告（2026-02～10），依申請單號從院內報告系統取回：腹超 19001-1（去重後 177 例）、TRUS 19017-1（173 例）、IVP 33012（105 例）、胸部 CT（隨機 140 例）。報告內文只放本機暫存區，不進 repo。
- **重跑**：把 impression 以 US.ahk 相同的 prompt 與參數送給各模型，CT 輸出再經 `I2F_FixCTScaffold` 處理。
- **評分**：關鍵字比對（漏寫 pleural effusion、ascites、hernia、Srs/Img 標記），以及由不知道模型身分的 LLM 評審（Claude Sonnet）逐例比較，計算漏寫、自行補出 impression 沒有的內容、細節錯誤、殘留診斷用語、格式問題，並選出最佳版本。
- **速度**：每例請求總耗時（AHK 為非串流，等完整回應才顯示）。

#### 結果一：OpenAI 各模型（腹超 177 例，關鍵字比對）

| 模型 | 中位數耗時 | Pleural 漏寫 /45 | Ascites 漏寫 /20 | Hernia 漏寫 /8 | Srs/Img 遺失 /256 |
|---|---|---|---|---|---|
| gpt-5.4-mini | 1.4 s | 1～3 | 1～3 | 0 | 11～15 |
| gpt-5.4-mini（effort low） | 2.1 s | 0 | 0 | 0 | 33 |
| gpt-5.4 | 2.8 s | 0 | 0 | 0 | 0 |
| gpt-5.6-luna | 2.4 s | 0 | 0 | 0 | 2 |
| gpt-5.6-terra（兩次重跑） | 2.3～2.4 s | 0 | 0 | 0 | 0 |

mini 兩次重跑結果不同（無法設定 temperature），剩下的漏寫屬隨機性；改 prompt 前（舊版 prompt）mini 漏 pleural 22/45、ascites 12/20、hernia 4/8。

#### 結果二：gpt-5.4-mini vs gpt-5.6-terra（盲評，數字為問題總數）

| 情境 | 漏寫 | 自行補出 | 細節錯誤 | 格式問題 | 中位數耗時 |
|---|---|---|---|---|---|
| TRUS（173） | 26 → 7 | 10 → 14 | 11 → 2 | 43 → 0 | 1.2 → 1.7 s |
| IVP（105） | 20 → 4 | 37 → 12 | 31 → 4 | 3 → 0 | 1.4 → 2.0 s |
| CT（140，框架修正後） | 50 → 44 | 0 → 2 | 33 → 20 | 1 → 1 | 1.8 → 2.7 s |

CT 在框架修正前，不打藥的 48 例中 METHOD 被寫成打藥：mini 8 例、Terra 16 例；修正後兩者皆 0。

#### 結果三：Terra vs Claude Haiku 5.5 vs Claude Sonnet 5.5（三方盲評，595 例）

實質錯誤 = 漏寫 + 自行補出 + 細節錯誤（越低越好）。

| 情境 | 實質錯誤 Terra／Haiku／Sonnet | 評審選為最佳（不含平手） | 中位數耗時 Terra／Haiku／Sonnet |
|---|---|---|---|
| 腹超（177） | 58／64／**31** | Sonnet 58、Terra 33、Haiku 9 | 2.4／1.9／2.6 s |
| TRUS（173） | 55／36／**13** | Sonnet 35、Haiku 10、Terra 7 | 1.7／1.5／2.2 s |
| IVP（105） | 34／75／33 | **Terra 34**、Sonnet 15、Haiku 7 | 2.0／1.6／2.2 s |
| CT（140） | 26／54／28 | **Terra 22**、Sonnet 17、Haiku 5 | 2.8／2.3／3.4 s |

- Haiku 最快、最便宜，但細節錯誤與殘留診斷用語最多（腹超診斷用語 176 處），不採用。
- Sonnet 在腹超、TRUS 明顯最好；IVP、CT 與 Terra 相當，評審略偏好 Terra，故維持 Terra。
- 費用：595 例 Sonnet 約 US$2.7、Haiku 約 US$0.14（system prompt 快取命中）。

#### 未納入或有限制

- **Claude Opus 5.5**：thinking 無法關閉，每例 4.8～11.8 s，太慢，未做完整測試。
- **Gemini 3.8 Flash**：測試時 API 回 402（預付額度用完），未測。
- 評審是 Claude 模型，雖然不知道各版本出自哪個模型，仍可能偏好 Claude 的寫法；Terra 與 mini 的比較不受此影響。
- 關鍵字比對與 LLM 評審都不等於臨床判讀驗證；結果仍須醫師覆核。
- 重跑與評審腳本在本機暫存區，未納入 repo；`tests/test_ct_scaffold.py`、`tests/test_i2f_claude.py` 只驗證 AHK 的組請求、解析與框架修正，不呼叫 API。

### CXR 報告範本

`ahk-scripts/cxr/` 目錄：

| 檔案 | 說明 |
|---|---|
| `cxr.ahk` | CXR 報告腳本 |
| `mammo.ahk` | Mammo 報告腳本 |
| `cxr.txt` | CXR 報告範本 |
| `kub.txt` | KUB 報告範本 |
| `ankle.txt` | Ankle 報告範本 |
| `健檢.txt` | 健檢報告範本 |

## 台鐵時刻表更新

`tool/timetable.html` 內嵌的時刻資料為靜態快照，台鐵改點後需重新抓取。
`tool/update_timetable.py` 會從台鐵官網抓取下列七站的平日時刻表，以車次號跨站合併後，
只改寫 HTML 中 `TRAIN DATA` 標記之間的區塊，版面與功能程式碼不受影響。

追蹤車站（由南往北）：高雄、美術館、新左營、台南、大橋、善化、新營。
凡停靠其中任一站的列車都會列入，包含經善化–大橋–台南往返的**沙崙支線**列車。

```powershell
cd tool
python update_timetable.py                    # 抓下一個平日（週末自動順延至週一）
python update_timetable.py --date 2026/09/07  # 指定日期
python update_timetable.py --dry-run          # 只抓取並印出統計，不寫檔
```

執行後會印出每站筆數與總計，可直接核對：

```
Ride date: 2026/08/17 (一)
  4120 新營   132 rows
  ...
Trains: 282 total, 142 northbound, 140 southbound, 73 via Shalun branch
```

更新後請確認頁面仍可正常開啟，再 commit 並 push（GitHub Pages 會自動發佈）。

注意事項：

- 頁首「資料日期」由腳本寫入的 `dataDate` 帶出，不需手動修改。
- 標記區塊內的資料為自動產生，請勿手動編輯，否則下次重跑會被覆蓋。
- 行駛方向以車次奇偶數判定（偶數北上），並與實際抓到的時刻交叉驗證；
  若兩者不一致會印出 `NOTE:` 指出是哪幾班車。
- 若台鐵改版導致某站解析不到任何班次，腳本會直接報錯中止，不會寫入空資料。

## 設定

`radiologist_settings.ini` 存放個人設定（帳號、AI API Key 等），不應包含實際密碼或 API Key。

## Mammo BI-RADS 0 追蹤

`radtracker/mammo_tracker.py` 掃描每月的乳房攝影篩檢案件。醫院系統匯出的 CSV
為 CP950 編碼；AHK 相關檔案通常為 UTF-8 with BOM，編輯時請維持原本編碼。

基本流程：

```powershell
python radtracker\mammo_tracker.py --month 2026-04
python radtracker\mammo_report_fetcher.py --month 2026-04
python radtracker\mammo_tracker.py --month 2026-04 --stats
python radtracker\mammo_report_fetcher.py --list-birads0
```

抓取報告需在院內網路（含院內 Wi-Fi）下執行。為避免影響白天臨床工作，
fetcher 僅於每日 21:00–03:00 之間運作。

### 追蹤欄位手動維護

追蹤狀態儲存於 `radtracker/output/mammo_birads0.json`。僅可編輯下列追蹤欄位，
自動產生的識別碼與日期請勿變動。

`status` 值：

- `pending`：尚需追蹤或尚未確認最終結果。
- `resolved`：已有最終結果，將計入 PPV1 統計。

`outcome` 值：

- `null`：尚無最終結果。
- `benign`：最終追蹤為良性。
- `malignant`：最終追蹤為惡性。
- `inadequate`：回招處置不充分或結果不明確，計為已結案但非惡性。
- `lost_to_followup`：病人未完成追蹤，計為已結案但非惡性。

`notes` 為自由文字，可填入臨床備註，例如：

```json
{
  "status": "pending",
  "outcome": null,
  "notes": "US BI-RADS 3, 6 個月後追蹤"
}
```

仍在追蹤中（例如超音波判定 BI-RADS 3 需後續追蹤）請使用 `pending + outcome null + notes`；
僅在案件可從待追蹤清單移除時，才使用 `resolved + outcome`。

USAI 每次重開視窗會清空影像與 OCR；更換影像、重跑 OCR、關閉視窗或逾時會取消背景工作。每次分析使用獨立暫存檔，回覆完整寫入後才讀取；多段文字依序保留。回歸測試使用隱藏 AHK GUI 與模擬 HTTP，不傳送影像至 API。
