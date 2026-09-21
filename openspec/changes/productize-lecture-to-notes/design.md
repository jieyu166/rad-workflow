## Context

現況是三個 skill 各自演化：`skills/lecture-to-notes/`（42 行路由 + 4 個 references + 12 支腳本）、`skills/whisper-srt-zh/`（轉錄與對照表校正）、`skills/obsidian-v4-cleanup/`（V4 格式、腳註、閱片 callout、PDF 深讀、新知查核）。本機共 29 份副本、12 個版本；`~/.agents/skills/whisper-srt-zh` 停在 7 月版，Radiology vault 內還有 778 行單體舊版。分支 codex/rebuild-nr-viewer 另有 6 支從未進 main 的腳本（frame_curator、lecture_audit、publish_transaction、rebuild_course、render_v4_note、rewrite_lecture）與兩個共用模組（lecture_model、lecture_content_rules），設計嚴謹但只針對 NR 課程一次性使用。

本 session 以現行流程完成 15 份講座筆記（增生 MRI 五場、izaax 一場、Will 保哥三場），過程中在 scratchpad 累積了六個未固化的程序：官方 VTT 偏移量測（offset3）、線性校正（vtt_fix）、PACS 固定間隔取樣（pacs_frames）、逐字稿每分鐘壓縮、分段 JSON 建構器（mkseg3）、課程首頁 `_titles.json` 覆寫。這些每次 session 結束就消失，下一次要重寫。

品質差距的證據：vault 內 `2. Areas/投資理財/Jenny/` 的 v4.1 筆記由較早的模型與流程產出，Summary 與 Note 的 bullet 是逐字稿原句直接貼入、ASR 錯字（揮達、木迪、到窮）未校正、Evergreen 是截斷的原話；同一流程在本 session 產出的筆記則有來源優先序、對照表、不確定項標註。差別不在模型能力上限，在於撰寫方法沒有被寫成規範。這批影片的原檔在本機 Downloads 的 YT 資料夾，可依日期對回筆記，用來做前後對照。

使用者決策（已確認）：兩者都要（agent skill + 純 CLI）；一個大 skill 帶路由；通用版優先對標財經、生產力、書籍類講座，放射科為可選 profile；使用者自己的 YAML、pbf、canvas、個人 corrections 放 private overlay 留在 rad-workflow；預設 LLM 擴寫、骨架為保底；style 預設 faithful；引擎為 Breeze-ASR-25 預設，faster-whisper、whisper.cpp、Qwen3-ASR 可選，CPU 可跑；Windows 優先；MIT；無可公開影片；README 明寫隱私邊界；測試為單元 + 30 秒 fixture E2E；全部長跑腳本補進度；把撰寫方法寫成規範讓其他 LLM 追平品質。

## Goals / Non-Goals

**Goals:**

- 一套程式碼、兩個發行面：public repo lecture2notes 是通用版；使用者專屬內容以 overlay 疊加，程式碼不分岔。
- 不靠 agent 也能跑完機械階段（轉錄、字幕校正、抓圖、OCR、骨架筆記、viewer、首頁）；LLM 階段（分段、擴寫）有明確的輸入輸出合約與撰寫規範。
- 正式 JSON 是唯一真實來源，所有衍生物（筆記、viewer、pbf、首頁）由它同源產生。
- 每個階段有驗收合約，失敗即停、可回滾。
- 本機三家 agent（Claude、Codex、OpenCode）安裝後讀到同一版本。

**Non-Goals:**

