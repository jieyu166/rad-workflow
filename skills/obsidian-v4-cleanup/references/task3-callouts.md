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
