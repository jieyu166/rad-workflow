## 1. Repo 骨架與套件（v0.1.0 起點）

- [x] 1.1 依「單一程式碼庫、公開版與 overlay 分層」在 GitHub 建立 public repo lecture2notes（MIT LICENSE、.gitignore 排除 frames/、*.srt、*.json 樣本以外的媒體），本機 clone 到 OneDrive 之外的磁碟；驗證：`gh repo view jieyu166/lecture2notes --json visibility,licenseInfo` 顯示 PUBLIC 與 MIT
- [x] 1.2 依「套件結構與 CLI 階段化子命令」建立 pyproject.toml 與 src/lecture2notes/ 套件骨架（cli、engines、schema、frames、notes、outputs、acceptance、profiles 子套件），實作「Installable package with a single console entry point」：extras 為 [breeze]、[qwen]、[whispercpp]、[scene]；驗證：乾淨 venv 內 `pip install -e .` 後 `l2n --help` exit 0 且列出 15 個子命令
- [x] 1.3 實作缺相依的統一錯誤路徑：任一子命令缺 ffmpeg／rapidocr／CT2 模型／qwen-asr 時印缺項與安裝指令、不產檔、exit 3；驗證：tests/test_cli_deps.py 以 monkeypatch 移除 PATH 上的 ffmpeg 後斷言 exit 3 與訊息
- [x] 1.4 依「進度回饋與 cp950 相容輸出」實作共用進度器與輸出層，滿足「Console output is cp950-safe and shows progress」：ASCII 標記、每 5 秒一行、`--quiet`、`--json-progress` 每行一個 JSON；驗證：tests/test_progress.py 在 PYTHONIOENCODING=cp950 下跑所有子命令的 --help 與一次假進度不拋 UnicodeEncodeError，且 --json-progress 每行 json.loads 成功並含 stage/done/total/elapsed_sec/eta_sec
- [x] 1.5 實作「Language is mandatory for transcription」：transcribe 與 run 缺 --lang 時印 `--lang is required (zh|en|ja|auto)`、不建檔、exit 2；驗證：tests/test_cli_lang.py 斷言 exit 2 且工作目錄無新檔

## 2. 移植與清理既有腳本

- [x] 2.1 依「移植來源與 ZeroType 內容清除」把 rad-workflow 的 skills/lecture-to-notes/scripts 與 skills/whisper-srt-zh/scripts 移入套件對應模組，檔頭保留原作者註記；驗證：`python -c "import lecture2notes.frames, lecture2notes.engines, lecture2notes.outputs"` 成功，且 `grep -r "ZeroType\|USER.md" src/ profiles/` 無結果
- [x] 2.2 從分支 codex/rebuild-nr-viewer 的 .worktrees/rebuild-nr-viewer/skills/lecture-to-notes/scripts 移植 lecture_model、lecture_content_rules、frame_curator、lecture_audit、publish_transaction、rebuild_course、render_v4_note 的資料結構與流程骨幹到 acceptance 與 notes 子套件，不移植 attestation 雙 digest；驗證：每支移植模組各有一個 tests/test_port_*.py 冒煙測試 import 並呼叫一個純函式
- [x] 2.3 把本 session 的 scratchpad 程序固化為模組：offset3 量測、vtt_fix 校正、pacs_frames 間隔取樣、condense 逐字稿壓縮、mkseg3 建構器、_titles.json 覆寫；驗證：tests/test_ported_procedures.py 對每支以固定輸入斷言固定輸出

## 3. Canonical JSON schema v2

