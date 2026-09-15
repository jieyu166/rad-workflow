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

## 驗證

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

