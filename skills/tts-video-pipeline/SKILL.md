---
name: tts-video-pipeline
description: 已核可的導讀稿 X.script.md 要用 C:\tts 的 BreezyVoice 合成旁白 mp3 並做成投影片影片（含 slides.json 撰寫與核對）時使用；單純 PDF 摘要或剪輯既有影片不適用（後者用 video-use）。
---

# tts-video-pipeline：導讀稿 → BreezyVoice 旁白 → 投影片影片

本技能只管 `C:\tts` 內的兩段：`synth.py`（逐句 TTS 合成 mp3）與 `video\make_video.py`（投影片＋字幕影片）。
安裝、修復、授權細節一律看 `C:\tts\SETUP.md`，不要在這裡重抄。slides.json 欄位全規格看 `C:\tts\video\SLIDES_SPEC.md`。

## 與其他技能的分工

- `pdf-to-tts-zh`：PDF 轉逐頁稿，走 edge-tts、輸出單一 mp3，不經 BreezyVoice、不做影片。本技能不重複它；若只要 edge-tts 有聲書，用它。
- 導讀稿本身（`X.script.md`）的撰寫與數字核對不在本技能範圍；本技能假設稿子已核可。
- 剪輯既有影片素材：用 `video-use`，不要用本技能。

## 前置條件

- Python 一律用 `C:\tts\.venv\Scripts\python.exe`（Python 3.11 venv，勿刪、勿重建；損壞才依 SETUP.md 修復）。
- 不必手動設 `PYTHONUTF8`：`synth.py` 與 `make_video.py` 偵測到未啟用 UTF-8 mode 會自動重啟自己。
- 路徑要短（Windows 260 字元上限）；工作都放在 `C:\tts` 底下。
- 稿件格式：選填 YAML front matter（會略過），`##` 標題＝段落（標題不唸，插 1.2 秒靜音），`[停頓 N 秒]` 轉靜音。注音可寫 `字[:ㄏㄠ3]`，少量使用。
- 開跑前關掉 LM Studio 等其他佔 GPU 的程式。

## 檔案命名與輸出位置

設稿名為 `X`：

