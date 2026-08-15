# Cephalometric English Report Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate all system-authored radiology report content in English while preserving physician-entered notes verbatim.

**Architecture:** Keep the Chinese wizard UI unchanged. Modify only the pure `CephCore.buildReport` wording and its report-focused tests; all measurement, state, snapshot, and copy interfaces remain unchanged.

**Tech Stack:** Self-contained HTML/JavaScript, Python `unittest`, Node VM, headless Chrome.

## Global Constraints

- All system-generated report wording is English.
- Physician-entered notes are preserved verbatim and are never automatically translated.
- Missing, skipped, uncertain, unassessed, limited, uncalibrated, and OSA-safe behavior remains conservative.
- The operational UI remains Traditional Chinese.

---

### Task 1: English report generator

**Files:**
- Modify: `tool/ceph-analysis.html`
- Modify: `tests/test_ceph_analysis.py`
- Modify: `openspec/changes/add-guided-ceph-analysis-v2/tasks.md`

**Interfaces:**
- Consumes: `CephCore.buildReport(study, suppliedAnalysis?) -> string`
- Produces: the same function signature with English system wording and verbatim physician notes.

- [ ] **Step 1: Write failing language-contract tests**

Add a report with six explicit normal states and verify it contains no `\u3400-\u9fff` characters. Keep a separate abnormal Chinese note fixture and verify that exact note remains present while adjacent generated labels are English.

- [ ] **Step 2: Run focused tests and verify failure**

Run `python -m unittest tests.test_ceph_analysis.CephReportGenerationTests -v`; expect failures on current Chinese system wording.

- [ ] **Step 3: Translate only system-generated report strings**

Change survey labels, normal/abnormal/limited/unassessed fallbacks, optional-group wording, uncertainty notices, impression, and limitations to clinical English. Do not modify wizard copy or physician note strings.

- [ ] **Step 4: Run focused and complete verification**

Run `python -m unittest tests.test_ceph_analysis tests.test_index_navigation -v`, `spectra validate --changes add-guided-ceph-analysis-v2`, and `git diff --check`; all must pass.

- [ ] **Step 5: Record Spectra completion**

Run `spectra task done --change add-guided-ceph-analysis-v2 16` and confirm `spectra instructions apply --change add-guided-ceph-analysis-v2 --json` reports `all_done`.
