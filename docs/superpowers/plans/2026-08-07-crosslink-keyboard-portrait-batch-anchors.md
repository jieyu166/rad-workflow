# Crosslink Keyboard Zoom, Portrait Layout, and Batch Anchors Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the approved Crosslink keyboard zoom, reversed Ctrl/Meta-wheel zoom, portrait single-column sequence layout, and atomic one-click S2/S3 anchor creation.

**Architecture:** Keep the standalone HTML architecture. Add a small pure-core atomic batch-anchor function, keep viewport hover/zoom state inside the existing app closure, and verify real keyboard, wheel, and portrait layout behavior with instrumented local headless Chromium fixtures that execute the production page.

**Tech Stack:** Standalone HTML/CSS/JavaScript, Canvas 2D, Python `unittest`, Node `vm`, local headless Chrome or Edge.

## Global Constraints

- All images and processing remain local; add no external asset or network dependency.
- `tool/us-probe-ct-plane.html` must remain unchanged.
- Keyboard `+` and `-` affect only the hovered viewport unless navigation sync is enabled.
- Ctrl/Meta-wheel down zooms in and wheel up zooms out; ordinary wheel remains slice navigation.
- Portrait rules apply only to Crosslink `#axial-viewports`, not MPR grids.
- Batch anchor creation is atomic across every active secondary sequence.
- Individual anchor selection, update, and delete behavior remains available.

---

### Task 1: Hover keyboard zoom and reversed Ctrl/Meta-wheel direction

**Files:**

- Modify: `tests/test_image_stack_mpr.py`
- Modify: `tool/image-stack-mpr.html`

**Interfaces:**

- Consumes: `state.viewports`, `state.viewportStates`, `viewportState(key)`, `copyNavigation(sourceState)`, `renderAllViewports(interactive)`, and `syncNavigationControl.checked`.
- Produces: `state.hoveredViewport`, `applyViewportZoom(viewport, factor)`, and `handleViewportZoomKey(event)`.

- [x] **Step 1: Add a real-browser interaction probe and failing test**

Instrument the app closure to expose `state` and `createViewport`, create three Crosslink AX viewports, and dispatch real `pointerenter`, `pointerleave`, `keydown`, and `WheelEvent` events. Add these assertions:

```python
def test_hover_keyboard_and_reversed_wheel_zoom(self) -> None:
    result = run_crosslink_interaction_probe()
    self.assertGreater(result["syncedPlus"]["2"], 1)
    self.assertEqual(result["syncedPlus"]["1"], result["syncedPlus"]["2"])
    self.assertEqual(result["syncedPlus"]["3"], result["syncedPlus"]["2"])
    self.assertEqual(result["unsyncedMinus"]["1"], 1)
    self.assertLess(result["unsyncedMinus"]["2"], 1)
    self.assertEqual(result["unsyncedMinus"]["3"], 1)
    self.assertEqual(result["noHover"], result["beforeNoHover"])
    self.assertGreater(result["wheelDown"], result["wheelStart"])
    self.assertLess(result["wheelUp"], result["wheelDown"])
```

- [x] **Step 2: Run the test and verify RED**

Run:

```powershell
python -m unittest tests.test_image_stack_mpr.ImageStackMprTests.test_hover_keyboard_and_reversed_wheel_zoom -v
```

Expected: FAIL because hover state and keyboard zoom are absent, and the current Ctrl/Meta-wheel multiplier makes positive `deltaY` zoom out.

- [x] **Step 3: Implement minimal zoom helpers and bindings**

Add `hoveredViewport: ""` to state and implement:

```js
function applyViewportZoom(viewport, factor) {
  const viewState = viewportState(viewport.key);
  viewState.zoom = Math.max(0.25, Math.min(12, viewState.zoom * factor));
  copyNavigation(viewState);
  renderAllViewports(true);
}

function handleViewportZoomKey(event) {
  const viewport = state.viewports.get(state.hoveredViewport);
  const zoomIn = event.key === "+" || event.code === "NumpadAdd";
  const zoomOut = event.key === "-" || event.code === "NumpadSubtract";
  if (!viewport || (!zoomIn && !zoomOut)) return;
  event.preventDefault();
  selectViewport(viewport.key);
  applyViewportZoom(viewport, zoomIn ? 1.1 : 1 / 1.1);
}
```

