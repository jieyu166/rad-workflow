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