- [x] 3.1 依「JSON schema v2 與 legacy 正規化」實作「Versioned canonical lecture JSON」的 pydantic 或 dataclass 模型與驗證器（頂層與 segments[] 所有必要鍵、100–500 字摘要、6–12 條重點、index 連號、首尾相接、start_time 與秒數一致、bullets 物件化）；驗證：tests/test_schema.py 覆蓋 spec 內 boundary 表五列，`l2n check json` 對合法檔 exit 0、對 1,2,4 索引與時間不接的檔 exit 2 並列出段落索引
- [x] 3.2 實作「Legacy documents are migrated, not silently accepted」：無 schema_version 時 check json 印 `legacy schema detected; run: l2n migrate <file>` 且 exit 2；`l2n migrate` 原地升級並留 .bak，字串 bullet 轉 {text,t:null,kind:"synthesis"}，缺欄位補預設；驗證：tests/test_migrate.py 以 41 段的 legacy 檔跑 migrate 後斷言 .bak 位元組相同、schema_version 為 2.0、段數 41、check json exit 0
- [x] 3.3 實作「Atomic UTF-8 writes without BOM」：tmp 檔同目錄寫入後 rename，UTF-8 無 BOM、二空格縮排、非 ASCII 不轉義；驗證：tests/test_atomic_write.py 在寫入中途注入例外後斷言原檔未變，並斷言檔案前三位元組非 EF BB BF

## 4. 轉錄引擎

- [x] 4.1 依「轉錄引擎抽象、Qwen3-ASR 與官方字幕偏移校正」定義 Engine 介面與中繼資料（name、local、needs_gpu、native_timestamps、default_model），實作「Pluggable local transcription engines」的四個引擎 breeze_ct2、faster_whisper、whisper_cpp、qwen3_asr，並提供 `--list-engines`；驗證：tests/test_engines.py 斷言四個引擎註冊且 local 皆為 true；`l2n transcribe --list-engines` 印四行並標示相依是否滿足
- [ ] 4.2 實作 qwen3_asr 引擎：以 qwen-asr 套件載入 Qwen3-ASR-0.6B 或 1.7B，transformers 後端預設、vLLM 選配、`--model-dir` 指向本機權重、以其時間戳產生 cue；驗證：CI 標記 gpu 的測試以 0.6B 對 fixture 轉錄產出合法 SRT 並通過 check transcribe（無 CUDA 時跳過），README 相容表記錄實測的 torch 版本
- [x] 4.3 實作「Cloud engines are gated」：local=false 的外掛引擎未帶 --allow-cloud 即 exit 2 並說明隱私規則；驗證：tests/test_engine_gate.py 註冊一個假的 local=false 引擎，斷言無旗標 exit 2、有旗標可執行
- [x] 4.4 實作「Model conversion helper for Breeze-ASR-25」：`l2n convert-model` 先印磁碟需求、float16 預設、目標存在時無 --force 拒絕；驗證：tests/test_convert_model.py 以 mock 的 converter 斷言參數與拒絕覆寫行為；手動於本機轉檔一次後 `l2n transcribe --lang zh` 預設引擎可用
- [x] 4.5 實作「Raw transcript and correction sidecar are preserved」：套用對照表時寫 .raw.srt 與 .corrections.json（heard/correct/count/source），校正檔保持序號、時間、空行結構；驗證：tests/test_corrections.py 以含 12 次「口拍的」的 SRT 斷言 sidecar 內容與 raw 檔保留原文、且兩檔 cue 數與時間碼完全相同
- [x] 4.6 實作「Hallucination loop detection」：≥30 個連續相同 cue 文字回報 warning 並標示首尾 cue 編號；驗證：tests/test_hallucination.py 以尾端 71 個「OK」的 SRT 斷言 check transcribe 印 `hallucination loop cues N..M (71 identical)` 且 exit 1
- [x] 4.7 實作「Official subtitle offset calibration」：`l2n calibrate-subs` 依 spec 的探針位置、最長共同子串門檻、cue 內插補、每探針中位數、最小平方擬合、零長度保底 0.3 秒，輸出 .srt、.official.srt、.offset.json；驗證：tests/test_calibrate.py 覆蓋常數偏移、漂移標示（全距 2.28 秒）、合成三點擬合 a≈3.06 與 b≈-0.000196、文字不變（兩檔文字行串接相等）、可靠探針不足 3 個時不寫檔 exit 2

## 5. 抓圖與 OCR

