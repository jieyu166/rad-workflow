# Slide Extractor

從影片偵測投影片切換、瀏覽縮圖、勾選匯出全解析度 PNG。本地 HTTP 介面（無外部依賴）。

> 2026-05-28 重建——原 `.py` 檔遺失，依 `__pycache__/*.pyc` 字串 + PySceneDetect API 還原。功能與原版一致。

## 依賴

- Python 3.10+
- ffmpeg / ffprobe（縮圖/匯出/duration 用）
- PySceneDetect（adaptive/content 模式用）：
  ```bash
  pip install scenedetect[opencv]
  ```
- 若無 PySceneDetect → 改用 `--detector ffmpeg`（純 ffmpeg scene-detect filter）

## 使用

```bash
cd slide-extractor
# 把影片放在這個資料夾（.mp4 / .mkv / .mov / .avi / .webm）
python server.py
# 瀏覽器自動 → http://127.0.0.1:8000
```

UI 流程：
1. 選影片 → 設參數（detector / threshold / min_scene_len）→ 按「偵測」
2. 縮圖出現後，點縮圖勾選想要的投影片
3. 設「輸出寬度」（預設 1920；空白＝原始）→ 按「匯出」
4. PNG 存到 `output/`，檔名 `{video_stem}-{MMSS}.png`

## CLI（不開網頁版）

```bash
# 只看偵測結果
python detector.py myvideo.mp4
python detector.py myvideo.mp4 --detector content --threshold 27
python detector.py myvideo.mp4 --detector ffmpeg --threshold 0.3
```

## 參數說明

| 參數 | 預設 | 說明 |
|---|---|---|
| `detector` | adaptive | adaptive / content / ffmpeg |
| `threshold` | (auto) | adaptive=3.0、content=27.0、ffmpeg=0.3。**愈低愈敏感** |
| `min_scene_len` | 1.5s | 兩偵測點最短間距（避免連發） |
| `width` (export) | 1920 | 匯出 PNG 寬度（保留比例），留空 = 原始 |

## 檔案

```
slide-extractor/
├── detector.py    PySceneDetect / ffmpeg wrapper
├── server.py      本地 HTTP (/api/frames, /api/export)
├── index.html     瀏覽器 UI
├── README.md      本檔
├── _thumbs/       縮圖快取（.gitignore）
└── output/        匯出 PNG（.gitignore）
```

## .gitignore 排除（已設定）

`*.mp4`、`_thumbs/`、`output/` 皆已 ignore，**只 commit 程式碼**。

## 已知差異 vs 原版

- 原版 `__pycache__` 顯示模組名與 API 一致；端點 / 參數 / 輸出檔名格式皆比對 .pyc 字串還原
- 若有微妙不同（如 UI 樣式），可隨時修
