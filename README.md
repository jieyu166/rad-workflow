# Rad Workflow

放射科工作流程自動化工具集，包含 AutoHotkey 腳本與網頁工具。

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
| [Rad Tracker](https://jieyu166.github.io/rad-workflow/tool/exam_clock_input.html) | 檢查時間記錄追蹤工具 |
| [台鐵時刻表](https://jieyu166.github.io/rad-workflow/tool/timetable.html) | 西部幹線時刻表（美術館-善化） |
| [信用卡回饋查詢](https://claude.ai/public/artifacts/aa39410d-a1c4-4e5d-8259-df094c2238b8) | 信用卡回饋查詢 |


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
