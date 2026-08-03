---
name: obsidian-v4-cleanup
description: >-
  Standardize Radiology Obsidian notes to V4, organize video/lecture content,
  and summarize papers. Trigger on: 整理, 修正, cleanup, V4, 影片整理, 字幕,
  論文筆記, paper summary, YAML fix, footnote conversion, 閱片 callout,
  Paper L3 creation, SRT分段, JSON導航,
  課程筆記, course listing, 新知查核, 現代知識更新, outdated claim audit,
  guideline update, Tier 1 evidence review.
  8-task pipeline: (1) YAML V4 frontmatter fix, (2) citation→footnote,
  (3) 閱片 table→callout, (4) video content from subtitles/audio/slides,
  (5) PDF-grounded L3 reconstruction with faithful full-text translation,
  coverage gates, figure/table audit, and canvas map,
  (6) SRT→segmented JSON for web player navigation,
  (7) course series listing note with media links,
  (8) evidence-grounded modern knowledge audit with a separate source layer.
  Also trigger for: 讀書筆記, 章節整理, textbook, 教科書, 深度閱讀,
  字幕導航, 更名, 目錄.
---

# Obsidian V4 Cleanup Skill

You are working with a Radiology Obsidian vault. Depending on the user's request, you apply one or more of 8 tasks. Always read the file first, assess which tasks apply, then execute them in order.

## Task Overview

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

## Task 4: 影片/講座內容整理

Applies when the user provides video-related materials (subtitle files, audio files, slides/PDFs) and asks to organize the content into an Obsidian note.

### Input Materials (one or more)

- **Subtitle files**: `.srt`, `.vtt`, `.txt` transcript files
- **Audio files**: `.mp3`, `.m4a`, `.wav` — use speech-to-text if needed
- **Slide images（投影片截圖）**: `.png`, `.jpg` files in a companion folder — these are the **primary visual reference** and should be read with the Read tool to see their actual content (text, tables, diagrams, case images). The filenames typically encode a timestamp (e.g., `Modifier S-0934.png` = screenshot at 09:34).
- **Slides/講義 PDF**: `.pdf`, `.pptx` — supplementary visual reference (when slide images are not available)
- **影片檔（video file）**: `.mp4`/`.mkv`/`.mov`/`.webm` — 當「沒有」現成投影片截圖資料夾時，用 `scripts/slide_frames.py` 自動抓換頁截圖（見下方 workflow 第 2b 步），讓 AI 直接看到實際畫面，而非只靠字幕。
- **官方筆記／講義（reference notes）**: 同層的 `.html` / `.md` / 講義 PDF（例如講者官方整理的課程筆記、招牌指令包）。**這是最高優先的文字 ground truth**——用 `defuddle parse <檔> --md` 解析 `.html`（保留 SECTION 結構），直接 Read `.md`。其術語、數值、史實、專有名詞**優先於 ASR 逐字稿與投影片截圖**，用來修正逐字稿聽錯/聽不出的內容。
- **Multiple sources**: Different lecturers or versions on the same topic

### Workflow

1. **Check for Task 6 JSON** — if a corresponding `.json` navigation file doesn't exist for the subtitle, run Task 6 first to generate it. The JSON provides pre-segmented structure that helps organize the note.
2. **Check for slide images** — look for a companion folder with the same name as the video/SRT file (e.g., `Modifier S/` for `Modifier S.zh.srt`). If it contains `.png`/`.jpg` files, these are slide screenshots and are a critical input.
2b. **無投影片資料夾但有影片檔 → 自動抓換頁截圖（2026-06-24 新增）**：若步驟 2 找不到投影片截圖，但同層有同名影片檔，執行：
   ```bash
   python scripts/slide_frames.py "<影片檔>" --json "<Task6 的 .json>" --width 1280
   ```
   它會用場景偵測抓「換頁」那幾張存到 `frames/`，並把 `frame`/`frames` 併入分段 JSON。
   接著**用 Read 工具逐一閱讀這些 `frames/*.png`**——它們就是本任務的「視覺 ground truth」，補上字幕看不到的投影片文字、表格、影像（CT/MRI/US）實際內容；ASR 錯字以截圖為準校正。
   （若已有手動投影片資料夾，優先用手動的；本步僅在缺截圖時啟用。完全無影片檔則維持只靠字幕。）
