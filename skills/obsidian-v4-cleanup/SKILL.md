---
name: obsidian-v4-cleanup
description: Obsidian 放射科筆記的標準化與深度整理。Task 1 V4 YAML frontmatter、Task 2 引用轉腳註、Task 3 閱片表格轉 callout、Task 5 PDF 深讀（忠實翻譯底稿 + 覆蓋率 gate + canvas 地圖）、Task 8 現代新知查核。Trigger：整理, 修正, cleanup, V4, YAML fix, footnote conversion, 閱片 callout, 論文筆記, paper summary, 讀書筆記, 章節整理, textbook, 教科書, 深度閱讀, 新知查核, 現代知識更新, outdated claim audit, guideline update。影片/講座/字幕/課程首頁 → 用 lecture-to-notes。
---

# Obsidian V4 Cleanup Skill

You are working with a Radiology Obsidian vault. Depending on the user's request, you apply one or more of 8 tasks. Always read the file first, assess which tasks apply, then execute them in order.

## Task Overview

> **Task 4／6／7 已移出**（2026-08-03）：影片整理、SRT 分段導航 JSON、課程系列目錄連同全部 scripts 搬到 **`lecture-to-notes`** skill。那條管線的 scripts 佔了本 skill 的全部腳本卻與本 skill 的主題無關，留在這裡只會讓兩邊都難找。編號保留不重排——`Task 5` 這個代號在別處被引用，重排的代價大於編號有缺口。

```
Tasks 1-3: Cleanup existing notes
  Read file → Assess needs → Task 1 (YAML) → Task 2 (Footnotes) → Task 3 (閱片) → Verify

Task 4: Organize video/lecture content
  Check Task 6 JSON exists → Read subtitle/audio + slide images (無投影片資料夾但有影片檔 → scripts/slide_frames.py 自動抓換頁截圖再 Read) + 官方筆記/講義 .html/.md (defuddle 解析，最高優先 ground truth) → Cross-reference to correct & enrich → Output V4 note

Task 5: PDF 閱讀筆記（L3 深度筆記 + Canvas 視覺地圖）
  Mode A (期刊論文): resolve PDF → extract + render every page → source inventory → faithful Stage 1 → quality gate → Stage 2 → canvas → verify
  Mode B (教科書章節): resolve PDF → extract + render every page → source-order full translation → quality gate → hierarchical reorganization → canvas → verify

Task 6: SRT → 分段 JSON（字幕導航檔）
  Read SRT + (optional) slide images/PDF → view images to correct terminology → segment into 8-15 chapters → (有影片檔 → scripts/slide_frames.py 抓換頁截圖併入每段 frame) → Output JSON for web player → (可選 → scripts/json_to_pbf.py 產 PotPlayer 章節檔 .pbf)

Task 7: 課程系列筆記（Course Listing Note）
  Collect lecture metadata → Create index note with wikilinks + media links → 目錄.md

Task 8: 任意筆記的現代新知查核（Modern Knowledge Audit）
  Read-only source-layer audit → Tier 1 research → claim-by-claim status matrix → archive → add a separately cited modern-update layer → verify
```

For cleanup (Tasks 1-3): Every file needs Task 1. Tasks 2 and 3 only apply if the file has inline citations or quiz-format 閱片 tables respectively.
Tasks 4-8 are standalone. Task 6 (SRT→JSON) is often an upstream step for Task 4 (影片整理). Task 8 audits an existing note without silently rewriting its historical/source-grounded layer.

---

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
已完成: false
source:
  - "來源描述"
---
```

### Fix Checklist (apply in order)

1. **aliases**: null/empty → `[]`
2. **noteVer**: `- v4` (list) → `v4` (scalar). Any other version → `v4`
3. **tags**: null/empty → `[]`. Remove tags that duplicate the subspecialty (e.g., `#NR` when subspecialty is already NR)
4. **subspecialty**: `- NR` (single-item list) → `NR` (scalar). Only use list when genuinely cross-specialty
5. **已完成**: null/empty → `false`
6. **date**: If it's a list like `[2021-06-23, 2022-08-06]`, keep only the earliest date. If comma-separated string, take the first date
7. **DateRev**: If missing, add it with today's date. If present, update to today's date
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

## Task 2: Inline Citation → Footnote Conversion

Only applies if the file contains `[Text](URL)` patterns that are external references (not wikilinks, not image embeds).

### Rules

