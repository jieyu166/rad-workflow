# Turtle Trader Manga Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a source-traceable, 14-chapter, approximately 120-page Traditional Chinese adult-density manga production package for 《撼動華爾街的海龜交易員》, with varied page layouts and one image-generation prompt per page.

**Architecture:** Shared character, scene, style, and layout bibles define the visual contract. Each chapter is then authored sequentially as a self-contained script plus per-page prompts, while a source-coverage map and production tracker record provenance and status. A small Python validator enforces page counts, required summaries, layout rotation, prompt fields, and package completeness.

**Tech Stack:** Markdown, YAML, JSON, Python 3.14 standard library, `unittest`, existing EPUB chapter text files.

## Global Constraints

- Source directory: `outputs/novel-to-manga/turtle-trader-adult-dense/source-chapters/`.
- Process chapters strictly from Chapter 1 through Chapter 14; do not merge or reorder them.
- Every chapter begins with a complete bullet-form chapter summary; the summary may not be omitted.
- Use real people from the source; do not add a fictional teacher, reader, or narrator character.
- Target length is approximately 120 pages with chapter counts fixed at `7, 12, 13, 10, 14, 8, 10, 5, 7, 6, 9, 5, 9, 5`.
- Pages use 3–7 panels; standard six-panel grids are limited to two pages per chapter.
- Adjacent pages may not share the same primary layout ID.
- Every chapter uses at least four layout IDs; chapters of ten or more pages use at least six.
- Information-only pages must be preceded and followed by a character-action or contextual page.
- Use the nine approved layouts: `cinematic_open`, `diagonal_debate`, `archive_collage`, `market_screen`, `timeline_scroll`, `ensemble_mosaic`, `info_breakdown`, `decision_matrix`, `silent_borderless`.
- Use limited-color cinematic manga: deep teal, paper beige, and copper-gold; red only for loss, crisis, litigation, or rule-breaking; green only for profit, breakout, or positive decisions.
- All visible text is readable Traditional Chinese.
- Historical quotations use quotation marks only when directly supported by the source.
- Every image prompt says `complete manga page`, declares page number, panel count, layout ID, character IDs, era, scene, exact visible text, continuity, final-panel emphasis, and negative constraints.
- This plan creates scripts and prompts only; it does not generate manga images.

## File Structure

### Shared production files

- Create: `outputs/novel-to-manga/turtle-trader-adult-dense/README.md`
- Create: `outputs/novel-to-manga/turtle-trader-adult-dense/adaptation-summary.md`
- Create: `outputs/novel-to-manga/turtle-trader-adult-dense/character-bible.md`
- Create: `outputs/novel-to-manga/turtle-trader-adult-dense/character-baseline.yaml`
- Create: `outputs/novel-to-manga/turtle-trader-adult-dense/scene-bible.md`
- Create: `outputs/novel-to-manga/turtle-trader-adult-dense/style-bible.md`
- Create: `outputs/novel-to-manga/turtle-trader-adult-dense/layout-library.md`
- Create: `outputs/novel-to-manga/turtle-trader-adult-dense/source-coverage.md`
- Create: `outputs/novel-to-manga/turtle-trader-adult-dense/production-tracker.md`

### Per-chapter files

- Create: `outputs/novel-to-manga/turtle-trader-adult-dense/chapters/chNN/chNN-manga-script.md`
- Create: `outputs/novel-to-manga/turtle-trader-adult-dense/image-prompts/chNN/chNN-pPP.txt`

### Validation files

- Create: `tool/validate_turtle_manga_package.py`
- Create: `tests/test_validate_turtle_manga_package.py`
- Create: `outputs/novel-to-manga/turtle-trader-adult-dense/validation-report.json`

---

### Task 1: Package Validator and Output Contract

**Files:**
- Create: `tests/test_validate_turtle_manga_package.py`
- Create: `tool/validate_turtle_manga_package.py`

**Interfaces:**
- Consumes: project root path, optional `--chapter` integer, optional `--shared-only`, and optional `--json PATH`.
- Produces: `validate_package(root: Path, chapter: int | None = None, shared_only: bool = False) -> list[dict[str, str]]`; an empty list means validation passed. The CLI writes the same issue list plus package counts to `--json PATH` when supplied.

- [ ] **Step 1: Write failing tests for missing summaries, repeated layouts, wrong page counts, and incomplete prompts**