- 不在本 change 內修改 rad-workflow 的 `sync_skills.py`、不刪除本機 29 份舊副本、不把 rad-workflow 改成 submodule 引用——這三件事屬後續 change adopt-lecture2notes-submodule。
- 不實作雲端 ASR；只保留引擎擴充點與雲端閘門。
- 不把 obsidian-v4-cleanup 的 Task 5（PDF 深讀）與 Task 8（新知查核）納入核心；它們維持在 rad-workflow，未來以「附加模組」形式評估。
- 不做 Obsidian canvas 產生器；canvas 屬 overlay 的既有工具。
- 不重做 viewer 的前端架構；沿用現有單檔 HTML，只改為由 schema v2 產生。
- 不把任何院內、付費或個人影片與其產物放進 Git；不把 NAS 路徑寫進程式碼。
- 不承諾 Linux／macOS 全功能；只保證 pure-Python 階段可跑，GPU 引擎為盡力支援。

## Decisions

### 單一程式碼庫、公開版與 overlay 分層

**決定**：只有一份程式碼（public repo）。使用者專屬的東西（V4 YAML frontmatter、pbf 輸出、個人 corrections、faithful 預設）全部以 overlay 檔案表達，放在 rad-workflow 的 `skills-overlay/lecture2notes/`，執行時由解析順序疊加。程式碼裡沒有任何「使用者專屬」分支。

**替代方案**：(a) 兩個 repo 各一份程式碼——會分岔，正是現在的問題；(b) 把使用者內容做成 radiology profile——錯誤歸類，YAML 與 pbf 是「使用者」不是「放射科」。

### 套件結構與 CLI 階段化子命令

**決定**：Python 套件 `lecture2notes`，`pyproject.toml` 定義 console script `l2n`。子命令對應階段：`transcribe`、`calibrate-subs`、`frames`、`ocr`、`scaffold`、`render`、`viewer`、`pbf`、`hub`、`check`、`migrate`、`run`（串接機械階段）、`publish`（交易式發布）、`convert-model`、`profile`、`install-skill`。每個子命令可獨立重跑、冪等（已有產物即跳過，`--force` 重做）。所有子命令輸出 cp950 安全字元（ASCII 標記）。

**替代方案**：單一 `l2n video.mp4` 一鍵到底——LLM 階段做不到無人化，且無法從中間階段續跑；保留 `run` 只串機械階段。

### JSON schema v2 與 legacy 正規化

**決定**：正式 JSON 頂層加 `schema_version: "2.0"`、`source`（影片、字幕來源與偏移模型）、`profile`、`corrections`、`unverified_terms`；段落內 `bullets_zh` 由字串陣列升級為物件陣列 `{text, t, kind}`（`t` 可為 null，`kind` 為 synthesis 或 quote），新增 `quotes_zh`（講者原話，含時間碼）與 `editorial_notes_zh`。提供 `normalize_legacy()`：無 `schema_version` 的舊檔視為 1.x，字串 bullet 轉為 `{text, t: null, kind: "synthesis"}`，其餘欄位補預設；驗證器只接受 2.0。寫入一律 UTF-8 無 BOM、原子替換（先寫 tmp 再 rename）。

**替代方案**：保留字串 bullet 以維持相容——viewer 的摘要層時間碼永遠只能內插推估；升級後可逐條標時。

### 轉錄引擎抽象、Qwen3-ASR 與官方字幕偏移校正

**決定**：`engines/` 定義 `Engine.transcribe(wav, lang) -> list[Cue]` 介面與引擎中繼資料（名稱、是否本機、是否需要 GPU、是否自帶時間戳）。四個本機實作：`breeze_ct2`（預設；使用者先跑 `l2n convert-model` 產生 CT2 權重）、`faster_whisper`（官方模型，零設定替代）、`whisper_cpp`（呼叫二進位，CPU 可跑）、`qwen3_asr`（以 qwen-asr 套件載入 Qwen3-ASR-0.6B 或 1.7B 開源權重，transformers 後端為預設、vLLM 為選配，使用其時間戳預測產生 cue）。`--lang` 無預設，缺少即 exit 2；Qwen3-ASR 雖有語言辨識，本工具仍要求使用者指定，維持 HARD RULE 1。`--engine` 為擴充點；任何標記為非本機的引擎（套件內不提供）必須加 `--allow-cloud` 才能執行，否則 exit 2。

