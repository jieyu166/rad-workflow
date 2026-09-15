# Crosslink Pan, Scroll Gutters, and Portrait Height Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Crosslink panning follow the drag direction, preserve page-scroll targets beside the viewer, and size three portrait Crosslink images to about 30% of the viewport height each.

**Architecture:** Keep all behavior in the standalone `tool/image-stack-mpr.html`. Extend the existing real-browser probes so interaction and responsive CSS are verified from rendered behavior, then make the smallest JavaScript and CSS changes needed.

**Tech Stack:** Offline HTML/CSS/JavaScript Canvas viewer, Python `unittest`, headless Chrome or Edge.

## Global Constraints

- PNG/JPG data remains fully local in browser memory and is never uploaded.
- Ordinary wheel over an image continues to change slices; Ctrl/Meta plus wheel continues to zoom.
- Left and right page-scroll gutters are at least 32 px wide.
- In portrait orientation, each Crosslink image card is `30vh` high and the three sequences remain stacked vertically.
- Do not touch or stage unrelated untracked files.

---

### Task 1: Add interaction and responsive layout regression coverage

**Files:**
- Modify: `tests/test_image_stack_mpr.py`
- Test: `tests/test_image_stack_mpr.py`

**Interfaces:**
- Consumes: Existing `run_crosslink_interaction_probe()` and `measure_crosslink_orientation_layout()` browser fixtures.
- Produces: Browser-observed `shiftPan`, portrait card height, viewport height, and horizontal `.main` padding measurements.

- [x] **Step 1: Extend the interaction browser probe**

Dispatch a Shift+pointer drag from `(100, 100)` to `(140, 130)` on the Sequence 2 Crosslink canvas and return the resulting `panX` and `panY`.

- [x] **Step 2: Extend the portrait browser probe**

Return each Crosslink card height, `innerHeight`, and the computed left/right padding of `.main` for portrait and landscape fixtures.

- [x] **Step 3: Add behavior assertions**

Assert that Shift-drag yields positive `panX` and `panY`, portrait cards are within 2 px of `innerHeight * 0.30`, and both horizontal gutters are at least 32 px.

- [x] **Step 4: Run the focused tests and verify RED**

Run: `python -m unittest tests.test_image_stack_mpr.ImageStackMprTests.test_hover_keyboard_and_reversed_wheel_zoom tests.test_image_stack_mpr.ImageStackMprTests.test_portrait_crosslink_viewports_stack_vertically -v`

Expected: FAIL because panning currently subtracts drag deltas, portrait cards use `clamp(280px, 54vw, 620px)`, and `.main` has only 14 px horizontal padding.

### Task 2: Implement direct panning and responsive workspace geometry

**Files:**
- Modify: `tool/image-stack-mpr.html`
- Test: `tests/test_image_stack_mpr.py`

**Interfaces:**
- Consumes: Pointer deltas from `bindViewportInteractions()` and portrait media-query state.
- Produces: Direct-manipulation pan offsets, 32–48 px horizontal scroll gutters, and `30vh` portrait Crosslink cards/canvases.

- [x] **Step 1: Reverse the pan calculation**

Change Crosslink pan updates from subtracting to adding `dx / zoom` and `dy / zoom`.

- [x] **Step 2: Add page-scroll gutters**

Set `.main` vertical padding to 14 px and horizontal padding to `clamp(32px, 3vw, 48px)` so wheel events outside the canvas can scroll the document.

- [x] **Step 3: Set portrait image height**

Within `@media (orientation: portrait)`, keep one grid column and set both Crosslink `.viewport-card` and its canvas to `height: 30vh; min-height: 0`.

- [x] **Step 4: Run focused and full verification**

Run the two focused tests, then `python -m unittest tests.test_image_stack_mpr tests.test_us_probe_ct_plane tests.test_index_navigation -v`.

Expected: Focused tests and the complete viewer/probe/navigation suite pass with no failures.

- [x] **Step 5: Inspect scope**

Run `git diff --check`, `git diff -- tool/image-stack-mpr.html tests/test_image_stack_mpr.py docs/superpowers/plans/2026-08-08-crosslink-pan-scroll-gutters-portrait-height.md`, and `git status --short` to confirm only intended files changed and excluded untracked files remain untouched.
