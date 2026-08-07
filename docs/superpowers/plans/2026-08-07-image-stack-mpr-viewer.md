# Image Stack MPR Viewer Implementation Plan

> **For Codex:** Execute this plan in order with `superpowers:executing-plans`, using strict RED→GREEN TDD and the Spectra `tasks.md` checkboxes as the sole progress tracker.

**Goal:** Add a completely offline single-file PNG/JPEG stack viewer that organizes 2–3 sequences, supports manually anchored reversible crosslinking, and renders AX/COR/SAG/Oblique pseudo-volume views without changing the existing probe simulator.

**Architecture:** `tool/image-stack-mpr.html` owns all CSS, markup, UI binding, decode code, and Canvas 2D rendering. A DOM-free `<script id="image-stack-mpr-core">` exposes deterministic functions through `globalThis.ImageStackMprCore`; `tests/test_image_stack_mpr.py` extracts that block and exercises it in a Node VM with synthetic volumes. Browser-only code consumes the same core functions but remains outside the pure block.

**Tech stack:** HTML5, CSS, JavaScript, Canvas 2D, TypedArray, Blob Worker fallback, Python `unittest`, Node `vm`.

---

## Task 1: Offline page and executable core contract

**Spectra tasks:** 1.1–1.2

**Files:**

- Create: `tests/test_image_stack_mpr.py`
- Create: `tool/image-stack-mpr.html`

1. Write `ImageStackPageParser` tests that require `image-file-input`, `sequence-count`, `organizer`, `crosslink-workspace`, `mpr-workspace`, and a pure script with id `image-stack-mpr-core`. Scan `script[src]`, `link[href]`, CSS `url(...)`, and HTTP(S)/protocol-relative strings.
2. Add a Node VM helper that evaluates only the pure block in a context containing standard typed arrays and reads `globalThis.ImageStackMprCore`.
3. Run `python -m unittest tests.test_image_stack_mpr.ImageStackMprTests.test_offline_single_file_image_stack_import tests.test_image_stack_mpr.ImageStackMprTests.test_core_script_is_extractable_and_executable -v`; confirm RED because both files/contracts are absent.
4. Create the standalone page skeleton with `default-src 'none'`, `img-src 'self' blob: data:`, `style-src 'unsafe-inline'`, `script-src 'unsafe-inline' blob:`, no external assets, and this export shape:

```js
globalThis.ImageStackMprCore = Object.freeze({
  naturalCompare,
  assignByBoundaries,
  canonicalDimensions,
  canonicalToSource,
  normalizeGeometry,
  estimateVolumeBytes,
  validateAnchor,
  mapReferenceToTarget,
  mapTargetToReference,
  synchronizePositions,
  sampleTrilinear,
  makeOrthogonalPlane,
  makeObliquePlane,
  reslicePlane,
  progressiveRenderPlan
});
```

5. Re-run the two tests and the external URL scan; confirm GREEN.
6. Mark Spectra tasks 1.1 and 1.2 complete.

## Task 2: Organizer, geometry, decode validation, and memory guard

**Spectra tasks:** 2.1–2.5

**Files:**

- Modify: `tests/test_image_stack_mpr.py`
- Modify: `tool/image-stack-mpr.html`

1. Add RED Node assertions for natural order (`IMG_1`, `img_2`, `IMG_10`), only sequence counts 2/3, boundaries `[30]` over 66 items, stable per-item reassignment/exclusion, and non-square orientation transforms for every rotation/flip/order combination.
2. Add RED assertions for `normalizeGeometry()` defaults and invalid inputs, `estimateVolumeBytes()` at 512 MiB, canonical dimension mismatch, minimum depth, and allocation-error result preservation.
3. Implement pure organizer/geometry functions. `assignByBoundaries()` returns immutable assignment records; `canonicalToSource()` maps canonical x/y/z to source x/y/slice without rewriting source bytes.
4. Implement browser organizer lanes with draggable boundary handles, thumbnail cards, include checkboxes, sequence dropdown/drop targets, and persistent stable sort keys.
5. Implement sequential `createImageBitmap`/`Image` fallback decode, RGBA-to-luminance conversion `(77R + 150G + 29B) >> 8`, dimension/depth error reporting, object URL/bitmap release, 512 MiB confirmation, and `Uint8Array` allocation recovery.
6. Run tests named `test_natural_ordering_and_sequence_count`, `test_boundary_and_per_image_assignment`, `test_sequence_geometry_configuration`, `test_decode_and_dimension_validation`, and `test_memory_aware_volume_construction`; confirm GREEN.
7. Mark Spectra tasks 2.1–2.5 complete.

## Task 3: Reference-based reversible crosslink and timeline

**Spectra tasks:** 3.1–3.5

**Files:**

- Modify: `tests/test_image_stack_mpr.py`
- Modify: `tool/image-stack-mpr.html`