新增 `calibrate-subs`：輸入影片與官方字幕（VTT／SRT），在 3 個以上時間點各抽 90 秒做 ASR 探針，對每個探針 cue 在字幕全文做最長共同子串比對、在命中的字幕 cue 內依字元比例內插，每探針取中位數；以最小平方擬合 `offset(t) = a + b·t`，輸出校正後 SRT（只改時間碼、不改文字、零長度 cue 保底 0.3 秒）與偏移報告。原始字幕保留為 `*.official.srt`。

**替代方案**：直接全片重跑 ASR——耗時十倍且文字品質低於官方字幕；只做常數平移——本 session 實測 3 小時影片有 2.3 秒漂移，線性擬合才夠；把 Qwen3-ASR 當雲端 API 接——它已有開源權重與本機推論套件，走本機才符合隱私規則。

### 抓圖雙模式與影格策展 staging

**決定**：`frames` 子命令提供 `--mode scene`（PySceneDetect adaptive，退 ffmpeg scene filter）與 `--mode interval --every 45`（固定間隔 + 相鄰灰階差去重，門檻可調）。兩種模式輸出相同 manifest 結構。移植 frame_curator：候選影格先進 `staging/` 目錄，策展（每段 1–4 張、雜湊驗證）後才進正式 `frames/`；正式 JSON 只引用正式影格。

**替代方案**：只有場景偵測——PACS 與螢幕錄影實測抓不到換頁（48 分鐘只得 4–5 張）。

### 兩層筆記產生：骨架 render 與 LLM 擴寫

**決定**：`render` 子命令從 JSON 決定性產出骨架筆記（固定章節：Evergreen／Summary／Note／References／題目／學習驗證；每段含標題、時間碼、summary、bullets、quotes、影格嵌入；References 含 corrections 與 unverified_terms 表），不呼叫任何 LLM。LLM 擴寫由 skill 指引：讀骨架 + 逐字稿 + 講義，依撰寫規範產出完整筆記，寫回同一檔。`--style faithful|concise` 決定骨架的原話引用密度與 LLM 指令；預設值由 profile／overlay 決定（公開版 concise，使用者 overlay 為 faithful）。frontmatter 由 profile／overlay 的 `note.frontmatter.yaml` 模板決定；公開版只輸出 title、date、source、tags。

**替代方案**：只有 LLM 版——CLI 模式沒有交付物；只有骨架——品質不足以取代人工。

### 筆記撰寫規範作為可檢查的合約

**決定**：`docs/note-writing-guideline.md` 為產品的一部分，同時在 skill references 內引用。規範分「LLM 必須遵守」與「機器可檢查」兩層。機器可檢查項由 `check note` 執行：Note 章節內不得有 ≥40 字與逐字稿完全相同、且未以「」或引用區塊標示的句子；`unverified_terms` 內每一項必須出現在 References、且不得出現在 Note 本文；`corrections` 表必須存在且每列有 heard／correct；faithful 風格下每段至少一句標示為原話的引用；不得出現 profile 定義的個資模式。LLM 必須遵守項寫成條列，含反例（以 vault 內財經筆記的失敗樣態為反例，去識別化後引用）。

**替代方案**：只在 SKILL.md 寫 HARD RULES——本 session 證明其他模型讀了規則仍會把原句倒進筆記；必須有機器檢查兜底。

### profile 與 overlay 解析順序

**決定**：解析順序為 CLI 參數 > 專案內 `.lecture2notes/` > 使用者家目錄 `~/.lecture2notes/` > `profiles/<name>/` > 套件內建預設。可覆寫的檔案：`note.frontmatter.yaml`、`note.template.md`、`corrections.json`（合併，後者優先）、`outputs.toml`（pbf、hub、viewer 開關與樣式預設）、`privacy.toml`（個資模式）。`profiles/generic` 內建；`profiles/radiology` 內建但不預設啟用，含閱片 callout 模板與放射術語對照表。`l2n profile show` 印出最終生效值與每一項的來源層。

