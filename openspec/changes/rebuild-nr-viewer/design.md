## Context

NR 神經放射學課程共有 11 講，現有 viewer 使用共用 `lecture-to-notes` 模板，但只有第一講有 72 張影格，其餘講次缺乏視覺索引；摘要與逐字稿高度重複、標題失焦，講者內容與後續補充也未明確分離。此變更跨越 canonical schema、內容重寫、影格策展、viewer/衍生檔、audit、批次 orchestration 與 NAS 發布，因此必須以單一自足設計維持資料流與安全 gate 一致。

限制包括：Windows PowerShell 5.1、主控台 cp950 strict、內容檔 UTF-8、PBF 延續既有編碼選項、PySceneDetect 固定 `>=0.6.4,<0.8`、正式課程位於 UNC NAS，且實際存取、長流程與發布必須另行取得明確授權。Git 工作樹可能有無關變更，實作只可 scoped stage 明列檔案。

## Goals / Non-Goals

**Goals:**

- 以正式 JSON 作為 11 講章節內容及正式媒體索引的唯一來源，所有衍生檔可重建並可稽核。
- 在 canonical `skills/lecture-to-notes/` 建立 extract、curate、evidence、rewrite-apply、render、audit 的可重跑兩階段流程。
- 強制內容來源分離、章節時間不變、每章正式 1–4 圖、typed search 與 viewer 既有核心功能。
- 以 TDD、synthetic fixture、769/768px browser E2E、三講抽樣、11 講全課 audit 與 fresh-context review 作為發布前 gate。
- 以備份、同檔案系統 staging、manifest、逐檔原子替換及全講 rollback 保護 NAS，首頁僅在 11/11 成功後最後切換。

**Non-Goals:**

- 不重新切章或更改任何起訖時間。
- 不建立 NR 專用生成器、第二套 viewer、手改衍生 HTML 或一次性 NAS hotfix。
- 不在未授權時執行真實三講、11 講處理、NAS probe、發布或清除備份。
- 不提交正式媒體、逐字稿、NAS/staging/backup/audit/rewrite 實例、敏感資料或憑證。

## Decisions

### Canonical schema and immutable chapter timing

`lecture_model` 是唯一 legacy adapter，將 aliases、舊 bullets、字串 frames 與 OCR map 正規化為 `start_sec`, `end_sec`, `title`, `summary_zh`, `takeaways_zh`, `editorial_notes_zh`, `frames`。正式 frame object 固定包含 `time`, `ocr`, `path`；路徑必須是安全相對路徑。每個 rewrite/render/publish gate 都比較完整 time signature，任何章節數或時間差異 hard fail。相較於讓各 renderer 自行理解舊格式，單一 normalization 可防止多條資料流與不一致 migration。

### Evidence-bound content rewrite and privacy gate

每章先由 SRT、正式選取影格 OCR 與既有內容建立帶 SHA-256 的 evidence packet，再由 manual-first rewrite 結果與 review record 套用。review 必須確認 packet hash、reviewer、source faithfulness、無臆造病例細節與 editorial separation。外部 LLM 預設關閉，只有明確旗標、確認字串與完整 outbound payload 敏感資料掃描通過時，才可產生候選文字；候選仍不得直接發布。此設計優於直接由模型改 JSON，因為它保留可追溯證據與人工責任界線。

### Staging-only candidate frames and deterministic 1–4 frame curation

Scene detection 與 OCR 只寫 `candidate_frames.json` 與 staging 資產，不直接改 canonical JSON。第一講既有 72 張正式影格必須先 `copy2` 到 staging 並逐檔驗 SHA-256，再與新候選依 path/time 去重。curator 依時間範圍、sharpness、luma、OCR 與 perceptual hash 排除低資訊或重複畫面，每章選 1–4 張且零張 hard fail；少於 4 張只產生可見 warning。相較於讓 viewer 顯示所有候選，此決策保證正式媒體索引小而可稽核。

### Single-flow derived renderers and typed search

Viewer 主流程固定為單次 `load_lecture`、單次 `load_srt`、five-argument `render(data, cues, title, video_rel, media_dir: Path)`，`render` 只由 `build_blocks(data, cues)` 建立唯一搜尋索引。每筆 search block 使用 `kind`, `label`, `start`, `end`, `text`；hub 只額外加入 `viewer`, `lecture_id`, `lecture_number`。所有 `application/json` script 使用 raw JSON 並只將 `</` 轉為 `<\/`。PBF、`.v4.md`、viewer snapshot 與 hub 都從 normalized JSON 產生，audit 逐 byte/結構比對關鍵內容。