```python
def test_rejects_chapter_without_required_summary(tmp_path):
    root = make_minimal_package(tmp_path, chapter=1, pages=7)
    script = root / "chapters/ch01/ch01-manga-script.md"
    script.write_text("# 第1章\n## Page 1\n- Layout ID: cinematic_open\n", encoding="utf-8")
    issues = validate_package(root, chapter=1)
    assert {"code": "missing-chapter-summary", "path": str(script)} in issues


def test_rejects_adjacent_duplicate_layout_ids(tmp_path):
    root = make_minimal_package(tmp_path, chapter=1, pages=7)
    write_script(root, 1, layouts=[
        "cinematic_open", "cinematic_open", "archive_collage",
        "timeline_scroll", "ensemble_mosaic", "decision_matrix", "silent_borderless",
    ])
    assert any(i["code"] == "adjacent-layout-repeat" for i in validate_package(root, chapter=1))


def test_rejects_prompt_without_complete_manga_page_contract(tmp_path):
    root = make_minimal_package(tmp_path, chapter=1, pages=7)
    (root / "image-prompts/ch01/ch01-p01.txt").write_text("Page 1", encoding="utf-8")
    assert any(i["code"] == "prompt-contract-missing" for i in validate_package(root, chapter=1))
```

- [ ] **Step 2: Run tests and confirm the validator is absent**

Run:

```powershell
& 'C:\Users\jai16\AppData\Local\Programs\Python\Python314\python.exe' -m unittest tests.test_validate_turtle_manga_package -v
```

Expected: import failure for `validate_turtle_manga_package`.

- [ ] **Step 3: Implement the validator**

Implement literal chapter page-count mapping, Markdown heading parsing, `Layout ID` extraction, prompt keyword checks, shared-file validation, file existence checks, `--chapter`, `--shared-only`, and `--json` handling. Keep it standard-library only.

- [ ] **Step 4: Run tests and verify all validator cases pass**

Run the same `unittest` command. Expected: all tests report `ok`.

- [ ] **Step 5: Commit the validator**

```powershell
git add tool\validate_turtle_manga_package.py tests\test_validate_turtle_manga_package.py
git commit -m "test: add turtle manga package validator"
```

### Task 2: Shared Canon, Character, Scene, Style, and Layout Bibles

**Files:**
- Create all shared production files listed under “Shared production files”.
- Read: `docs/superpowers/specs/2026-07-25-turtle-trader-manga-design.md`
- Read: `outputs/novel-to-manga/turtle-trader-adult-dense/source-chapters/manifest.json`
- Read: all 14 source chapter text files.

**Interfaces:**
- Produces stable character IDs, scene IDs, layout IDs, color rules, prompt contract, and tracker columns consumed by every chapter task.

- [ ] **Step 1: Build the canon index**

Record every recurring named person, role, first chapter, era, relationship, and source spelling in `adaptation-summary.md`. Separate directly sourced facts from visual adaptation choices.

- [ ] **Step 2: Build `character-bible.md` and `character-baseline.yaml`**

Include at minimum Richard Dennis, William Eckhardt, the named Turtle trainees, and later-generation traders actually present in the source. Every YAML entry must contain non-empty `id`, `name_zh`, `role`, `age_or_apparent_age`, `visual_tags`, `dialogue_style`, `relationship_cues`, `do_not_change`, and `first_appears`.

- [ ] **Step 3: Build scene, style, and layout bibles**

Define Chicago trading pits, C&D offices, the 1983 training room, trading desks, post-program fund offices, court/media environments, and the nine approved layouts. Include the historical-prop bans and exact color semantics from Global Constraints.

- [ ] **Step 4: Initialize source coverage and production tracking**

`source-coverage.md` must list all source section headings under their chapter with empty page mappings represented as `pending`. `production-tracker.md` must contain 120 page rows with chapter, page, theme, layout ID, script status, prompt status, image status, and notes.

- [ ] **Step 5: Validate shared files**

Run:

```powershell
& 'C:\Users\jai16\AppData\Local\Programs\Python\Python314\python.exe' tool\validate_turtle_manga_package.py outputs\novel-to-manga\turtle-trader-adult-dense --shared-only
```

Expected: `0 shared issues`.

- [ ] **Step 6: Commit shared production foundations**

```powershell
git add outputs\novel-to-manga\turtle-trader-adult-dense
git commit -m "docs: establish turtle manga production bibles"
```

### Task 3: Chapter 1 — 先天與後天的贏家爭論

**Files:**
- Read: `source-chapters/01-第一章 先天與後天的贏家爭論.txt`
- Create: `chapters/ch01/ch01-manga-script.md`
- Create: `image-prompts/ch01/ch01-p01.txt` through `ch01-p07.txt`
- Modify: `source-coverage.md`, `production-tracker.md`

