## Task 5: PDF 閱讀筆記

Applies when the user provides a PDF (journal paper, textbook chapter, or reference material) and asks for reading notes. L3 不是預設——**先跑 Step 0 兩層分流**；只有通過分流的材料才產出 **L3 深讀筆記** 加一份 **visual canvas map**，其餘停在 L1 檢索摘要。

### Step 0：兩層分流（必做，不可跳過）

不要先讀全文。先跑兩層判斷，決定這份材料值不值得 L3。判讀結果與理由要先告訴使用者，再開始執行。

**第一層——檢視閱讀（Adler）**：只看 title / abstract、章節標題與小標、圖表清單、結論與 Limitations、參考文獻的年代分佈（教科書章節看章首摘要與章末總結）。目標只有一個：判斷這份材料值不值得多花時間仔細閱讀。

**第二層——貢獻三問（彭明輝）**：

1. 這篇解決了什麼別人沒解決的問題？（前人卡在哪。要寫出**是哪個東西不知道**，不可寫「相關研究不多」這種空話）
2. 它用什麼方法解決？（學術界怎麼稱呼這個方法）
3. 跟既有知識差在哪？（作者自承的 limitation 是什麼）

**判決（預設是「停在 L1」，要升 L3 必須說得出理由）**：

- 三問都填得出來，且符合下列任一 → 跑 L3：(a) 直接影響目前的臨床判讀或報告流程；(b) 是進行中專案的方法學依據；(c) 要拿來教學或簡報；(d) 與 vault 中既有筆記衝突，需要解決分歧。
- **任何一問填不出來 → 停在 L1 檢索摘要**，不跑 Stage 1／Stage 2、不產 canvas。填不出第 1 問代表這篇沒有在跟既有文獻對話（可能是 review 或 case report）；填不出第 3 問代表還沒讀懂，回頭補背景，不要硬跑 L3——硬跑只會產出似懂非懂的長篇筆記。
- 三問都填得出來但與當前關注只是間接相關 → 一樣停在 L1。
- 使用者明確指定要 L3 → 直接跑 L3，跳過本判讀。