### Responsive viewer and browser-observable interaction contract

每章呈現標題、1–2 段整理稿、正好 4 項核心重點、正式影格、非空時才出現的編輯補充、可展開逐字稿與 OCR。viewport 769px 使用 2 欄，768px 使用單欄；1–4 張圖不得補空格、裁掉重要內容或水平溢位。正式縮圖可 modal 放大及 seek，搜尋結果標示來源並導航，`?t=` 與 stable chapter hash 保持深連結，實際 media `timeupdate` 更新章節與逐字稿狀態。

### Fail-stop audit and cp950-safe staged orchestration

Pipeline 階段固定為 `extract, curate, evidence, rewrite-apply, render, audit`，前後以人工 review 分成兩次 invocation。每講獨立 staging，失敗講次記錄錯誤但不阻止其他講次產生；然而發布 invocation 遇到任何 audit 或 publish failure 必須立刻停止，不建立後續 manifest，也不更新首頁。進度事件包含 lecture、stage、completed/total、percent、status、chapter counters 與 failure summary，輸出必須 cp950 strict 可編碼。Audit report 結構化記錄 severity、code、lecture、stage、input hashes、browser result 及原始錯誤。

### Manifested same-filesystem publication and whole-lecture rollback

Preflight 預設只讀；live/staging replace probe 必須另有 course ID 確認與 opt-in，使用唯一 disposable 檔案驗證 create/read/hash/replace/cleanup。每次發布在建立狀態前以本機時間產生精確 `YYYYMMDD-HHMMSS` run ID，backup directory/name 必須包含相同 run ID；同秒碰撞時依序選取最低未使用的 `-01`, `-02`, `-03` 等 decimal suffix。任意非時間識別字不符合契約且必須 fail before backup/live mutation。發布前 preflight receipt 必須與 live/staging/backup roots、11 講 source full-content hashes、已解析 run ID 及 `course-run.json` SHA-256 綁定；`course-run.json`、每講與首頁 manifest、外部 recovery evidence 皆記錄同一 run ID 與 backup path，確保可由失敗證據追溯實體備份。每講 manifest 記錄 live、immutable staged source、backup、old/new hashes 與逐項狀態；每次替換先複製到 live sibling temp，再以 `os.replace` 切換。任一檔失敗即以逆序恢復整講，新增檔則刪除；manifest 無法持久化時，在 transaction directory 外保留 recovery evidence。首頁是獨立最後一筆交易，只有 11 個同 run committed manifests 與 course audit 通過後才能切換。

### TDD fixture E2E sampling and fresh verification gates

16 項實作依 RED/GREEN 分解：schema/content/frame/rewrite/render/audit/preflight/orchestration/transaction 均先寫單元測試；synthetic fixture 涵蓋 1/2/3/4 圖、空 OCR、零圖失敗與非法 schema；headless Chrome/Edge 直接開 production staging viewer，量測 769/768 邊界、lazy image load/decode、modal/seek/search/details/deep link、真實 MP4 播放與 transcript highlight。完成程式後先 full suite、cp950、compile、sync、diff/secret/output scans，再由 fresh-context verifier read-back。真實 Brain tumor、Vascular、Spine 與 11 講 rollout 仍各需另行授權。

## Implementation Contract

### Behavior and interfaces

- Canonical lecture JSON SHALL retain original chapter count and exact time ranges and SHALL expose each segment's focused title, 250–600 Han-character summary in 1–2 paragraphs, exactly four distinct takeaways, editorial note list, and 1–4 formal frame objects.
- Candidate extraction SHALL write only a staging manifest. Curate SHALL copy and hash all 72 first-lecture legacy assets before selection and SHALL reject a chapter with zero valid frames.
- Rewrite SHALL default to manual reviewed imports. External provider mode SHALL require `--allow-external-llm`, confirmation `TEXT-EVIDENCE-ONLY`, a clean sensitive-data scan, environment/profile credentials, and human review before apply.
- Viewer SHALL preserve playback, navigation, deep links, search, transcript sync and seek, expose only formal frames, use the single typed block schema, and parse embedded raw JSON with `JSON.parse(textContent)`.
- `rebuild_course.py` SHALL support preflight, two-phase build/resume, exact lecture selection, failed/awaiting-review resume with source hash checks, fixture mode, publish, and homepage publish controls. Publish and live probe SHALL require `--confirm-course-id 20150804-NR`; publish SHALL also require backup root and a bound passing preflight receipt.
- Every publication run ID and backup directory/name SHALL share an exact local `YYYYMMDD-HHMMSS` identity, extended only by the deterministic lowest available `-01`, `-02`, and subsequent decimal suffix on same-second collision. Non-temporal IDs SHALL fail before backup or live mutation, and receipt/run/manifest/recovery records SHALL preserve the resolved ID and backup path.
- Structured findings SHALL be surfaced rather than silently downgraded. Zero frame, changed times, source confusion, inconsistent derivatives, failed browser result, stale preflight, backup/hash/replace/rollback failure SHALL block the affected transition.