**Requirements:** Seven pages. Cover the Turtle experiment proposition, the nature-versus-training debate, the recruitment concept, and “傳奇海龜計畫”／“非典型明智之舉”. Favor `cinematic_open`, `diagonal_debate`, `archive_collage`, and `timeline_scroll`.

- [ ] Write the complete bullet chapter summary and must-keep list.
- [ ] Create the seven-page list with distinct page functions and non-repeating adjacent layout IDs.
- [ ] Write all panel scripts with exact Traditional Chinese visible text.
- [ ] Write seven complete manga-page prompts using stable character and scene IDs.
- [ ] Map every Chapter 1 source section to pages in `source-coverage.md`.
- [ ] Run `validate_turtle_manga_package.py ... --chapter 1`; expected: `0 issues`.
- [ ] Commit with `git commit -m "docs: script turtle manga chapter 1"`.

### Task 4: Chapter 2 — 交易廳王者的崛起

**Files:** Create Chapter 2 script and 12 prompts; update coverage and tracker.

**Requirements:** Twelve pages. Cover “反骨的金錢觀”, “習得莊家思維”, “世界最大交易廳”, “幕後操盤”, “投資政治版圖”, and “非理性期望”. Use at least six layouts, emphasizing trading-pit cinema, market screens, archival material, and timeline progression.

- [ ] Write the complete bullet chapter summary and must-keep list.
- [ ] Build the 12-page plan with at least six layouts and no adjacent repetition.
- [ ] Script all panels and historically appropriate props.
- [ ] Write prompts `ch02-p01.txt` through `ch02-p12.txt`.
- [ ] Update source coverage and tracker.
- [ ] Validate Chapter 2 with expected `0 issues`.
- [ ] Commit with `git commit -m "docs: script turtle manga chapter 2"`.

### Task 5: Chapter 3 — 包羅萬象的海龜組合

**Files:** Create Chapter 3 script and 13 prompts; update coverage and tracker.

**Requirements:** Thirteen pages. Cover “致富好運來自隨機”, “攸關一生的面試”, “簽下五年賣身契”, and “傳授獲利之道的殿堂”. Establish the trainee ensemble with stable IDs and distinguish candidates through silhouette, posture, and interview behavior.

- [ ] Write the complete bullet chapter summary and named-person checklist.
- [ ] Build a 13-page plan using at least six layouts, led by ensemble mosaic and archive collage.
- [ ] Script interview cross-cutting, contract details, and training-room transition.
- [ ] Write prompts `ch03-p01.txt` through `ch03-p13.txt`.
- [ ] Update coverage and tracker.
- [ ] Validate Chapter 3 with expected `0 issues`.
- [ ] Commit with `git commit -m "docs: script turtle manga chapter 3"`.

### Task 6: Chapter 4 — 規則，最強交易哲理

**Files:** Create Chapter 4 script and 10 prompts; update coverage and tracker.

**Requirements:** Ten pages. Cover scientific-method thinking, “系統框限，收益無限”, and “不怕損失，只怕錯失”. Interleave debate, action examples, decision matrices, and information breakdowns; never place two information-only pages consecutively.

- [ ] Write the complete bullet chapter summary and concept list.
- [ ] Build the 10-page plan with at least six layouts.
- [ ] Script abstract rules as observable decisions and market consequences.
- [ ] Write prompts `ch04-p01.txt` through `ch04-p10.txt`.
- [ ] Update coverage and tracker.
- [ ] Validate Chapter 4 with expected `0 issues`.
- [ ] Commit with `git commit -m "docs: script turtle manga chapter 4"`.

### Task 7: Chapter 5 — 致勝海龜交易法則

**Files:** Create Chapter 5 script and 14 prompts; update coverage and tracker.

**Requirements:** Fourteen pages. Preserve expectation-value formula and definitions, entry timing, breakout system, avoidance of market timing, N-value volatility, unit limits, pyramiding, loss response, exit rules, and portfolio/correlation rules. Use real numeric examples from the source and the densest C-style pages, separated by character-action pages.

- [ ] Write the complete bullet chapter summary and exact formula glossary.
- [ ] Build a 14-page plan using at least seven of the nine layouts.
- [ ] Script all rules with examples, decisions, and consequences.
- [ ] Write prompts `ch05-p01.txt` through `ch05-p14.txt`.
- [ ] Update coverage and tracker with one mapping per rule section.
- [ ] Validate Chapter 5 with expected `0 issues`.
- [ ] Commit with `git commit -m "docs: script turtle manga chapter 5"`.

### Task 8: Chapter 6 — 實戰開始！海龜入市初試

**Files:** Create Chapter 6 script and eight prompts; update coverage and tracker.