**L1 檢索摘要格式**（約 15 行；V4 YAML，`tags: ["L1"]`，`消化層級: 1`，其餘欄位規則同 L3）：

    # Summary
    ## 這篇的貢獻
    - **前人卡在哪**：
    - **這篇做了什麼**：
    - **剩下沒解決的**：

    ## 我為什麼開這篇
    - 讀前想解決的問題：
    - 讀完的答案：
    - 下一步：□ 改報告用語 □ 進專案 □ 只存檔備查 □ 丟棄

    ## 什麼情況下要回來讀 L3
    -

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
non-whitespace characters in the Stage 1 working draft
÷
non-whitespace characters extracted from the PDF
```

Stage 1 是**工作底稿**（暫存檔或工作區），不寫進交付的 .md；本關卡對底稿計算，不對最終筆記計算。

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

0. **跑 Step 0 兩層分流**；判決為「停在 L1」時只產 L1 檢索摘要，以下步驟不執行。
1. **Resolve source**: locate the exact PDF; record its path, page count, citation, edition, and SHA-256 when applicable.
2. **Archive existing note** before overwriting; confirm the archive hash equals the original hash.
3. **Extract text** page by page with page boundaries retained.
4. **Render every PDF page** to images. Build contact sheets for efficient review, then inspect full-resolution pages containing figures, tables, equations, small labels, or extraction anomalies.
5. **Build a source inventory**: original section hierarchy, page ranges, all figure/table/box/equation IDs, study design, sample size, important numbers, and appendices.
6. **Determine subspecialty** and create correct V4 YAML using the source edition—not newer classifications or outside knowledge.
7. **Write Stage 1 in source order**（工作底稿，不進 .md）with bilingual headings mirroring the PDF. Work in bounded chunks and re-check the PDF after each chunk.
8. **Run the Stage 1 gate**: calculate the coverage ratio, check section coverage, and compare every figure/table ID against the inventory. Continue translating until all checks pass.
9. **Write Stage 2** from the verified Stage 1: restructure into a hierarchical clinical learning note without adding content. Stage 2 是唯一寫進 .md 的筆記層；每個段落標題後標原文頁碼 `[p.12]`。
10. **Write Summary**：Canvas link、我為什麼開這篇、這篇的貢獻（三格）、KEY TAKEAWAYS、Slides Outline。
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

L3 的交付內容是 **Stage 2 結構重組**，加上 deep-dive 段落與一份 visual canvas map。**Stage 1 忠實翻譯是工作底稿，不寫進 .md**：它是通過品質關卡用的中間產物，留在暫存檔或工作區，交付檔只保留 Stage 2 的重組結果。需要逐句細節時回查原文 PDF；因此 Stage 2 每個段落標題後標原文頁碼 `[p.12]`。

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
消化層級: 1
source:
  - "Author et al. Journal. Year" or "Author(s). Book Title. Edition. Publisher, Year. Chapter X."
---

# Summary
[[Learning Map/Note Title.canvas|Note Title]]

## 我為什麼開這篇（讀前填）
- 讀前想解決的問題：
- 讀完的答案：
- 下一步：□ 改報告用語 □ 進專案 □ 只存檔備查 □ 丟棄

## 這篇的貢獻（必填，禁止寫「本文探討…」「本文回顧…」）
- **前人卡在哪**：既有文獻具體的不足或矛盾，一句話。不可寫「相關研究不多」這種空話——要寫出是哪個東西不知道
- **用什麼方法**：新證據／新方法／新的研究範圍剪裁，擇一，一句話
- **跟既有知識差在哪**：作者自承的 limitation ＋ 讀出來但作者沒說的，一句話

（三格有任一格填不出來 → **當場停止 L3，降級為 L1 檢索摘要**，並說明是哪一格填不出來）

## KEY TAKEAWAYS
- 臨床要點
- 考試要點
- 教學要點

## Slides Outline
（one teachable concept per slide, ready for Google Slides via Apps Script）
1. **Slide title** — key message
2. **Slide title** — key message
3. ...

# Note (Stage 2 — 結構重組)
（Stage 1 忠實翻譯為工作底稿，不出現在本檔；段落標題後標原文頁碼 `[p.12]`）

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
（只寫原文實際涵蓋的模態；原文沒談的模態整個子標題刪除，不留 `N/A` 佔位。原文完全不涉及影像時，整個 `## Key Imaging Findings` 段落省略）

## Differential Diagnosis｜鑑別診斷

| 診斷 | 影像特徵 | 鑑別重點 |
|------|---------|---------|
|      |         |         |
（只列原文實際提出的鑑別診斷，不設行數下限；原文未討論鑑別診斷時整段省略，不留空表、不留 N/A 佔位）

## Classification / Staging｜分類分期
- ...

## Clinical Significance & Pitfalls｜臨床意義與陷阱
- ...

## 我應該記住的 3 件事（AI 預寫 3 條候選，使用者只做保留／刪除／改寫；一個字都沒改則 `消化層級` 停在 1）
1.
2.
3.

## Important Figures｜重要圖片
- Fig X: {描述}

# Anatomy / Pathophysiology｜解剖與病理生理
- ...

# Management & Treatment｜處置與治療
- 只寫 PDF 明確支持的治療、影像決策角色與 follow-up
- 原文未涵蓋時整段省略，不留空標題；不得以教科書通論補滿

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

**河川路徑（必要，每張 canvas 恰好一條）**
除了概念節點之外，canvas 必須包含一條單線主路徑，由 5 個節點、4 條 edge 串成：

    [這份材料要回答的問題] → [立足點 1] → [立足點 2] → [立足點 3] → [結論]

