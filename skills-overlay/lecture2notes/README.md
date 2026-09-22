# lecture2notes overlay

這個目錄是 lecture2notes 的**個人 overlay canonical**：使用者對筆記格式、輸出設定、ASR 對照表與個資比對樣式的所有客製化，只改這裡，不改 `vendor/lecture2notes/` 套件本身。overlay 設定解析順序（由高到低，先命中的贏）：

```
CLI 參數 > 專案內 .lecture2notes/ > 家目錄 ~/.lecture2notes/ > profiles/<name>/（如 radiology） > 套件內建
```

本目錄部署後即成為使用者家目錄的 `~/.lecture2notes/`——也就是上面這一層。

## 目錄內容

- `note.frontmatter.yaml`：筆記 frontmatter 模板，取代（不是疊加）下層 profile 的 frontmatter；含 vault V4 欄位 `title`、`date`、`DateRev`、`aliases`、`noteVer`、`tags`、`subspecialty`、`tier`、`source`、`sourceType`，以及本 vault 自訂的 **消化層級**（0=只有骨架、1=AI 已寫完沒人看過、2=看過但沒留下自己的字、3=答過題並留下修改；AI 產出一律從 1 起算）。
- `note.template.md`：筆記正文模板，用的是 radiology 版——比通用模板多一段「# 閱片」，內含 `[!reading-case]`（影像判讀）、`[!reading-pearl]`（判讀要點）、`[!differential]`（鑑別診斷）三個 Obsidian callout。
- `outputs.toml`：輸出設定，逐鍵合併下層。設 `profile = "radiology"`（啟用閱片模板與放射術語對照表）、`note.style = "faithful"`（保留講者原話，不摘要成 concise）、`pbf = true`（輸出 PotPlayer 章節檔）、`hub = true`（產生課程首頁）。
- `corrections.json`：ASR 對照表，由舊 `skills/whisper-srt-zh/references/corrections.json` 一次性轉換而成。舊表的 deterministic（135 條）與 radiology（44 條）兩區合併進新格式的確定性取代區（共 179 條），舊表的 context_sensitive（7 條）進新格式的語境區；每條的 `source` 標為 `rad-workflow-legacy`，因為舊表本身沒有逐條 source 欄位可以延用。
- `privacy.toml`：`l2n check note` 用來抓病患識別資訊的正規表示式樣式（病歷號、病人/病患標籤、電話、email、radtracker case_id 等）；`patterns` 是單一鍵、整表取代下層，所以每次改動要確認沒有漏掉下層原有的樣式。

改 overlay 的標準流程：改這裡的檔 → 回到 repo 根目錄跑 `python deploy_lecture2notes.py`（覆蓋 `~/.lecture2notes/` 對應檔）→ `python deploy_lecture2notes.py --check`（確認沒有 drift）。

## 升級

升級 lecture2notes 版本（submodule）：

1. 進入 `vendor/lecture2notes`，取得新版 tag：`git fetch --tags && git checkout vX.Y.Z`（detached HEAD 即可，與目前 v0.2.1 的釘法一致）。
2. 回到上層 repo，把新的 submodule 指標 commit 進去：`git add vendor/lecture2notes && git commit`。
3. 跑部署腳本套用新版：`python deploy_lecture2notes.py`。
4. 跑 `python deploy_lecture2notes.py --check` 確認三家 skill 目錄與家目錄 overlay 都與新版一致。
5. 若新版的 overlay 檔格式（例如 frontmatter 鍵名、`outputs.toml` 的鍵）有變動，對照 `vendor/lecture2notes/README.md` 的「Overlay 設定」段調整這五個檔，再重跑第 3、4 步。

## 部署與檢查

- `python deploy_lecture2notes.py`：依序確認 submodule 已初始化並在某個 tag 上、對 submodule 做 editable 安裝、執行 `l2n install-skill --all`、把本目錄五個檔逐一複製到 `~/.lecture2notes/`、印出 `note.style`／`pbf`／`profile` 的值與來源層。exit code：`0` 成功；`2` 前置條件不符（例如 submodule 未初始化）或複製中途失敗；`3` PATH 找不到 `l2n`。
- `python deploy_lecture2notes.py --check`：不寫任何檔，只跑 `l2n install-skill --check --all` 並以 sha256 逐檔比對本目錄與 `~/.lecture2notes/` 的內容。exit code：`0` 一致；`2` 有 drift（會列出差異檔）；`3` 缺 `l2n`。
- 全新 clone 這個 repo 時，submodule 預設是空的，需要先 `git clone --recurse-submodules ...`，或事後補一次 `git submodule update --init vendor/lecture2notes`，否則部署腳本會 exit 2 並提示這行指令。

## 回滾

若要整套退回舊的 `skills/lecture-to-notes`／`skills/whisper-srt-zh`：

1. 還原 Git 內移除的內容：`git revert <退役 commit c21fdc9>`（優先，保留歷史記錄）；或若只想先取回檔案本身、之後再決定要不要正式 revert，可用 `git checkout c22a2f8 -- skills/whisper-srt-zh skills/lecture-to-notes`。
2. 從退役資料夾把 Git 外的使用者層副本搬回原位（見下方「退役紀錄」的完整清單），至少包含：
   - `~\.claude\skills-retired-20260922\user-claude\lecture-to-notes` → `~\.claude\skills\lecture-to-notes`
   - `~\.claude\skills-retired-20260922\user-claude\whisper-srt-zh` → `~\.claude\skills\whisper-srt-zh`
   - `~\.claude\skills-retired-20260922\user-agents\whisper-srt-zh` → `~\.agents\skills\whisper-srt-zh`
