## Context

lecture2notes（public repo，本機開發位置在 OneDrive 之外）已發布 v0.2.x：pip 可安裝的 `l2n` CLI、單一路由 skill、撰寫規範與 R1–R11 檢查。rad-workflow 目前仍以 skills/lecture-to-notes 與 skills/whisper-srt-zh 為 canonical，由 sync_skills.py（自動掃 skills 目錄下含 SKILL.md 的子目錄）散佈到三家專案資料夾，使用者層副本靠手動覆蓋。盤點（2026-09-22）：

- lecture-to-notes 5 份副本 1 個版本；whisper-srt-zh 6 份 2 個版本（使用者層 `~/.agents/skills/whisper-srt-zh` 停在 112 行舊版）；obsidian-v4-cleanup 8 份 3 個版本，`~/.claude/skills/obsidian-v4-cleanup` 是指向 `~/.agents/skills/` 的 junction，vault 內另有 778 行與 1023 行兩份過期分岔。
- 個人化資料：skills/whisper-srt-zh/references/corrections.json 共 186 條（deterministic 135、radiology 44、context_sensitive 7）。
- 引用舊腳本路徑的只有三份歷史文件；CLAUDE.md、sync_skills.py、radtracker、tool、settings、全域 playbooks 與 hooks 皆無引用。
- .worktrees 下有未提交與未合併的工作，與本案無關或不可動。

限制：OneDrive 有遺失前例（寫完立即 commit）；主控台輸出需 cp950 相容；subagent 的 shell cwd 會被重設回本 repo，任何建立 venv 或暫存檔的動作必須使用 repo 以外的絕對路徑。

## Goals / Non-Goals

**Goals:**

- 三家 agent 載入的講座流程 skill 只剩 lecture2notes 一份，且內容與 submodule 釘住的版本一致、可用一個指令驗證。
- 使用者的 V4 frontmatter、faithful、pbf 與 186 條對照表在 lecture2notes 下持續生效，且留在 rad-workflow 版控內。
- 退役過程可逆：Git 內以歷史還原，Git 外以退役資料夾還原。

**Non-Goals:**

- 不動 .worktrees 下任何 worktree 與其分支。
- 不修改 lecture2notes 產品原始碼。
- 不變更 obsidian-v4-cleanup 的 canonical 位置與同步方式，只搬走它的過期分岔副本。

## Decisions

### submodule 位置與版本釘選

submodule 放在 vendor/lecture2notes，checkout 在 v0.2.1 tag（detached HEAD）。升級方式為進入 submodule 取得新 tag、回到上層 commit 指標，再跑部署腳本。選 vendor 目錄而非 skills 目錄，是因為 sync_skills.py 會自動掃 skills 下含 SKILL.md 的子目錄；lecture2notes 的 skill 檔在其 repo 的 skill 子目錄，放在 skills 之外可確保不被當成另一個要散佈的 skill。

替代方案：釘 main 分支——每次 clone 結果不同，overlay 相容性無法保證。

### overlay 內容與對照表轉換

skills-overlay/lecture2notes/ 為 overlay 的 canonical。五個檔名與 lecture2notes 的 overlay 規格一致。corrections.json 由舊對照表一次性轉換：deterministic 與 radiology 兩區進入新格式的確定性取代區，context_sensitive 進入新格式的語境區；每條保留原 source 欄位值，缺 source 者填 `rad-workflow-legacy`。轉換腳本為一次性工具，放在 scratchpad 執行、不進版控；轉換後以條數（135＋44＝179 與 7）與抽樣 10 條人工比對驗收。新格式的鍵名以 submodule 內 generic profile 的 corrections.json 為準，實作時先讀該檔再轉換。

outputs.toml 設 profile 為 radiology、note.style 為 faithful、pbf 為 true、hub 為 true。note.frontmatter.yaml 含 title、date、DateRev、aliases、noteVer、tags、subspecialty、tier、消化層級、source、sourceType，其中消化層級預設 1。

替代方案：把對照表留在舊路徑並讓 l2n 以 `--corrections` 指過去——每次都要帶旗標，agent 會漏。

### 部署腳本與 drift 檢查

deploy_lecture2notes.py（repo 根目錄，與 sync_skills.py 同層）：

- 無旗標：依序執行 (1) 確認 vendor/lecture2notes 已初始化且位於某個 tag；(2) 以目前的 Python 對 submodule 做 editable 安裝；(3) 執行 `l2n install-skill --all`；(4) 把 skills-overlay/lecture2notes/ 下五個 overlay 檔逐檔複製到使用者家目錄的 .lecture2notes/（覆蓋同名檔、不刪其他檔）；(5) 執行 `l2n profile show` 並印出 note.style、pbf、profile 三個鍵的值與來源層。每步印一行 ASCII 標記的進度。
- `--check`：不寫任何檔；執行 `l2n install-skill --check --all`，並以 sha256 逐檔比對 overlay 來源與家目錄副本；全部一致 exit 0，否則列出差異檔並 exit 2；l2n 不在 PATH 時 exit 3 並印安裝指令。
- `--home <path>`：測試用，覆寫家目錄位置（同時傳給 l2n 的環境變數 HOME 與 USERPROFILE）。

測試 tests/test_deploy_lecture2notes.py 以暫時家目錄與假的 l2n 可執行檔（記錄被呼叫的參數）驗證步驟順序、overlay 複製、`--check` 的三種 exit code；不實際 pip 安裝。

替代方案：擴充 sync_skills.py——它的職責是散佈 skills 目錄，混入套件安裝與家目錄 overlay 會讓 `--check` 的語意變複雜。

### 舊 skill 退役採搬移而非刪除

