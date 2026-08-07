# Image Stack MPR Single-Column Layout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the fixed left setup sidebar with a full-width vertical document flow that can organize approximately 100 images per sequence without clipping boundary sliders.

**Architecture:** Preserve the existing HTML structure and JavaScript behavior. Change only layout CSS, while a real headless Chromium regression test injects representative boundary controls and 100 thumbnail cards into the existing page and measures their rendered geometry.

**Tech Stack:** Standalone HTML/CSS/JavaScript, Python `unittest`, local headless Chrome or Edge.

## Global Constraints

- All image processing remains local and offline.
- Do not change `tool/us-probe-ct-plane.html`.
- Keep each sequence's thumbnails in one horizontally scrollable row.
- Do not modify crosslink, volume, MPR, or viewport interaction logic.

---

### Task 1: Full-width vertical setup and timeline layout

**Files:**

- Modify: `tests/test_image_stack_mpr.py`
- Modify: `tool/image-stack-mpr.html`

**Interfaces:**

- Consumes: existing `.body`, `.sidebar`, `.main`, `.boundary-row`, `.thumbnail-strip`, and `.thumbnail-card` DOM/CSS contracts.
- Produces: a single-column rendered layout in which setup precedes the viewer, boundary controls stay contained, and 100 thumbnails form one horizontal timeline.

- [x] **Step 1: Write the failing rendered-layout test**

Add a headless-browser helper that loads the real standalone page, injects two `.boundary-row` elements and 100 `.thumbnail-card` elements, then returns bounding boxes and scroll dimensions. Assert these literal behaviors:

```python
def test_setup_and_sequence_timeline_use_full_width_vertical_flow(self) -> None:
    layout = measure_full_width_layout()
    self.assertGreaterEqual(layout["mainTop"], layout["sidebarBottom"] - 1)
    self.assertAlmostEqual(layout["sidebarWidth"], layout["mainWidth"], delta=2)
    self.assertLessEqual(layout["sliderRight"], layout["boundaryRight"] + 0.5)
    self.assertEqual(layout["thumbnailRows"], 1)
    self.assertGreater(layout["timelineScrollWidth"], layout["timelineClientWidth"])
```

- [x] **Step 2: Run the test and confirm RED**

Run:

```powershell
& 'C:\Users\jai16\AppData\Local\Programs\Python\Python314\python.exe' -m unittest tests.test_image_stack_mpr.ImageStackMprTests.test_setup_and_sequence_timeline_use_full_width_vertical_flow -v
```

Expected: FAIL because `.body` currently renders 300 px setup and viewer columns side by side.

- [x] **Step 3: Implement the minimal CSS change**

Use one grid column and document scrolling, while preserving the existing markup:

```css
.body { grid-template-columns: minmax(0, 1fr); }
.sidebar { min-width: 0; overflow: visible; border-right: 0; border-bottom: 1px solid var(--line); }
.main { min-width: 0; overflow: visible; }
.boundary-row { grid-template-columns: 76px minmax(0, 1fr) 42px; min-width: 0; }
.boundary-row input { width: 100%; min-width: 0; max-width: 100%; margin: 0; }
```

- [x] **Step 4: Verify GREEN and regression safety**

Run:

```powershell
& 'C:\Users\jai16\AppData\Local\Programs\Python\Python314\python.exe' -m unittest tests.test_image_stack_mpr -v
& 'C:\Users\jai16\AppData\Local\Programs\Python\Python314\python.exe' -m unittest tests.test_us_probe_ct_plane -v
git diff --check
```

Expected: all tests PASS; `git diff --check` produces no output; `tool/us-probe-ct-plane.html` remains unchanged.

- [x] **Step 5: Record the result**

Update this task's checkboxes only after RED, GREEN, full regression, offline scan, and diff verification have each completed successfully.