**替代方案**：環境變數控制——不可版控、不可分享給團隊。

### 階段驗收合約與交易式發布

**決定**：`check` 升級為每階段合約：`check transcribe` 驗 SRT 格式與 raw／corrections sidecar 存在；`check frames` 驗 manifest 與檔案雜湊；`check json` 驗 schema v2、index 連號、時間單調、每段有影格；`check note` 驗撰寫規範機器項與影格引用存在。任一 error 即 exit 2 並停止 `run`。移植 lecture_audit 為結構化 audit 輸出（JSON 報告）；移植 publish_transaction：發布到目標目錄時先寫 manifest、帶時間備份、多檔原子替換、失敗整場 rollback。移植 rebuild_course 的 preflight（唯讀、列出將變更的檔）。rewrite_lecture 只移植其 evidence-bound 的資料結構，不移植 NR 專用的 attestation 雙 digest。

**替代方案**：沿用單一 check_lecture.py——只能事後稽核，不能在階段間擋住壞產物。

### 單一 SKILL.md 路由與 install.py 三家部署

**決定**：repo 內 `skill/SKILL.md`（frontmatter name: lecture2notes）為路由：依「本次工作」表指向 `skill/references/` 下的 transcription、segmentation、frames-and-notes、note-writing、outputs-and-batch、profiles-and-overlay 六份文件；HARD RULES 六條與完成條件保留並更新。`install.py`（同時掛為 `l2n install-skill`）把 `skill/` 複製到目標：`--target claude` → `~/.claude/skills/lecture2notes`、`--target codex` → `~/.agents/skills/lecture2notes`、`--target opencode` → `~/.config/opencode/skills/lecture2notes`，`--dest` 可覆寫、`--all` 三家一次；複製而非 symlink；寫入 `.installed.json`（版本、來源 hash、時間）；`--check` 比對內容 hash 回報 drift（不一致 exit 2）。安裝時不覆蓋目標內既有 overlay 檔。

**替代方案**：symlink——rad-workflow 已有明文禁止；各家對 symlink 支援不一。

### 測試策略與 CC fixture

**決定**：pytest。單元測試涵蓋：schema 驗證與 legacy 正規化、偏移擬合（含合成漂移資料）、interval 去重、SRT／VTT 解析與寫出、profile 解析順序、撰寫規範機器檢查、install.py 部署與 drift、引擎中繼資料與雲端閘門。E2E：一支 ≤30 秒、CC BY 或 CC0 授權的公開演講片段（來源與授權記錄於 `tests/fixtures/README.md`），跑 `run --engine faster_whisper --model tiny` 到骨架筆記，驗證每階段 check 皆 0 error；GPU 相關測試以 marker 標記、無 CUDA 時跳過。LLM 擴寫不測內容，只測其輸出通過 `check note`。

**替代方案**：用使用者影片當 fixture——全部不可公開。

### 進度回饋與 cp950 相容輸出

**決定**：所有可能超過 10 秒的階段（轉錄、抓圖、OCR、首頁索引）每處理一個單位或每 5 秒印一行進度（已完成／總數、已耗時、預估剩餘），格式只用 ASCII 標記。提供 `--quiet` 與 `--json-progress`（每行一個 JSON 事件，供 agent 追蹤）。

### 移植來源與 ZeroType 內容清除

**決定**：`corrections.json` 重建為兩層：套件內 `profiles/generic/corrections.json` 只含通用 AI／開發術語且由本專案自寫；`profiles/radiology/corrections.json` 含放射術語；原 `references/corrections.json` 中標記來源為 ZeroType USER.md 的項目全部不移植。移植腳本時保留原作者註記於檔頭。