3. 跑 `python sync_skills.py`，把還原後的 `skills/` 內容重新散佈到三家專案資料夾。

回滾後 lecture2notes 的三家 agent skill 目錄（`~/.claude/skills/lecture2notes`、`~/.agents/skills/lecture2notes`、`~/.config/opencode/skills/lecture2notes`）不會自動消失；用 `l2n install-skill --check --all` 確認它們是否仍與 submodule 版本一致，若決定不再並行使用兩套，可直接手動刪除這三個目錄。

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

## 退役紀錄

退役日期：2026-09-22。版控外副本一律**搬移不刪除**，退役資料夾：
`C:\Users\jai16\.claude\skills-retired-20260922\`（子資料夾名＝原位置）。

| 退役資料夾內路徑 | 原位置 | 檔數 |
|---|---|---|
| `user-claude\lecture-to-notes` | `~\.claude\skills\lecture-to-notes` | 24 |
| `user-claude\whisper-srt-zh` | `~\.claude\skills\whisper-srt-zh` | 4 |
| `user-agents\whisper-srt-zh` | `~\.agents\skills\whisper-srt-zh`（112 行舊版分岔） | 4 |
| `project-claude\lecture-to-notes` | `rad-workflow-main\.claude\skills\lecture-to-notes` | 21 |
| `project-claude\whisper-srt-zh` | `rad-workflow-main\.claude\skills\whisper-srt-zh` | 4 |
| `project-agents\lecture-to-notes` | `rad-workflow-main\.agents\skills\lecture-to-notes` | 21 |
| `project-agents\whisper-srt-zh` | `rad-workflow-main\.agents\skills\whisper-srt-zh` | 6 |
| `project-opencode\lecture-to-notes` | `rad-workflow-main\.opencode\skills\lecture-to-notes` | 21 |
| `project-opencode\whisper-srt-zh` | `rad-workflow-main\.opencode\skills\whisper-srt-zh` | 4 |
| `vault-claude\obsidian-v4-cleanup` | `Radiology\.claude\skills\obsidian-v4-cleanup`（778 行過期分岔） | 3 |
| `vault-tmp-skill-validate\obsidian-v4-cleanup` | `Radiology\tmp\skill-validate\obsidian-v4-cleanup`（1023 行過期分岔） | 1 |

共 11 份、113 檔，逐檔 sha256 比對相同後才移除來源，無被鎖或失敗的檔。
未動：`~\.agents\skills\obsidian-v4-cleanup`（本體）與 `~\.claude\skills\obsidian-v4-cleanup`（指向它的 junction）、
`skills\obsidian-v4-cleanup`（canonical）、剛部署的 lecture2notes 三家副本。

Git 內移除：commit `c21fdc97a0088b0e5d268d5bd8e2fa4a5ed40b39`
（`chore(skills): retire lecture-to-notes and whisper-srt-zh`）。
最後一個含舊 skill 的 commit：`c22a2f81513d725a9b92d7f5f0bdb7413be9752b`。還原指令：

```bash
git checkout c22a2f81513d725a9b92d7f5f0bdb7413be9752b -- skills/whisper-srt-zh
git checkout c22a2f81513d725a9b92d7f5f0bdb7413be9752b -- skills/lecture-to-notes
```

還原已於 2026-09-22 實測通過（whisper-srt-zh 4 檔含 scripts 與 references 全數回來），測後已還原為退役狀態。

確認一個月無問題後（約 2026-10-22），可自行刪除整個 `C:\Users\jai16\.claude\skills-retired-20260922\` 資料夾。

## Worktree 現況

本次遷移**未動任何 worktree、未刪除任何分支**；下表為 2026-09-22 退役當下的狀態快照，僅供日後接手參考。

| 路徑 | 分支 | 未提交檔數 | 相對 main 未合併 commit |
|---|---|---|---|
| `.claude\worktrees\great-kirch-1a3518` | `claude/great-kirch-1a3518` | 1 | 0 |
| `.worktrees\image-stack-mpr-viewer` | `codex/image-stack-mpr-viewer-clean` | 0 | 0 |
| `.worktrees\rebuild-nr-viewer` | `codex/rebuild-nr-viewer` | 24 | 0 |
| `.worktrees\turtle-trader-manga` | `codex/turtle-trader-manga` | 7 | 53 |

`.worktrees\card-rewards-2026-h2` 不是註冊的 git worktree（`git worktree list` 未列出），同樣未動。

退役前後各記錄一次 `git worktree list` 與 `git branch --list`：worktree 路徑與分支清單、分支列表完全相同；
唯一差異是主 worktree 的 HEAD 由 `c22a2f8` 前進到 `c21fdc9`，即本次退役 commit 本身。
`.worktrees\rebuild-nr-viewer` 的 24 個未提交變更直接針對舊 `skills/lecture-to-notes/scripts/*`；
若日後要續做該工作，需先 `git checkout c22a2f8 -- skills/lecture-to-notes` 還原，或改以 `l2n` 為基礎重寫。
