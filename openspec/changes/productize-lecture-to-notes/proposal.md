## Why

影片→字幕→分段→截圖→viewer→筆記這條管線目前拆在三個 skill（lecture-to-notes、whisper-srt-zh、obsidian-v4-cleanup）裡，本機有 29 份副本、12 個版本在漂移（Codex 讀到的 whisper-srt-zh 停在 7 月），而且只能靠 agent 驅動、沒有測試、沒有安裝方式，別人裝不起來；同時筆記品質完全取決於執行的 LLM——同一份逐字稿由 Codex 產出的筆記把 ASR 原句直接倒進 Summary、術語錯字未校正（vault 內 300 份非放射科筆記多屬此類），而本 session 用同一流程產出的 15 份筆記品質高得多，差別只在「撰寫方法有沒有被寫下來」。現在把它收斂成一個可安裝、可測試、有撰寫規範的獨立產品，發布到公開 repo，並讓本機各家 agent 都指向同一份新版。

## What Changes

- 新建 public GitHub repo lecture2notes（MIT），一套程式碼、兩個發行面：公開通用版，以及留在 rad-workflow 的 private overlay（使用者的 V4 YAML、PotPlayer pbf、Obsidian canvas、個人 corrections）。公開版不含這些。
- 合併三個 skill 為**一個** agent skill（單一 SKILL.md 路由 + references），同時提供不依賴 agent 的 pip 可安裝 CLI（console entry point），可跑完轉錄→分段骨架→截圖→OCR→viewer→骨架筆記；LLM 才能做的分段與擴寫由 skill 指引。
- 轉錄引擎：預設 Breeze-ASR-25（使用者自行以 ct2 轉檔，附轉檔腳本）、faster-whisper 官方模型選配、無 NVIDIA 時可用 CPU 或 whisper.cpp；保留 --engine 擴充點但**預設不接任何雲端**。--lang 無預設值維持不變。
- 新增「官方字幕時間校正」：以短段 ASR 探針量測 VTT/SRT 偏移（多點取中位數、cue 內插補），線性校正時間碼、不改文字。
- 截圖新增固定間隔取樣模式（場景偵測在 PACS／螢幕錄影失效時的替代），並移植 staging 式候選影格策展。
- 正式 JSON schema 升級並定版：加 schema_version、每則 bullet 可選時間碼、講者原話與整理內容分欄、frame 與 OCR 為一等欄位；提供 legacy 正規化與驗證器。
- 筆記兩層：從 JSON 決定性 render 的骨架筆記（保證 CLI 模式有交付物）＋ LLM 擴寫的完整筆記（預設）；style 可選 faithful｜concise，使用者預設 faithful；筆記結構固定為 Evergreen／Summary／Note／References／題目／學習驗證；frontmatter 由 profile 與 overlay 決定。
- profiles/generic 為預設（對標財經、生產力、書籍類講座），profiles/radiology 可選（閱片 callout、放射術語對照表）；overlay 解析順序為 專案 > 使用者家目錄 > profile > 內建。
- 新增「筆記撰寫規範」為產品的一部分：來源優先序、原話引用政策、不確定術語一律進 References 對照表並註明未寫入、學員／病例不寫姓名、講者能力邊界照錄、禁止逐字稿原句直接當 bullet、ASR 錯字→正確術語對照表格式。目標是讓 Codex 等其他 LLM 依規範產出同等品質。
- 固化本 session 的 scratchpad 程序為正式腳本：VTT 偏移量測與校正、固定間隔取樣、逐字稿每分鐘壓縮、對照表格式、課程首頁 _titles.json 覆寫、分段 JSON 建構器。
- check_lecture.py 升級為**階段驗收合約**：每階段產出做 schema 驗證，失敗即停；移植結構化 audit、rebuild preflight 與交易式發布（manifest + 整場 rollback）。
- 全部長跑腳本補 cp950 安全的進度回饋。
- 提供 install.py，把 skill 部署到 Claude（~/.claude/skills）、Codex（~/.agents/skills）、OpenCode 三家目錄，取代 rad-workflow 的 sync_skills.py 對這三個 skill 的散佈。
- 測試：腳本層單元測試＋一支 CC 授權公開演講的 30 秒 fixture 跑 end-to-end；LLM 步驟只測驗收規則。無可公開的自有影片。
- corrections.json 去除源自 ZeroType USER.md 的內容，只保留使用者自寫項目；README 明寫隱私邊界（本機 ASR 不上傳；LLM 步驟會把逐字稿送給模型供應商）。
- 本專案部分程式碼修改自上游 drpwchen/lecture-to-notes（MIT）：以逐檔比對產出 ATTRIBUTION.md，保留上游著作權聲明於 NOTICE 與衍生檔檔頭，README 致謝段連結上游並說明差異。
- **BREAKING**：舊 JSON（無 schema_version）需經正規化才被新驗證器接受；三個舊 skill 名稱停用，改由單一 skill 路由。