- [x] 5.1 依「抓圖雙模式與影格策展 staging」實作「Two capture modes with one manifest format」：--mode scene（PySceneDetect，缺套件退 ffmpeg scene filter 並印訊息）與 --mode interval --every，輸出 frames/<stem>-<MMSS>.png 與含 sha256 的 manifest；驗證：tests/test_frames.py 以 30 秒 fixture 在兩種模式各產 manifest 並斷言每筆有 timestamp_sec、frame、sha256；以 monkeypatch 使 scenedetect 不可 import 時斷言印出 fallback 訊息
- [x] 5.2 實作「Adjacent-duplicate suppression in interval mode」：64x36 灰階平均絕對差低於 --diff-min（預設 4.0，含等於則保留）即丟棄；驗證：tests/test_dedup.py 以合成影格斷言 3.99 丟、4.00 留、25.3 留，並斷言十張相同畫面只留第一張
- [x] 5.3 實作「Frames are merged into the canonical JSON by time range」：依 [start_sec,end_sec) 指派 frames、frame 取第一張、無則取最近的前一張或首張、原子寫回；驗證：tests/test_frame_merge.py 以段落 1260–1440 與影格 1254、1441 斷言 frames 為空且 frame 為 1254 那張
- [x] 5.4 實作「Staged candidate curation」：--stage 寫入 staging/frames/、--curate 依 --max-per-segment（預設 4）與 sha256 驗證晉升並寫 .curation.json，正式 JSON 只引用晉升影格；驗證：tests/test_curation.py 竄改一張 staged 檔後斷言該候選被拒（reason: hash mismatch）、其餘照常處理、exit 2
- [x] 5.5 實作「OCR is cached and attached to frames」：RapidOCR 以 size+mtime 指紋快取於 .frames_ocr.json，寫入每段 frame_ocr，缺 rapidocr exit 3；驗證：tests/test_ocr.py 以 mock OCR 跑兩次，第二次印 `[ocr] N frames, 0 need OCR (N cached)` 且未呼叫 OCR

## 6. 筆記產生

- [x] 6.1 依「兩層筆記產生：骨架 render 與 LLM 擴寫」實作「Deterministic skeleton note rendered from canonical JSON」：固定章節順序、每段影格嵌入→summary→quotes（「」+時間）→bullets、References 含 corrections 表與 unverified_terms（標「未寫入本文」）與 source 區塊；驗證：tests/test_render.py 斷言同一 JSON 兩次 render 的 sha256 相同、unverified 詞只出現在 References、frame 為 null 時無嵌入行
- [x] 6.2 實作「Style selection」：--style faithful 全量 quotes、concise 每段最多一則且省略 kind=quote 的 bullet，預設取 outputs.toml 的 note.style（generic 為 concise）；驗證：tests/test_style.py 以三則 quotes 的段落斷言 concise 只出現一個 blockquote
- [x] 6.3 實作「Frontmatter comes from templates, not code」：frontmatter 完全由 note.frontmatter.yaml 模板渲染，generic 只含 title、date、source、tags；驗證：tests/test_frontmatter.py 斷言無 overlay 時 frontmatter 鍵集合恰為四鍵，套用含 noteVer/DateRev/subspecialty 的 overlay 模板後出現該三鍵，且 `grep -rn "noteVer\|DateRev" src/` 無結果
- [x] 6.4 實作「LLM expansion contract」：`l2n render --expand-prompt` 印出擴寫指令包（規範文字 + 需讀取的檔案路徑），並在 skill 的 note-writing 參考中規定擴寫後必須通過 check note；驗證：tests/test_expand_prompt.py 斷言輸出含規範版本字串與 .v4.md／.srt／.json 三個路徑；以 Claude Code 對 fixture 擴寫一次後 `l2n check note` exit 0（手動驗收，結果記錄於 PR 描述）

## 7. 筆記撰寫規範