1. Each **unique URL** gets a `[^n]` number starting from 1
2. Same URL appearing multiple times → same footnote number
3. All `[^n]:` definitions go in the `### 參考來源` block (between note body and `## 題目`)
4. Convert citations in quiz answers too

### Before → After

```markdown
<!-- Before -->
起源於 pituicytes [PubMed](https://pubmed.ncbi.nlm.nih.gov/20403698/)。

<!-- After -->
起源於 pituicytes [^1]。

### 參考來源
[^1]: https://pubmed.ncbi.nlm.nih.gov/20403698/
```

### DO NOT Convert

- **Synology NAS links** (`jieyu166.synology.me`): These are personal video/lecture files. Keep them as `[影片](url)` or `[講義](url)` — never convert to footnotes
- **Blockquote book references**: `> [[Essentials of Osborn's brain]]` — leave as-is
- **Wikilinks**: `[[other note]]` — leave as-is
- **Image embeds**: `![[image.png]]` — leave as-is
- **Radiopaedia/internal links used as inline references**: `[Anisotropy](https://radiopaedia.org/...)` — these are contextual links for quick reference, convert them to footnotes like other URLs

---

## Task 3: 閱片 Table → Callout Conversion

Only applies if the file contains quiz-format 閱片 tables. These are tables where each row is a case with an image and an answer, designed for self-testing.

### How to Identify Quiz-Format Tables

Quiz-format tables look like this — they have `#閱片` in the header and an `Ans` column:

```markdown
| #閱片 Topic | Ans |
| ----------- | --- |
| ![[image1.png]] | diagnosis description |
| ![[image2.jpg]] | another diagnosis |
```

### Convert To

```markdown
## 閱片

> [!case]- ![[image1.png]]
> diagnosis description

> [!case]- ![[image2.jpg]]
> another diagnosis
```

- Callout type: `case`
- `-` means collapsed by default
- Title: the image embed `![[filename]]`
- Body: the answer text (can be multi-line, supports markdown)

### Add YAML Field

When converting 閱片 tables, add a `閱片:` field to the YAML listing the disease names:

```yaml
閱片:
  - Disease name 1
  - Disease name 2
```

### DO NOT Convert

**Educational/descriptive tables** are NOT quiz tables. Leave these as-is:
- Anatomy reference tables (e.g., Shoulder US anatomy with structure descriptions)
- Comparison tables (e.g., BI-RADS categories, imaging feature comparisons)
- Statistical tables
- Any table where the purpose is reference/learning rather than self-testing

The key distinction: if a table has `#閱片` + `Ans` columns and each row is an image case to diagnose, it's a quiz table → convert. If it's organizing information for reference, leave it alone.

---

## Task 5: PDF 閱讀筆記

Applies when the user provides a PDF (journal paper, textbook chapter, or reference material) and asks for reading notes. This task always produces **L3 deep-study notes** plus a **visual canvas map**.

### Mandatory Default: PDF-grounded Reconstruction

Treat the actual PDF as the only medical-content ground truth. An existing `.md` may help locate omissions and preserve personal artifacts, but never use its prose, numbers, recommendations, figure interpretations, or citations as evidence.

For an existing note:

1. Resolve the exact PDF uniquely. If missing or ambiguous, stop that note as `source_pending`; do not overwrite it.
2. Before overwriting, archive the original note at the user-designated archive root while preserving its vault-relative path.
3. Record SHA-256 for the original, archive, PDF, and rebuilt note when working in an audit or batch.
4. Carry forward only personal artifacts that remain valid:
   - preserve SR comments exactly;
   - preserve Dataview blocks only when still semantically applicable;
   - preserve image embeds only when the target exists and the image belongs to this source;
   - preserve wikilinks only when the target exists and the relationship is useful;
   - otherwise leave the artifact only in the archived original.
5. Do not create placeholder wikilinks such as `[[]]`, speculative Topics, or automatic Parent links merely to preserve the old layout.

This Task 5 policy overrides the generic preservation rules under **Critical Safety Rules** when rebuilding an L3 note from a PDF.

### Non-negotiable Quality Gate

Define:

```text
Stage 1 coverage ratio =
non-whitespace characters between the Stage 1 and Stage 2 headings
÷
non-whitespace characters extracted from the PDF
```

