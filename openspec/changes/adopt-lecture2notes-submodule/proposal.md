## Summary

rad-workflow 改以 git submodule 引用已發布的 lecture2notes 產品，個人化設定放進版控內的 overlay 目錄，並讓 lecture-to-notes 與 whisper-srt-zh 兩個舊 skill 及其所有副本退役（搬移保存、不硬刪）。

## Motivation

lecture2notes v0.2.x 已在獨立 public repo 發布並通過實地驗證（同一份逐字稿：舊筆記盲評 9/40、新流程 39/40），但本機三家 agent（Claude Code、Codex、OpenCode）實際載入的仍是舊的 lecture-to-notes 與 whisper-srt-zh。盤點結果：lecture-to-notes 5 份副本、whisper-srt-zh 6 份副本 2 個版本（使用者層 Codex 讀到的停在 112 行舊版）、obsidian-v4-cleanup 8 份副本 3 個版本（vault 內兩份 778 行與 1023 行的過期分岔）。只要舊 skill 還在，agent 就會繼續走沒有撰寫規範、沒有 check 的舊流程，新產品等於沒上線。另外使用者累積的 186 條錯字對照（135 deterministic、44 radiology、7 context_sensitive）與 V4 frontmatter、pbf、faithful 等個人偏好，目前綁在即將退役的 skill 裡，需要搬到 lecture2notes 的 overlay 機制，否則退役即遺失。

## Proposed Solution

1. 在 rad-workflow 新增 submodule 於 vendor/lecture2notes，釘在 lecture2notes 的 v0.2.1 tag（該版起一般安裝即可使用 install-skill）。
2. 新增 skills-overlay/lecture2notes/ 目錄存放個人 overlay：note.frontmatter.yaml（V4 欄位含 noteVer、DateRev、subspecialty、消化層級）、note.template.md（含閱片 callout）、outputs.toml（note.style 為 faithful、pbf 為 true、profile 為 radiology）、corrections.json（由舊對照表轉換，條數與轉換前一致）、privacy.toml。
3. 新增部署腳本 deploy_lecture2notes.py：以 editable 方式安裝 submodule 內的套件、執行 l2n install-skill --all 部署到三家 agent、把 overlay 複製到使用者家目錄的 .lecture2notes/；提供 --check 以內容雜湊比對三家 skill 與 overlay 是否 drift（不一致 exit 2），輸出 cp950 相容。
4. 舊 skill 退役：skills/lecture-to-notes 與 skills/whisper-srt-zh 以 git rm 移出版控（歷史可救回）；Git 以外的副本（使用者層、各家衍生 copy、vault 內 obsidian-v4-cleanup 的兩份過期分岔）一律搬到帶日期的退役資料夾，不硬刪。obsidian-v4-cleanup 保留並維持現行 canonical 與同步方式。
5. 更新指引：專案 CLAUDE.md 路由表與常用指令、docs/PITFALLS.md、記憶檔；對仍引用舊腳本路徑的歷史計畫文件在檔頭加註「已由 lecture2notes 取代」，不改寫內文。
6. 以一支真實短片在遷移後的環境實跑 l2n 全流程，確認 overlay 生效（frontmatter 為 V4 欄位、style 為 faithful、對照表條數正確）。

## Non-Goals

- 不處理 .worktrees 下的 worktree：rebuild-nr-viewer 有 24 個未提交檔、turtle-trader-manga 有 53 個未合併 commit、image-stack-mpr-viewer 與 card-rewards-2026-h2 與本案無關；全部原樣保留，只在文件記錄現況。
- 不修改 lecture2notes 產品本身；產品缺口另開 issue 或走該 repo 的 PR。
- 不把 Task 5 PDF 深讀、Task 8 新知查核搬進 lecture2notes；obsidian-v4-cleanup 繼續負責。
- 不改寫引用舊腳本路徑的歷史計畫與報告內文。
- 不硬刪任何 Git 以外的檔案；退役資料夾由使用者日後自行清理。

## Alternatives Considered

- 直接 pip install 已發布的 tag、不用 submodule：少一層 Git 操作，但 rad-workflow 無法釘住與 overlay 相容的版本，也看不到 skill 原始檔；使用者先前已選定 submodule。
- 把 overlay 放進 lecture2notes public repo 的 radiology profile：使用者已否決，V4 YAML 與 pbf 屬個人偏好。
- 沿用 sync_skills.py 散佈 lecture2notes 的 skill：它只會複製 skills 目錄下的內容，無法處理 overlay 與套件安裝，且 lecture2notes 已自帶 install-skill 與 drift 檢查，重做一套沒有意義。

## Impact

- Affected specs: 新增 lecture2notes-vendoring、legacy-skill-retirement
- Affected code:
  - New:
    - vendor/lecture2notes
    - .gitmodules
    - skills-overlay/lecture2notes/note.frontmatter.yaml
    - skills-overlay/lecture2notes/note.template.md
    - skills-overlay/lecture2notes/outputs.toml
    - skills-overlay/lecture2notes/corrections.json
    - skills-overlay/lecture2notes/privacy.toml
    - skills-overlay/lecture2notes/README.md
    - deploy_lecture2notes.py
    - tests/test_deploy_lecture2notes.py
  - Modified:
    - CLAUDE.md
    - docs/PITFALLS.md
    - README.md
    - docs/superpowers/plans/2026-08-08-nr-viewer-rebuild.md
    - docs/superpowers/specs/2026-08-08-nr-viewer-rebuild-design.md
  - Removed:
    - skills/lecture-to-notes
    - skills/whisper-srt-zh
