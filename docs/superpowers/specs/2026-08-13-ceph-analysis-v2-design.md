# Cephalometric Analysis V2 — Approved Design

**Date:** 2026-08-13
**Status:** Approved through four-stage user review
**Target:** `tool/ceph-analysis.html`
**Primary user:** Radiologist without specialist orthodontic training

## 1. Objective

Replace the current theory-heavy and manual-value workflow with an image-first progressive wizard:

> Paste image → survey the full field → calibrate the visible ruler → place S/N/A/B → generate a basic report → optionally add skeletal and dental landmarks.

The tool is a reporting aid. It does not replace orthodontic assessment, automate landmark detection, diagnose obstructive sleep apnea, or infer missing measurements.

## 2. Approved Clinical Positioning

The output is a formal radiology report body with a minimal cephalometric appendix. The minimum complete cephalometric analysis requires only S, N, A, and B. Advanced vertical skeletal and incisor analyses are optional and appear only when their landmark dependencies are complete.

The tool uses conservative language such as “supports” or “is in keeping with a skeletal Class tendency.” It does not convert missing or uncertain data into normal findings.

## 3. Physician Workflow

### Step 1 — Load one image

- Accept clipboard paste, drag/drop, and PNG/JPG file selection.
- Keep the image and study state in current-page browser memory only.
- Provide zoom, pan, invert, fit, and reset controls.
- Reject unsupported, undecodable, over-50-MiB, or over-16384-pixel-per-side inputs without clearing the current study.

### Step 2 — Complete the six-area survey

The six items are:

1. Image quality and positioning
2. Sella and skull base
3. Paranasal sinuses and nasopharyngeal region
4. Temporomandibular joints
5. Maxilla, mandible, and visible dentition
6. Cervical spine, prevertebral soft tissues, and airway

Each item starts as `unassessed` and can be changed to `normal`, `abnormal`, or `limited`, with a note. A physician-confirmed batch-normal action is allowed but cannot overwrite abnormal or limited items.

### Step 3 — Calibrate the visible ruler

- The physician selects two clear ruler ticks and enters their known distance in millimeters.
- `mmPerPixel = knownDistanceMm / sourcePixelDistance`.
- The points must be at least 20 source pixels apart and the entered distance must be finite and positive.
- Calibration can be skipped. Angles remain available, but no pixel-derived millimeter value is generated.

### Step 4 — Place the four core landmarks

The wizard shows one landmark at a time, with its definition and common placement pitfall:

- **S:** center of the sella turcica
- **N:** most anterior point of the frontonasal suture
- **A:** deepest anterior maxillary concavity between ANS and the maxillary alveolar process
- **B:** deepest anterior mandibular concavity between the mandibular alveolar process and pogonion

Each point can be repositioned, nudged with arrow keys, deleted, undone/redone, or marked uncertain. Completing all four unlocks basic report generation.

### Step 5 — Add optional landmark groups

- **Vertical skeletal group:** ANS, PNS, Go, Me
- **Dental group:** U1 tip, U1 apex, L1 tip, L1 apex

Each optional group can be skipped. A partial group produces no measurement that requires its missing points.

The dental group includes a compact “one tooth, two points, one axis” guide. U1 means a maxillary permanent central incisor (FDI 11 or 21), and L1 means a mandibular permanent central incisor (FDI 31 or 41). Because the lateral projection superimposes right and left incisors, the user selects a relatively labial trace whose incisal tip and root apex can both be followed clearly. Both endpoints must come from the same tooth; an unreliable pair is marked uncertain or the optional group is skipped. The interface uses FDI labels explicitly and does not write `#11/#21`, which could be mistaken for Universal numbering.

### Step 6 — Generate and edit the report

- Generate an editable plain-text snapshot.
- If survey, calibration, landmarks, measurements, or metadata later changes, preserve physician edits and mark the report stale.
- Regeneration requires an explicit confirmation because it replaces the editable snapshot.
- Copy through the Clipboard API when available; retain selectable text and manual-copy instructions when it is blocked.

## 4. Measurement Rules

### Core measurements

- `SNA = angle(S, N, A)`
- `SNB = angle(S, N, B)`
- `ANB = SNA - SNB`

The named core reference is Steiner adult reference: SNA 82° ± 2°, SNB 80° ± 2°, and ANB 2° ± 2°.

- ANB < 0°: Class III tendency
- ANB 0° through 4°: Class I tendency
- ANB > 4°: Class II tendency

The report displays raw values and the named reference. Age, population, positioning, and Nasion sensitivity remain explicit limitations.

