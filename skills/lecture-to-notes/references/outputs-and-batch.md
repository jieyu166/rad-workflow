# 路徑約定

`<skill>`／`<lecture-skill>` 是目前載入的 lecture-to-notes 根目錄；`<whisper-skill>` 從技能目錄取得，先確認 `scripts/transcribe.py` 存在。命令中的相對腳本路徑均以相應 skill 根目錄為基準。

## Step 5 — 產出可讀的東西

```bash
python <skill>/scripts/build_lecture_viewer.py "<stem>.json"   # 單檔雙向同步網頁
python <skill>/scripts/json_to_pbf.py         "<stem>.json"    # PotPlayer 章節
python <skill>/scripts/collect_note_images.py "<stem>.v4.md"   # 挑筆記用到的圖 → images/
python <skill>/scripts/check_lecture.py       "<stem>.json" --note "<stem>.v4.md"
```

- **viewer**：摘要層與逐字稿層並排，播放時**兩層同時**高亮跟隨，點任一行／段落卡片／
  投影片 OCR 都跳播；三閱讀模式、跨層全文搜尋、浮動播放器、字級縮放。影片與截圖走相對
  路徑，把 html 跟影片放同層即可離線看。支援 `?t=<秒>` 深連結。
  ==摘要層時間碼是段落內插補的推估值（標 `~`）==，因為 bullets 沒有各自的時間碼；
  逐字稿層與投影片層才是真實時間。
- **`.pbf`**：主檔名必須與影片同名，腳本會自動對齊；PotPlayer 開影片時自動載入。
- **`collect_note_images.py`**：==改名場次後才能跑==，否則挑出的檔名與筆記引用對不上。
- **`check_lecture.py`**：機械稽核（必要 key、index 連號、時間碼單調不重疊、
  `start_time` 與 `start_sec` 一致、每段有圖、圖與筆記引用實際存在、無 BOM）。
  離開碼 0 全過／1 只有警告／2 有錯。==改名或重跑 slide_frames 後務必再跑一次。==

## 批次：整個課程資料夾

```bash
python <skill>/scripts/batch_course.py    "<課程資料夾>"     # 截圖→OCR→viewer→稽核
python <skill>/scripts/build_course_hub.py "<課程資料夾>"    # 十場串成一頁課程首頁
```

- `batch_course.py` ==可重跑==：已有截圖的跳過抓圖、已有 OCR 的跳過 OCR，中斷後再跑一次
  即可。`--only 09` 只跑一場、`--force-frames` 重抓、`--skip-ocr` 只要圖與 viewer。
  它**不做**轉錄與分段——那兩步要人決定語言與段落切點，開跑前每場都要先有
  `<stem>.json` + 同名影片 + 字幕。
- `build_course_hub.py` 產 `課程首頁.html`：每場一張卡片（講者、題目、時長、段數、
  投影片數、縮圖、一句摘要），加上**跨場搜尋**——把所有場次的段落標題、摘要、投影片 OCR
  建成索引，搜尋結果直接帶 `?t=` 開到那一場的那個時間點。「哪一場講過 stereotactic」
  只有這裡答得出來。

### 課程系列筆記（Obsidian 版目錄）

要在 vault 裡留一份文字目錄時用這個格式（與 HTML 首頁並存，用途不同）：

```markdown
# 課程名稱(N)
| 主題 | 影片 | 講義 | json |
| ---- | ---- | ---- | ---- |
| [[講者 - 簡短主題]] | [影片](base_url/YYYYMMDD-NN.mp4) | [講義](base_url/YYYYMMDD-NN.pdf) | Y |
```

規則：第一欄用 wikilink `[[講者 - 簡短主題]]`（10–15 字，保留核心關鍵字，不用原始長標題）；
場次**逆時間序**（最新在上）；沒有的檔案欄位留空；`json` 欄追蹤分段 JSON 是否已產生；
有前後年同名課程用 `sibling ::` 互連。媒體檔名慣例 `YYYYMMDD-NN.ext`，
NAS URL `http://jieyu166.synology.me/courses/{課程代碼}/YYYYMMDD-NN.ext`。

## 單場流程範例（依所在 shell 調整）

```bash
SK="<lecture-skill>/scripts"
cd "<影片資料夾>"
python "<whisper-skill>/scripts/transcribe.py" "<影片.mp4>" --lang zh
defuddle parse "<講義.html>" -m > _ref.md          # 講義轉文字當 ground truth
#   由 SRT + _ref.md 建分段 JSON（Step 2）→ 寫 "<stem>.json"
python "$SK/slide_frames.py" "<影片.mp4>" --json "<stem>.json" --width 1280   # 等待完成並核對輸出
python "$SK/ocr_frames.py"   "<stem>.json"
python "$SK/json_to_pbf.py"  "<stem>.json"
#   寫 V4 筆記（Step 4）→ "<stem>.v4.md"
python "$SK/build_lecture_viewer.py" "<stem>.json"
python "$SK/check_lecture.py" "<stem>.json" --note "<stem>.v4.md"
# 完成後可移除本次建立的 _ref.md；先確認目標路徑。
```

## 每場產出的檔案

```
<stem>.srt / .raw.srt / .corrections.json   字幕、原始、取代紀錄
<stem>.json                                 分段導航（frames + frame_ocr 併入）
<stem>.frames.json / .frames_ocr.json       換頁 manifest / OCR 快取
frames/<stem>-MMSS.png                      換頁截圖
<stem>.v4.md                                Obsidian 筆記
<stem>.viewer.html                          雙向同步網頁
<stem>.pbf                                  PotPlayer 章節（主檔名對齊影片）
課程首頁.html                                多場才有
```

## scripts

| 腳本 | 做什麼 |
|---|---|
| `slide_frames.py` | 場景偵測抓換頁截圖，併入 JSON |
| `ocr_frames.py` | 截圖 OCR，併入 `frame_ocr` |
| `build_lecture_viewer.py` | 單檔雙向同步 viewer |
| `json_to_pbf.py` | PotPlayer 章節檔 |
| `collect_note_images.py` | 挑筆記實際引用的圖 → `images/` |
| `check_lecture.py` | 機械稽核（原 `check_task6.py`） |
| `batch_course.py` | 整個資料夾跑完截圖/OCR/viewer/稽核 |
| `build_course_hub.py` | 多場 → 課程首頁 + 跨場搜尋 |

相依：`ffmpeg`/`ffprobe` on PATH、`pip install rapidocr-onnxruntime opencc-python-reimplemented`、
選配 `scenedetect`（無則退 ffmpeg scene filter）、`defuddle` CLI（解析 `.html` 講義）。

## 與其他 skill 的分工

- **whisper-srt-zh** — 上游：影片/音檔 → 校正過的 SRT。只要字幕、不做筆記時單獨用它。
- **obsidian-v4-cleanup** — 平行：純文字筆記的 V4 標準化、PDF 深讀、新知查核。
  本 skill 產出的 `.v4.md` 若要再做引用轉腳註、閱片 callout 等整理，交給它。