2c. **檢查官方筆記／講義（最高優先 ground truth，2026-06-24 新增）**：若同層有 `.html`/`.md`/講義 PDF（講者官方整理）：
   - `.html` → `defuddle parse "<檔>" --md`（去雜訊、保留 SECTION/標題結構）；`.md` 直接 Read；PDF 用 `pdftotext`。
   - **以它為準校正逐字稿**：ASR 常把專有名詞、數字、史實聽錯（甚至整段漏聽或誤解因果）。官方筆記 > 投影片截圖 > ASR 逐字稿。
   - 範例（實證）：某 AI 講座 ASR 把「Naval 三槓桿」誤傳為四槓桿、把「增冊」說成別的詞、整段 Chomsky/Codex routine 被壓縮——皆靠官方 `.html` 筆記校回。
3. **Read all provided materials**:
   - **官方筆記／講義** = 最高優先文字 ground truth（術語/數值/史實/因果以此為準）
   - **Subtitles** = primary spoken content source
   - **Slide images** = primary visual/structural reference. Use the Read tool to view each image — they contain the actual slide text, tables, figures, and diagrams that the speaker is referencing. ASR transcripts are often garbled for medical/technical terms; the slide images are the ground truth for correct terminology, numbers, and proper nouns.
   - **PDF/PPTX** = fallback visual reference when slide images are not available
   - If Task 6 JSON exists, use its segment structure as a starting scaffold.
4. **Cross-reference subtitles with slide images** — use timestamp-encoded filenames to align slides with the corresponding transcript segment. The slide content takes priority over the transcript for: English terminology, proper nouns, numeric values, table data, and classification criteria.
5. **Identify the topic and subspecialty** from content
6. **Choose Prompt mode**:
   - Multiple sources/lecturers → use **Prompt A** (multi-version) format
   - Single source → use **Prompt B** (single source) format
7. **Generate structured note** following the template at `1. Projects/AI相關/=影片學習流程與Prompt Template（通用版）.md`
8. **Embed slide images in the note** — insert `![[filename.png]]` at the corresponding sections so the reader can see the original slides inline. Place each image embed above or below the content it illustrates.

### Output Structure

```markdown
---
(V4 YAML — source lists the lecturer/course name)
---
Topics :: [[relevant topics]] <br>
Parent Link :: [[=索引頁]] <br>

---
# Evergreen Note
「**一句話核心觀念**」

# Summary
- **重點1**
- **重點2**
- 易混淆觀念：...

# Note (layer 1-3)
## 小標題1
（detailed content, comparisons in tables）
## 小標題2
（if multiple lecturers, mark **(講師A觀點)** / **(講師B觀點)**）

### 參考來源
[^1]: URL or source description

## 題目
Q: 自我測驗問題
A: 答案 + 解釋

## 閱片
（if applicable）
```

### Rules

1. **繁體中文**，專有名詞保留英文
2. **不可自行編造內容** — 所有資訊必須來自提供的素材
3. 講者額外補充的經驗或洞見也要記錄
4. 若多個來源內容一致，不需特別標註觀點差異
5. **學習驗證** 至少選一項：費曼輸出 / 應用情境 / 行動清單 / 知識連結 / 自我測驗
6. Subtitle parsing: strip timestamps, merge fragmented sentences, handle overlapping lines
7. **Slide image embeds**: When slide images exist (手動投影片資料夾，或由 `scripts/slide_frames.py` 自動抓的 `frames/*.png`), embed them at the matching note sections with `![[filename.png]]`. Every major section should have at least one relevant slide image if available. Place the embed right after the section heading or before the content it illustrates. 自動換頁截圖的檔名帶時間碼（`<stem>-MMSS.png`），可依此對齊到對應段落。
8. **Ground-truth 優先順序（校正逐字稿時）**：**官方筆記／講義（.html/.md/PDF）> 投影片截圖 > ASR 逐字稿**。ASR 常把英文醫學/專有名詞、數字、史實、甚至因果關係聽錯（如 "Lunnerate" → "Lung-RADS"、"Infisima" → "emphysema"，或把「三」聽成「四」）。當官方筆記或投影片清楚顯示正確內容時，以它為準，不可盲信 SRT。
9. **Slide image reading strategy**: For large slide sets (>20 images), read them in batches or use filenames' timestamps to prioritize slides that correspond to the current transcript segment. You don't need to read every single image upfront — read them as you process each section of the transcript.

### Subtitle File Parsing

```python
# SRT format: strip timestamps and sequence numbers
import re

def parse_srt(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    # Remove sequence numbers and timestamps
    lines = re.sub(r'\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n', '', content)
    # Merge lines, remove duplicates from overlapping subtitles
    paragraphs = [line.strip() for line in lines.split('\n\n') if line.strip()]
    return '\n'.join(paragraphs)
```

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

