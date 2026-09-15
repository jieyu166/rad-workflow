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