- Require `ratio >= 0.20` by default. Treat this as a minimum anti-summary gate, not proof of completeness.
- If extracted PDF text is usable and the ratio is below 0.20, continue translating; do not write around the gate with filler, duplicated prose, figure-number lists, or copied English source text.
- If the PDF is scanned, OCR-poor, or extraction is clearly incomplete, mark the numeric ratio `N/A` and use page/section coverage plus visual verification instead. State the reason in the audit.
- Require every source section, figure ID, table ID, box, equation, and appendix to have an explicit disposition: translated/reconstructed, explained in a callout, or marked N/A with the source reason.
- Do not begin final Stage 2 condensation until Stage 1 passes the coverage and source-inventory checks.

### Core Design: Two-Stage Model

This is the most critical design decision. Splitting the work into two stages prevents the quality collapse that happens when translation, comprehension, restructuring, and condensation all compete in a single pass.

**Stage 1 — 忠實翻譯底稿**
Translate the original text in source order, segment by segment, into Taiwan Traditional Chinese (正體中文). Translate the substantive full text rather than producing a section summary. Every definition, numeric value, sample size, method, acquisition parameter, diagnostic threshold, condition, comparison, causal chain, limitation, and clinical implication must survive intact. Include figure captions, table contents, boxes, equations, and appendix material. Omit only running headers/footers, duplicated boilerplate, and the bibliography unless the user asks for it.

**Stage 2 — 結構重組**
Working from the Stage 1 draft, do two things:
- **Restructure（重排）**: Convert flat prose into a hierarchical outline. Each paragraph's internal logic — cause/effect, conditions, comparisons, general→specific — becomes visible through indentation levels.
- **Distill（去蕪）**: Remove filler words that carry no information. But **preserve all logical connectors**: 因為、所以、導致、若、則、除非、然而、但是、僅、所有. When in doubt, keep the word.

### Workflow

1. **Resolve source**: locate the exact PDF; record its path, page count, citation, edition, and SHA-256 when applicable.
2. **Archive existing note** before overwriting; confirm the archive hash equals the original hash.
3. **Extract text** page by page with page boundaries retained.
4. **Render every PDF page** to images. Build contact sheets for efficient review, then inspect full-resolution pages containing figures, tables, equations, small labels, or extraction anomalies.
5. **Build a source inventory**: original section hierarchy, page ranges, all figure/table/box/equation IDs, study design, sample size, important numbers, and appendices.
6. **Determine subspecialty** and create correct V4 YAML using the source edition—not newer classifications or outside knowledge.
7. **Write Stage 1 in source order** with bilingual headings mirroring the PDF. Work in bounded chunks and re-check the PDF after each chunk.
8. **Run the Stage 1 gate**: calculate the coverage ratio, check section coverage, and compare every figure/table ID against the inventory. Continue translating until all checks pass.
9. **Write Stage 2** from the verified Stage 1: restructure into a hierarchical clinical learning note without adding content.
10. **Write Summary**: Canvas link, One-liner, KEY TAKEAWAYS, and Slides Outline.
11. **Create and validate Canvas** in `Learning Map/`.
12. **Verify final artifacts**: YAML, citation, ratios, figures/tables, numbers, Canvas JSON, preserved artifacts, archive hashes, and absence of unresolved placeholders.

For batch work, finish and verify one PDF at a time. A failure blocks only that note; continue other uniquely resolved notes and record the exact blocker.

### Writing Rules (apply to all levels)

#### Title Structure: Mirror the Original

Section headings precisely reproduce the original document's hierarchy, including original numbering. Each heading is bilingual:

```markdown
## 3.2 椎間盤退化｜Disc Degeneration
### 3.2.1 訊號變化｜Signal Changes
```

This is essential because the reader will cross-reference the notes against the original — matching structure enables fast lookup.

#### Figure and Table Analysis

Figures and tables often contain information not mentioned in the body text. Skipping them is a significant loss.

First enumerate the source IDs from extracted text and visual pages. After writing the note, compare the two sets mechanically: every `Figure X-Y` and `Table X-Y` in the PDF must appear in Stage 1. Visually inspect every page containing a figure or table; extracted captions alone are insufficient for image findings, arrows, labels, graphs, or multi-panel relationships.

**For each figure**, add a collapsible analysis block:

```markdown
> [!figure]- **Figure 3.4** 椎間盤退化分級｜Pfirrmann Classification
> **結構描述**：（describe the figure so the reader can understand it without seeing it）
> **關鍵數值/縮寫**：Grade I–V, NP = nucleus pulposus, AF = annulus fibrosus
> **與本節關聯**：illustrates the MRI grading system described in 3.2.1
> **常見誤解**：Grade III often confused with Grade IV when NP signal is intermediate
> **臨床情境**：used in pre-surgical planning to determine candidacy for disc replacement
```

