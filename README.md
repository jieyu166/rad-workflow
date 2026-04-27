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

## Mammo BI-RADS 0 Tracker

`radtracker/mammo_tracker.py` scans monthly mammography screening cases from
CSV exports. CSV files from the hospital system are CP950 encoded by default.
AHK-related files are usually UTF-8 with BOM; preserve the existing encoding
when editing those files.

Basic workflow:

```powershell
python radtracker\mammo_tracker.py --month 2026-04
python radtracker\mammo_report_fetcher.py --month 2026-04
python radtracker\mammo_tracker.py --month 2026-04 --stats
python radtracker\mammo_report_fetcher.py --list-birads0
```

Report fetching requires the hospital intranet, including hospital Wi-Fi. The
fetcher only runs during 21:00-03:00 to avoid adding load during daytime
clinical work.

### Manual Follow-Up Fields

Follow-up state is stored in `radtracker/output/mammo_birads0.json`. Edit only
the tracking fields below; generated identifiers and dates should be left as-is.

`status` values:

- `pending`: still needs follow-up or final outcome confirmation.
- `resolved`: final outcome is available and should be included in PPV1
  statistics.

`outcome` values:

- `null`: no final outcome yet.
- `benign`: final follow-up is benign.
- `malignant`: final follow-up is malignant.
- `inadequate`: recall workup was inadequate or inconclusive and should be
  counted as resolved but non-malignant for PPV1.
- `lost_to_followup`: patient did not complete follow-up and should be counted
  as resolved but non-malignant for PPV1.

`notes` is free text for clinical context, for example:

```json
{
  "status": "pending",
  "outcome": null,
  "notes": "US BI-RADS 3, 6-month follow-up"
}
```

Use `pending + outcome null + notes` when follow-up is still ongoing, such as
after ultrasound BI-RADS 3. Use `resolved + outcome` only when the case should
leave the pending list.