**Requirements:** Eight pages. Cover “簡單環境，自由發揮”, “策略性不交易的時間”, and “同生共死的部落氛圍”. Emphasize live-market tension, restraint, and group identity.

- [ ] Write the complete bullet chapter summary.
- [ ] Build the eight-page plan with at least four layouts.
- [ ] Script action-led market sequences and quiet non-trading decisions.
- [ ] Write prompts `ch06-p01.txt` through `ch06-p08.txt`.
- [ ] Update coverage and tracker.
- [ ] Validate Chapter 6 with expected `0 issues`.
- [ ] Commit with `git commit -m "docs: script turtle manga chapter 6"`.

### Task 9: Chapter 7 — 檯面下潛藏的角力鬥爭

**Files:** Create Chapter 7 script and 10 prompts; update coverage and tracker.

**Requirements:** Ten pages. Cover unequal capital allocation, strong performance being undervalued, Table 7.1 performance material, and trading-system misjudgment. Use archive collage, data/dashboard pages, diagonal conflict, and decision matrices.

- [ ] Write the complete bullet chapter summary and performance-data checklist.
- [ ] Build the 10-page plan with at least six layouts.
- [ ] Script conflict through allocations, reactions, and consequences rather than exposition alone.
- [ ] Write prompts `ch07-p01.txt` through `ch07-p10.txt`.
- [ ] Update coverage and tracker.
- [ ] Validate Chapter 7 with expected `0 issues`.
- [ ] Commit with `git commit -m "docs: script turtle manga chapter 7"`.

### Task 10: Chapter 8 — 毫無預警的計畫終止

**Files:** Create Chapter 8 script and five prompts; update coverage and tracker.

**Requirements:** Five pages. Cover the sudden end, litigation involving the Turtle originator, and the first public appearance of the Turtle story. Favor cinematic, archival, and silent-borderless layouts.

- [ ] Write the complete bullet chapter summary.
- [ ] Build a five-page dramatic arc using at least four layouts.
- [ ] Script the termination and litigation with restrained dialogue and desaturated imagery.
- [ ] Write prompts `ch08-p01.txt` through `ch08-p05.txt`.
- [ ] Update coverage and tracker.
- [ ] Validate Chapter 8 with expected `0 issues`.
- [ ] Commit with `git commit -m "docs: script turtle manga chapter 8"`.

### Task 11: Chapter 9 — 自力更生，還是掙扎求生

**Files:** Create Chapter 9 script and seven prompts; update coverage and tracker.

**Requirements:** Seven pages. Cover “靠神祕感獲資金”, institutional preference for safety, adherence to original rules, and the “all the same” label. Use ensemble comparison, archive collage, and decision matrices.

- [ ] Write the complete bullet chapter summary.
- [ ] Build the seven-page comparison arc using at least four layouts.
- [ ] Script divergent post-program outcomes without collapsing individuals.
- [ ] Write prompts `ch09-p01.txt` through `ch09-p07.txt`.
- [ ] Update coverage and tracker.
- [ ] Validate Chapter 9 with expected `0 issues`.
- [ ] Commit with `git commit -m "docs: script turtle manga chapter 9"`.

### Task 12: Chapter 10 — 傳奇交易員重出江湖

**Files:** Create Chapter 10 script and six prompts; update coverage and tracker.

**Requirements:** Six pages. Cover public sale of the once-secret system and the final major profit episode. Contrast secrecy, commercialization, and actual edge.

- [ ] Write the complete bullet chapter summary.
- [ ] Build a six-page arc using at least four layouts.
- [ ] Script media/commercialization scenes against live market evidence.
- [ ] Write prompts `ch10-p01.txt` through `ch10-p06.txt`.
- [ ] Update coverage and tracker.
- [ ] Validate Chapter 10 with expected `0 issues`.
- [ ] Commit with `git commit -m "docs: script turtle manga chapter 10"`.

### Task 13: Chapter 11 — 初代海龜群的佼佼者

**Files:** Create Chapter 11 script and nine prompts; update coverage and tracker.

**Requirements:** Nine pages. Cover the nine top-Turtle traits, confidence in the system, rejection of fundamental-analysis fashion, the danger of mean reversion, and the role of luck. Use ensemble mosaic and information breakdown while retaining character examples.

- [ ] Write the complete bullet chapter summary and nine-trait checklist.
- [ ] Build the nine-page plan using at least four layouts.
- [ ] Script each abstract trait through a sourced person, action, or decision.
- [ ] Write prompts `ch11-p01.txt` through `ch11-p09.txt`.
- [ ] Update coverage and tracker.
- [ ] Validate Chapter 11 with expected `0 issues`.
- [ ] Commit with `git commit -m "docs: script turtle manga chapter 11"`.

