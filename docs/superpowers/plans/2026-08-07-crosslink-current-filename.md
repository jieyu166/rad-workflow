# Crosslink Current Filename Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Display each Crosslink axial viewport's current source PNG/JPG filename below the image and keep it synchronized with the rendered slice.

**Architecture:** Add deterministic canonical filename mapping to `ImageStackMprCore`, store that mapping as `volume.sliceNames`, and add a Crosslink-only filename footer to each axial viewport. A pure Node VM test verifies forward/reverse/fractional mapping, while an instrumented local headless Chromium fixture calls the real viewport functions and verifies rendered footer text, title, and MPR exclusion.

**Tech Stack:** Standalone HTML/CSS/JavaScript, Canvas 2D, Python `unittest`, Node `vm`, local headless Chrome or Edge.

## Global Constraints

- Display format is `檔案：<原始檔名>`.
- Fractional positions use the same rounded axial slice shown by the Crosslink viewport.
- Excluded and decode-failed images are absent because `includedItems()` is the mapping input.
- Forward/reverse ordering must use the same `canonicalToSource()` mapping as volume voxel construction.
- MPR AX/COR/SAG/Oblique viewports must not show a filename footer.
- Do not change `tool/us-probe-ct-plane.html` or introduce external assets/network access.

---

### Task 1: Canonical slice filename mapping and Crosslink footer

**Files:**

- Modify: `tests/test_image_stack_mpr.py`
- Modify: `tool/image-stack-mpr.html`

**Interfaces:**

- Consumes: `canonicalToSource(x, y, z, sourceWidth, sourceHeight, sourceDepth, geometry)`, `includedItems(sequenceId)`, `state.positions`, and existing `createViewport()`/`renderViewportNow()` lifecycle.
- Produces: `canonicalSliceNames(items, geometry) -> string[]`, `sliceNameAtPosition(sliceNames, position) -> string`, `volume.sliceNames`, and Crosslink-only `viewport.filename` elements.

- [ ] **Step 1: Write failing mapping and browser behavior tests**

Add a pure-core test with literal expected names:

```python
def test_canonical_slice_filename_mapping(self) -> None:
    result = run_core(r"""
(() => {
  const items = [
    {name: "0001.jpg", width: 8, height: 6},
    {name: "0002.jpg", width: 8, height: 6},
    {name: "0003.jpg", width: 8, height: 6}
  ];
  const forward = ImageStackMprCore.canonicalSliceNames(
    items, ImageStackMprCore.normalizeGeometry({order: "forward"})
  );
  const reverse = ImageStackMprCore.canonicalSliceNames(
    items, ImageStackMprCore.normalizeGeometry({order: "reverse"})
  );
  return {
    forward,
    reverse,
    fractional: ImageStackMprCore.sliceNameAtPosition(forward, 1.4),
    roundedUp: ImageStackMprCore.sliceNameAtPosition(forward, 1.6),
    clamped: ImageStackMprCore.sliceNameAtPosition(forward, 99)
  };
})()
""")
    self.assertEqual(result["forward"], ["0001.jpg", "0002.jpg", "0003.jpg"])
    self.assertEqual(result["reverse"], ["0003.jpg", "0002.jpg", "0001.jpg"])
    self.assertEqual(result["fractional"], "0002.jpg")
    self.assertEqual(result["roundedUp"], "0003.jpg")
    self.assertEqual(result["clamped"], "0003.jpg")
```

Add a headless-browser test that instruments the real app IIFE to expose `state`, `createViewport`, and `updateViewportFilename`; create one Crosslink AX and one MPR AX viewport, then assert:

```python
self.assertEqual(result["crosslinkText"], "檔案：0002.jpg")
self.assertEqual(result["crosslinkTitle"], "0002.jpg")
self.assertTrue(result["footerBelowCard"])
self.assertFalse(result["mprHasFilename"])
```

- [ ] **Step 2: Run the two tests and confirm RED**

Run:

```powershell
& 'C:\Users\jai16\AppData\Local\Programs\Python\Python314\python.exe' -m unittest tests.test_image_stack_mpr.ImageStackMprTests.test_canonical_slice_filename_mapping tests.test_image_stack_mpr.ImageStackMprTests.test_crosslink_viewport_displays_current_filename_below_image -v
```

Expected: FAIL because the core mapping functions and `.viewport-filename` footer do not exist.

- [ ] **Step 3: Implement minimal mapping, storage, and footer rendering**

Add core functions and export them:

```js
function canonicalSliceNames(items, geometry) {
  if (!items.length) return [];
  return items.map(function (_, canonicalZ) {
    const sourceZ = canonicalToSource(
      0, 0, canonicalZ,
      items[0].width, items[0].height, items.length, geometry
    ).z;
    return items[sourceZ].name;
  });
}

function sliceNameAtPosition(sliceNames, position) {
  if (!sliceNames.length) return "";
  const index = Math.max(0, Math.min(
    sliceNames.length - 1, Math.round(Number(position) || 0)
  ));
  return sliceNames[index];
}
```

In `constructVolume()`, compute `const sliceNames = Core.canonicalSliceNames(items, geometry)` and return it with the volume. In `createViewport()`, wrap only Crosslink axial cards in `.viewport-stack` and append `.viewport-filename`. In `updateViewportFilename(viewport)`, set `檔案：${name}` and `title = name`; call it from `renderViewportNow()` after the HUD update.

Use non-overlay layout CSS:

```css
.viewport-stack { display: grid; align-content: start; gap: 5px; min-width: 0; }
.viewport-filename { min-width: 0; overflow: hidden; padding: 0 4px; color: var(--muted); font-size: 11px; text-overflow: ellipsis; white-space: nowrap; }
```

- [ ] **Step 4: Verify GREEN and regressions**

Run:

```powershell
& 'C:\Users\jai16\AppData\Local\Programs\Python\Python314\python.exe' -m unittest tests.test_image_stack_mpr -v
& 'C:\Users\jai16\AppData\Local\Programs\Python\Python314\python.exe' -m unittest tests.test_us_probe_ct_plane -v
& 'C:\Users\jai16\AppData\Local\Programs\Python\Python314\python.exe' -m py_compile tests\test_image_stack_mpr.py
git diff --check
```

Expected: all tests PASS, no Python syntax errors, no whitespace errors, and `tool/us-probe-ct-plane.html` remains unchanged.

- [ ] **Step 5: Record completion and preserve reviewability**

Mark all plan checkboxes complete only after RED and GREEN evidence exists. Show the exact feature-file scope before committing because the standalone viewer and its tests are currently untracked as whole files; do not push or merge without the user's instruction.