Only include `常見誤解` or `臨床情境` when the PDF supports it. Otherwise write `N/A（原文未涵蓋）`. Do not infer diagnoses from an unseen figure or invent a “typical” image to fill a template.

**For each table**, translate and reconstruct in markdown, then add a collapsible reading guide:

```markdown
| Grade | NP Signal | NP Structure | Disc Height | ... |
|-------|-----------|-------------|-------------|-----|
| I     | Bright    | Homogeneous | Normal      | ... |

> [!table-guide]- 讀表教學
> **行列意義**：rows = Pfirrmann grades I–V; columns = MRI characteristics
> **鑑別診斷用法**：compare NP signal + structure to distinguish Grade III vs IV
> **教學用途**：systematic grading approach for residents
> **常見陷阱**：disc height preserved in early degeneration (Grade II) may be falsely reassuring
```

Reconstruct the actual rows, columns, units, denominators, footnotes, and statistical qualifiers. If a table is too large for practical Markdown, preserve all information through a faithful structured synopsis and state exactly what was not reproduced.

The collapsible design is intentional — expand when first learning, collapse afterward for quick review.

#### Language Rules

1. **台灣正體中文**，避免中國大陸譯法（如：影像 not 图像，椎間盤 not 椎间盘）
2. 學術名詞首次出現括號保留英文（如：核磁共振（MRI）），之後可只寫中文
3. 藥物學名一律英文
4. 若涉及方程式，以 LaTeX 表示

#### 不做的事

1. **不把階層結構攤回散文** — the whole point is the hierarchy
2. **不過度精簡** — preserve all logical connectors and reasoning chains
3. **不加引用標記**（citation markers like [1], [2]）
4. **不保留章末參考文獻**（the original bibliography is omitted）
5. **不加開場白和收尾語**（no preamble like "以下是筆記整理..."）

---

### L3 Output: 深度筆記（唯一產出格式）

L3 outputs **both stages**: the full faithful translation (Stage 1) followed by the restructured outline (Stage 2), plus additional deep-dive sections and a visual canvas map.

```markdown
---
title: "Paper/Chapter Title"
date: YYYY-MM-DD
DateRev: YYYY-MM-DD
aliases: []
noteVer: v4
tags:
  - "L3"
subspecialty: XX
已完成: false
source:
  - "Author et al. Journal. Year" or "Author(s). Book Title. Edition. Publisher, Year. Chapter X."
---

# Summary
[[Learning Map/Note Title.canvas|Note Title]]

> [!abstract] One-liner
> 一句話核心價值

## KEY TAKEAWAYS
- 臨床要點
- 考試要點
- 教學要點

## Slides Outline
（one teachable concept per slide, ready for Google Slides via Apps Script）
1. **Slide title** — key message
2. **Slide title** — key message
3. ...

# Note (Stage 1 — 忠實翻譯)
（segment-by-segment faithful translation, every definition/value/condition preserved）
（bilingual section headings mirroring original structure）
（figure and table callouts included inline）

# Note (Stage 2 — 結構重組)

## Background｜背景
- 為什麼這個題目重要？
- 臨床上的問題或困境是什麼？

## X.1 第一節標題｜Original Section Title
（hierarchical outline — indented, logical connectors preserved）

> [!figure]- **Figure X.1** ...
> （figure analysis）

## X.2 第二節標題｜Original Section Title
（more content...）

| Column 1 | Column 2 | ... |
|----------|----------|-----|

> [!table-guide]- 讀表教學
> （table reading guide）

## Key Imaging Findings｜影像發現
### CT
- ...
### MRI
- ...
### US
- ...
（if paper only covers one modality, fill that and mark others N/A）

## Differential Diagnosis｜鑑別診斷

| 診斷 | 影像特徵 | 鑑別重點 |
|------|---------|---------|
|      |         |         |
（只列 PDF 支持的診斷；原文未涵蓋時寫 N/A，不強補三項）

## Classification / Staging｜分類分期
- ...

## Clinical Significance & Pitfalls｜臨床意義與陷阱
- ...

## 我應該記住的 3 件事
1.
2.
3.

## Important Figures｜重要圖片
- Fig X: {描述}

# Anatomy / Pathophysiology｜解剖與病理生理
- ...

# Management & Treatment｜處置與治療
- 只寫 PDF 明確支持的治療、影像決策角色與 follow-up
- 原文未涵蓋時寫 `N/A（原文未涵蓋）`

# Pearls
1. ...
2. ...

# 和我的知識庫的連結
- 僅加入已確認存在且確實有用的 wikilink
- 沒有可靠連結時寫 N/A；不得產生 placeholder link

# Questions for Further Study
- ...

### 參考來源

## 題目

## 閱片
```