Bind canvas `pointerenter`/`pointerleave`, bind `globalThis.keydown`, and change Ctrl/Meta wheel to `event.deltaY > 0 ? 1.1 : 1 / 1.1`. Update the toolbar copy to include `游標置於影像後按 +/-：縮放` and retain the Shift-pan instruction.

- [x] **Step 4: Run the interaction test and full viewer test module**

Run:

```powershell
python -m unittest tests.test_image_stack_mpr.ImageStackMprTests.test_hover_keyboard_and_reversed_wheel_zoom -v
python -m unittest tests.test_image_stack_mpr -v
```

Expected: PASS with the new interaction test and all prior viewer tests green.

---

### Task 2: Portrait Crosslink single-column layout

**Files:**

- Modify: `tests/test_image_stack_mpr.py`
- Modify: `tool/image-stack-mpr.html`

**Interfaces:**

- Consumes: `#axial-viewports.viewport-grid`, `.viewport-stack`, and `.viewport-card`.
- Produces: an `@media (orientation: portrait)` Crosslink-only layout rule.

- [x] **Step 1: Add a failing headless-browser portrait layout test**

Create three production Crosslink viewports at a portrait viewport size and measure their stack rectangles:

```python
def test_portrait_crosslink_viewports_stack_vertically(self) -> None:
    result = measure_crosslink_orientation_layout()
    self.assertEqual(result["portraitRows"], 3)
    self.assertTrue(all(result["portraitFullWidth"]))
    self.assertLess(result["landscapeRows"], 3)
```

Use `--window-size=700,1100` for portrait and `--window-size=1200,700` for landscape. Each full-width assertion permits a 2 CSS-pixel tolerance against `#axial-viewports`.

- [x] **Step 2: Run the portrait test and verify RED**

Run:

```powershell
python -m unittest tests.test_image_stack_mpr.ImageStackMprTests.test_portrait_crosslink_viewports_stack_vertically -v
```

Expected: FAIL because the generic auto-fit grid can place more than one Crosslink viewport in a portrait row.

- [x] **Step 3: Add the Crosslink-only portrait rule**

Add:

```css
@media (orientation: portrait) {
  #axial-viewports.viewport-grid { grid-template-columns: minmax(0, 1fr); }
  #axial-viewports .viewport-card,
  #axial-viewports .viewport-card canvas { min-height: clamp(280px, 54vw, 620px); }
}
```

Do not alter `.primary-mpr-grid`, `.secondary-grid`, or `.mpr-layout` in this rule.

- [x] **Step 4: Run portrait and responsive regression tests**

Run:

```powershell
python -m unittest tests.test_image_stack_mpr.ImageStackMprTests.test_portrait_crosslink_viewports_stack_vertically tests.test_image_stack_mpr.ImageStackMprTests.test_responsive_comparison_workspace -v
```

Expected: PASS in both portrait and landscape measurements while existing MPR assertions remain green.

---

### Task 3: Atomic one-click anchor creation for all active targets

**Files:**

- Modify: `tests/test_image_stack_mpr.py`
- Modify: `tool/image-stack-mpr.html`

**Interfaces:**

- Consumes: `upsertAnchor(anchors, candidate, editIndex)`, `activeSequenceIds()`, `currentAnchorCandidate(targetId)`, `state.crosslinks`, and `renderTimelines()`.
- Produces: `batchUpsertAnchors(maps, candidates)` in `ImageStackMprCore` and `saveAllCurrentAnchors()` in the app closure.

- [x] **Step 1: Add failing atomic-core and UI contract tests**

Add pure-core cases for three-sequence success, one invalid target with no partial mutation, and two-sequence success:

```python
def test_batch_anchor_creation_is_atomic(self) -> None:
    result = run_core(r"""
(() => {
  const C = ImageStackMprCore;
  const maps = {2: [{referenceIndex: 5, targetIndex: 8}], 3: []};
  return {
    success: C.batchUpsertAnchors(maps, {
      2: {referenceIndex: 10, targetIndex: 14},
      3: {referenceIndex: 10, targetIndex: 12}
    }),
    rejected: C.batchUpsertAnchors(maps, {
      2: {referenceIndex: 5, targetIndex: 20},
      3: {referenceIndex: 10, targetIndex: 12}
    }),
    original: maps
  };
})()
""")
    self.assertTrue(result["success"]["valid"])
    self.assertEqual(sorted(result["success"]["maps"]), ["2", "3"])
    self.assertFalse(result["rejected"]["valid"])
    self.assertEqual(result["rejected"]["maps"], result["original"])
    self.assertEqual(result["rejected"]["failedTargetId"], 2)
```

