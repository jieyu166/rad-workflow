## Task 8: 任意筆記的現代新知查核

Applies when the user asks to verify, update, fact-check, modernize, or identify outdated medical/radiology knowledge in any existing note. The note may originate from a paper, textbook, lecture, website, conference, personal synthesis, or mixed sources; it does not need to be a Harnsberger or PDF L3 note.

Before acting, read [references/task8-modern-knowledge-audit.md](task8-modern-knowledge-audit.md) completely and follow it as the execution contract and reusable prompt.

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

## 驗證

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

