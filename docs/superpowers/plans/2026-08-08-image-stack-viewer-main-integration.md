# Image Stack Viewer Main Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Merge the completed offline image stack viewer branch into local `main` and expose it from the root `index.html` Web Tools navigation.

**Architecture:** Preserve the seven existing viewer commits with a non-fast-forward merge from `codex/image-stack-mpr-viewer-clean`. Add one root-navigation regression test and one matching list item in `index.html`; do not copy the HTML manually or squash away its tests, OpenSpec artifacts, and design history.

**Tech Stack:** Git, static HTML, Python `unittest`, local headless Chrome or Edge for the existing viewer suite.

## Global Constraints

- Preserve every existing untracked Manga output, `ahk-scripts/0knee wait.txt`, `新增 文字文件.txt`, and `rib-fracture-cxr/` without staging or modifying them.
- Merge into local `main`; do not push `main` unless the user asks separately.
- Keep `tool/us-probe-ct-plane.html` unchanged.
- The root link must use relative href `tool/image-stack-mpr.html` and visible text `影像序列 Crosslink 與 MPR`.
- Add no external assets or network dependency.

---

### Task 1: Verify and merge the viewer branch

**Files:**

- Integrate: commits on `codex/image-stack-mpr-viewer-clean`
- Preserve: all existing untracked paths in the main checkout

**Interfaces:**

- Consumes: branch head `8ec80c3` and local `main`.
- Produces: a merge commit on `main` containing `tool/image-stack-mpr.html`, `tests/test_image_stack_mpr.py`, and the related OpenSpec/design files.

- [x] **Step 1: Run the viewer branch regression suite**

```powershell
python -m unittest tests.test_image_stack_mpr -v
```

Expected: 29 tests pass before integration.

- [x] **Step 2: Reconfirm merge scope and untracked preservation**

```powershell
git status --short --branch
git diff --name-status main...codex/image-stack-mpr-viewer-clean
```

Expected: the branch diff contains only viewer plans/specs, OpenSpec files, `tests/test_image_stack_mpr.py`, and `tool/image-stack-mpr.html`; no existing main untracked path overlaps.

- [x] **Step 3: Merge without flattening history**

```powershell
git merge --no-ff codex/image-stack-mpr-viewer-clean -m "merge: integrate image stack MPR viewer"
```

Expected: merge succeeds without conflicts and untracked paths remain untracked.

---

### Task 2: Add the root navigation link with TDD

**Files:**

- Create: `tests/test_index_navigation.py`
- Modify: `index.html`

**Interfaces:**

- Consumes: root `index.html` Web Tools `<ul>` and merged `tool/image-stack-mpr.html`.
- Produces: one navigable list item with exact href and visible label.

- [x] **Step 1: Write the failing navigation test**

```python
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).parents[1]


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag, attrs) -> None:
        if tag == "a":
            self._href = dict(attrs).get("href")
            self._text = []

    def handle_data(self, data) -> None:
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag) -> None:
        if tag == "a" and self._href is not None:
            self.links.append((self._href, "".join(self._text).strip()))
            self._href = None
            self._text = []


class IndexNavigationTests(unittest.TestCase):
    def test_index_links_to_image_stack_mpr_viewer(self) -> None:
        parser = LinkParser()
        parser.feed((ROOT / "index.html").read_text(encoding="utf-8"))

        self.assertIn(
            ("tool/image-stack-mpr.html", "影像序列 Crosslink 與 MPR"),
            parser.links,
        )
        self.assertTrue((ROOT / "tool" / "image-stack-mpr.html").is_file())
```

- [x] **Step 2: Run the new test and verify RED**

```powershell
python -m unittest tests.test_index_navigation -v
```

Expected: FAIL because the viewer link is not yet present in `index.html`.

- [x] **Step 3: Add the minimal Web Tools entry**

Insert this list item with the other local radiology tools:

```html
<li><a href="tool/image-stack-mpr.html">影像序列 Crosslink 與 MPR</a></li>
```

- [x] **Step 4: Run the new test and verify GREEN**

```powershell
python -m unittest tests.test_index_navigation -v
```

Expected: PASS and the target file exists in the merged tree.

---

### Task 3: Verify and commit the index integration

**Files:**

- Create: `docs/superpowers/plans/2026-08-08-image-stack-viewer-main-integration.md`
- Create: `tests/test_index_navigation.py`
- Modify: `index.html`

**Interfaces:**

- Consumes: the merged viewer and Task 2 navigation entry.
- Produces: a clean local `main` with a separate index-navigation commit.

- [x] **Step 1: Run complete relevant verification**

```powershell
python -m unittest tests.test_image_stack_mpr tests.test_us_probe_ct_plane tests.test_index_navigation -v
python -m py_compile tests/test_image_stack_mpr.py tests/test_us_probe_ct_plane.py tests/test_index_navigation.py
spectra validate add-image-stack-mpr-viewer
git diff --check
git diff --exit-code HEAD^ -- tool/us-probe-ct-plane.html
```

Expected: all tests pass, OpenSpec is valid, whitespace is clean, and the probe HTML remains unchanged.

- [x] **Step 2: Confirm exact staged scope**

Stage only:

```text
docs/superpowers/plans/2026-08-08-image-stack-viewer-main-integration.md
index.html
tests/test_index_navigation.py
```

Existing untracked paths must remain unstaged.

- [x] **Step 3: Commit the navigation integration**

```powershell
git commit -m "feat: link image stack viewer from index"
```

- [x] **Step 4: Preserve the linked worktree and report local-main status**

Do not delete the worktree or feature branch and do not push `main`. Report the merge commit, navigation commit, tests, and remaining untracked groups.