- [x] 7.1 依「筆記撰寫規範作為可檢查的合約」撰寫 docs/note-writing-guideline.md 並完成「The guideline is a shipped, versioned document」：含版本字串、「LLM 必須遵守」與「機器可檢查」兩部分，skill/references/note-writing.md 指向它；驗證：tests/test_guideline_doc.py 斷言檔案存在、含兩個部分標題與版本字串，且 check note 報告印出同一版本
- [x] 7.2 在規範中寫入「Source precedence and evidence rules for the model」（講義＞人眼看的影格＞逐字稿＞OCR，OCR 不入文，不可證實的術語進 unverified_terms 並只在 References 出現）與「Quotation and synthesis rules for the model」（「」標示原話、faithful 每段至少一句、禁止原句直貼、講者能力邊界照錄、ASR 錯字入表）；驗證：內容審閱——以本 session 的 A hip（Schrodinger's lobe sign）與 C1 wrist（韌帶長回來「我沒有經驗」）兩案例作為規範內的正例說明
- [x] 7.3 在規範中寫入「Privacy rules for the model」（與會者／病患姓名以角色取代、講者姓名只採檔名／講義／畫面名牌）並附錄一份去識別化的失敗樣態範例（財經講座筆記：原句倒入、錯字未校、Evergreen 截斷）；驗證：tests/test_guideline_appendix.py 對附錄範例跑 check note 斷言至少一個 R5 與一個 R4 finding
- [x] 7.4 實作「Machine-checkable rules」R1–R7 於 `l2n check note`：章節順序、嵌入存在、unverified 只在 References、corrections 表完整、≥40 字（去空白標點）逐字稿重複且未以「」或 blockquote 標示（預設 warning，profile 可設 error）、faithful 每段至少一句引用、privacy.toml 模式；每項 finding 一行含 rule id／severity／位置，exit 0/1/2；驗證：tests/test_check_note.py 覆蓋 R5 boundary 表四列（39 過、40 報、120 加「」過、120 blockquote 過）與 R1–R7 各一個正反例

## 8. 衍生輸出

- [x] 8.1 實作「Viewer is generated from canonical JSON v2」：改寫 viewer 產生器讀 v2，非 null 的 bullet t 用真實時間、null 者內插並標波浪號，保留三層同步、點擊跳播、跨層搜尋、?t= 深連結；驗證：tests/test_viewer.py 斷言產出 HTML 內嵌的段落資料與 JSON 一致，t=812.5 的 bullet 在 HTML 中無波浪號；瀏覽器手動驗證 ?t=1234 跳播並高亮對應段
- [x] 8.2 實作「PotPlayer chapter file is opt-in via outputs configuration」：`l2n pbf` 產每段一章的 .pbf，run 只在 outputs.toml 的 pbf=true 時執行，generic 預設 false；驗證：tests/test_pbf.py 斷言無 overlay 時 run 不產 .pbf 且階段清單無 pbf，overlay 設 true 時章數等於段數
- [x] 8.3 實作「Course hub with cross-lecture search」：`l2n hub` 掃資料夾內 v2 JSON 產 課程首頁.html，索引含段落標題、重點、bullet、quote、frame OCR，結果連到 ?t=段落起點，卡片依 (no, stem) 字串排序；驗證：tests/test_hub.py 以兩份 JSON（其中一份只有 OCR 含「Haglund」）斷言搜尋索引含該詞並指向正確段落
- [x] 8.4 實作「Card overrides via _titles.json」：stem→{no, speaker, topic} 覆寫卡片與排序，未列者用推導值；驗證：tests/test_hub_titles.py 斷言覆寫的 topic 文字出現且卡片位置符合 no
- [x] 8.5 實作「Hub link integrity」：寫出後對每個相對 href 做 percent-decode 後檢查存在，缺檔即 exit 2；驗證：tests/test_hub_links.py 刪除一份 .viewer.html 後斷言 hub 報缺檔並 exit 2

## 9. 階段驗收、稽核與發布