## Task 6: SRT → 分段 JSON（字幕導航檔）

Applies when subtitle files (.srt/.vtt) need to be processed into structured JSON for web player navigation. This is the upstream step of Task 4 — the JSON enables time-coded navigation when viewing lectures online.

### When to Use

- User provides SRT/VTT files and asks for segmentation or JSON generation
- Task 4 is triggered but no corresponding `.json` exists for the subtitle file
- User says: 分段, json, 字幕整理, 導航, navigation

### Reference Materials for Correction

ASR-generated subtitles are often riddled with errors — especially for English medical terms embedded in Chinese speech. To produce an accurate JSON, you need a reference source for ground-truth terminology. Check for these in priority order:

1. **官方筆記／講義（.html/.md）** — 同層的講者官方整理筆記（最高優先文字 ground truth）。`.html` 用 `defuddle parse "<檔>" --md` 解析、`.md` 直接 Read。術語/數值/史實/因果以此為準，校正 ASR 與投影片。
2. **Slide images（投影片截圖）** — A companion folder with `.png`/`.jpg` files named by timestamp (e.g., `Modifier S-0934.png` = slide at 09:34). **Use the Read tool to visually read each image** — they contain the actual slide text, tables, classification criteria, and proper nouns that the speaker is referencing.
3. **PDF 講義** — A same-name `.pdf` file. Extract text with `pdftotext` for terminology cross-reference.
4. **No reference available** — Rely on domain knowledge; mark uncertain terms with「（可能為 XXX）」.

**Why slide images matter**: A typical medical lecture SRT will have dozens of garbled English terms (e.g., "Lunnerate" → "Lung-RADS", "Arteryal Calculification" → "Arterial Calcification", "Infisima" → "emphysema"). The slide images show the correct spelling on screen. Without reading them, the JSON will propagate these errors into segment titles and summaries.

### Prompt Template

The following is the complete prompt to use (or provide to the user for API usage):

```
你是一位「字幕整理 +（可選）投影片校正」助手。
我會提供：
(1) 字幕（VTT 或 SRT，可能有錯字但含時間碼）
(2) 投影片/講義內容（可選，用來校正名詞與架構）
    — 若有投影片圖片，已事先閱讀並提取正確的術語、數值、表格內容

【任務】
1) 自動分段（8–15 段為主，除非影片很長）
   - 以主題轉換/投影片標題為主要分段依據
   - 每段給 start_time/end_time (mm:ss 或 hh:mm:ss)
   - 同時提供 start_sec/end_sec（秒數）
2) 每段輸出：
   - title：段落標題（像投影片標題，使用投影片上的正確術語）
   - summary_zh：繁中 2–4 句摘要
   - bullets_zh：繁中 2–6 點重點（保留英文專有名詞，以投影片為準）
3) 全片輸出：
   - overall_summary_zh：100–180 字繁中
   - takeaways_zh：6–12 點（偏結論/可應用原則）

【校正規則】
- 專有名詞若字幕明顯錯字，必須用投影片/講義校正（例如血管名稱、器材、術式、分類系統）
- 投影片上清楚可見的正確拼寫優先於字幕文字
- 不得腦補字幕沒提到的內容；若投影片有但字幕沒講到，請不要硬塞
- 不確定拼字就保留原字幕並加註「（可能為XXX）」
- 中文錯字也要校正（如「方測科」→「放射科」、「送神」→「送審」）

【只輸出 JSON，不要輸出其他文字】
```

### Output JSON Schema

```json
{
  "overall_summary_zh": "100-180字繁中整體摘要",
  "takeaways_zh": ["結論/可應用原則 1", "...最多12點"],
  "segments": [
    {
      "index": 1,
      "start_time": "mm:ss",
      "end_time": "mm:ss",
      "start_sec": 0,
      "end_sec": 62,
      "title": "段落標題",
      "summary_zh": "繁中2-4句摘要",
      "bullets_zh": ["重點1", "重點2", "重點3"],
      "frame": "frames/<stem>-MMSS.png",
      "frames": ["frames/<stem>-MMSS.png", "..."]
    }
  ]
}
```

> **`frame` / `frames` 欄位（2026-06-24 新增，影片截圖整合）**：當影片檔存在時，由
> `scripts/slide_frames.py` 自動填入。`frames` = 該段時間範圍內偵測到的所有「換頁截圖」
> 相對路徑；`frame` = 代表圖（該段第一張換頁；若該段無換頁則為段落開始時螢幕上那張）。
> web player 可用 `frame` 顯示縮圖、用 `frames` 做段內輪播。無影片檔時這兩個欄位省略。

