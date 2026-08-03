---
name: whisper-srt-zh
description: 用本機 GPU Whisper（PotPlayer CUDA + ggml-large-v3-turbo）把影片/音檔批次轉成繁體中文字幕，並自動套用 ASR 錯字對照表校正。全本機、用 CUDA、不需網路不上傳雲端，適合院內/病患或大量本機講座影片。Use when 把影片轉字幕/逐字稿、批次產生 SRT、本機 whisper 轉錄、影片轉文字、字幕錯字修正、transcribe video/audio to Chinese SRT。取代手動 bat 批次轉檔；產物直接接 lecture-to-notes（分段 JSON／截圖／筆記／viewer）。
---

# whisper-srt-zh

把本機影片/音檔批次轉成繁中字幕（SRT/逐字稿），再用對照表校正常見 ASR 錯字。**全本機、GPU（CUDA）、零雲端**。

## 何時用

- 「把這資料夾的影片轉字幕 / 逐字稿」「批次產 SRT」「本機 whisper 轉錄」
- 已有影片想要字幕，但**不想上傳雲端**（院內錄影、病患相關、大量講座）
- 轉完想**修正 ASR 錯字**（保哥、Markdown、Claude、放射科術語…）
- 產出的 `.srt` 直接接 `lecture-to-notes`（分段導航 JSON → 截圖/OCR → 筆記 → viewer）

## 需求（本機，已隨使用者環境設定）

| 工具 | 用途 | 預設路徑（可用 env/CLI 覆寫）|
|------|------|------|
| Whisper CUDA `main.exe` | GPU 辨識 | `C:\Program Files\DAUM\PotPlayer\Module\Whisper\CUDA\main.exe` |
| 模型 `ggml-large-v3-turbo.bin` | 辨識模型 | `C:\Users\jai16\AppData\Roaming\PotPlayerMini64\Model\ggml-large-v3-turbo.bin` |
| `ffmpeg` | 轉 16kHz mono wav | PATH 優先，退 FormatFactory 版 |

覆寫：`--whisper / --model / --ffmpeg`，或環境變數 `WHISPER_SRT_BIN / WHISPER_SRT_MODEL / WHISPER_SRT_FFMPEG`。

## 流程（一鍵）

```bash
# 整個資料夾（取代 bat.bat）
python scripts/transcribe.py "<資料夾>" --lang zh

# 單檔
python scripts/transcribe.py "<影片.mp4>" --lang en

# 已存在 .srt 也重跑 / 不做錯字修正 / 保留 wav
python scripts/transcribe.py "<dir>" --lang zh --force
python scripts/transcribe.py "<檔>" --lang zh --no-correct
```

每檔流程：`ffmpeg 16kHz mono wav → whisper CUDA -osrt → .srt → correct_srt.py 校正`（已存在 `.srt` 預設跳過）。

### ⚠️ `--lang` 必填，沒有預設值

轉錄階段**忠實記錄講者原本的語言**，翻譯成繁體中文是後續處理的事。腳本沒給 `--lang`
會直接 exit 2 並問你講者說哪種語言（`zh` / `en` / `ja` / `auto`）。

**為什麼不給預設**：拿預設 `zh` 去轉一場英文演講時，Whisper 不會報錯，而是把帶口音的
英文**幻覺成一份流暢通順的中文逐字稿**——讀起來完全正常，錯得看不出來，一路污染到分段
JSON 與 V4 筆記才會發現。多問一句遠比事後重跑整條管線便宜。

`--lang` 非 `zh`/`auto` 時，會自動對 `correct_srt.py` 加 `--no-s2t`：s2twp 對英文是
no-op，但對日文會把漢字轉成台灣用字。

## 錯字修正（兩段式）

### 1) 對照表（deterministic，腳本自動）
`references/corrections.json` 內 `deterministic` + `radiology` 直接取代（長鍵優先）。
來源：使用者 ZeroType `USER.md`（AI/開發領域）+ 放射科補充。校正後覆寫 `.srt`，原始留為 `*.raw.srt`。

```bash
python scripts/correct_srt.py "<檔.srt>"            # 套用並覆寫（備份 .raw.srt + 稽核 sidecar）
python scripts/correct_srt.py "<檔.srt>" --report   # 只看會改哪些、不寫檔
python scripts/correct_srt.py "<檔.srt>" --no-sidecar
```

**稽核 sidecar `<stem>.corrections.json`**：每次實際寫檔會另存一份取代紀錄
（`wrong` / `right` / `count` / `source`，加上 s2t 是否套用、用了哪張對照表、備份檔名）。