**上游標示**：本專案部分程式碼修改自 drpwchen/lecture-to-notes（MIT，2026-09 仍在更新）。依 MIT 條款，凡修改自上游的檔案必須保留其著作權聲明：以來源稽核（逐檔比對本專案與上游 scripts/、SKILL.md、docs/）產出 ATTRIBUTION.md 列出檔案、上游路徑與 commit；NOTICE 收錄上游 LICENSE 著作權行；每個衍生檔檔頭加註 Adapted from 與 commit；README 致謝段連結上游並說明差異。不憑記憶認定哪些檔衍生自上游，一律以比對結果為準。

## Implementation Contract

**可觀察行為**

- `pip install lecture2notes` 後，`l2n --help` 列出全部子命令；`l2n run <video> --lang zh` 依序執行 transcribe → frames → ocr → scaffold → render → viewer，每階段結束印 `[stage] ok` 或 `[stage] error: <原因>` 並在 error 時停止，exit code 2。
- `l2n transcribe <video>` 未給 `--lang` 時印出「--lang is required (zh|en|ja|auto)」並 exit 2；不產生任何檔案。`--engine qwen3_asr` 時使用本機開源權重推論，不發出任何網路請求（首次權重下載除外，且可用 `--model-dir` 指向已下載目錄）。
- `l2n calibrate-subs <video> <subs.vtt>` 產生 `<stem>.srt`（校正後）與 `<stem>.official.srt`（原始），並印偏移報告：每探針點的中位偏移、全距、`offset(t)=a+b*t` 係數。全距 ≥ 1.5 秒時報告標示 drift。
- `l2n frames <video> --mode interval --every 45` 產生 `frames/<stem>-<MMSS>.png` 與 `<stem>.frames.json`；manifest 每筆含 `timestamp_sec`、`frame`、`sha256`。
- `l2n render <stem>.json` 產生 `<stem>.v4.md` 骨架，內容只來自 JSON；同一 JSON 兩次 render 位元組相同。
- `l2n check json <stem>.json` 對缺 `schema_version` 的檔印 `legacy schema detected; run: l2n migrate` 並 exit 2；`l2n migrate <stem>.json` 原地升級並保留 `<stem>.json.bak`。
- `l2n profile show` 印出最終生效設定，每一項標示來源層（cli／project／user／profile／builtin）。
- `l2n install-skill --all` 在三家目錄各建立 `lecture2notes/`，並印每家路徑；`--check` 在任一家內容 hash 不符時 exit 2 並列出差異檔。

**介面與資料形狀**

- 正式 JSON v2 頂層必要鍵：`schema_version`（"2.0"）、`stem`、`title`、`duration_sec`、`source`（`video`、`subtitle.path`、`subtitle.origin` 為 asr 或 official、`subtitle.engine`、`subtitle.lang`、`subtitle.offset_model` 可為 null）、`profile`、`overall_summary_zh`（100–500 字）、`takeaways_zh`（6–12 條）、`segments`、`corrections`（陣列，每筆 `heard`、`correct`、`source`）、`unverified_terms`（字串陣列）。
- `segments[]` 必要鍵：`index`（1 起連號）、`start_sec`、`end_sec`（單調、首尾相接、末段 end 等於 duration 取整）、`start_time`、`end_time`（HH:MM:SS，與秒數一致）、`title`、`summary_zh`、`bullets_zh`（物件陣列，每筆 `text` 必要、`t` 為 float 或 null、`kind` 為 synthesis 或 quote）、`quotes_zh`（物件陣列，`text`、`t`）、`frame`（字串或 null）、`frames`（字串陣列）、`frame_ocr`（物件陣列，`frame`、`text`）、`editorial_notes_zh`（字串陣列）。
- 引擎中繼資料：`name`、`local`（bool）、`needs_gpu`（bool）、`native_timestamps`（bool）、`default_model`。
- SRT 輸出：UTF-8 無 BOM、`\n` 換行、cue 序號連號、時間碼 `HH:MM:SS,mmm`、每 cue 結束時間嚴格大於開始時間。
- 偏移報告 JSON：`probes[]`（`at_sec`、`n_points`、`median_offset`、`min`、`max`）、`fit`（`a`、`b`）、`drift`（bool，全距 ≥ 1.5）。
- 骨架筆記章節順序固定：frontmatter（依模板）→ `# Evergreen Note` → `# Summary` → `# Note (layer 1-3)` → `### References` → `## 題目` → `## 學習驗證`；Note 內每段為 `## <序號>、<標題>`，段內依序為影格嵌入、summary、quotes（「」）、bullets。
- overlay 檔案名固定：`note.frontmatter.yaml`、`note.template.md`、`corrections.json`、`outputs.toml`、`privacy.toml`；不存在即跳過該層。
- `.installed.json`：`version`、`source_sha256`、`installed_at`（ISO 8601）、`target`。