| 檔案 | 位置 |
|---|---|
| 導讀稿 `X.script.md`、投影片 spec `X.slides.json`、核對報告 `X.script_verify.md`／`X.slides_verify.md` | `C:\tts\video\` |
| 旁白 mp3 `X.mp3`、逐句 wav 快取 `X_parts\`（含 `_split.json`）、log | `C:\tts\out\` |
| 影片 `X.mp4`、`X.srt`、`X.timeline.tsv`、`X.report.json`、`X_slides\*.png`、`X_720p.mp4` | `C:\tts\video\out\` |

`X_parts\` 是快取，勿手動刪；續跑與改語速都靠它。

## 步驟（依序）

1. **確認稿子**：`C:\tts\video\X.script.md` 已核可；`--dry-run` 先看切句：
   ```bat
   C:\tts\.venv\Scripts\python.exe C:\tts\synth.py C:\tts\video\X.script.md -o C:\tts\out\X.mp3 --dry-run
   ```
2. **合成旁白**（長時間，逐句顯示 `[i/N]` 進度與預估剩餘；實測 RTF 約 1.9–2.0，即約 2 倍稿長時間）：
   ```bat
   C:\tts\.venv\Scripts\python.exe C:\tts\synth.py C:\tts\video\X.script.md -o C:\tts\out\X.mp3
   ```
   可調參數：`--max-chars`（預設 60，實測上限 80，超過 100 字會崩）、`--gap`、`--para-gap`、`--speed`、`--bitrate`、`--splitter`（auto/v1/v2）、`--no-number-normalize`；細節以 `--help` 為準。
   - 中斷後原指令重跑會跳過已完成句子。
   - 只改 `--speed` 重跑不載入模型，數秒內重新合併。
   - 建議背景執行並把輸出導到 `C:\tts\out\X.synth.log`，避免靜默長跑。
3. **列句子索引**（寫 slides.json 的唯一依據；已合成就必須給 `--parts`，舊稿可能是 v1 切句）：
   ```bat
   C:\tts\.venv\Scripts\python.exe C:\tts\video\make_video.py --list-sentences --script C:\tts\video\X.script.md --parts C:\tts\out\X_parts [--tsv]
   ```
4. **撰寫 `X.slides.json`**，嚴守 SLIDES_SPEC.md：
   - 內容只能取自導讀稿或來源筆記，不得補充、推論、換算數字。
   - bullet 每條 ≤ 20 字、表格格子 ≤ 16 字、表格每頁 ≤ 5 列（超過自動分頁）。
   - 每張以 `sentence`（索引）加 `anchor`（6–15 字獨特片段）雙重定位；slides 依句序嚴格遞增。
   - 圖用 `figure.n`（需 `--pdf` 或筆記 frontmatter `rawSource`）或 `figure.image`；流程圖用 `kind: "flowchart"`；自我測驗用 question／answer 兩張（答案頁 `at: "start"`）。
   - 稿子一改，句子索引就變，必須重跑步驟 3。
5. **驗證 spec**（不需音檔）：
   ```bat
   C:\tts\.venv\Scripts\python.exe C:\tts\video\make_video.py --validate --script C:\tts\video\X.script.md --slides C:\tts\video\X.slides.json --parts C:\tts\out\X_parts [--note 筆記.md]
   ```
   要看到 `OK：…` 與每張出場句；`!` 開頭的提醒修到沒有。
6. **先看圖再編碼（建議）**：加 `--render-only`，檢查 `C:\tts\video\out\X_slides\*.png`。
7. **產生影片**：
   ```bat
   C:\tts\.venv\Scripts\python.exe C:\tts\video\make_video.py --script C:\tts\video\X.script.md --parts C:\tts\out\X_parts ^
       --slides C:\tts\video\X.slides.json [--note 筆記.md] [--pdf 原文.pdf] --check --mobile
   ```
   - `--check`：比對影片長度 ＝ mp3 長度 ＋ 總 hold，並抽 5 個時間點核對投影片與字幕。
   - `--mobile`：另輸出 `X_720p.mp4`（手機版）。
   - `--encoder nvenc|x264`（預設 nvenc）、`--sections N`（只做前 N 段短版試片）。
   - `--speed` 必須與合成 mp3 時一致（兩者預設皆 1.2；`--audio` 省略時用 `X.mp3`）。
   - 目錄裡另有 `uterine-lms_yt.mp4` 之類的 `_yt` 版本，但 make_video.py 的 argparse 沒有對應旗標，產法未查到；需要時先問使用者，不要猜。
8. **核對報告**：用 fresh-context subagent（不要自己驗自己）產出唯讀核對檔：
   - `X.script_verify.md`：逐項對照來源筆記核稿（數字、門檻、自我測驗答案、措辭忠實度）。
   - `X.slides_verify.md`：逐張看 `X_slides\*.png`，查圖是否正確、表格數字是否與筆記相符、版面（孤字折行等）。
   - 兩者結論為「需修改」時，修稿或 slides 後重做受影響的步驟。改稿會讓句子索引與快取失效，改動範圍要先評估。

## 硬規則

- **VRAM**：`bv_common.py` 預設 `BV_VRAM_FRACTION=0.75`（8 GB 卡）。不設上限曾使 RTF 從 1.9 惡化到 35（溢出到共用 GPU 記憶體）。要調整只用環境變數 `BV_VRAM_FRACTION`，不要拿掉上限。
- **說話人 prompt**：只用 repo 內附 `C:\tts\BreezyVoice\data\example.wav`（搭配 `data\batch_files.csv` 的完整逐字稿）。使用者自己提供聲音才換；不得自行使用他人聲音。
- **語音複製與公開散布**：repo 沒寫明範例語音是誰的聲音、可怎麼用。音檔或影片若要公開散布，先提醒使用者確認這點或改用自己的聲音（見 SETUP.md §1）。個人使用沒問題。
- **不 commit 音檔與影片**（mp3、wav、mp4、srt 產物與 `_parts\`、`_slides\`）。要入版控的只有稿子與 slides.json，且須使用者同意。
- **內容忠實**：投影片與稿子不得放病人可識別資訊；事實限導讀稿與來源筆記。
- **同一失敗最多重試兩輪**：第三次改方法或回報使用者。
- 不改 `C:\tts\BreezyVoice` repo 程式碼；相容層都在 `bv_common.py`。

## 常見症狀（出自 SETUP.md 已知問題，修復細節見該檔）

| 症狀 | 可能原因／處理 |
|---|---|
| 合成速度忽然慢十幾倍 | VRAM 溢出到共用 GPU 記憶體；確認 `BV_VRAM_FRACTION` 沒被拿掉，關掉其他佔 GPU 程式 |
| 某句音訊拉長、幻覺、靜音 | 句子過長（≥ 100 字）或 LLM 取樣不穩；`synth.py` 會依秒/字自動重抽，仍異常就縮短該句或調 `--max-chars` |
| 唸錯字、專有名詞怪 | 自動檢查只抓長度異常；可用 `[:注音]` 少量修正，或粗篩用 `asr_check.py`（whisper-small 回聽算 CER） |
| 日期、電話、分數、縮寫數字讀法不對 | `zh_normalize` 只處理數字、%、mm/cm、範圍、年份；改稿時直接寫成中文讀法 |
| FileNotFoundError／WinError 206 | 路徑太長；改放短路徑 |
| slides 驗證報「找不到 anchor」「sentence 必須在前一張之後」 | 稿子改過或 anchor 被切句拆開；重跑 `--list-sentences` 並對照 SLIDES_SPEC.md §12 |
| 影片長度與 mp3 不符 | 檢查 `--speed` 與合成時是否一致、`--parts` 是否指向同一份快取 |
| 舊稿重跑句子編號變了 | 一定要給 `--parts`，讓 `_split.json`／舊稿自動用 v1 |

## 已知文件不一致（未解）

SETUP.md §5 寫 `--speed` 預設 1.1，但 `synth.py` 與 `make_video.py` 的 argparse 實際預設是 1.2；以程式與 `--help` 為準，且兩階段須一致。