---

### Visual Canvas Map（.canvas 視覺化摘要）

After writing the L3 .md note, create a companion `.canvas` file that provides a visual overview of the note's structure and concept relationships. This is valuable because it allows the reader to see the "big picture" at a glance in Obsidian's canvas view.

#### Canvas Location

Place the `.canvas` file in a `Learning Map/` subfolder relative to where the `.md` file is saved. Create the folder if it doesn't exist.

Example: if the .md is at `2. Areas/NR相關知識/2024 RG Paper Title.md`, the canvas goes to `2. Areas/NR相關知識/Learning Map/2024 RG Paper Title.canvas`.

#### Canvas Design Pattern

Follow the **JSON Canvas Spec 1.0** format. The canvas should visualize the note's knowledge structure, not just list sections:

**Central node** (color "6" purple, ~500×300, at position 0,0):
- `# Title` + core summary / evergreen note / key takeaway

**Surrounding concept nodes** — one per major knowledge unit, using semantic colors:
- "4" green: definitions, classification systems, anatomy
- "2" orange: key diagnostic criteria, imaging findings
- "1" red: warnings, pitfalls, contraindications
- "3" yellow: management decisions, clinical algorithms
- "5" cyan: evidence, landmark studies, statistics

**Group nodes** to cluster related sub-concepts (e.g., a "Radiotherapy" group containing Hypofractionation + Boost + Cardiac Protection nodes).

**Edges** with Chinese labels describing the logical relationship between concepts (e.g., "切緣標準", "復發處理", "鑑別診斷").

**File node** linking back to the original .md (path: vault-relative, e.g., `2. Areas/NR相關知識/2024 RG Paper Title.md`).

For a normal L3 source, default to approximately 9 nodes and 9 labeled edges: central concept, 6–7 major knowledge units/pitfalls, and one file node. Use a smaller 6-node/5-edge map only when the source is genuinely short. Node count is secondary to covering all major source units.

#### Layout Guidelines

- Spread nodes across x range -900 to 900, y range -500 to 700
- Don't just make a column of nodes — arrange them spatially to reflect logical groupings
- Use 50-100px spacing between nodes
- Keep text concise in nodes — bullet points, not paragraphs
- Use `\n` for newlines in JSON text strings (not literal newlines)
- Generate unique 16-character lowercase hex IDs for all nodes and edges

#### Canvas Link in .md

After creating the canvas, add a wikilink in the `.md` file's `# Summary` section, right after the `# Summary` heading. The link MUST include the `.canvas` extension (Obsidian requires it for non-.md files):

```markdown
# Summary
[[Learning Map/Note Title.canvas|Note Title]]
```

#### Minimal Canvas

If the source note has very little content (<15 meaningful lines), create a minimal canvas with just the central summary node + file node.

#### JSON Validation

After writing each canvas file, validate:
1. JSON parses without errors
2. All `id` values are unique across nodes and edges
3. Every `fromNode` and `toNode` in edges references an existing node ID
4. Required fields present for each node type

---

### Additional Rules for Task 5

1. 每個定義、數值、條件、因果推理、臨床意涵都必須保留，一個都不能丟
2. **source 欄位**格式：期刊用 `"First Author et al. Journal Abbreviation. Year;Volume:Pages"`；書籍用 `"Author(s). Book Title. Edition. Publisher, Year. Chapter X."`
3. 不可省略 imaging modality section — 即使只涉及一種影像模式，也要填寫並標註其他為 N/A
4. DDx、classification、management、treatment、follow-up 只寫 PDF 支持的內容；原文未涵蓋時明確寫 `N/A（原文未涵蓋）`
5. 不得把一般醫學知識、新版 WHO／guideline、典型 imaging pattern 或外部 cutoff 冒充原文內容；需要更新資訊時另立「外部更新」區並附來源，除非使用者要求，預設不加
6. Important Figures: 提取教學價值最高的圖片描述；完整 figure inventory 仍須在 Stage 1 逐號交代
7. 若有包含數據的表格，需解讀原文支持的數據走勢並保留 denominators、units、conditions 與 uncertainty
8. 所有關鍵數值、公式、sample size、scan parameters、diagnostic thresholds、treatment recommendations 與 conclusions 必須能定位至 PDF 頁面或章節
9. **Canvas 必須產生** — 每份 L3 筆記都要搭配一份 .canvas 視覺地圖