- [x] 9.1 依「階段驗收合約與交易式發布」實作「Per-stage acceptance checks」的 transcribe／frames／json／note 四階段與統一輸出格式（每 finding 一行、`<stage>: N errors, M warnings`、exit 0/1/2）；驗證：tests/test_check_stages.py 對竄改 sha256 的影格斷言 `error sha256 ...: manifest .. actual ..` 與 exit 2；對 fixture 全流程產物四階段皆 exit 0
- [x] 9.2 實作「Structured audit report」：`l2n check --all <stem> --report <path>` 寫 JSON（guideline_version、各階段 findings、summary.errors/warnings），exit 取各階段最大值；驗證：tests/test_audit_report.py 斷言 summary.errors 等於 severity=error 的 finding 數
- [x] 9.3 實作「Rebuild preflight is read-only」：hub 與 viewer 的 --preflight 列出將建立／覆蓋的檔與是否存在，不寫任何檔；驗證：tests/test_preflight.py 前後記錄資料夾檔案清單與 mtime 斷言完全相同
- [x] 9.4 實作「Transactional publication with rollback」：`l2n publish` 同檔案系統檢查、manifest、時間戳備份、tmp 名複製、sha256 驗證、整批 rename、任一失敗全數還原並清 tmp、成功寫 <stem>.publish.json；驗證：tests/test_publish.py 在第三檔注入雜湊失敗斷言目的地檔案集合與內容不變、備份目錄移除、exit 2 並指出失敗檔；成功案例斷言 manifest 列出每檔 sha256
- [x] 9.5 實作 `l2n run` 的階段串接與「Stage subcommands are idempotent and resumable」：已有產物即 `[stage] skip (exists)`、--force 重做、check error 即停 exit 2、僅 warning 續行 exit 1；驗證：tests/test_run.py 對 fixture 連跑兩次斷言第二次所有階段 skip 且檔案 mtime 不變；注入一個 error 後斷言後續階段未執行

## 10. Profile 與 overlay

- [x] 10.1 依「profile 與 overlay 解析順序」實作「Layered configuration resolution」：cli > 專案 .lecture2notes/ > ~/.lecture2notes/ > profiles/<name>/ > builtin；模板檔整檔取代、corrections／outputs／privacy 逐鍵合併；驗證：tests/test_config_layers.py 斷言專案層 concise 勝過使用者層 faithful，且 corrections 合併後兩組替換皆生效並可被高層覆寫
- [x] 10.2 建立「Built-in profiles」：profiles/generic（concise、pbf=false、hub=true、四鍵 frontmatter、自寫通用術語表）與 profiles/radiology（閱片 callout 模板、放射術語表、病患識別 privacy 模式，不預設啟用）；驗證：tests/test_profiles.py 斷言無指定時 profile=generic 來源 builtin，且兩份 corrections 表無 source 含 ZeroType 或 USER.md 的項目
- [x] 10.3 實作「Effective configuration is inspectable」：`l2n profile show` 列每鍵的值與來源層，--json 輸出同內容；驗證：tests/test_profile_show.py 斷言 --json 可解析且 note.style 項有 value 與 source
- [x] 10.4 實作「Invalid overlay files fail loudly」：TOML／YAML 解析錯誤時印路徑與行號、exit 2、不套用該檔任何部分；驗證：tests/test_overlay_errors.py 以第 7 行壞掉的 outputs.toml 斷言輸出含路徑與 `line 7` 且 exit 2
- [x] 10.5 完成「Minimal overlay example ships with the repository」：examples/overlay-minimal/ 含五個 overlay 檔的合法佔位範例，README 說明複製到 ~/.lecture2notes/；驗證：tests/test_overlay_example.py 把範例複製到暫時 HOME 後 `l2n profile show` 每個定義鍵來源為 user 且無解析錯誤

## 11. Skill 打包與安裝

- [x] 11.1 依「單一 SKILL.md 路由與 install.py 三家部署」撰寫「Single routed skill」：skill/SKILL.md（name: lecture2notes，≤80 行，路由表指向六份 references，保留六條 HARD RULES 與完成條件）與 skill/references/ 六份文件，segmentation.md 明寫 LLM 產 JSON v2、機械階段一律呼叫 l2n 子命令；驗證：tests/test_skill_doc.py 斷言 SKILL.md 行數 ≤80、路由表提及十個 CLI 階段、六個 reference 檔存在
- [x] 11.2 實作「Three-target installer」：install.py 與 `l2n install-skill`，--target claude/codex/opencode、--dest、--all，複製不 symlink、不覆蓋既有 overlay 檔名、寫 .installed.json；驗證：tests/test_install.py 以暫時 HOME 斷言三目標各有 SKILL.md 與六份 references 與 .installed.json，且預先放入的 corrections.json 位元組不變
- [x] 11.3 實作「Drift check」：--check 重算來源與目標內容 hash，逐檔列差異，缺目標印 `not installed`，全符 exit 0 否則 2；驗證：tests/test_install_check.py 修改目標 SKILL.md 一行後斷言 `[drift]` 與 exit 2；刪除 opencode 目標後斷言 `not installed`
- [x] 11.4 撰寫 README 完成「README states scope and privacy boundary」：隱私段（本機 ASR 不上傳、LLM 擴寫送模型供應商）、Windows 優先聲明、MIT、四引擎表（local／GPU）、安裝與 overlay 教學、引擎相容表；驗證：tests/test_readme.py 斷言含「隱私」或「Privacy」標題且段內同時提及本機 ASR 與模型供應商