## Non-Goals (optional)

（留給 design.md 的 Goals/Non-Goals。）

## Capabilities

### New Capabilities

- `lecture-pipeline-cli`: pip 可安裝的端到端 CLI 與階段化子命令（transcribe／frames／ocr／segment-scaffold／render／viewer／pbf／hub），含進度回饋、Windows 優先的路徑與編碼行為。
- `transcription-engines`: 引擎選擇（Breeze-ASR-25 CT2 預設、faster-whisper 官方模型、whisper.cpp CPU）、--lang 強制、raw.srt 與 corrections sidecar、官方字幕時間偏移量測與校正。
- `lecture-json-schema`: 定版的 canonical JSON schema（schema_version）、legacy 正規化、驗證器、UTF-8 無 BOM 原子寫入。
- `frame-capture`: 場景偵測與固定間隔取樣兩種抓圖模式、相鄰去重、staging 候選影格策展、OCR 併入。
- `note-generation`: 骨架筆記決定性 render、LLM 擴寫入口、style 選項、固定章節結構、frontmatter 由 profile／overlay 決定。
- `note-writing-guideline`: 供 LLM 執行的筆記撰寫規範（來源優先序、引用政策、不確定處理、隱私、反例），以及對產出的可檢查規則。
- `derived-outputs`: 雙向同步 viewer、PotPlayer pbf（overlay 才啟用）、課程首頁與跨場搜尋索引、_titles.json 覆寫。
- `stage-acceptance`: 每階段驗收合約、fail-stop audit、rebuild preflight、交易式發布與 rollback。
- `profiles-and-overlay`: generic／radiology profile、private overlay 的解析順序與可覆寫項目（模板、對照表、frontmatter、輸出開關）。
- `agent-skill-packaging`: 單一 SKILL.md 路由與 references 結構、install.py 三家部署、與 CLI 的分工。

### Modified Capabilities

（無既有 spec。）

## Impact

- Affected specs: 上列十項全為新建。
- Affected code:
  - New（位於新 repo lecture2notes，不在本專案內；主要路徑以純文字列出）: pyproject.toml；src/lecture2notes/ 下的 cli、engines、schema、frames、notes、outputs、acceptance、profiles 子套件；skill/SKILL.md 與 skill/references/；profiles/generic 與 profiles/radiology；install.py；tests/ 與 tests/fixtures/；README.md、LICENSE、docs/note-writing-guideline.md。
  - Source（本專案內，唯讀移植來源）: `skills/lecture-to-notes/`、`skills/whisper-srt-zh/`、`skills/obsidian-v4-cleanup/references/task1-v4.md`、`skills/obsidian-v4-cleanup/references/task2-footnotes.md`、`skills/obsidian-v4-cleanup/references/task3-callouts.md`，以及分支 codex/rebuild-nr-viewer 下 `.worktrees/rebuild-nr-viewer/skills/lecture-to-notes/scripts/` 的 render_v4_note、lecture_audit、publish_transaction、rebuild_course、frame_curator、rewrite_lecture、lecture_model、lecture_content_rules。
  - Modified（本專案）: 無。rad-workflow 改為 submodule 引用、清除 29 份舊副本、退休 `sync_skills.py` 對這三個 skill 的散佈，另立後續 change adopt-lecture2notes-submodule 處理，不在本 change。
  - Removed: 無。
- 相依：ffmpeg／ffprobe（PATH）、faster-whisper + CTranslate2、rapidocr-onnxruntime、opencc-python-reimplemented、scenedetect（選配）、opencv-python、pypdf、whisper.cpp 二進位（選配）；Node 的 defuddle CLI 降為選配。
- 使用者資料：測試 fixture 只用 CC 授權公開素材；任何院內、付費或個人影片與其產物不進 Git。