### Task 14: Chapter 12 — 靠向失敗的海龜

**Files:** Create Chapter 12 script and five prompts; update coverage and tracker.

**Requirements:** Five pages. Cover using fame for profit and the “false charity, real profit” example. Maintain a restrained, evidence-led ethical critique and avoid caricature.

- [ ] Write the complete bullet chapter summary.
- [ ] Build a five-page cautionary arc using at least four layouts.
- [ ] Script claims, actions, and consequences with archival and decision-matrix evidence.
- [ ] Write prompts `ch12-p01.txt` through `ch12-p05.txt`.
- [ ] Update coverage and tracker.
- [ ] Validate Chapter 12 with expected `0 issues`.
- [ ] Commit with `git commit -m "docs: script turtle manga chapter 12"`.

### Task 15: Chapter 13 — 青出於藍的二代海龜

**Files:** Create Chapter 13 script and nine prompts; update coverage and tracker.

**Requirements:** Nine pages. Cover meeting first-generation Turtles, courage to take the chance, securing investment, revival of Turtle training, and “killer-like” trading decisions. Distinguish inheritance from imitation.

- [ ] Write the complete bullet chapter summary and generation-link checklist.
- [ ] Build the nine-page plan using at least four layouts.
- [ ] Script mentorship, risk-taking, and second-generation adaptation.
- [ ] Write prompts `ch13-p01.txt` through `ch13-p09.txt`.
- [ ] Update coverage and tracker.
- [ ] Validate Chapter 13 with expected `0 issues`.
- [ ] Commit with `git commit -m "docs: script turtle manga chapter 13"`.

### Task 16: Chapter 14 — 交易員的偉大典範

**Files:** Create Chapter 14 script and five prompts; update coverage and tracker.

**Requirements:** Five pages. Cover resilience after falling, deliberate practice, and the final synthesis that durable performance comes from human behavior plus system discipline. End with a cinematic and quiet conclusion rather than a classroom summary.

- [ ] Write the complete bullet chapter summary.
- [ ] Build a five-page concluding arc using at least four layouts.
- [ ] Script resilience and deliberate practice through action, repetition, and visual callbacks.
- [ ] Write prompts `ch14-p01.txt` through `ch14-p05.txt`.
- [ ] Update coverage and tracker.
- [ ] Validate Chapter 14 with expected `0 issues`.
- [ ] Commit with `git commit -m "docs: script turtle manga chapter 14"`.

### Task 17: Whole-Book Coverage and Prompt QA

**Files:**
- Modify: `source-coverage.md`
- Modify: `production-tracker.md`
- Create: `validation-report.json`

**Interfaces:**
- Consumes all shared files, 14 scripts, and 120 prompt files.
- Produces the final machine-readable issue report.

- [ ] **Step 1: Run full validation**

```powershell
& 'C:\Users\jai16\AppData\Local\Programs\Python\Python314\python.exe' tool\validate_turtle_manga_package.py outputs\novel-to-manga\turtle-trader-adult-dense --json outputs\novel-to-manga\turtle-trader-adult-dense\validation-report.json
```

Expected: 14 chapters, 120 pages, 120 prompts, and `0 issues`.

- [ ] **Step 2: Audit source coverage**

Confirm that every source heading listed in `source-coverage.md` maps to one or more page IDs and no entry remains `pending`.

- [ ] **Step 3: Audit layout diversity**

Confirm chapter minimum layout counts, adjacent layout rotation, six-grid limits, and the action-page buffer around every information-only page.

- [ ] **Step 4: Audit prompt readability and continuity**

Check every prompt for exact page number, panel count, layout ID, stable character IDs, Traditional Chinese visible text, era, scene, previous-page context, final-panel emphasis, and negative constraints.

- [ ] **Step 5: Update README and tracker to final script/prompt status**

Images remain `pending`; scripts and prompts become `passed`.

- [ ] **Step 6: Commit final package QA**

```powershell
git add outputs\novel-to-manga\turtle-trader-adult-dense
git commit -m "docs: finalize turtle trader manga production package"
```

## Execution Checkpoints

- Checkpoint A: Tasks 1–2 complete — validator and shared bibles reviewed.
- Checkpoint B: Tasks 3–7 complete — Chapters 1–5 reviewed before continuing.
- Checkpoint C: Tasks 8–12 complete — Chapters 6–10 reviewed before continuing.
- Checkpoint D: Tasks 13–17 complete — Chapters 11–14 and whole-book QA reviewed.