### Workflow

1. Read the `.srt` file content (handle encoding: check for UTF-16/UTF-8 BOM)
2. **Check for slide images** — look for a companion folder with the same base name as the SRT (e.g., `Lecture Name/` for `Lecture Name.zh.srt`). If it contains `.png`/`.jpg` files:
   a. List all image files and note their timestamp-based filenames
   b. **Read each slide image using the Read tool** to extract the visual content (slide titles, English terminology, tables, classification criteria, numeric thresholds, proper nouns)
   c. Build a correction map: ASR-garbled term → correct term from slide
   d. For large slide sets (>30 images), read in batches aligned with SRT timestamp ranges
3. If no slide images exist, check if a same-name `.pdf` exists — if so, extract text with `pdftotext` for terminology correction
4. **Correct the SRT transcript** before segmentation — apply the correction map from slide images to fix English medical terms, Chinese ASR errors, and proper nouns throughout the transcript. Optionally save the corrected SRT back to the same file (convert to UTF-8 if originally UTF-16).
5. Segment the corrected transcript into 8–15 chapters based on topic transitions (aligned with slide changes where possible)
6. Generate the JSON output with corrected terminology in all titles, summaries, and bullet points
7. Validate output JSON: all required keys present, segments in chronological order, no time overlaps
8. Save as `<same-name>.json` in the same directory as the SRT file (e.g., `Modifier S.zh.json`). If the SRT follows `YYYYMMDD-NN.srt` naming, save as `YYYYMMDD-NN.json`.
9. **抓換頁截圖併入 JSON（2026-06-24 新增）** — 若 SRT 同層存在同名影片檔（`.mp4/.mkv/.mov/.webm/...`），執行：
   ```bash
   python scripts/slide_frames.py "<影片檔>" --json "<剛存的.json>" --width 1280
   ```
   - ⚠️ **必須前景同步執行、等它印完「截圖張數＋併入」訊息再繼續**。長片場景偵測要數分鐘；**切勿丟到背景後就結束這一回合**（曾發生：截圖跑背景、回合提早結束 → JSON 併入了但 V4 沒寫成，留下半成品）。委派子代理時務必在指示中明寫這點。
   - 沿用 slide-extractor 的場景偵測（PySceneDetect adaptive，無則退 ffmpeg scene filter）抓「真正換頁」那張，存到 `frames/<stem>-MMSS.png`（1280px）。
   - 自動把每段的 `frame`/`frames` 欄位併回 JSON（見上方 schema 說明），web player 即可顯示縮圖。
   - 另產 `<stem>.frames.json` 換頁清單 manifest。
   - **若已有手動投影片資料夾**：以手動資料夾為準（畫質/挑選較佳），可跳過本步或僅作補充。
   - **無影片檔**：跳過，JSON 不含 frame 欄位（行為與舊版相同）。
10. **（可選）產 PotPlayer 章節檔 .pbf（2026-06-25 新增）** — 若使用者用 PotPlayer 本機看影片，可把分段 JSON 轉成章節書籤，於進度條顯示可點擊章節（`Ctrl+PgUp/PgDn` 跳轉）：
    ```bash
    python scripts/json_to_pbf.py "<分段 JSON 或整個資料夾>"
    # 整個資料夾批次（自動排除 *.frames.json 與 _ 開頭、無 segments 者）
    python scripts/json_to_pbf.py "<資料夾>"
    ```
    - 用各段 `start_sec` + `title` 產生 `[Bookmark]` 章節（毫秒）；輸出 UTF-8（少數版本中文亂碼可加 `--bom`）。
    - **.pbf 主檔名必須與影片同名**：腳本會自動對齊同目錄影片檔（同名或前綴相符，如 JSON `…原則.json` 對應影片 `…原則-2937.mp4`）；找不到才退用 JSON 主檔名。
    - PotPlayer 開影片時會自動載入同名 `.pbf`。重建 JSON 後重跑本步即可讓章節與筆記同步。
    - 與 web player 用的 `frame`/`frames` 並存、互不影響；這是「本機播放器導航」的平行輸出。
11. **（可選）挑出筆記用到的截圖搬進 Obsidian（2026-06-26 新增）** — V4 筆記常只嵌入 `frames/` 裡眾多截圖的一小部分（例 12/155）。要把筆記搬進 Obsidian 時，只需「用到的那幾張」：
    ```bash
    python scripts/collect_note_images.py "<某.v4.md>"            # 解析引用 → 複製到 ./images/（使用者偏好夾名）
    python scripts/collect_note_images.py "<資料夾>"             # 批次：夾內每篇 *.v4.md 各自輸出
    ```
    - 同時支援 Markdown `![](frames/xxx.png)`（含 %20）與 Obsidian wikilink `![[xxx.png]]`；預設來源夾為筆記同層 `frames/`，可用 `--frames` 指定。
    - **改名場次後要重跑**：若先用 `reorg`/改 stem 改了 frames 檔名與筆記引用，這裡要在「改名後」才執行，挑出的檔名才會與筆記一致。
