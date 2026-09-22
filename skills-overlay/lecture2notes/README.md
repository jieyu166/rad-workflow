# lecture2notes overlay

## 部署驗證

- 日期：2026-09-22
- lecture2notes 版本：`lecture2notes 0.2.1`（`l2n --version`）
- Python 版本：`Python 3.14.3`（系統 Python，editable 安裝）
- 驗證方式：在 repo 外暫存目錄以 submodule 內建 CC BY fixture
  `vendor/lecture2notes/tests/fixtures/media/copyrightx-12-1-clip.mp4`（複製為 `clip.mp4`）
  跑完整流程（transcribe → check transcribe → frames → check frames →
  scaffold → check json → render → check note → profile show → run --preflight）；
  全程未帶 `--style`，用以驗證 overlay 的 faithful 是否自動生效。

### 各階段 exit code

| 階段 | 指令 | exit code | 備註 |
|---|---|---|---|
| 1 | `l2n transcribe clip.mp4 --lang en --engine faster_whisper --model tiny` | 0 | 偵測語言 en，2 條字幕 |
| 2 | `l2n check transcribe clip.srt` | 0 | 0 errors / 0 warnings |
| 3 | `l2n frames clip.mp4 --mode interval --every 5` | 0 | warn：1 個取樣點無畫面（片長短，非異常） |
| 4 | `l2n check frames clip.frames.json` | 0 | 0 errors / 0 warnings |
| 5 | `l2n scaffold clip.srt --segments 2` | 0 | 產出 clip.json 已自動併入 clip.frames.json 的影格，未另外執行合併步驟 |
| 6 | `l2n check json clip.json` | 1 | 2 warnings（draft 欄位未填、summary 過短）——預期內，因未做 LLM 擴寫 |
| 7 | `l2n render clip.json`（未帶 `--style`） | 0 | 輸出訊息：`render -> clip.v4.md (style faithful, profile radiology)` |
| 8 | `l2n check note clip.json --note clip.v4.md` | 2 | 2 errors（R6 faithful 缺引用）+ 3 warnings（R10 未擴寫骨架）——預期內，同上原因 |
| 9 | `l2n profile show --json` | 0 | 用以核對 overlay 來源與對照表條數 |
| 10 | `l2n run --preflight clip.mp4 --lang en` | 0 | 列出含 `clip.pbf (new)` |

### 斷言結果

- (a) `clip.v4.md` frontmatter 含 `noteVer` 與 `消化層級`：**PASS**——frontmatter 內為 `noteVer: v4`、`消化層級: 1`
- (b) 筆記含 faithful 樣式標記：**PASS**——內文第一行為 `<!-- l2n:style=faithful guideline=1.3 -->`
- (c) `profile show --json` 中 `profile`／`note.style`／`pbf` 三鍵 source 為 user：**PASS**——`profile=radiology(user)`、`note.style=faithful(user)`、`pbf=true(user)`
- (d) 對照表條數＝186（overlay）＋radiology profile 內建條數：**PASS，實算 186 + 42 = 228**
  - overlay（`~/.lecture2notes/corrections.json`）：deterministic 179 + context_sensitive 7 = 186（與 `profile show --json` 內 source=user 的條目加總 186 一致）
  - radiology profile 內建（`vendor/lecture2notes/src/lecture2notes/profiles/radiology/corrections.json`）：radiology 40 + context_sensitive 2 = 42（與 `profile show --json` 內 source=profile 的條目加總 42 一致）
  - 另有套件本身通用 builtin 30 + 3 = 33 條，不計入本項加總（不屬 overlay 也不屬 radiology profile）
- (e) 模板為 radiology 版（含閱片 callout 章節）：**PASS**——`clip.v4.md` 含「# 閱片」章節與 `> [!reading-case]`、`> [!reading-pearl]`、`> [!differential]` 三個 callout
- (f) pbf 在 `l2n run --preflight clip.mp4 --lang en` 清單中出現：**PASS**——清單含 `run create clip.pbf (new)`

### 產物保留位置

驗證產物保留於暫存工作目錄（未 commit 進 repo）：
`C:\Users\jai16\AppData\Local\Temp\claude\C--Users-jai16-OneDrive-00-----5---rad-workflow-main\7dfccd5b-6c07-43ad-b120-8772012717ea\scratchpad\adopt\verify31\`
（含 clip.mp4、clip.srt、clip.frames.json、clip.json、clip.v4.md、各階段 log、profile.json 等）
