---
name: lecture-to-notes
description: 演講/課程影片 → 字幕、分段導航 JSON、投影片截圖與 OCR、V4 筆記、雙向同步 viewer、PotPlayer 章節、課程首頁。整個資料夾可批次跑。Trigger：影片整理, 講座整理, 影片轉筆記, 課程筆記, 分段JSON, 字幕導航, SRT分段, 換頁截圖, 投影片OCR, viewer, 同步播放器, 課程首頁, 課程目錄, 批次整理影片, course listing, lecture notes。單純只要字幕不做筆記 → 用 whisper-srt-zh；純文字筆記標準化 → 用 obsidian-v4-cleanup。
---

# lecture-to-notes

一個裝著影片的資料夾進去，可讀的成果出來：校正過的字幕、分段導航 JSON、投影片截圖與
OCR、V4 筆記、影片↔筆記雙向同步的單檔網頁、PotPlayer 章節檔，多場還能串成課程首頁。

重頭工作全在本機（Whisper CUDA、場景偵測、RapidOCR），0 雲端、0 病患資料外流。
LLM 只做兩件機器做不了的事：**切段落**與**寫筆記**。

## HARD RULES

1. ==轉錄前先問語言==。`transcribe.py --lang` 沒有預設值。猜錯時 Whisper 不會報錯，
   而是把帶口音的英文**幻覺成一份流暢通順的中文逐字稿**——讀起來完全正常，錯得看不出來，
   一路污染到分段 JSON 與筆記才會發現。
2. ==逐字稿不自動改寫==。錯字用對照表取代時必留 `*.raw.srt` 與 `*.corrections.json`；
   語境校正由人／LLM 判斷，不做自動套用。
3. ==來源優先序：官方講義 > 投影片截圖（人眼看的）> ASR 逐字稿 > OCR 文字==。
   ASR 常把專有名詞、數字、甚至因果關係聽錯；OCR 會把「分類與追蹤」讀成「分類興追蹦」。
   ==OCR 只用來決定「要不要打開那張圖」，不可直接抄進筆記。==
4. ==`slide_frames.py` 必須前景同步執行==，等它印完「截圖張數＋併入」再繼續。長片場景偵測
   要數分鐘；丟背景後就結束回合會留下「JSON 併好但筆記沒寫」的半成品。委派子代理時要在
   指示中明寫這一點。
5. ==院內／病患相關影片一律本機轉錄==，不得用雲端 ASR。不確定就當作是。
6. 使用者介面文字用繁體中文台灣用語；專有名詞保留英文原文。

## 輸入長什麼樣就走哪條路

| 資料夾裡有 | 怎麼做 |
|---|---|
| 只有影片 | Step 1 轉錄 → Step 2 分段 → Step 3 抓換頁截圖 |
| 影片 + 官方講義（`.pdf`/`.html`/`.md`） | 同上，但**講義是最高真實來源**，用來校正 ASR 與 OCR |
| 影片 + 手動投影片截圖資料夾 | 跳過 Step 3 抓圖，直接用手動那份（畫質/挑選較佳） |
| 只有音檔 | Step 1–2、Step 4 寫「逐段筆記」，沒有投影片層 |
| 已有 `.srt` 與 `.json` | 直接從 Step 3 開始 |
| **整個系列資料夾（多場）** | `batch_course.py` + `build_course_hub.py`，見〈批次〉 |

## Step 1 — 轉錄（whisper-srt-zh）

```bash
python ~/.claude/skills/whisper-srt-zh/scripts/transcribe.py "<影片或資料夾>" --lang zh
```

本機 GPU ASR + 錯字對照表校正，產 `<stem>.srt`（原始留 `<stem>.raw.srt`、
取代紀錄留 `<stem>.corrections.json`）。細節與對照表維護見 whisper-srt-zh。

==預設引擎是 Breeze-ASR-25==（聯發創新基地的台灣口音/中英夾雜模型）。教學講座實測
precision **92.5% vs turbo 的 78.1%**，關鍵在它不會亂拼術語——turbo 把 mammogram
拼成七種變體，那些全要人回頭對講義改。代價是慢十倍（約 1.2 倍實時）。
這條管線的產物要拿去對講義、寫筆記、做跨場搜尋，術語拼錯的代價遠高於等待時間，
所以==走完整管線的講座不要改用 turbo==；只想快速拿字幕才加 `--engine whisper.cpp`。

已經有字幕就跳過這步。

## Step 2 — 分段導航 JSON

把逐字稿切成 8–15 段（長片可多），每段給時間碼、標題、摘要、重點。這步是 LLM 做的，
沒有腳本。

**先找校正依據**，優先序如 HARD RULE 3：
1. 官方講義 `.html` → `defuddle parse "<檔>" --md`；`.md` 直接讀；`.pdf` → `pdftotext`
2. 投影片截圖 → 用 Read 工具逐張看
3. 都沒有 → 靠領域知識，不確定的標「（可能為 XXX）」

<details>
<summary>分段 prompt（可直接用，或交給 API）</summary>