12. **收尾稽核（2026-08-03 新增，建議必跑）** — Task 5 有 coverage ratio gate，Task 4/6 之前完全沒有自動檢查，半成品只能靠人眼發現（JSON 併好但截圖沒抓、改名後筆記引用的圖不存在、時間碼重疊）：
    ```bash
    python scripts/check_task6.py "<某.json>" --note "<某.v4.md>"
    python scripts/check_task6.py "<資料夾>"          # 批次，自動配對同名 .v4.md
    python scripts/check_task6.py "<資料夾>" --strict # 警告也算失敗
    ```
    - 檢查：必要 key / index 連號 / `start_sec < end_sec` / 單調不重疊 / `start_time` 與 `start_sec` 一致 / title 與 summary_zh 非空 / 每段至少一張 frame（僅當該檔已併入截圖）/ frame 與筆記引用的圖片實際存在 / 無 BOM。
    - 離開碼 **0 全過、1 只有警告、2 有錯誤**；只做機械檢查，不判斷內容品質。
    - **改名或重跑 slide_frames 之後務必再跑一次**——這兩個動作最常留下「JSON 指向已不存在的檔名」。

### Special Characters

The JSON will be consumed by a web player, so ensure:
- Proper UTF-8 encoding
- HTML-sensitive characters (`<`, `>`, `&`) are safe in JSON string values (they'll be escaped by the player)
- No BOM (Byte Order Mark) in the output file
- Use `\n` for newlines within JSON strings, not literal newlines

---

## Task 7: 課程系列筆記（Course Listing Note）

Applies when organizing a series of lectures/courses into a single index note with media links. Examples: 年度教育訓練課程、研討會、workshop 系列。

### When to Use

- User asks to create a course listing or 課程筆記
- Multiple lectures from the same series need to be organized
- User provides a folder of renamed media files (YYYYMMDD-NN.ext) to be listed

### Output Template

```markdown
---
title: YYYY課程名稱
date: YYYY-MM-DD
DateRev: YYYY-MM-DD
aliases: []
noteVer: v4
tags: []
subspecialty: XX
已完成: false
source:
  - "課程全名"
---
Topics :: [[相關主題1]], [[相關主題2]] <br>
Parent Link :: [[=索引頁]] <br>
sibling :: [[前一年課程筆記]] <br>

---
# Summary

# 課程名稱(N)
| 主題 | 影片 | 講義 | json |
| ---- | ---- | ---- | ---- |
| [[講者 - 簡短主題]] | [影片](base_url/YYYYMMDD-NN.mp4) | [講義](base_url/YYYYMMDD-NN.pdf) | Y |
```

### Rules

1. **第一欄用 wikilink**：`[[講者 - 簡短主題]]`，不用原始完整標題。簡短主題控制在 10-15 字內，保留核心關鍵字
2. **場次從最新排到最舊**（逆時間序），每個場次一個 `#` 標題
3. **影片/講義欄位**：有檔案就放 `[影片](url)` / `[講義](url)`，沒有就留空
4. **json 欄位**：追蹤分段 JSON 是否已產生（`Y` = 已有，空 = 待處理）
5. **sibling 連結**：若有前一年/下一年的同名課程，用 `sibling ::` 互相連結
6. **NAS URL pattern**：`http://jieyu166.synology.me/courses/{課程代碼}/YYYYMMDD-NN.ext`

### File Naming Convention

課程相關的媒體檔案統一使用 `YYYYMMDD-NN.ext` 格式：
- `YYYY` = 西元年
- `MM` = 月（兩位數）
- `DD` = 日（兩位數）
- `NN` = 該場次的講序（01-06）
- `ext` = 附檔名（mp4, pdf, srt, json）

搭配 `目錄.md` 索引檔（放在媒體檔案同目錄）記錄原始講者、主題、檔案可用性：

```markdown
| 檔名 | 日期 | 講者 | 主題 | PDF | SRT | JSON |
|------|------|------|------|:---:|:---:|:----:|
| 20250517-01 | 2025/05/17 | 黃其晟 | USPSTF及篩檢新政策 | ✅ | ✅ | ✅ |
```

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