- 起點節點用疑問句，不用章節名稱。
- 立足點恰好 3 個。少於 3 表示路徑跳步，多於 3 表示沒有做取捨。
- 這 4 條 edge 的 label 必須是**推理關係**（「因為」「所以」「但僅限於」「證據是」「反例是」），**不得**是章節名稱或主題詞。
- 主線只有一條。其餘概念節點視為**支流**，各自從它匯入主線的那個立足點拉一條 edge 進來，edge label 標明匯入點的關係（例：「補充此步證據」「此步的例外」）。支流不得自成第二條主線。
- 若一份材料拉不出這條路徑，在 `# Summary` 的貢獻三格下方註明一行：「本篇無法構成單一論證線，原因：____」。這通常表示原文是綜述或列舉而非論證——這件事本身值得知道。

**Reader-voice nodes（必要，1–3 個）**
上述顏色全部在描述原文，沒有一種代表讀者本人的反應。每張 canvas 必須另有 1–3 個代表「讀者本人立場」的節點：

- 節點文字以 `？` 開頭，用 `1` 紅色，靠開頭的 `？` 與其他紅色警告節點在視覺上區分；描述原文的 AI 節點一律不得用 `？` 開頭。
- AI 的工作是**預寫候選**：提出 3 個這篇材料沒有回答、或其論證最薄弱的挑戰性問題，每個 ≤25 字，放進這些節點。讀者只需保留／刪除／改寫，不需從零構思。
- 每個 reader-voice 節點至少要有一條 edge 連到它挑戰的那個概念節點，edge label 用「這裡存疑」「未回答」「與我的經驗不符」之類的關係詞。
- 讀者改寫過任一 reader-voice 節點，才能把 `消化層級` 推到 `3`；AI 預寫的候選不算讀者自己的字。

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

1. **必須保留（無上限）＝臨床數值層**：分級分期標準、判讀閾值、藥物劑量、測量值、統計結果與其信賴區間，以及支撐這些數字的條件與因果鏈。這些一個都不能丟。
   **必須壓縮（有上限）＝背景層**：背景、文獻回顧、討論、作者的推測與展望。
   - 背景層每一小節 ≤150 字
   - Stage 2 正文整體 ≤ 原文頁數 × 40 字
   - 超過上限時，先壓縮背景層，**絕不動臨床數值層**
   需要原文沒有的背景補充時，另開一節 `## 我補的背景（非原文內容）` 與原文內容嚴格分開；混寫會讓這份筆記日後無法判斷哪一句有出處。
2. **source 欄位**格式：期刊用 `"First Author et al. Journal Abbreviation. Year;Volume:Pages"`；書籍用 `"Author(s). Book Title. Edition. Publisher, Year. Chapter X."`
3. **Imaging modality 段落只寫原文實際涉及的模態。** 原文只談 MRI 就只有 `### MRI`，**不要列出 CT／US 再標 N/A**。原文完全不涉及影像（方法學論文、流行病學研究、DL 技術報告）時，整個 `## Key Imaging Findings` 段落省略，不保留空標題。
4. **DDx table 只列原文實際提出的鑑別診斷，不設行數下限。** 原文提出幾個就寫幾個；原文未討論鑑別診斷，整個 `## Differential Diagnosis` 段落省略。同理 `## Classification / Staging`、`# Anatomy / Pathophysiology`、`# Management & Treatment` 原文沒有對應內容時一律整段刪除，不留空標題、不留 `N/A` 佔位。
   **嚴禁為湊行數或湊版面而從教科書常識補充原文沒有的內容**——這與 Task 4 Rule 2「不可自行編造內容」是同一條規則，只是換了觸發情境。筆記的 source 欄位指向這篇原文，寫進去的東西就必須出自這篇原文；AI 補的教科書套語在筆記裡看起來跟原文一模一樣，回看時分辨不出來源，這是安全問題，不只是效率問題。想補教科書知識就另開 `## 我補的背景（非原文內容）` 並明確標記。
5. 不得把一般醫學知識、新版 WHO／guideline、典型 imaging pattern 或外部 cutoff 冒充原文內容；需要更新資訊時另立「外部更新」區並附來源，除非使用者要求，預設不加
6. Important Figures: 提取教學價值最高的圖片描述；完整 figure inventory 仍須在 Stage 1 逐號交代
7. 若有包含數據的表格，需解讀原文支持的數據走勢並保留 denominators、units、conditions 與 uncertainty
8. 所有關鍵數值、公式、sample size、scan parameters、diagnostic thresholds、treatment recommendations 與 conclusions 必須能定位至 PDF 頁面或章節
9. **Canvas 僅在 L3 時產生** — 每份 L3 筆記都要搭配一份 .canvas 視覺地圖（含河川路徑與 reader-voice 節點）；L1 檢索摘要不產 canvas

