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


## 驗證

### Tasks 1-3 (Cleanup)
- [ ] YAML parses without errors
- [ ] All required V4 fields present with correct types
- [ ] No non-standard fields remain
- [ ] No old inline metadata lines remain
- [ ] Footnotes properly numbered and defined (if converted)
- [ ] 閱片 callouts use correct format (if converted)
- [ ] SR comments untouched
- [ ] Image embeds untouched