### Optional measurements

- SN–MP requires S, N, Go, and Me.
- PP–MP requires ANS, PNS, Go, and Me.
- U1–PP requires U1 tip/apex and ANS/PNS.
- L1–MP requires L1 tip/apex and Go/Me.
- Interincisal angle requires both incisor axes.
- A user-labeled linear distance requires valid ruler calibration and remains a raw value without automated normal/abnormal interpretation.

Overjet and overbite are not inferred from the screen horizontal/vertical axes. A lateral cephalogram is not used by this tool to diagnose or exclude obstructive sleep apnea.

## 5. Report Contract

The generated report contains:

1. **Examination / Technique** — lateral cephalometric radiograph, image quality/positioning, and calibration status.
2. **Findings** — only the explicit six-area survey selections and physician-entered abnormal notes.
3. **Cephalometric Analysis** — completed measurements, named reference, uncertainty, and groups not performed.
4. **Impression** — conservative sagittal conclusion, completed optional conclusions, and explicit incidental abnormalities.
5. **Limitations** — two-dimensional projection, positioning, magnification, landmark variability, calibration status, and screening-only airway assessment.

A whole-field negative statement is permitted only when every anatomy survey item was explicitly marked normal. Missing ANB never defaults to Class I. Uncertain landmarks propagate uncertainty only to their dependent measurements.

## 6. Technical Design

- Replace the existing page at the same path; the root navigation link remains unchanged.
- Keep a single self-contained HTML file with no external fonts, scripts, styles, fetches, or uploads.
- Store landmarks as normalized source-image coordinates `{x, y, uncertain}` so viewport transforms never change geometry.
- Separate a DOM-free `CephCore` script from application code. The core exposes deterministic angle, scale, dependency, measurement, and report functions to both the browser and Node VM tests.
- Keep survey, calibration, landmarks, history, and report snapshot in a single in-memory study state.
- Use a standard `beforeunload` warning for a modified in-memory study; do not claim that closed studies can be recovered.

## 7. Verification Contract

Automated acceptance requires:

- Pure-function fixtures for SNA, SNB, signed ANB, ANB boundaries, advanced dependency gates, uncertainty propagation, and calibrated distances.
- HTML parser checks for required DOM contracts, no external assets, no network primitives, and no persistent browser storage.
- Headless production-DOM fixtures for source/display coordinate round trips, progressive unlock, optional skip, undo/redo, keyboard nudge, stale-report protection, copy fallback, and layouts at 1440×900 and 1024×768.
- `python -m unittest tests.test_ceph_analysis tests.test_index_navigation -v`
- `git diff --check`
- `spectra validate add-guided-ceph-analysis-v2`

Manual acceptance uses a real lateral cephalometric PNG/JPG to exercise paste/file intake, all survey states, a known 40 mm ruler interval, S/N/A/B, one optional group, report editing, regeneration, and copy.

## 8. Scope Boundaries

Functional changes are limited to `tool/ceph-analysis.html` and the new `tests/test_ceph_analysis.py`. The existing `index.html` link stays at the same path. Other tools, radiology trackers, AHK scripts, image viewers, publication workflows, and unrelated dirty-worktree files are out of scope.

## 9. Clinical Evidence Guardrails

- Dental radiographs must be justified, optimized, and interpreted across the entire exposed image, including incidental findings: [ADA radiographic imaging guidance](https://www.ada.org/resources/practice/practice-management/radiographic-imaging), [FDA patient-selection guidance](https://www.fda.gov/radiation-emitting-products/medical-x-ray-imaging/selection-patients-dental-radiographic-examinations), and [British Orthodontic Society radiograph guideline](https://www.bos.org.uk/wp-content/uploads/2022/03/Orthodontic-Radiographs-2016-2.pdf).
- Incidental findings on lateral cephalograms are common enough to justify a structured full-field survey: [PubMed study](https://pubmed.ncbi.nlm.nih.gov/35585297/).
- Two-dimensional airway assessment has measurement limitations and cannot establish OSA: [airway validity review](https://pmc.ncbi.nlm.nih.gov/articles/PMC8923553/) and [AASM diagnostic guideline](https://pubmed.ncbi.nlm.nih.gov/28162150/).

## 10. Approved Decisions

The user approved:

- Formal radiology report body plus minimal cephalometric appendix
- Visible-ruler calibration using two known ticks
- Six-area survey with no default normal selection
- Progressive S/N/A/B-first wizard with optional ANS/PNS/Go/Me and incisor groups
- Dependency-gated output with no guessed values
- Same-path V2 replacement of the existing page
