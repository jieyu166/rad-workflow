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
| [台鐵時刻表](https://jieyu166.github.io/rad-workflow/tool/timetable.html) | 西部幹線時刻表（美術館-善化） |

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