Also assert button text `新增全部序列錨點`, label text `編輯目標`, and the continued presence of individual update/delete controls.

- [x] **Step 2: Run the atomic test and verify RED**

Run:

```powershell
python -m unittest tests.test_image_stack_mpr.ImageStackMprTests.test_batch_anchor_creation_is_atomic -v
```

Expected: FAIL because `batchUpsertAnchors` does not exist and the add button still targets one selected sequence.

- [x] **Step 3: Implement pure atomic batching and app commit-on-success**

Implement the core function without mutating the input maps:

```js
function batchUpsertAnchors(maps, candidates) {
  const original = {};
  Object.keys(maps).forEach(function (targetId) {
    original[targetId] = cloneAnchors(maps[targetId] || []);
  });
  const next = {};
  Object.keys(original).forEach(function (targetId) {
    next[targetId] = cloneAnchors(original[targetId]);
  });
  const targetIds = Object.keys(candidates).map(Number).sort(function (a, b) { return a - b; });
  for (const targetId of targetIds) {
    const result = upsertAnchor(next[targetId] || [], candidates[targetId]);
    if (!result.valid) {
      return {valid: false, reason: result.reason, failedTargetId: targetId, maps: original};
    }
    next[targetId] = result.anchors;
  }
  return {valid: true, reason: "", failedTargetId: null, maps: next};
}
```

Export it from `ImageStackMprCore`. `saveAllCurrentAnchors()` builds candidates for every active target, calls the core once, assigns `state.crosslinks = result.maps` only on success, clears `state.selectedAnchor`, renders timelines once, and reports every added pair. Keep `saveAnchor(true)` for individual editing.

- [x] **Step 4: Run atomic, existing anchor, and timeline tests**

Run:

```powershell
python -m unittest tests.test_image_stack_mpr.ImageStackMprTests.test_batch_anchor_creation_is_atomic tests.test_image_stack_mpr.ImageStackMprTests.test_anchor_creation_and_editing tests.test_image_stack_mpr.ImageStackMprTests.test_timeline_crosslink_visualization -v
```

Expected: PASS with atomic rollback and existing individual edit/delete behavior intact.

---

### Task 4: Acceptance records, complete verification, and commit

**Files:**

- Modify: `openspec/changes/add-image-stack-mpr-viewer/tasks.md`
- Test: `tests/test_image_stack_mpr.py`
- Verify: `tool/image-stack-mpr.html`

**Interfaces:**

- Consumes: all behavior from Tasks 1–3.
- Produces: updated Spectra task evidence and one scoped implementation commit.

- [x] **Step 1: Record automated acceptance evidence without closing broader manual gates**

Add the new test names to OpenSpec tasks 3.5, 5.1, and 5.2, but leave those tasks unchecked because their broader marker-pointer, pan/crosshair/right-drag, and screenshot gates are not fully covered by this interaction change. Leave 2.2 and 6.2 unchecked for the same evidence-based reason.

- [x] **Step 2: Run the full verification suite**

Run:

```powershell
python -m unittest tests.test_image_stack_mpr -v
python -m py_compile tests/test_image_stack_mpr.py
spectra validate add-image-stack-mpr-viewer
git diff --check
git diff --exit-code origin/main...HEAD -- tool/us-probe-ct-plane.html
```

Expected: all viewer tests pass, Python and Spectra validation succeed, no whitespace errors appear, and the probe file has no diff.

- [x] **Step 3: Review the exact commit scope**

Expected implementation scope:

```text
docs/superpowers/plans/2026-08-07-crosslink-keyboard-portrait-batch-anchors.md
openspec/changes/add-image-stack-mpr-viewer/tasks.md
tests/test_image_stack_mpr.py
tool/image-stack-mpr.html
```

- [x] **Step 4: Commit the implementation**

```powershell
git add docs/superpowers/plans/2026-08-07-crosslink-keyboard-portrait-batch-anchors.md openspec/changes/add-image-stack-mpr-viewer/tasks.md tests/test_image_stack_mpr.py tool/image-stack-mpr.html
git commit -m "feat(tool): refine crosslink interactions"
```