---

## Task 8: 任意筆記的現代新知查核

Applies when the user asks to verify, update, fact-check, modernize, or identify outdated medical/radiology knowledge in any existing note. The note may originate from a paper, textbook, lecture, website, conference, personal synthesis, or mixed sources; it does not need to be a Harnsberger or PDF L3 note.

Before acting, read [references/task8-modern-knowledge-audit.md](references/task8-modern-knowledge-audit.md) completely and follow it as the execution contract and reusable prompt.

### Non-negotiable Rules

1. **Separate knowledge layers**: preserve the note's original/source-grounded content as its historical layer. Put newer evidence in a distinct `# 現代新知查核` section. Never silently back-project a newer WHO classification, guideline, threshold, terminology, or recommendation into an older source.
2. **Establish the baseline**: resolve and read the note's declared sources when available. If the source is missing, ambiguous, mixed, or inaccessible, label claims `source_unresolved`; do not pretend the existing prose is verified source content.
3. **Research from evidence**: use `radiology-topic-research` for the modern layer. Prefer current society guidelines/consensus and WHO classifications, followed by STATdx, current ClinicalKey chapters, RadioGraphics, AJR, and Radiopaedia as structured support. Important claims require article/chapter/guideline-level citations.
4. **Audit claim by claim**: classify each material claim as `仍成立`, `需補充`, `已更新`, `已淘汰`, `來源衝突`, or `無法查證`. Preserve competing numbers or recommendations with separate citations.
5. **No unsupported completion**: if a Tier 1 page requires authentication, ask the user to log in and leave the item `待登入查核`. Do not substitute model memory or a weaker source and mark it complete.
6. **Read-only first, archive before write**: complete the audit matrix before modifying the note. Archive the original at the user-designated root, preserve its vault-relative path, and verify original/archive SHA-256 equality.
7. **Preserve personal artifacts**: keep SR comments exactly; retain valid embeds, Dataview blocks, and wikilinks without changing their semantics.
8. **Figures remain source figures**: external research may update how a figure is interpreted today, but must not add findings absent from the original image or rewrite its original caption as modern evidence.
9. **Batch discipline**: audit and verify one note at a time. A blocked note does not block other notes, but every blocker must be explicit.

### Required Note Addition

Append or update this independently cited layer:

```markdown
# 現代新知查核（查核日期：YYYY-MM-DD）

> [!update] 現代更新摘要
> 只列會影響目前判讀、報告、classification、protocol或management的變動。

## 仍然成立的核心觀念
## 已更新的術語與分類
## 新增的影像判讀重點
## 已不建議或已淘汰的觀點
## 現代 Management / Follow-up 差異
## 原有 Figures / Tables 的現代閱讀方式
## 證據分歧與尚未確定事項
## 新知查核矩陣

| 原筆記主張 | 原始來源定位 | 判定 | 現行知識 | Tier 1 證據 | 主文處理 |
|---|---|---|---|---|---|

### 新知查核參考來源
```

Do not force empty categories: write `N/A（本次查核未發現）`. Keep the original YAML `source` for original sources; record modern evidence in footnotes under the audit layer rather than presenting it as the original note's source.

### Deliverables

- Updated note with a separate modern layer
- Archived original and verified hashes
- Claim-level audit matrix with source locator and modern citation
- Audit report recording counts by status, access blockers, sources consulted, changes made, original/archive/replacement SHA-256, and PASS/FAIL
- Updated Canvas only when modern evidence materially changes the concept map; visually distinguish historical/source nodes from modern-update nodes

---

## Critical Safety Rules

For Tasks 1–4 and 6–7 cleanup, preserve the following exactly. For Task 5 PDF-grounded rebuilds, apply the stricter artifact policy under **Mandatory Default: PDF-grounded Reconstruction**. For Task 8, archive first, preserve the original/source layer, and add modern evidence only in the explicitly separated audit layer.

1. **Spaced Repetition comments**: `<!--SR:!2024-01-15,30,270-->` — do not touch these under any circumstance
2. **Image embeds**: `![[image.png]]` — preserve exactly during ordinary cleanup; validate before carrying into a Task 5 rebuild
3. **Embed references**: `![[other note#heading]]` — preserve exactly during ordinary cleanup; validate before carrying into a Task 5 rebuild
4. **Dataview queries**: ` ```dataview ... ``` ` blocks — preserve during ordinary cleanup; retain in Task 5 only when still applicable
5. **Existing wikilinks**: `[[any link]]` — never break them during ordinary cleanup; do not blindly copy stale or placeholder links into a Task 5 rebuild

