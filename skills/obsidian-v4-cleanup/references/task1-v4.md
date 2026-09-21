## Task 1: V4 YAML Frontmatter Standardization

### Target Format

```yaml
---
title: <標題>
date: <YYYY-MM-DD>
DateRev: <YYYY-MM-DD>
aliases: []
noteVer: v4
tags: []
subspecialty: NR
消化層級: 0
source:
  - "來源描述"
---
```

### Fix Checklist (apply in order)

1. **aliases**：這個欄位是**搜尋入口**，不是標題變體清單。不再只做空陣列正規化，而是填入 2–4 個「未來的我會實際打出來去搜的字」：
   - 疾病／病灶的中文俗稱、英文全名與縮寫（例：`["椎間盤突出", "HIVD", "disc herniation"]`）
   - 若這份筆記是為了某個具體場合而做（某項專科考試、某堂課、某個專案），把那個場合的名稱也放進去
   - 論文筆記不要只放論文標題——使用者不會用論文標題搜尋，而是用臨床問題搜尋
   只有在真的想不出任何人會搜的字時才留 `[]`。
2. **noteVer**: `- v4` (list) → `v4` (scalar). Any other version → `v4`
3. **tags**: null/empty → `[]`. Remove tags that duplicate the subspecialty (e.g., `#NR` when subspecialty is already NR)
4. **subspecialty**: `- NR` (single-item list) → `NR` (scalar). Only use list when genuinely cross-specialty
5. **消化層級**（取代舊欄位 `已完成`）：整數 0–3，語意是「這份筆記被消化到哪一層」：
   - `0` 未處理／材料還沒進來
   - `1` AI 已寫完筆記，沒人看過
   - `2` 看過了，但沒在筆記裡留下任何自己的字
   - `3` **答過 `## 題目` 的題並留下任何修改**（在題目區留下答案、註記、標記答錯、改寫題目，或改寫過任一 reader-voice 節點皆算）——二元判準，看 `## 題目` 區有沒有本人留下的字即可驗證
   **AI 產出任何筆記時一律自動填 `1`。** 只有人為編輯能把它推到 `2` 或 `3`，AI 不得自行填 `2` 或 `3`。
   特別注意：模型預寫的候選（`## 我應該記住的 3 件事` 下方的摺疊 callout、canvas 的 reader-voice 節點、
   `## 題目` 的題目與答案）**一律不算使用者的字**；只要使用者一個字都沒改，`消化層級` 就停在 `1`。
   遷移舊檔：`已完成: false` → `消化層級: 0`；`已完成: true` → `消化層級: 2`（無法回溯判定，保守估計）。
   （選配，目前不實作）回看時段與回看流程 Step R：三個月後依 `消化層級` 的實際分佈再決定要不要做。
6. **date**: If it's a list like `[2021-06-23, 2022-08-06]`, keep only the earliest date. If comma-separated string, take the first date
7. **DateRev**：只在這次作業改動了「`# Note` 以下的實質內容」時，才更新為今天。
   若本次僅做 YAML 正規化、footnote 轉換、callout 轉換等格式整理，**DateRev 保持原值不動**；若欄位完全缺失才補上今天。
   （DateRev 要能回答「這份筆記上次被我實質更新是什麼時候」，而不是「上次被腳本掃過是什麼時候」。）
8. **source**: Extract from the note body — look for lecturer names, course titles, URLs, book references. Format as list of quoted strings: `- "description"`. If empty, set `- ""`

### Fields to DELETE

Remove these non-standard fields entirely:
- `keyperson`
- `PrivateData`
- `到期日`
- `source_PDF`
- `location`
- Any field with `dv_` prefix

### Inline Fields to Keep

After the closing `---`, keep these inline fields:

```markdown
Topics :: [[topic1]], [[topic2]] <br>
Parent Link :: [[parent]], [[=索引頁]] <br>
sibling :: [[相關筆記]] <br>
```

- `sibling ::` links notes covering the same topic across different years or versions (e.g., `sibling :: [[2024乳疑陽課程]]` in the 2025 version). Only add when there's a clear sibling relationship.

- Replace template placeholder text like `{筆記和什麼有關...}` with actual `[[wikilinks]]` based on the note's content
- For Parent Link, add the corresponding index page based on subspecialty:

| subspecialty | Index page |
|---|---|
| NR | `[[=NR]]` |
| H&N | `[[=H&N]]` |
| ABD | `[[=ABD]]` |
| CH | `[[=CH]]` |
| CV | `[[=CV]]` |
| IR | `[[=IR]]` |
| MSK | `[[=MSK]]` |
| PED | `[[=PED]]` |
| US | `[[=US]]` |
| Physics | `[[=物理]]` |

### Old Inline Metadata to DELETE

Remove these lines entirely (they were migrated to YAML in V4):

```
Status :: #...
Source type :: #📥/...
Source URL :: ...
Note Type :: #...
Subspecialty :: [[=...]]
source :: <br>
完成度 :: ...
Author :: ...
score :: ...
```

### Section Structure

Ensure the note body follows this skeleton (add missing sections as empty headers):

```markdown
# Evergreen Note
# Summary
# Note (layer 1-3)
（content here, headings start at ##）

### 參考來源
（footnote definitions）

## 題目
（quiz content — preserve <!--SR:!...--> comments!）

## 閱片
（image case callouts）
```

- `# 考題` or `# 交換考` → rename to `## 題目`
- Top-level `#` headings in the body (like `# Anatomy`, `# 治療`) should be demoted to `##` so they sit under `# Note (layer 1-3)`
- Sub-sections adjust accordingly (`##` → `###`, etc.)

---