**失敗模式**

- 缺外部相依（ffmpeg、rapidocr、CT2 模型、qwen-asr 套件或權重）：明確訊息指出缺什麼與安裝指令，exit 3；不靜默降級。
- 引擎轉錄產生 ≥30 個連續相同 cue 文字：判定幻覺迴圈，印警告並在 SRT 標記，`check transcribe` 回報 warning（exit 1）。
- 偏移校正比對可靠點不足 3 個：不寫出校正檔，印原因，exit 2。
- `check` 的 warning 不阻擋 `run`（exit 1 續行），error 阻擋（exit 2）。
- overlay 檔格式錯誤：指出檔案與行號，exit 2；不套用部分內容。
- 非本機引擎未加 `--allow-cloud`：exit 2，訊息說明隱私規則。

**驗收條件**

- `pytest` 全綠；E2E fixture 在無 GPU 的 Windows 與 Linux CI 各跑一次通過（GPU 測試跳過）。
- 對本 session 的 9 份既有 JSON（增生 MRI 五場、izaax、Copilot 三場，僅本機、不進 Git）跑 `l2n migrate` 後 `check json` 皆 0 error；`render` 產出的骨架與現有 `.v4.md` 的章節結構一致。
- 對 Copilot 三場的官方 VTT 跑 `calibrate-subs`，量測結果與本 session 手工量測（agent1 +3.14/+2.23/+0.86，agent2 +1.44/+0.80/+0.96，agent3 +1.81/+2.37/+2.66）各點差異在 0.5 秒內。
- 以 `--engine qwen3_asr` 與 `--engine breeze_ct2` 各對 fixture 轉錄一次，兩者皆產出格式合法的 SRT 且通過 `check transcribe`。
- 從本機 Downloads 的 YT 資料夾選一支有對應 Jenny 舊筆記的影片，以新流程與撰寫規範重產筆記，`check note` 0 error；並以人工對照舊筆記，確認舊版的三種失敗樣態（原句倒入、錯字未校、Evergreen 截斷）在新版不再出現。此對照僅在本機執行，結果不進 Git。
- `l2n install-skill --all && l2n install-skill --check` exit 0；改動任一家的 SKILL.md 後 `--check` exit 2。
- 以 Claude Code 與 Codex 各對 fixture 跑一次 skill 擴寫，兩者輸出皆通過 `check note`。
- README 含隱私邊界段落、Windows 優先聲明、MIT LICENSE 存在、`corrections.json` 無 ZeroType 來源項目。

**範圍邊界**

- 範圍內：新 repo 全部內容、install.py、規範文件、測試、對本機既有 JSON 的遷移驗證與 Jenny 筆記重產對照（結果不進 Git）。
- 範圍外：rad-workflow 的 submodule 化、sync_skills.py 修改、29 份舊副本清除、NAS 上任何檔案的變更、Task 5／8、canvas、雲端 ASR 實作、viewer 前端重寫、批次重產 vault 內 300 份舊筆記。

## Risks / Trade-offs