1. Add RED tests for separate target maps, duplicate/crossing rejection, zero-anchor independence, one-anchor offset, 7→39 plus 27→63 interpolation (17→51), outer extrapolation/clamp, inverse mapping, secondary→reference→other-secondary routing, and retention of fractional positions.
2. Implement `validateAnchor()` by sorting a candidate copy and requiring unique, strictly increasing reference and target indices. Never mutate anchors on invalid input.
3. Implement a shared piecewise mapper: no anchor returns `null`, one anchor applies offset, multiple anchors select the inner/nearest outer segment, interpolate/extrapolate, then clamp. Inverse mapping swaps axes on the same anchors.
4. Implement `synchronizePositions(sourceId, position, maps, depths)` so secondary sources route through Sequence 1 and MPR positions remain floating point; axial display alone rounds.
5. Add target selector, add/update/delete controls, selected-anchor state, timeline diamonds, and an SVG connector overlay that uses thumbnail centers without intercepting pointer events.
6. Run `test_reference_based_crosslink_model`, `test_strictly_monotonic_anchor_validation`, `test_piecewise_mapping_behavior`, `test_reversible_synchronization`, `test_anchor_creation_and_editing`, and `test_timeline_crosslink_visualization`; confirm GREEN.
7. Mark Spectra tasks 3.1–3.5 complete.

## Task 4: Sampling and AX/COR/SAG/Oblique reslicing

**Spectra tasks:** 4.1–4.4

**Files:**

- Modify: `tests/test_image_stack_mpr.py`
- Modify: `tool/image-stack-mpr.html`

1. Add RED synthetic-volume tests for the 2×2×2 center value 35, outside value 0, and x/y/z gradients through AX/COR/SAG.
2. Implement `sampleTrilinear()` with inclusive bounds, floor/ceil corner fetches, and x→y→z interpolation.
3. Implement orthogonal planes in canonical coordinates:

```js
AX: u=[1,0,0], v=[0,1,0], normal=[0,0,1]
COR: u=[1,0,0], v=[0,0,1], normal=[0,1,0]
SAG: u=[0,1,0], v=[0,0,1], normal=[1,0,0]
```

4. Convert output millimetres into voxel coordinates with per-axis spacing and render RGBA through the common trilinear sampler.
5. Add RED tests that oblique u/v/normal remain unit and mutually orthogonal for non-zero azimuth/tilt/roll, reset preserves center, and a mapped z=50.4 reaches the plane unchanged.
6. Implement yaw/pitch/roll basis construction with vector normalize/cross/dot helpers and Oblique controls/reset.
7. Run `test_trilinear_intensity_sampling`, `test_standard_orthogonal_reslices`, `test_arbitrary_oblique_reslice`, and `test_crosslinked_mpr_location`; confirm GREEN.
8. Mark Spectra tasks 4.1–4.4 complete.

## Task 5: Progressive rendering, interactions, and responsive workspace

**Spectra tasks:** 4.5 and 5.1–5.3

**Files:**

- Modify: `tests/test_image_stack_mpr.py`
- Modify: `tool/image-stack-mpr.html`

1. Add RED tests for preview max 256, full max 1024, 120 ms debounce metadata, monotonically increasing generation, and stale-result rejection.
2. Implement a render coordinator that immediately paints a preview, debounces a full render, checks generation before commit, and falls back to synchronous main-thread rendering if Blob Worker creation fails.
3. Add RED HTML/binding tests for wheel slice, Ctrl/Meta wheel zoom, left crosshair drag, pan modifier, context-menu suppression/right-drag Intensity, Fit, Reset, Invert, zoom/pan sync, and Intensity sync. Assert visible copy never uses `HU`, `Window Level`, or DICOM WL wording.
4. Implement Canvas axial/MPR draw, shared viewport state, interaction bindings, orientation labels, crosshair, and controls.
5. Implement Crosslink mode with 2–3 axial panels and timelines. Implement MPR mode with Sequence 1 2×2 primary grid plus Sequence 2/3 comparison grids.
6. Add CSS gates: at `min-width: 1400px` primary and secondary regions share one row; below `900px` all regions stack with no fixed minimum width. Add persistent `.geometry-warning` positioning-only text per default-spacing sequence.
7. Run `test_progressive_reslice_quality`, `test_basic_image_interaction_bindings`, `test_responsive_comparison_workspace`, and `test_unknown_geometry_warning_and_copy`; confirm GREEN.
8. Mark Spectra tasks 4.5 and 5.1–5.3 complete.

## Task 6: Integrated verification and file:// browser evidence

**Spectra tasks:** 6.1–6.2

**Files:**

- Modify only if a failing acceptance test identifies a defect: `tests/test_image_stack_mpr.py`, `tool/image-stack-mpr.html`
- Record verification in the Spectra change task/evidence mechanism; do not add uploaded patient images.

1. Run `python -m unittest discover -s tests -p test_image_stack_mpr.py -v`.
2. Run `python -m unittest tests/test_us_probe_ct_plane.py -v` and verify `tool/us-probe-ct-plane.html` has no diff.
3. Run `git diff --check` and an explicit external-URL scan against the new HTML.
4. Generate local synthetic PNG stacks with distinctive x/y/z gradients and labels: two-sequence 30+36 slices and three-sequence 12+14+16 slices. Keep them under ignored `tmp/`.
5. Open the new page through `file://` in Chrome/in-app browser. Verify import, 2/3 lanes, boundaries, reassignment/exclusion, orientation controls, anchor add/edit/delete, reversible scrolling, AX/COR/SAG/Oblique, fractional positioning, all viewport gestures, 1600px layout, 800px layout, no network requests, and empty state after reload.
6. Capture screenshots/evidence without patient data and mark Spectra tasks 6.1–6.2 complete only after every assertion passes.
7. Run `spectra validate add-image-stack-mpr-viewer`, `spectra analyze add-image-stack-mpr-viewer`, full relevant tests, and `git status --short` immediately before reporting completion.
