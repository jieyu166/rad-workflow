# Task 8 — 任意筆記的現代新知查核

## Purpose

Use this workflow for any existing Radiology/medical Obsidian note, regardless of whether its original source is a PDF, textbook, journal article, lecture, website, transcript, personal synthesis, or mixed material. Preserve provenance: original-source content and modern evidence are distinct layers.

## Workflow

1. Read the target note without modifying it.
2. Parse YAML and inventory declared sources, dates, note type, sections, figures/tables, SR comments, embeds, Dataview blocks, and wikilinks.
3. Resolve and read original sources when available. For PDF sources, use Task 5 extraction/rendering rules when a source claim or figure requires page-level verification. For lecture/video sources, use Task 4 source priority. If no reliable original source exists, mark the affected claims `source_unresolved`.
4. Extract material claims into an audit ledger. Include terminology, anatomy, epidemiology, pathology, imaging findings, protocols, diagnostic thresholds, classification/staging, differential diagnosis, pitfalls, management, follow-up, and figure/table interpretation.
5. Use `radiology-topic-research` to verify current knowledge. Prioritize:
   1. current society guidelines, formal consensus, and WHO classifications;
   2. STATdx current topic;
   3. current ClinicalKey radiology textbook chapter;
   4. RadioGraphics review;
   5. AJR review or primary study;
   6. Radiopaedia for structured orientation, not as sole support for critical thresholds or management.
6. Record exact article/chapter/guideline metadata and the date accessed. Do not cite a search result, snippet, AI summary, or unread link as verified evidence.
7. Assign exactly one primary status to every material claim:
   - `仍成立`: materially consistent with current evidence.
   - `需補充`: not wrong, but missing a clinically important qualifier or modern development.
   - `已更新`: terminology, classification, cutoff, protocol, or recommendation has changed.
   - `已淘汰`: current evidence/guideline advises against it or the concept is no longer accepted.
   - `來源衝突`: credible current sources disagree; preserve all positions.
   - `無法查證`: available evidence is insufficient.
   Use `source_unresolved` as an additional provenance flag when the original basis cannot be verified.
8. Finish the read-only matrix before edits. If critical Tier 1 sources require authentication, list the pages and leave affected rows `待登入查核`.
9. Archive the original note at the user-designated archive root, preserving vault-relative path. Record original and archive SHA-256 and require equality before overwrite.
10. Preserve the original/source-grounded layer. Correct it only when comparison with its own original source proves mistranscription, mistranslation, or misquotation; never use modern evidence as the justification for rewriting historical content.
11. Append/update the modern audit layer using the output template below. Add concise update callouts to Summary only for changes that materially affect current interpretation/reporting/management.
12. Update Canvas only when the conceptual model changes materially. Use visually distinct nodes for the modern layer and labeled edges such as `現代更新`, `已淘汰`, `補充限制`, or `證據衝突`.
13. Validate the note, artifacts, citations, hashes, and audit report.

## Research Scope

Audit all material claims relevant to the note:

- Anatomy and terminology
- Disease names and WHO classification
- Epidemiology and risk factors
- Pathology and mechanism
- Imaging findings by modality
- Acquisition protocol and sequences
- Diagnostic criteria, quantitative thresholds, and grading/staging
- Differential diagnosis and pitfalls
- Management, biopsy, follow-up, and surveillance
- Existing figure/table interpretation
- Important modern concepts absent from the original note when omission would affect current practice

Do not manufacture updates to fill every category. Use `N/A（本次查核未發現）` when appropriate.

## Evidence Rules

- Every modern factual statement must map to an actually reviewed source.
- Cite journals at article level with DOI; books at chapter/edition/page level; guidelines by organization/version/section/official URL/access date.
- Prefer current guidelines for management, treatment thresholds, follow-up, and protocols.
- Preserve historical and current guidance side by side when an older question/source depends on the older version.
- When numbers conflict, report each number with its population, denominator, conditions, and source; do not average them or choose one silently.
- Radiopaedia may support overview and navigation but should not be the only source for consequential recommendations or cutoffs.
- Do not use model memory as evidence.
- Do not log in, handle credentials, bypass access controls, or download restricted PDFs. Ask the user to authenticate in their own browser and resume on the accessible page.

## Claim Matrix

```markdown
| 原筆記主張 | 原始來源定位 | 判定 | 現行知識 | Tier 1證據 | 主文處理 |
|---|---|---|---|---|---|
| 原文或精確摘要 | PDF p./section/lecture timestamp/note section；無則source_unresolved | 仍成立／需補充／已更新／已淘汰／來源衝突／無法查證 | 保守摘要，保留條件與例外 | [^n] | 保留／加update callout／移至歷史觀點／待人工複核 |
```

## Required Note Layer