---

## Bulk Processing

When the user asks to process an entire folder:

1. List all `.md` files in the folder
2. Write a Python script to assess all files and categorize issues
3. Write a bulk YAML fix script that handles all files programmatically
4. Run footnote conversion on files that need it (can be scripted or manual)
5. Handle 閱片 conversion manually per-file (requires judgment on table type)
6. Verify final state

For bulk YAML processing, use `ruamel.yaml` (preserves formatting better than PyYAML) or write YAML blocks manually with Python string operations to avoid serialization issues. Be careful with the `source` field — YAML serializers can split strings into individual characters if the field type is ambiguous.

### Common Bulk Script Pattern

```python
import os, re, yaml

NONSTD_FIELDS = {'keyperson', 'PrivateData', '到期日', 'source_PDF', 'location'}
OLD_INLINE_PATTERNS = [
    r'^Status\s*::.*', r'^Source type\s*::.*', r'^Source URL\s*::.*',
    r'^Note Type\s*::.*', r'^Subspecialty\s*::.*', r'^完成度\s*::.*',
    r'^source\s*::\s*<br>\s*$', r'^Author\s*::.*',
]

# For each file:
# 1. Parse YAML (handle errors gracefully — some files have malformed YAML)
# 2. Fix fields per checklist
# 3. Remove non-standard fields
# 4. Write back
# 5. Remove old inline metadata lines from body
```

---

## Verification

### Tasks 1-3 (Cleanup)
- [ ] YAML parses without errors
- [ ] All required V4 fields present with correct types
- [ ] No non-standard fields remain
- [ ] No old inline metadata lines remain
- [ ] Footnotes properly numbered and defined (if converted)
- [ ] 閱片 callouts use correct format (if converted)
- [ ] SR comments untouched
- [ ] Image embeds untouched

### Task 4 (影片整理)
- [ ] V4 YAML complete (source lists lecturer/course)
- [ ] Topics and Parent Link filled with actual wikilinks
- [ ] Evergreen Note 核心觀念 written
- [ ] Summary includes 易混淆觀念
- [ ] Note sections organized with ## headings
- [ ] Multi-source viewpoint differences marked (if applicable)
- [ ] 學習驗證 at least one item completed
- [ ] No fabricated content — everything sourced from provided materials
- [ ] **Slide images read** — if a companion image folder exists, slide images were viewed with Read tool and used for terminology correction
- [ ] **Image embeds placed** — `![[filename.png]]` embeds inserted at corresponding note sections
- [ ] **Terminology matches slides** — English medical terms in note match the slide image content, not the garbled ASR transcript

### Task 5 (PDF 閱讀筆記)
- [ ] Exact PDF resolved uniquely; unresolved/ambiguous sources were not overwritten
- [ ] Existing note archived before overwrite; original and archive SHA-256 match
- [ ] PDF text extracted with page boundaries and all pages rendered
- [ ] Every PDF page visually reviewed via renders/contact sheets
- [ ] Full-resolution visual review completed for every figure/table/equation page and extraction anomaly
- [ ] Source inventory covers every section, figure, table, box, equation, and appendix
- [ ] L3 format used (Stage 1 + Stage 2 both output)
- [ ] Stage 1 is a substantive source-order full translation, not a summary or translated outline
- [ ] Stage 1 non-whitespace/PDF extracted non-whitespace ratio is ≥0.20, or ratio is N/A with documented OCR/extraction reason and page-based coverage proof
- [ ] Ratio was not inflated with filler, duplication, copied English text, or identifier-only lists
- [ ] Stage 2 was written only after Stage 1 passed coverage checks
- [ ] Two-stage process applied (Stage 1 忠實翻譯 + Stage 2 結構重組)
- [ ] V4 YAML complete (source in proper citation format, tags: ["L3"])
- [ ] YAML parses; required fields and types are correct
- [ ] subspecialty correctly identified
- [ ] Title structure mirrors original with bilingual headings and numbering
- [ ] Hierarchical outline with proper indentation (not flat prose)
- [ ] All logical connectors preserved (因為、所以、導致、若、則、除非、然而)
- [ ] Every figure has collapsible `[!figure]-` analysis block
- [ ] Every table has collapsible `[!table-guide]-` reading guide
- [ ] Mechanical figure/table ID comparison reports no missing source IDs
- [ ] Summary contains: One-liner + KEY TAKEAWAYS + Slides Outline
- [ ] All imaging modality sections addressed (even if N/A)
- [ ] DDx/classification/management contain only PDF-supported content; absent topics are explicitly N/A
- [ ] No newer classification, guideline, external threshold, typical finding, or recommendation is presented as source content
- [ ] Every important number, formula, sample size, parameter, threshold, recommendation, and conclusion is locatable in the PDF
- [ ] Important Figures described
- [ ] 台灣正體中文, 專有名詞 English with Chinese in parentheses
- [ ] No preamble or closing statements
- [ ] **Canvas file created** in `Learning Map/` subfolder with valid JSON
- [ ] **Canvas link added** in `# Summary` section with `.canvas` extension and correct relative path
- [ ] Canvas nodes cover all major sections with semantic color coding
- [ ] Canvas edges labeled with concept relationships in Chinese
- [ ] Canvas IDs are unique 16-character lowercase hex; all edges reference existing nodes
- [ ] SR comments preserved; retained embeds/Dataview/wikilinks are valid; unresolved artifacts remain only in archive
- [ ] Rebuilt note hash recorded and final batch/report status updated when auditing