## 12. 測試基礎、fixture 與遷移驗證

- [x] 12.1 依「測試策略與 CC fixture」選定並裁切一支 ≤30 秒的 CC BY 或 CC0 公開演講片段（Wikimedia Commons 為首選來源）放 tests/fixtures/，附 README 記錄來源 URL、授權文字與裁切區間；驗證：fixtures README 存在且授權欄非 NC／ND；`l2n run fixture.mp4 --lang en --engine faster_whisper --model tiny` 到 render 為止四階段 check 皆 exit 0
- [x] 12.2 建立 GitHub Actions：Windows 與 Linux 各跑 pytest（GPU 測試以 marker 跳過），Windows job 以 PYTHONIOENCODING=cp950 跑一次；驗證：兩個 job 皆綠，且 `gh run view --log` 可見 cp950 job 名稱
- [x] 12.3 本機遷移驗證（不進 Git）：對本 session 的 9 份既有 JSON 跑 `l2n migrate` 與 `check json`，對 Copilot 三場 VTT 跑 calibrate-subs 與手工量測值比對；驗證：9 份皆 exit 0；三場各探針中位偏移與 (+3.14/+2.23/+0.86)、(+1.44/+0.80/+0.96)、(+1.81/+2.37/+2.66) 差異皆 ≤0.5 秒，結果摘要貼入 PR 描述
- [x] 12.4 本機品質對照（不進 Git）：從 Downloads 的 YT 資料夾依日期選一支有對應 Jenny 舊筆記的影片，以新流程 + 規範重產筆記；驗證：新筆記 `l2n check note` exit 0，且人工對照確認舊版三種失敗樣態（原句倒入、錯字未校、Evergreen 截斷）不再出現，對照結論寫入 PR 描述
- [ ] 12.5 以 Claude Code 與 Codex 各對 fixture 執行一次 skill 擴寫；驗證：兩者輸出皆 `l2n check note` exit 0，Codex 產出的 R5 finding 數記錄於 PR 描述作為規範有效性的基準
- [ ] 12.6 打 tag v0.1.0（第 1–2、5、8 群可用）與 v0.2.0（全部群），README 加入版本說明；驗證：`gh release list` 顯示兩個 tag，且 `pip install git+https://github.com/jieyu166/lecture2notes@v0.2.0` 後 `l2n --help` exit 0

## 14. 筆記方法第二批決議（B 系列，落在 lecture2notes 的部分）