```markdown
# 現代新知查核（查核日期：YYYY-MM-DD）

> [!update] 現代更新摘要
> 僅列會影響目前判讀、報告、classification、protocol或management的變動。

## 仍然成立的核心觀念

## 已更新的術語與分類

## 新增的影像判讀重點

## 已不建議或已淘汰的觀點

## 現代 Management / Follow-up 差異

## 原有 Figures / Tables 的現代閱讀方式

## 證據分歧與尚未確定事項

## 新知查核矩陣

| 原筆記主張 | 原始來源定位 | 判定 | 現行知識 | Tier 1證據 | 主文處理 |
|---|---|---|---|---|---|

### 新知查核參考來源
[^1]: Article/chapter/guideline-level citation.
```

Keep the original YAML `source` entries unchanged unless they are factually malformed. Modern sources belong in audit-layer footnotes. If machine-readable provenance is requested, add an optional YAML list such as:

```yaml
evidence_update:
  - "Organization. Guideline title. Version/year. Accessed YYYY-MM-DD."
```

Do not require this optional field by default.

## Figure and Table Audit

For every important existing figure/table:

1. Verify what the original artifact actually shows and how the original source described it.
2. State whether terminology, classification, differential diagnosis, or management implication has changed.
3. Never add a finding absent from the image/table.
4. Keep the source caption/description in the original layer; place the current interpretation in the modern layer.
5. Mark unavailable or unreadable artifacts `無法查證` rather than inventing a typical appearance.

## Archive and Artifact Rules

- Archive before write and preserve the vault-relative path.
- Verify original/archive SHA-256 equality.
- Preserve SR comments byte-for-byte.
- Preserve valid image embeds, Dataview blocks, and wikilinks.
- Do not create placeholder wikilinks.
- Record replacement SHA-256 after the final write.

## Batch Rules

- Default to five notes per batch unless the user specifies otherwise.
- Complete the read-only audit, research, edit, and verification for one note before the next.
- Do not paste a generic update paragraph into every note.
- A blocked note remains unchanged and receives an explicit blocker; continue other in-scope notes.

## Audit Report

For each note record:

- Note path and original-source paths
- Source resolution status
- Archive path
- Modern sources actually reviewed
- Counts: 仍成立／需補充／已更新／已淘汰／來源衝突／無法查證／待登入查核
- Material changes and why they matter
- Figure/table updates
- Access blockers and unresolved claims
- Original, archive, and replacement SHA-256
- Validation date and PASS/FAIL

## Reusable User Prompt

```text
請使用 $obsidian-v4-cleanup Task 8，對以下既有筆記進行現代新知查核：

目標筆記：
"<筆記或資料夾完整路徑>"

原始來源：
"<若已知，填入PDF／書籍／期刊／影片／講義／網站路徑；未知則寫請從YAML解析>"

另使用 $radiology-topic-research 查核Tier 1來源。

要求：
1. 先做read-only audit，解析原筆記主張與來源；來源缺失或無法唯一解析時標示source_unresolved。
2. 原始／歷史內容與現代知識必須分層，不得用新版資料靜默改寫舊來源。
3. 對術語、WHO分類、imaging findings、protocol、criteria、threshold、DDx、pitfalls、management、follow-up及figures/tables逐項判定：
   仍成立／需補充／已更新／已淘汰／來源衝突／無法查證。
4. 現代更新必須來自實際讀過的guideline／WHO／STATdx／ClinicalKey／RadioGraphics／AJR等article或chapter級來源。
5. 重要數值或建議若分歧，保留各來源條件與數值，不自行選一個。
6. 付費來源需要登入時，列出待登入頁面讓我自行登入；不得用模型記憶或較弱來源假裝完成。
7. 完成查核矩陣後才可修改。修改前依vault相對路徑封存原稿並驗證SHA-256。
8. 在筆記新增獨立的「# 現代新知查核（查核日期）」區塊及footnotes；原YAML source保留原始來源。
9. SR comments、有效image embeds、Dataview blocks與wikilinks保持不變。
10. 產出稽核報告，列出判定統計、重要更新、來源、阻塞、archive及原稿／新稿SHA-256、PASS／FAIL。

若為資料夾，每批先做5篇，每篇獨立完成查核與驗證，不得套用相同通用更新文字。
```

## Verification

- YAML and Markdown structure remain valid.
- Original/source layer remains distinguishable from modern evidence.
- Every matrix row has source locator, status, evidence, and disposition.
- Every modern factual addition has a reviewed citation.
- No unsupported threshold, classification, protocol, management, or figure finding was added.
- Conflicts and access blockers are explicit.
- Archive hash matches original; replacement hash is recorded.
- SR comments and valid personal artifacts remain intact.
- Canvas parses if changed and distinguishes modern nodes.
- Audit report is complete.
