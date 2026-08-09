## Why

現有 NR 神經放射學 11 講 viewer 的章節摘要、標題、影格索引與來源界線不一致，無法支援快速複習、可靠搜尋或可稽核重建。需要把已核准的重建設計與 16 項驗證計畫納入 canonical `skills/lecture-to-notes/`，以可測試、可重跑且不危及 NAS 正式產物的共同流程取代一次性修補。

## What Changes

- 建立以正式 JSON 為單一內容來源的章節 schema、legacy normalization、時間不變性與 UTF-8 原子寫入契約。
- 建立內容與來源規則：標題作為第六個受 review 內容單元，病例事實型標題須有可信引用與逐 claim attestation，否則只能是非病例主題標籤；每章 `summary_zh` 與四項 `takeaways_zh`（包含未改寫 legacy 內容）皆須由可信逐字稿段落或外部可信 canonical frame manifest 引用並具備逐 claim attestation。採非循環雙 digest：`approved_candidate_sha256` 綁定完整 rewritten candidate 與 order-insensitive canonical citation map，`review_attestation_sha256` 再綁定 candidate digest、canonical attestations、正規化 reviewer identity、確認欄位及 review schema/version；approved run state 必須同時綁定兩者，另保留繁體中文、未完成標記與敏感資料 fail-stop。
- 將 extract 候選影格限制於 staging，策展每章正式 1–4 張影格；第一講既有 72 張影格須完整複製、雜湊驗證並納入候選池。
- 重建詳細型 viewer、PBF、`.v4.md` 與課程首頁，使搜尋 schema、章節時間、標題及內容由 canonical JSON 同源產生；保留播放器、章節導覽、深連結、同步逐字稿與跳播。
- 建立結構化 audit、cp950 相容進度、fixture/TDD、瀏覽器 E2E、三講抽樣與 11 講全課驗證 gate；任何必要門檻失敗即停止該講發布。
- 建立同檔案系統 staging、帶時間備份、manifest、多檔交易式替換、全講 rollback、外部 recovery evidence 與首頁最後獨立切換。
- 外部 LLM 維持預設關閉；只有明確旗標、敏感資料 preflight 通過與人工確認同時成立時，才可傳送文字 evidence，且輸出仍須人工 review 後才能套用。

## Non-Goals

- 不變更章節起訖時間、不重新切章。
- 不建立 NR 專用長期生成器、第二套 viewer 或 NAS hotfix。
- 本 change 的 application 階段未取得另行授權前，不存取、修改或發布 NAS 正式課程。
- 不將 NAS 產物、逐字稿、正式影格、病患資料、憑證、staging、backup、audit 實例或 rewrite 實例納入 Git。

## Capabilities

### New Capabilities

- `lecture-content-contract`: Canonical 章節資料模型、內容品質、逐 claim 可信引用與人工來源支持 attestation、來源分離、時間不變性、敏感資料與人工 review 契約。
- `lecture-frame-curation`: Staging-only 候選影格、legacy 影格移轉、OCR 與每章正式 1–4 圖策展契約。
- `lecture-derived-viewer`: JSON 同源 viewer、PBF、`.v4.md`、課程首頁、typed search、深連結、逐字稿與 responsive 影格互動契約。
- `lecture-rebuild-verification`: Preflight、分階段重建、cp950 進度、fail-stop audit、TDD、fixture、E2E、三講與 11 講驗證契約。
- `lecture-safe-publication`: NAS 同檔案系統 staging、備份、manifest、交易式替換、rollback、recovery 與首頁最後發布契約。

### Modified Capabilities

（無；目前沒有既有 capability spec。）

## Impact

- Affected specs: `lecture-content-contract`, `lecture-frame-curation`, `lecture-derived-viewer`, `lecture-rebuild-verification`, `lecture-safe-publication`
- Affected code:
  - Modified: `skills/lecture-to-notes/SKILL.md`, `skills/lecture-to-notes/scripts/slide_frames.py`, `skills/lecture-to-notes/scripts/ocr_frames.py`, `skills/lecture-to-notes/scripts/build_lecture_viewer.py`, `skills/lecture-to-notes/scripts/json_to_pbf.py`, `skills/lecture-to-notes/scripts/build_course_hub.py`, `skills/lecture-to-notes/scripts/check_lecture.py`, `skills/lecture-to-notes/scripts/batch_course.py`, `sync_skills.py`
  - New: `skills/lecture-to-notes/scripts/lecture_model.py`, `skills/lecture-to-notes/scripts/lecture_content_rules.py`, `skills/lecture-to-notes/scripts/rewrite_evidence.py`, `skills/lecture-to-notes/scripts/rewrite_lecture.py`, `skills/lecture-to-notes/scripts/frame_curator.py`, `skills/lecture-to-notes/scripts/render_v4_note.py`, `skills/lecture-to-notes/scripts/lecture_audit.py`, `skills/lecture-to-notes/scripts/rebuild_course.py`, `skills/lecture-to-notes/scripts/publish_transaction.py`, `skills/lecture-to-notes/requirements-rebuild.txt`, `tests/test_lecture_model.py`, `tests/test_lecture_content_rules.py`, `tests/test_lecture_rewrite.py`, `tests/test_lecture_frame_curator.py`, `tests/test_lecture_renderers.py`, `tests/test_lecture_audit.py`, `tests/test_lecture_rebuild_pipeline.py`, `tests/test_lecture_publish_transaction.py`, `tests/test_lecture_viewer_e2e.py`, `tests/test_lecture_console_encoding.py`, `tests/test_sync_skills.py`, `tests/fixtures/lecture_rebuild/course/`
  - Removed: none
- Runtime/dependencies: Python 3.10+, `scenedetect>=0.6.4,<0.8`, ffmpeg/ffprobe, RapidOCR, OpenCC, HTML/CSS/vanilla JavaScript, Node VM, Chrome or Edge headless；可選官方 Anthropic Python SDK 僅用於明確允許的文字 rewrite candidate。
- External system: `\\jieyu_nas\web\files\2015\08\20150804 NR 神放複習` 僅在後續另行明確授權的 rollout 階段使用。