- [x] 14.1 骨架與規範加入「題目不得留空」：render 骨架在 `## 題目` 放 3–5 題的 ai-draft 佔位（至少一題標 `[推論]`），答案以 `> [!answer]-` 收合；docs/note-writing-guideline.md 升 1.1 並規定推論題句型；`l2n check note` 加 R9（warning）：題目節少於 3 題或無 `[推論]` 標記；驗證：tests/test_check_note.py 加 R9 正反例，tests/test_render.py 斷言骨架含 `[!answer]-`
- [x] 14.2 首段定位宣告與句首空槽：骨架第一行為 `> 本筆記為模型產出的初稿，未經本人確認。`；Summary 的「我為什麼開這篇」改為兩個有句首的空槽（`開這篇之前我卡在___`、`這篇沒回答到的是___`）；「我應該記住的 3 件事」候選移入 `> [!note]- 模型候選（未經本人確認）` 收合 callout；規範新增「坡道句自檢」：模型寫不出坡道句即在 Summary 首行加 `> [!warning] 降級：本筆記只是資訊重排`；驗證：tests/test_render.py 斷言宣告行與收合 callout 存在，tests/test_guideline_doc.py 斷言規範含自檢條
- [x] 14.3 講者骨架（Reverse Outline）：骨架新增 `## 講者骨架` 節，由 JSON segments 機械生成每段一行「時間碼 ｜ 佔比% ｜ 動詞開頭一句（ai-draft）」；規範規定只寫「做了什麼」不寫「講了什麼」、坡道（前 5–8%）是 Evergreen 的原料、首段與末段不呼應時檢查分段；驗證：tests/test_render.py 以三段 JSON 斷言三行且佔比合計 100±1
- [x] 14.4 摘要不重寫與六選一：規範規定 Summary 直接引用 `takeaways_zh`、筆記相對 JSON 只新增講者骨架／跨版本對照／閱片連結；講者補充採六選一（界定概念／後果嚴重／與認知相反／遞進缺環／轉折／多面向印證），不符者只在 JSON 留時間碼；schema v2 新增選填 `questions_zh`（跨段出題，每題含 `text` 與 `segments` 索引陣列），skill/references/segmentation.md 要求 LLM 產出並寫入四段弧（坡道／背景／正文／昇華）檢查項；驗證：tests/test_schema.py 斷言 `questions_zh` 缺省合法、格式錯誤報 error；segmentation.md 含四段弧字樣
- [x] 14.5 Step 0 第三層與課程首頁摘要：規範 §0 加「產物型態」層（看到 X→判斷 Y 且題材已自動化者不做完整筆記，只講機制者才做；以題材而非專科為單位）；`l2n hub` 支援選填 `_course.json`（`question`、`start_with`、`no_common_thread` 三鍵）在卡片上方輸出「本系列在回答的問題／最該先看的一場」，`no_common_thread: true` 時輸出「本系列各場主題獨立，無共同主線」；驗證：tests/test_hub.py 斷言兩種輸出，tests/test_guideline_doc.py 斷言規範含「產物型態」

## 15. 實地試跑回饋修正（12.4 財經講座全流程試跑發現）