```
你是一位「字幕整理 +（可選）投影片校正」助手。
我會提供：(1) 字幕（VTT 或 SRT，可能有錯字但含時間碼）(2) 投影片/講義內容（可選）

【任務】
1) 自動分段（8–15 段為主，除非影片很長）
   - 以主題轉換/投影片標題為主要分段依據
   - 每段給 start_time/end_time (mm:ss 或 hh:mm:ss)，同時給 start_sec/end_sec
2) 每段輸出：title（像投影片標題，用投影片上的正確術語）、summary_zh（繁中 2–4 句）、
   bullets_zh（繁中 2–6 點，保留英文專有名詞）
3) 全片輸出：overall_summary_zh（100–500 字，長講座寫滿沒關係）、takeaways_zh（6–12 點）

【校正規則】
- 專有名詞若字幕明顯錯字，必須用投影片/講義校正（血管名稱、器材、術式、分類系統）
- 投影片上清楚可見的正確拼寫優先於字幕文字
- 不得腦補字幕沒提到的內容；投影片有但字幕沒講到的，不要硬塞
- 不確定拼字就保留原字幕並加註「（可能為XXX）」
- 中文錯字也要校正（如「方測科」→「放射科」、「送神」→「送審」）

【只輸出 JSON，不要輸出其他文字】
```
</details>

### JSON schema

```json
{
  "overall_summary_zh": "100-500字繁中整體摘要",
  "takeaways_zh": ["結論/可應用原則 1", "...最多12點"],
  "segments": [{
    "index": 1, "start_time": "mm:ss", "end_time": "mm:ss",
    "start_sec": 0, "end_sec": 62,
    "title": "段落標題", "summary_zh": "繁中2-4句", "bullets_zh": ["重點1", "重點2"],
    "frame": "frames/<stem>-MMSS.png",
    "frames": ["frames/<stem>-MMSS.png"],
    "frame_ocr": [{"frame": "frames/<stem>-MMSS.png", "text": "投影片上的文字…"}]
  }],
  "ocr_meta": {"engine": "rapidocr-onnxruntime", "frames_total": 0}
}
```

`frame`/`frames` 由 Step 3 的 `slide_frames.py` 填、`frame_ocr`/`ocr_meta` 由
`ocr_frames.py` 填。存成 `<stem>.json`，UTF-8 **不得有 BOM**（web player 會解析失敗）。

## Step 3 — 換頁截圖 + OCR

```bash
python <skill>/scripts/slide_frames.py "<影片>" --json "<stem>.json" --width 1280
python <skill>/scripts/ocr_frames.py "<stem>.json"
```

- `slide_frames.py`：PySceneDetect adaptive（無則退 ffmpeg scene filter）抓「真正換頁」
  那張存到 `frames/<stem>-MMSS.png`，把 `frame`/`frames` 併回 JSON，另產
  `<stem>.frames.json` manifest。==前景同步，見 HARD RULE 4。==
- `ocr_frames.py`：每張 OCR 一次（RapidOCR，CPU，約 0.5 s/張），文字併進 `frame_ocr`，
  快取在 `<stem>.frames_ocr.json`（size+mtime 指紋，重跑只補新圖）。需要
  `pip install rapidocr-onnxruntime`，缺套件直接 exit 3 不默默略過。

**OCR 是這條管線最划算的一步**：實測乳攝講座中 `Architectural Distortion`、`vacuum`
只出現在投影片上、逐字稿完全沒有——沒有這層就永遠搜不到。但它也把「處置」讀成「鬣置」，
所以只當定位線索（HARD RULE 3）。

## Step 4 — 寫 V4 筆記

1. 讀齊素材：**官方講義（最高）→ `frame_ocr` → 需要細看的截圖 → 逐字稿**
2. ==讀圖策略==：有 `frame_ocr` 時**先讀 OCR 決定哪幾張值得開**，不要整批 Read 圖——
   長片 100+ 張時這是最大的一筆浪費。需要開圖的情況：表格、分類標準、影像（CT/MRI/US）、
   OCR 明顯亂掉、以及任何要寫進筆記的數值與術語。
3. 產出 `<stem>.v4.md`：

```markdown
---
(V4 YAML — source 放講者/課程名)
---
Topics :: [[相關主題]] <br>
Parent Link :: [[=索引頁]] <br>

---
# Evergreen Note
「**一句話核心觀念**」

# Summary
- **重點1**
- 易混淆觀念：...

# Note (layer 1-3)
## 小標題
（內容；比較用表格。多講者時標 **(講師A觀點)**）
![[frames/<stem>-MMSS.png]]

### 參考來源
[^1]: 出處

## 題目
Q: / A:

## 閱片
（如適用）
```

規則：繁體中文、專有名詞保留英文；**不可自行編造**，所有內容須來自素材；講者的經驗與洞見
也要記；每個主要段落至少嵌一張相關截圖；至少做一項學習驗證（費曼輸出／應用情境／行動清單／
知識連結／自我測驗）。

> **草稿豁免**：這是機器轉錄＋合成的產物，直接寫進 inbox，不必先給草稿——使用者在
> Obsidian 裡審閱。

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

## 一條龍（單場，含絕對路徑）

```bash
SK="C:/Users/jai16/OneDrive/00 放射科/5工作/rad-workflow-main/skills/lecture-to-notes/scripts"
cd "<影片資料夾>"
python "C:/Users/jai16/.claude/skills/whisper-srt-zh/scripts/transcribe.py" "<影片.mp4>" --lang zh
defuddle parse "<講義.html>" -m > _ref.md          # 講義轉文字當 ground truth
#   由 SRT + _ref.md 建分段 JSON（Step 2）→ 寫 "<stem>.json"
python "$SK/slide_frames.py" "<影片.mp4>" --json "<stem>.json" --width 1280   # 前景同步！
python "$SK/ocr_frames.py"   "<stem>.json"
python "$SK/json_to_pbf.py"  "<stem>.json"
#   寫 V4 筆記（Step 4）→ "<stem>.v4.md"
python "$SK/build_lecture_viewer.py" "<stem>.json"
python "$SK/check_lecture.py" "<stem>.json" --note "<stem>.v4.md"
rm -f _ref.md
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
