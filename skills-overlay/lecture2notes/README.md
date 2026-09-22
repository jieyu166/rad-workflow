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