- [ ] 15.1 `l2n render --expand-prompt` 的指令包必須帶實際生效的 style（cli > overlay > profile），且「完成後必做」的驗收指令含 `--style <同一值>`；驗證：tests/test_expand_prompt.py 斷言 `--style faithful` 時指令包內 style 為 faithful 且驗收指令含 `--style faithful`
- [ ] 15.2 `l2n ocr` 輸入正規化：傳資料夾時改以同層唯一的 `<stem>.json`／`<stem>.frames.json` 解析 stem，找不到或多於一個即 exit 2 並說明，不得產出 `frames.frames_ocr.json` 這種孤兒檔；skill/references/frames-and-notes.md 同步；驗證：tests/test_ocr.py 加資料夾輸入的成功與 exit 2 兩案
- [ ] 15.3 文件內 JSON 範例必須可驗證：修正 skill/references/segmentation.md 的最小 v2 範例（bullets_zh 物件含 kind、frame 鍵、takeaways ≥6），並統一「每段條列數」說法與檢查器一致；驗證：tests/test_skill_doc.py 從 segmentation.md 抽出 json 區塊跑 validate_document 無 error
- [ ] 15.4 影格與分段解耦：`check json` 對「區間內無影格但已沿用前一張（frame 非 null、frames 為空）」的段落不得報 error；frames-and-notes.md 改寫指引為「scene 張數少於預計段數即改 interval」；驗證：tests/test_schema.py 加沿用影格段落 exit 0 的案例
- [ ] 15.5 場景偵測期間的進度回饋：ffmpeg scene filter 與 PySceneDetect 掃描時以 ffmpeg `-progress`（或 scenedetect callback）每 5 秒印一次已掃秒數／總秒數；驗證：tests/test_frames.py 以假的 ffmpeg 進度輸出斷言 Progress 被呼叫多次
- [ ] 15.6 新增 `l2n condense <srt> [--window 60]` 暴露 schema/condense（子命令數 17，回補 lecture-pipeline-cli 規格與 SKILL 路由表）並實作 `l2n scaffold <srt> --segments N`：產出形狀合法、內容為 ai-draft 佔位的 v2 JSON 骨架（等時間切段、每段附壓縮逐字稿路徑），`--help` 明寫「段落語意由 LLM 填寫」；驗證：tests/test_scaffold.py 斷言輸出通過 validate_document 的結構檢查（內容長度類規則以 draft 旗標豁免並在 check json 報 warning `draft`）
- [ ] 15.7 R5 涵蓋範圍擴大到 Evergreen 與 Summary 章節（題目的答案區亦同），仍以「」與 blockquote 為豁免；規範同步；驗證：tests/test_check_note.py 加 Summary 貼 40 字原句報 R5 的案例，既有 boundary 四列不退步
- [ ] 15.8 `check note` 統計殘留的 `<!-- ai-draft -->` 標記數，於結尾行後加印 `note: ai_draft_remaining=N`，並寫入 `check --all --report` 的 note 階段；不影響 exit code；驗證：tests/test_check_note.py 與 tests/test_audit_report.py 各加一案
- [ ] 15.9 以真實 cmd.exe（chcp 950）重現 `l2n --help` 是否亂碼：可重現即修（help 字串改為 cp950 可編碼字元或在 stdout 非 UTF-8 時以 errors=replace 輸出並印一次提示），不可重現則在 README 疑難排解記錄結論；驗證：結論與重現步驟寫入 README 疑難排解段
- [ ] 15.10 未擴寫偵測：`check note` 新增 R10（warning，profile 可升 error）——段落本文與同一 JSON／style 重新 render 的骨架相同即報 `unexpanded skeleton`，Evergreen 仍為佔位句亦同；結尾加印 `note: unexpanded_segments=K/N` 並寫入稽核報告；驗證：tests/test_check_note.py 斷言骨架直接 check 得到每段一條 R10 且 exit 1，擴寫其中一段後 K 減 1
- [ ] 15.11 style 單一來源：render 寫入 `<!-- l2n:style=… guideline=… -->` 標記，`check note` 未給 --style 時讀取之、與 CLI 不同時報 `style mismatch` warning；驗證：tests/test_style.py 斷言 faithful 骨架在不帶 --style 的 check 下仍套用 R6
- [ ] 15.12 指令包與規範補洞：`--expand-prompt` 加「已落地／待擴寫」逐章節清單；規範明定 `[推論]` 標記格式且 R9 訊息提示之；釐清 `<stem>.frames_ocr.json`（快取）與 JSON 內 `frame_ocr`（筆記階段來源）的關係；驗證：tests/test_expand_prompt.py 斷言清單存在，tests/test_guideline_doc.py 斷言規範含標記格式定義

## 13. 上游標示與授權（Upstream attribution）

- [x] 13.1 依「移植來源與 ZeroType 內容清除」對上游 drpwchen/lecture-to-notes（MIT）做來源稽核：以 git 取得上游最新 commit，逐檔比對本專案 src/ 與 skill/ 內容與上游 scripts/、SKILL.md、docs/，產出 ATTRIBUTION.md 列出每個「修改自上游」的檔案、對應的上游路徑與 commit hash、修改摘要；驗證：ATTRIBUTION.md 存在且每列的上游路徑以 `gh api repos/drpwchen/lecture-to-notes/contents/<path>` 可取得，未列入的檔案在 PR 描述中說明為原創或移植自 rad-workflow
- [x] 13.2 依 MIT 條款保留上游著作權聲明：新增 NOTICE（或 LICENSE 附錄）收錄上游 LICENSE 的著作權行與全文，ATTRIBUTION.md 列出的每個檔案檔頭加註「Adapted from drpwchen/lecture-to-notes (MIT), <upstream path>@<commit>」；驗證：tests/test_attribution.py 斷言 ATTRIBUTION.md 內每個檔案的檔頭含該註記，且 NOTICE 含上游著作權行
- [x] 13.3 README 的致謝段以連結明確標示本專案部分程式碼修改自 https://github.com/drpwchen/lecture-to-notes，並說明兩者差異（profile／overlay 分層、schema v2、官方字幕偏移校正、撰寫規範與機器檢查、三家 skill 安裝器）；驗證：tests/test_readme.py 斷言 README 含該 URL 與「修改自」或「Adapted from」字樣