自動取代本質上是有風險的操作——正確詞常常根本不在對照表的語境裡，一次錯誤取代會把原始
證據抹掉、事後查不到。`.raw.srt` 告訴你「原本長什麼樣」，sidecar 告訴你「哪一條規則改了
它、改了幾處」，兩者互補才能比對、回溯、回滾。有做 LLM 語境校正時，把該場專屬的
wrong→right 也記進同一份檔案（`source` 標成講義名或 `llm-context`）。

### 2) 語境校正（LLM，由你/Claude 判斷）
`corrections.json` 的 `context_sensitive` 清單**不盲改**（如「以色列→Excel」只在談試算表時才對），由 Claude 讀逐字稿依語境判斷。處理影片時：
- 若同層有**投影片截圖/PDF**，以畫面為準校正英文術語、數值、專有名詞（同 lecture-to-notes Step 2 邏輯）。
- 放射科講座：Lung-RADS / BI-RADS / TI-RADS / emphysema / hydronephrosis 等以截圖或領域知識校正。

> **實務心得（重要）**：固定對照表（第 1 段）對「非 AI/開發、非放射」的一般講座**幾乎 0 命中**（多場實測 0 處）。真正的校正主力是「**對照官方講義/投影片，建立該場專屬 wrong→right 對照、套回 SRT**」：
> 1. 先把講義轉成文字當 ground truth：`.html` 用 `defuddle parse <檔> --md`、`.pdf` 用 pypdf/pdftotext 抽文字存 sidecar。
> 2. 讀 SRT 找反覆出現、被聽錯的**英文術語/人名/書名/專名/同音中文**（例：Plaud Note、Tyrer-Cuzick、BRCA、Lung-RADS、高雄榮總、γνῶθι σεαυτόν）。
> 3. 建立 dict（長鍵優先），對字幕**文字內容**逐一取代，**務必保留序號/時間碼/空行結構與時間軸**（只改文字，不重排不刪行；用 `text.replace("\r","")` 後寫 `newline="\n"`）。
> 4. 數值也要對講義校正（曾見逐字稿把 75% 誤聽成 50%）。中英夾雜屬講者原貌，只修明顯錯字、不要改寫語句。
>
> 注意 ASR 偶發整段亂碼（例「1.2.3.5.5…」）或把中文誤判成英文殘片前綴——依語意與投影片還原並註明。簡體輸出（whisper -l zh 偶發）由 `correct_srt.py` 的 s2twp 轉繁處理。

## 維護對照表

- 直接編 `references/corrections.json`。
- 新錯字歸類：明確且不會誤傷正常詞 → `deterministic`；醫學詞 → `radiology`；同音/可能是正常詞 → `context_sensitive`。
- ZeroType 是即時語音輸入的後處理；本 skill 是「影片批次轉錄」的後處理。兩者對照表可同步增修，概念一致。

## 與其他工具的關係

- **取代** 你資料夾裡手動跑的 `bat.bat`（同一條 ffmpeg+whisper 管線，多了錯字校正與單檔/資料夾彈性）。
- **不使用 yt-dlp**：純本機檔（與 sum-the-yt / claude-video `/watch` 不同，那些是為了從 YouTube 抓檔）。
- **下游接** `lecture-to-notes`：`.srt` → 分段導航 JSON → 換頁截圖 + OCR → V4 筆記 → 雙向同步 viewer / 課程首頁。

## 下游：要做筆記就交給 lecture-to-notes

本 skill 只負責「影片/音檔 → 校正過的 SRT」這一件事。分段導航 JSON、換頁截圖、投影片
OCR、V4 筆記、雙向同步 viewer、PotPlayer 章節、課程首頁——整條下游都在 **`lecture-to-notes`**
skill，那裡有完整的一條龍指令與批次流程。

只要字幕、不做筆記時（大量講座批次轉檔、只想要逐字稿），單獨用本 skill 就夠了。

## 注意

- 校正會覆寫 `.srt`，但保留 `*.raw.srt` 原始檔與 `*.corrections.json` 取代紀錄，可比對/還原。
- **本 skill 的 canonical 在 `rad-workflow/skills/whisper-srt-zh/`（Git 追蹤）**；
  `~/.claude/skills/whisper-srt-zh/` 是同步過去的執行副本。要改一律改 canonical 再覆蓋過去，
  不要兩邊各改各的。
- `context_sensitive` 與 `radiology` 表偏使用者語料，跨領域影片可能需增修。
- GPU 辨識速度依顯卡而定（AMD CPU + NVIDIA 4060 可用 CUDA）。
