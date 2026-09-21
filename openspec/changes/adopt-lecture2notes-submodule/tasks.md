## 1. Submodule 與 overlay

- [ ] 1.1 依「submodule 位置與版本釘選」加入 submodule 完成「Pinned submodule」：`git submodule add https://github.com/jieyu166/lecture2notes vendor/lecture2notes`，checkout v0.2.1 tag 後 commit；驗證：`git -C vendor/lecture2notes describe --tags --exact-match` 印 v0.2.1，`python sync_skills.py --check` 輸出不含 lecture2notes 且 exit 0
- [ ] 1.2 依「overlay 內容與對照表轉換」建立 skills-overlay/lecture2notes/ 的 note.frontmatter.yaml、note.template.md、outputs.toml、privacy.toml 完成「Versioned personal overlay」的模板與設定部分：先讀 submodule 內 generic 與 radiology profile 的同名檔確認格式；frontmatter 含 title、date、DateRev、aliases、noteVer、tags、subspecialty、tier、消化層級、source、sourceType；outputs.toml 設 profile=radiology、note.style=faithful、pbf=true、hub=true；驗證：把該目錄複製到暫時家目錄的 .lecture2notes 後 `l2n profile show --json` 無解析錯誤且三個鍵來源為 user
- [ ] 1.3 依「overlay 內容與對照表轉換」把 skills/whisper-srt-zh/references/corrections.json 轉成 overlay 的 corrections.json（轉換腳本放 scratchpad 不進版控；新格式鍵名以 submodule 內 generic profile 的 corrections.json 為準；缺 source 者填 rad-workflow-legacy）；驗證：確定性區 142 條、語境區 44 條、每條 source 非空，並抽樣 10 條與原檔逐條比對一致

## 2. 部署腳本

- [ ] 2.1 依「部署腳本與 drift 檢查」實作 deploy_lecture2notes.py 的無旗標流程與 `--home`，完成「Deployment script」：submodule 初始化檢查（未初始化印 `run: git submodule update --init vendor/lecture2notes` 並 exit 2）、editable 安裝、`l2n install-skill --all`、逐檔複製五個 overlay 檔、印 note.style／pbf／profile 的值與來源；每步一行 ASCII 進度；驗證：tests/test_deploy_lecture2notes.py 以暫時家目錄與記錄參數的假 l2n 斷言呼叫順序、五檔位元組相同、exit 0，以及未初始化時 exit 2 且未呼叫安裝
- [ ] 2.2 實作 `--check` 完成「Drift check」：不寫任何檔、呼叫 `l2n install-skill --check --all`、sha256 逐檔比對 overlay，exit 0／2／3；驗證：同一測試檔斷言改動 outputs.toml 一個位元組後輸出指名該檔且 exit 2、PATH 無 l2n 時 exit 3 且訊息含 deploy_lecture2notes.py、`--check` 前後暫時家目錄的檔案清單與 mtime 相同
- [ ] 2.3 在本機實際執行部署：`python deploy_lecture2notes.py`，再 `python deploy_lecture2notes.py --check`；驗證：三家使用者層目錄各有 lecture2notes/SKILL.md 與六份 references、家目錄 .lecture2notes 有五個 overlay 檔、`--check` exit 0、`l2n profile show` 顯示 faithful／pbf true／radiology 且來源為 user

## 3. 遷移後實跑驗收

- [ ] 3.1 依「遷移後實跑驗收」完成「Post-migration verification run」：在 repo 以外的暫存目錄（絕對路徑）以 submodule 內的 CC BY fixture 跑 transcribe（faster_whisper、tiny、en）→ frames → scaffold → render → check note；驗證：骨架 frontmatter 含 noteVer 與 消化層級、含 faithful 的 style 標記、`l2n profile show` 的 overlay 來源為 user、對照表條數為 186 加 radiology profile 內建條數；四項結果連同日期與版本寫入 skills-overlay/lecture2notes/README.md 的「部署驗證」段

## 4. 舊 skill 退役

- [ ] 4.1 依「舊 skill 退役採搬移而非刪除」完成「Copies outside version control are moved, not deleted」：先記錄 `~/.agents/skills/obsidian-v4-cleanup` 全部檔案的 sha256 與 `~/.claude/skills/obsidian-v4-cleanup` 的 junction 目標；把使用者層與三家專案層的 lecture-to-notes、whisper-srt-zh 副本，以及 vault 內 `.claude/skills/obsidian-v4-cleanup` 與 `tmp/skill-validate/obsidian-v4-cleanup` 兩份過期分岔，逐檔 copy 到 `~/.claude/skills-retired-20260922/<原位置名>/` 後移除來源；被鎖的檔列出、保留來源、回報；驗證：退役資料夾每個子資料夾都有 SKILL.md、原位置不再有這兩個 skill 的資料夾、obsidian-v4-cleanup 的 sha256 與 junction 前後相同
- [ ] 4.2 完成「Legacy lecture skills leave version control」：`git rm -r skills/lecture-to-notes skills/whisper-srt-zh`，commit 訊息記錄最後一個含它們的 commit hash；接著 `python sync_skills.py` 與 `python sync_skills.py --check`；驗證：`git ls-files skills` 無這兩個前綴且 obsidian-v4-cleanup 仍在、兩個指令皆 exit 0、`git checkout <記錄的 hash> -- skills/whisper-srt-zh` 可還原（驗證後再移除還原出的檔）
- [ ] 4.3 確認「Worktrees are out of scope」：退役前後各記錄一次 `git worktree list` 與 `git branch --list`；驗證：兩次記錄完全相同，現況（各 worktree 的未提交檔數與未合併 commit 數）寫入 skills-overlay/lecture2notes/README.md

## 5. 指引與記憶

- [ ] 5.1 依「指引與歷史文件」完成「Guidance points to the new product」：CLAUDE.md 路由表加一列、常用指令加部署與檢查兩行、核心規則第 7 條補一句 lecture2notes 不經 sync_skills.py（Spectra 區塊外本文維持 60 行以內）；三份歷史文件各在檔頭加一行註記；docs/PITFALLS.md 加 submodule 未初始化的症狀與修法；README.md 的目錄說明加 vendor 與 skills-overlay；驗證：`grep -n lecture2notes CLAUDE.md` 有路由列與 deploy_lecture2notes.py，三份歷史文件的 `git diff --stat` 各為 1 行新增
- [ ] 5.2 撰寫 skills-overlay/lecture2notes/README.md：overlay 各檔用途、升級 submodule 的步驟、部署與檢查指令、退役資料夾位置與一個月後可自行刪除的說明、回滾步驟；驗證：檔案含「升級」「部署驗證」「回滾」「退役」四個段落標題
- [ ] 5.3 更新自動記憶：project_skill_canonical_locations.md 與 project_lecture2notes.md 反映新現況（lecture2notes 由 submodule 與 deploy 腳本管理、舊兩個 skill 已退役、退役資料夾位置）；驗證：MEMORY.md 索引對應條目的描述已更新，兩個記憶檔不再稱舊 skill 為 canonical