### Task 6 (SRT → JSON)
- [ ] JSON parses without errors
- [ ] All required top-level keys present: `overall_summary_zh`, `takeaways_zh`, `segments`
- [ ] Segments in chronological order, no time overlaps
- [ ] Each segment has: `index`, `start_time`, `end_time`, `start_sec`, `end_sec`, `title`, `summary_zh`, `bullets_zh`
- [ ] 8–15 segments (unless video is exceptionally long)
- [ ] `overall_summary_zh` is 100–180 characters
- [ ] `takeaways_zh` has 6–12 items
- [ ] **Slide images read** — if a companion image folder exists, all slide images were viewed with Read tool to extract correct terminology
- [ ] **Terminology corrected from slides** — segment titles, summaries, and bullets use correct English terms from slide images (not ASR-garbled text)
- [ ] **SRT also corrected** — if slide images were available, the SRT transcript itself was corrected and saved back (UTF-8)
- [ ] If no slide images but PDF was available, key terminology corrected from PDF
- [ ] No phantom content added — only information actually spoken in the video
- [ ] Proper UTF-8, no BOM
- [ ] （可選）若要 PotPlayer 本機導航，已用 `scripts/json_to_pbf.py` 產出與影片同名的 `.pbf` 章節檔

### Task 7 (課程系列筆記)
- [ ] V4 YAML complete with correct subspecialty and source
- [ ] `sibling ::` links to previous/next year course (if exists)
- [ ] First column uses `[[講者 - 簡短主題]]` wikilink format
- [ ] Sessions ordered newest-first (reverse chronological)
- [ ] 影片/講義 links use correct `YYYYMMDD-NN.ext` naming
- [ ] json tracking column present
- [ ] `目錄.md` index file exists in media folder with file availability markers

### Task 8 (現代新知查核)
- [ ] The complete Task 8 reference was read before research or edits
- [ ] Existing note and declared original sources were inventoried read-only
- [ ] Missing, ambiguous, mixed, or inaccessible source claims are marked `source_unresolved`
- [ ] Every material claim has one explicit status: 仍成立／需補充／已更新／已淘汰／來源衝突／無法查證
- [ ] Current guidelines/consensus/WHO are prioritized for classification, thresholds, protocol, and management
- [ ] Every modern factual addition has an actually reviewed article/chapter/guideline-level citation
- [ ] Conflicting numbers or recommendations are preserved side by side with separate citations
- [ ] Original/source-grounded content was not silently rewritten with modern knowledge
- [ ] A separate `# 現代新知查核（查核日期：...）` layer and audit matrix are present
- [ ] Empty audit categories are explicitly N/A rather than padded with invented updates
- [ ] Authentication blockers remain `待登入查核`; weaker sources or model memory were not substituted
- [ ] Original note was archived before modification; original/archive SHA-256 match
- [ ] SR comments are unchanged; embeds, Dataview blocks, and wikilinks remain valid
- [ ] Figure/table modern interpretation does not invent findings absent from the original artifact
- [ ] Canvas is updated only for material conceptual changes and visually separates modern nodes
- [ ] Audit report records status counts, blockers, sources, modifications, hashes, date, and PASS/FAIL