### Acceptance criteria

- Focused unit tests and full `test_lecture_*.py` discovery pass; cp950 strict tests produce no `UnicodeEncodeError`; Python compile checks and `sync_skills.py --check` pass.
- Fixture pipeline completes lecture 01 with formal frame counts `[1,2,3,4]`, preserves an empty OCR value, and isolates lecture 02 zero-frame failure.
- Browser E2E records a real PASS at 769px/768px, validates 10 formal images, raw JSON parsing, modal/seek/search/deep link/details, actual MP4 time advancement and transcript highlighting.
- Failure-injection tests prove every replace position restores old files, deletes transaction-created live assets, preserves immutable staging, supports retry, and emits external recovery evidence when needed.
- Publication tests prove a local time of `2026-08-09 14:05:07` resolves to run ID and backup name `20260809-140507`; existing `20260809-140507` and `20260809-140507-01` resolve deterministically to `20260809-140507-02`; arbitrary `nr-final` is rejected; and every receipt, run record, manifest, and recovery record preserves the resolved run ID and backup path.
- No application step accesses NAS until a new explicit authorization. No NAS, sensitive, staging, backup, audit or rewrite content becomes tracked.

### Scope boundaries

Implementation includes only canonical generator, renderers, orchestration, tests, fixture, skill contract and sync behavior named by the proposal. Real sample processing, 11-lecture publication and backup cleanup are operational handoffs requiring separate authorization and are not automatic consequences of apply.

## Risks / Trade-offs

- [Automated rules cannot prove medical truth] → Evidence packets, mandatory human review and explicit editorial separation remain hard gates.
- [One to three valid frames reduce visual density] → Allow 1–3 with a visible audit warning; never use duplicates or placeholders to reach four.
- [UNC/SMB does not provide multi-file atomicity] → Use per-file same-filesystem replace plus manifest-backed whole-lecture compensating rollback and verify every hash.
- [Rollback itself can fail] → Preserve backups and immutable staging, mark `recovery_required`, write external evidence and stop homepage publication.
- [Headless browser/media behavior varies] → Support installed Chrome or Edge, use deterministic tiny fixture media, and require a real PASS on the implementation machine.
- [Long 11-lecture processing is costly] → Emit foreground cp950-safe progress, isolate failures, support exact resume, and require three representative lectures before full rollout.
- [Strict sync copies can expose drift] → Modify only canonical skill, run sync once after canonical edits, then require byte/file-set equality.

## Migration Plan

1. 依序完成 checkbox `1.1`–`5.1`、`6.1`–`6.2` 與 `7.1` 的 TDD 實作及 scoped commits，全程不存取 NAS。
2. 完成 checkbox `8.1` 的 full automated、cp950、fixture/browser E2E 與 fresh-context verification；若有缺陷，以 focused commit 修正並重跑全部 gate。
3. 取得 local/de-identified source 明確授權後，執行 checkbox `7.2` 的 Brain tumor、Vascular、Spine 三講 sample gate；三講 rewrite review、audit 與 browser evidence 全部通過後，才可進入 11 講流程。
4. 另行取得 NAS、長流程與發布授權後，依 checkbox `8.2` 凍結已驗證 Git revision，建立 timestamped run/backup identity，執行 11-pair preflight 與 opt-in live/staging probe，並將 receipt 綁定至 staged run。
5. 依 checkbox `8.2` 在 staging 完成全 11 講 build/review/audit 與 full-course verification；未達 11/11 passing 時不得開始正式 lecture publication。
6. 全課驗證通過後，依 checkbox `5.1`, `7.1`, `8.2` 逐講執行 manifested transaction；第一個失敗立即停止，並以該講完整 manifest rollback。
7. 11 講均 committed 且 post-publish smoke/E2E 與 course audit 通過後，才依 checkbox `7.1` 與 `8.2` 將 NAS homepage 作為最後一筆獨立交易發布；homepage rollback 不改動 lecture files，backup/staging evidence 保留至另行授權 cleanup。

## Open Questions

無；設計與 16 項實作計畫已核准。真實三講來源存取、NAS 長流程、發布及備份保留期間均刻意延後至各自的明確操作授權。