---

## 驗證

### Task 5 (PDF 閱讀筆記)
- [ ] Exact PDF resolved uniquely; unresolved/ambiguous sources were not overwritten
- [ ] Existing note archived before overwrite; original and archive SHA-256 match
- [ ] PDF text extracted with page boundaries and all pages rendered
- [ ] Every PDF page visually reviewed via renders/contact sheets
- [ ] Full-resolution visual review completed for every figure/table/equation page and extraction anomaly
- [ ] Source inventory covers every section, figure, table, box, equation, and appendix
- [ ] Step 0 兩層分流已執行，判決與理由已先告知使用者
- [ ] 交付檔只含 Stage 2；Stage 1 底稿未寫進 .md
- [ ] 貢獻三格三格皆有實質內容（任一格空白時應已降級為 L1）
- [ ] Stage 1 is a substantive source-order full translation, not a summary or translated outline
- [ ] Stage 1 工作底稿 non-whitespace/PDF extracted non-whitespace ratio is ≥0.20, or ratio is N/A with documented OCR/extraction reason and page-based coverage proof
- [ ] Ratio was not inflated with filler, duplication, copied English text, or identifier-only lists
- [ ] Stage 2 was written only after Stage 1 passed coverage checks
- [ ] Two-stage process applied (Stage 1 忠實翻譯 + Stage 2 結構重組)
- [ ] V4 YAML complete (source in proper citation format, tags: ["L3"], `消化層級: 1`)
- [ ] YAML parses; required fields and types are correct
- [ ] subspecialty correctly identified
- [ ] Title structure mirrors original with bilingual headings and numbering
- [ ] Hierarchical outline with proper indentation (not flat prose)
- [ ] All logical connectors preserved (因為、所以、導致、若、則、除非、然而)
- [ ] Every figure has collapsible `[!figure]-` analysis block
- [ ] Every table has collapsible `[!table-guide]-` reading guide
- [ ] Mechanical figure/table ID comparison reports no missing source IDs
- [ ] Summary contains: 我為什麼開這篇 + 這篇的貢獻（三格）+ KEY TAKEAWAYS + Slides Outline
- [ ] Imaging modality 段落只含原文涉及的模態，無 `N/A` 佔位段落與空標題
- [ ] DDx／classification／management 內容全部可回溯到原文；原文未談的整段省略，無教科書套語補充
- [ ] No newer classification, guideline, external threshold, typical finding, or recommendation is presented as source content
- [ ] Every important number, formula, sample size, parameter, threshold, recommendation, and conclusion is locatable in the PDF
- [ ] Important Figures described
- [ ] 背景層未超過字數上限；臨床數值層完整未被壓縮
- [ ] 台灣正體中文, 專有名詞 English with Chinese in parentheses
- [ ] No preamble or closing statements
- [ ] **Canvas file created** in `Learning Map/` subfolder with valid JSON
- [ ] **Canvas link added** in `# Summary` section with `.canvas` extension and correct relative path
- [ ] Canvas nodes cover all major sections with semantic color coding
- [ ] Canvas edges labeled with concept relationships in Chinese
- [ ] Canvas 有一條河川路徑（5 節點 4 edge，edge label 為推理關係），其餘節點為標註匯入點的支流
- [ ] Canvas 有 1–3 個 `？` 開頭的 reader-voice 節點，各自連到它挑戰的概念節點
- [ ] Canvas IDs are unique 16-character lowercase hex; all edges reference existing nodes
- [ ] SR comments preserved; retained embeds/Dataview/wikilinks are valid; unresolved artifacts remain only in archive
- [ ] Rebuilt note hash recorded and final batch/report status updated when auditing