- [Breeze-ASR-25 需使用者自行轉 CT2，安裝門檻高] → `l2n convert-model` 一鍵轉檔並印出磁碟需求；README 提供 faster-whisper 官方模型作為零設定替代。
- [Qwen3-ASR 的 qwen-asr 套件與 transformers 版本耦合，升級易斷] → 引擎為 optional extra（`pip install lecture2notes[qwen]`），版本上界鎖定並在 CI 內以 0.6B 權重跑一次冒煙測試。
- [schema v2 破壞既有 viewer／hub 腳本對字串 bullet 的假設] → 所有衍生腳本改讀 v2；`migrate` 保留 `.bak`；E2E 與本機 9 份 JSON 遷移驗證兜底。
- [撰寫規範的機器檢查誤判合理引用為原句倒入] → 只檢查未以「」或引用區塊標示的 ≥40 字完全相同片段；門檻可在 profile 調整；誤判以 warning 回報。
- [其他 LLM 仍不遵守規範] → 機器檢查擋住最常見失敗；無法保證判斷品質，README 明說。
- [rebuild-nr-viewer 的移植腳本帶有 NR 專用假設] → 只移植資料結構與流程骨幹，逐支加測試；attestation 雙 digest 不移植。
- [overlay 存於 rad-workflow，公開版使用者看不到完整範例] → repo 內提供 `examples/overlay-minimal/` 示範所有可覆寫檔案的格式（內容為假資料）。
- [OneDrive 路徑下的 I/O 極慢] → 所有腳本以顯式路徑操作、不做遞迴掃描；文件建議把工作目錄放在本機磁碟。
- [Windows cp950 主控台] → 輸出只用 ASCII 標記；測試中以 `PYTHONIOENCODING=cp950` 跑一次確認不拋 UnicodeEncodeError。
- [fixture 授權] → 只採 CC BY 或 CC0，來源與授權文字記錄於 fixtures README；不採 NC／ND。

## Migration Plan

1. 在 GitHub 建立 public repo lecture2notes（MIT），本機 clone 至 OneDrive 之外的本機磁碟目錄。
2. 依移植來源表複製腳本並重構進套件；先讓既有功能在新結構下跑通（v0.1.0），再做 schema v2、Qwen3-ASR 與新功能（v0.2.0）。
3. 對本機 9 份既有 JSON 跑 migrate 與 check、對一支 Jenny 影片重產筆記，作為遷移與品質驗證；結果不進 Git。
4. `l2n install-skill --all` 部署到本機三家；此時舊 skill 仍在，新 skill 同名會遮蔽專案版——這是預期行為，`--check` 用來確認三家讀到同一版。
5. 後續 change adopt-lecture2notes-submodule：rad-workflow 以 submodule 引用、建立 `skills-overlay/lecture2notes/`、修改 sync_skills.py、清除 29 份舊副本與三個 worktree 內的舊版。
6. 回滾：新 repo 打 tag，本機以 `l2n install-skill --dest` 指回舊 skill 目錄即可；正式 JSON 遷移保留 `.bak`。

## Open Questions

- （已決策）名稱定為 lecture2notes：repo、Python 套件、skill name、overlay 目錄（.lecture2notes/）與安裝目標皆用此名，以區隔上游 drpwchen/lecture-to-notes 並在 README 明示衍生關係。CLI 指令維持 l2n。
- fixture 的具體來源：需選定一支 CC BY／CC0 的公開演講並裁 ≤30 秒片段；候選來源為 Wikimedia Commons 的授課影片，選定後記錄於 fixtures README。
- OpenCode 的使用者層 skill 目錄慣例需以其現行文件確認；設計暫定 `~/.config/opencode/skills/`，`--dest` 可覆寫。
- Qwen3-ASR 在 Windows 上的 transformers 後端是否需要額外的 CUDA／torch 版本組合，於實作時以 0.6B 權重實測後寫進 README 的相容表。
- Radiology vault 內 300 份非放射科 v4.1 筆記是否要用新產品重產：不在本 change，但 generic profile 的模板要能容納其既有 frontmatter 欄位（tier、已完成、sourceType）以便日後遷移。