- Git 追蹤的 skills/lecture-to-notes 與 skills/whisper-srt-zh：git rm，commit 訊息記錄最後一個含它們的 commit，供日後 `git checkout <sha> -- <path>` 還原。
- Git 以外的副本：搬到 `~/.claude/skills-retired-20260922/` 下，保留原始相對結構（例如 `user-claude/lecture-to-notes`、`user-agents/whisper-srt-zh`、`project-claude/…`、`vault-claude/obsidian-v4-cleanup`、`vault-tmp/obsidian-v4-cleanup`）。搬移前逐一確認目標不是 junction 或 symlink 的來源端；`~/.claude/skills/obsidian-v4-cleanup` 這個 junction 與其目標 `~/.agents/skills/obsidian-v4-cleanup` 都不動。
- 搬移後跑 `python sync_skills.py` 與 `python sync_skills.py --check`，確認三家專案資料夾只剩仍在 skills 目錄下的 skill。
- OneDrive 會鎖資料夾：搬移用逐檔 copy 再逐檔移除來源，失敗的檔列出後重試一次，仍失敗則回報，不強制。

替代方案：直接刪除——不可逆，且使用者層副本不在任何版控下。

### 指引與歷史文件

CLAUDE.md：路由表加一列「講座影片→筆記：用 lecture2notes skill 與 `l2n`；升級與部署見 skills-overlay/lecture2notes/README.md」，常用指令加部署與檢查兩行，核心規則第 7 條補一句 lecture2notes 不經 sync_skills.py。三份引用舊腳本路徑的歷史文件只在檔頭加一行註記，不改內文。docs/PITFALLS.md 加一條：submodule 未初始化時部署腳本的症狀與修法。

### 遷移後實跑驗收

以 lecture2notes repo 內的 CC BY fixture 短片，在 repo 以外的暫存目錄跑 transcribe（faster_whisper、tiny、英文）→ frames → scaffold → render → check note，確認：frontmatter 含 noteVer 與 消化層級、筆記內的 style 標記為 faithful、`l2n profile show` 顯示 corrections 條數為 186 加上 radiology profile 內建條數、profile 來源為 user 層。結果寫進 skills-overlay/lecture2notes/README.md 的「部署驗證」段。

## Implementation Contract

**可觀察行為**

- `git submodule status` 顯示 vendor/lecture2notes 位於 v0.2.1。
- `python deploy_lecture2notes.py` 結束後，`~/.claude/skills/lecture2notes`、`~/.agents/skills/lecture2notes`、`~/.config/opencode/skills/lecture2notes` 三處各有 SKILL.md 與六份 references；`~/.lecture2notes/` 有五個 overlay 檔；`python deploy_lecture2notes.py --check` exit 0。
- 任一家的 SKILL.md 或家目錄 overlay 被手改一行後，`--check` exit 2 並指名該檔。
- `l2n profile show` 報告 note.style 為 faithful、pbf 為 true、profile 為 radiology，來源層皆為 user。
- skills 目錄下不再有 lecture-to-notes 與 whisper-srt-zh；三家專案資料夾與使用者層也沒有；`~/.claude/skills-retired-20260922/` 內可找到每一份被搬走的副本。
- obsidian-v4-cleanup 在 `~/.agents/skills/` 的副本與 junction 不變，`python sync_skills.py --check` exit 0。

**介面**

- `python deploy_lecture2notes.py [--check] [--home <path>]`，exit code：0 成功、2 drift 或前置條件不符、3 缺 l2n。
- overlay 檔名：note.frontmatter.yaml、note.template.md、corrections.json、outputs.toml、privacy.toml。

**失敗模式**

- submodule 未初始化：印 `run: git submodule update --init vendor/lecture2notes` 並 exit 2，不做任何安裝。
- submodule 不在 tag 上：印目前的 commit 與警告後繼續（開發情境）。
- 家目錄 overlay 複製中途失敗：已複製的檔保留、印出失敗檔與原因、exit 2；重跑即可（逐檔覆蓋為冪等）。
- 搬移退役副本時檔案被鎖：列出未搬成功的路徑，不刪除任何來源，exit 非 0。

**驗收**

- tests/test_deploy_lecture2notes.py 全過；既有測試不退步。
- `python deploy_lecture2notes.py --check` 與 `python sync_skills.py --check` 皆 exit 0。
- 對照表條數：轉換後確定性區 179 條、語境區 7 條。
- 遷移後實跑驗收段的四項皆成立。
- `git status` 無含病歷號或機密的檔案被加入；.gitignore 行數與內容不變。

## Risks / Trade-offs

- editable 安裝綁定本機路徑，repo 搬家後 l2n 失效 → 部署腳本重跑即可修復，README 記載。
- 使用者層同名 skill 會遮蔽專案層 → lecture2notes 只裝使用者層三家，專案層不放，避免兩層版本不一致。
- 退役資料夾長期佔空間 → README 註明確認一個月無問題後可自行刪除。
- 歷史計畫文件仍描述舊腳本 → 檔頭註記指向新產品；rebuild-nr-viewer worktree 保留，日後若要續做需先改以 l2n 為基礎。

## Migration Plan

1. 等 lecture2notes v0.2.1 發布後加入 submodule 並 commit。
2. 建 overlay 與轉換對照表，commit。
3. 寫部署腳本與測試，commit。
4. 執行部署，跑 `--check` 與實跑驗收。
5. 確認新 skill 可用後才退役舊 skill（先 Git 外搬移、再 git rm），跑兩個 `--check`。
6. 更新指引與記憶，commit。
7. 回滾：`git revert` 退役的 commit 還原 skills 目錄、從退役資料夾搬回使用者層副本、`python sync_skills.py`。

## Open Questions

- 無。worktree 的去留已明確排除在本案之外。
