# Card Rewards Tool Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a self-contained, offline `tool/card-rewards.html` that deterministically presents the approved 2026 H2 existing-customer card corpus with search, filters, three-card comparison, complete evidence details, and source links.

**Architecture:** `docs/card-rewards/2026-h2/` remains the sole source of reward facts. A Python 3.14 standard-library generator validates and parses the approved Markdown into deterministic JSON, then replaces only the marked data block in one native HTML/CSS/JavaScript file; browser code never fetches Markdown or remote assets. Pure JavaScript state functions are exercised in Node, while Chrome/Edge headless probes and an in-app browser read-back verify real desktop/mobile behavior.

**Tech Stack:** Python 3.14 standard library, `unittest`, native HTML5, CSS, vanilla JavaScript, Node `vm`, Chrome or Edge headless mode.

**Spec:** `docs/superpowers/specs/2026-08-18-card-rewards-tool-design.md`

## Global Constraints

- Work only in `.worktrees/card-rewards-2026-h2` on branch `codex/card-rewards-2026-h2`; do not touch unrelated main-worktree changes.
- Phase 1 baseline is `fe59115a8ba40dd47d571d43f565e91682c64366`; any reward-fact correction must first update the evidence Markdown and pass the Phase 1 validator.
- The accepted corpus is exactly 15 product documents plus 3 payment documents for 2026-08-01 through 2026-12-31, existing customers only.
- Markdown under `docs/card-rewards/2026-h2/` is the only factual source; generated HTML data must never become an independent editable source.
- Use Python standard library only. Do not add React, Vue, npm dependencies, CDN assets, external fonts, analytics, runtime APIs, or runtime `fetch`.
- `tool/card-rewards.html` must work when opened directly with `file://`; only user-activated official HTTPS links may use the network.
- Preserve reward currencies as text. Do not compute a cross-currency score, convert points to cash, rank a universal winner, or hide limited/partial conditions.
- Search/filter state stays in page memory only; do not store personal or financial data in localStorage.
- All dynamic user-visible text must be created with `textContent` or equivalent escaped DOM construction; do not inject corpus strings through `innerHTML`.
- Use the installed interpreter in PowerShell commands:

```powershell
$py = 'C:\Users\jai16\AppData\Local\Programs\Python\Python314\python.exe'
```

- Every implementation task stages only its listed paths and ends with its own reviewable commit.
- Do not push, merge, publish, deploy, create a PR, or change remote state.

## File Map

| Path | Change | Single responsibility |
|---|---|---|
| `scripts/build_card_rewards_tool.py` | Create | Validate Phase 1, parse records, serialize deterministic JSON, replace/check the HTML data block, expose the CLI |
| `tool/card-rewards.html` | Create | Self-contained semantic UI, styles, pure state helpers, DOM rendering, comparison and detail dialogs |
| `tests/test_card_rewards_tool.py` | Create | Parser, data-contract, deterministic build, offline structure, JavaScript core, desktop/mobile browser probes |
| `tests/test_index_navigation.py` | Modify | Assert the repo homepage uses the local card tool and no longer uses the Claude artifact URL for this entry |
| `index.html` | Modify | Replace the historical external card-tool link with `tool/card-rewards.html` |
| `README.md` | Modify | Link to the repo-local tool and document its date-scoped offline snapshot behavior |

## Shared Interfaces

The implementation tasks use these exact Python interfaces:

```python
DATA_START = "<!-- CARD_REWARDS_DATA_START -->"
DATA_END = "<!-- CARD_REWARDS_DATA_END -->"

class BuildError(ValueError):
    """A deterministic corpus or generated-artifact contract failure."""

def parse_markdown_table(section: str) -> tuple[list[str], list[list[str]]]: ...
def parse_document(path: Path) -> tuple[dict[str, str], dict[str, object]]: ...
def build_dataset(repo_root: Path) -> dict[str, object]: ...
def serialize_dataset(dataset: dict[str, object]) -> str: ...
def read_embedded_dataset(html_text: str) -> str: ...
def replace_embedded_dataset(html_text: str, json_text: str) -> str: ...
def build_output(repo_root: Path, output_path: Path, *, check: bool) -> bool: ...
def main(argv: list[str] | None = None) -> int: ...
```

`build_output()` returns `True` when the file already matches or was successfully updated. In check mode, drift raises `BuildError` and the CLI returns exit 1 after printing the exact failure to stderr.

The HTML exposes one testable pure JavaScript namespace:

```javascript
globalThis.CardRewardsCore = Object.freeze({
  normalizeText,
  cardMatchesQuery,
  cardMatchesFilters,
  filterCards,
  toggleSelection
});
```

`toggleSelection(selectedIds, productId, limit = 3)` returns a new object shaped as `{ ids, limitReached }` and never mutates its input.

---

### Task 1: Deterministic Phase 1 Dataset Parser

**Files:**
- Create: `scripts/build_card_rewards_tool.py`
- Create: `tests/test_card_rewards_tool.py`

**Interfaces:**
- Consumes: `scripts.validate_card_rewards_docs.validate_corpus()` and `parse_frontmatter()`; Phase 1 `README.md`, `comparison.md`, 15 card files, and 3 payment files.
- Produces: `BuildError`, `parse_markdown_table()`, `parse_document()`, `build_dataset()`, and `serialize_dataset()` from Shared Interfaces.
- Produces dataset keys: `schemaVersion`, `auditDate`, `targetFrom`, `targetTo`, `baselineCommit`, `coverageCounts`, `cards`, `payments`, `scenarios`.

- [ ] **Step 1: Write the failing dataset-contract tests**

Create `tests/test_card_rewards_tool.py` with imports, constants, and concrete assertions:

```python
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.build_card_rewards_tool import BuildError, build_dataset, serialize_dataset


ROOT = Path(__file__).parents[1]


class CardRewardsDatasetTests(unittest.TestCase):
    def test_dataset_contains_exact_approved_products_and_payments(self) -> None:
        dataset = build_dataset(ROOT)
        cards = dataset["cards"]
        payments = dataset["payments"]

        self.assertEqual("1", dataset["schemaVersion"])
        self.assertEqual("2026-08-18", dataset["auditDate"])
        self.assertEqual("2026-08-01", dataset["targetFrom"])
        self.assertEqual("2026-12-31", dataset["targetTo"])
        self.assertEqual({"complete": 9, "partial": 9, "unavailable": 0}, dataset["coverageCounts"])
        self.assertEqual(15, len(cards))
        self.assertEqual(15, len({card["id"] for card in cards}))
        self.assertEqual(["line-pay", "ipass-money", "px-pay"], [item["id"] for item in payments])
        self.assertTrue(all(len(item["rows"]) == 15 for item in payments))

    def test_card_record_preserves_comparison_sections_sources_and_badges(self) -> None:
        dataset = build_dataset(ROOT)
        cards = {card["id"]: card for card in dataset["cards"]}
        cube = cards["cathay-cube"]

        self.assertEqual("國泰世華 CUBE 卡", cube["product"])
        self.assertEqual("partial", cube["coverageStatus"])
        self.assertIn("8/3", cube["comparison"]["domestic"])
        self.assertIn("2.5%", cube["comparison"]["overseas"])
        self.assertIn("partial", cube["badges"])
        self.assertIn("overseas", cube["facetIds"])
        self.assertIn("CUBE", cube["searchAliases"])
        self.assertTrue(cube["sections"]["uncertainties"]["blocks"])
        self.assertTrue(all(source["url"].startswith("https://") for source in cube["sources"]))

    def test_payment_names_map_back_to_stable_product_ids(self) -> None:
        dataset = build_dataset(ROOT)
        line_pay = next(item for item in dataset["payments"] if item["id"] == "line-pay")
        rows = {row["productId"]: row for row in line_pay["rows"]}

        self.assertEqual("supported", rows["sinopac-daway"]["supported"])
        self.assertIn("26.5%", rows["sinopac-daway"]["stacking"])
        self.assertEqual("not officially confirmed", rows["esun-pi"]["supported"])

    def test_serialized_dataset_is_deterministic_and_utf8_readable(self) -> None:
        first = serialize_dataset(build_dataset(ROOT))
        second = serialize_dataset(build_dataset(ROOT))

        self.assertEqual(first, second)
        self.assertIn("國泰世華 CUBE 卡", first)
        self.assertNotIn(str(ROOT), first)
        self.assertNotIn("generatedAt", first)
        self.assertEqual(json.loads(first), json.loads(second))
```

- [ ] **Step 2: Run the focused test and verify the missing module failure**

Run:

```powershell
& $py -m unittest tests.test_card_rewards_tool.CardRewardsDatasetTests -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'scripts.build_card_rewards_tool'`.

- [ ] **Step 3: Implement the parser and stable dataset model**

Create `scripts/build_card_rewards_tool.py` with these concrete constants and processing rules:

```python
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from scripts.validate_card_rewards_docs import parse_frontmatter, validate_corpus


CORPUS_RELATIVE = Path("docs/card-rewards/2026-h2")
COMPARISON_HEADERS = [
    "產品", "國內一般", "國外一般", "最佳特殊回饋", "條件",
    "上限／推導可刷額", "LINE Pay", "iPASS MONEY", "全支付", "覆蓋狀態",
]
COMPARISON_KEYS = [
    "product", "domestic", "overseas", "bestSpecial", "conditions",
    "capAndDerivedSpend", "linePay", "ipassMoney", "pxPay", "coverage",
]
PAYMENT_IDS = {"line-pay.md": "line-pay", "ipass-money.md": "ipass-money", "px-pay.md": "px-pay"}
SCENARIO_FACETS = {
    "國內實體一般消費": ("domestic",),
    "國內網路消費": ("domestic", "online"),
    "海外實體消費": ("overseas",),
    "海外網路消費": ("overseas", "online"),
    "數位訂閱": ("subscriptions",),
    "交通與加油": ("transit",),
}
SECTION_KEYS = {
    "結論摘要": "summary",
    "一般回饋": "generalRewards",
    "特殊回饋": "specialRewards",
    "行動支付相容性": "paymentCompatibility",
    "排除交易": "exclusions",
    "來源證據": "sourceEvidence",
    "不確定事項": "uncertainties",
}
BASELINE_COMMIT = "fe59115a8ba40dd47d571d43f565e91682c64366"
PRODUCT_ID_RE = re.compile(r"<!--\s*product-id:\s*([a-z0-9-]+)\s*-->")
FOOTNOTE_USE_RE = re.compile(r"\[\^([^\]]+)\]")
FOOTNOTE_DEFINITION_RE = re.compile(r"(?m)^\[\^([^\]]+)\]:\s*\[[^\]]+\]\((cards/([a-z0-9-]+)\.md)\)\s*$")
SOURCE_RE = re.compile(r"(?m)^(\d+)\.\s+(.+?)\s+(https://\S+)\s*$")


class BuildError(ValueError):
    """A deterministic corpus or generated-artifact contract failure."""
```

Implement these exact rules:

1. Call `validate_corpus(corpus_root)` first and raise `BuildError` with every `code: path: message` if any issue exists.
2. Extract a level-two section by exact heading; reject missing or duplicate required headings.
3. `parse_markdown_table()` requires a header row, separator row, fixed row width, and at least one data row.
4. Parse the comparison table in source order; remove the inline product comment and footnote only from the display label, but retain the unique ID and footnote mapping.
5. Convert body sections to safe block records using only `paragraph`, `list`, and `table`. Strip `**` emphasis markers and Markdown link syntax to display text; preserve source-reference text such as `[來源 1]`. Do not create HTML strings.
6. Parse official source lines to `{label, description, url}` and reject non-HTTPS URLs in the generated dataset.
7. Map payment `使用者產品` names to the comparison display labels; raise `BuildError` for zero, multiple, duplicate, or missing matches.
8. Parse scenario headings below `## 情境選擇`, map their footnote uses through comparison footnote definitions, and store `{id, title, entries, searchTerms}`.
9. Derive `badges` only from deterministic text checks: coverage `partial`, `登錄`, `限量`／`名額`／`額滿`, `推導`, `非保證`, `衝突`, and `not officially confirmed`／`未確認`.
10. Compute `coverageCounts` across all 18 card/payment documents and cross-check the expected `9/9/0` baseline.
11. Build each card's `facetIds` from the exact `SCENARIO_FACETS` heading map plus payment facets. `line-pay`, `ipass-money`, and `px-pay` are added only when that payment matrix row's `可綁／可連結` cell begins with `supported`; `not officially confirmed` is not treated as supported.
12. Build `searchAliases` from the official product name, comparison display label, issuer, and visible parenthetical/English names already present in those strings. Do not invent bank-marketing aliases absent from Phase 1.

Use this serializer exactly so repeated builds are byte-stable:

```python
def serialize_dataset(dataset: dict[str, object]) -> str:
    return json.dumps(
        dataset,
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
        separators=(",", ": "),
    ) + "\n"
```

- [ ] **Step 4: Add mutation tests for parser failures**

Append tests that copy the corpus to a temporary directory and make one controlled mutation per test:

```python
    def test_unknown_payment_product_name_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "repo"
            shutil.copytree(ROOT / "docs", fixture / "docs")
            payment = fixture / "docs/card-rewards/2026-h2/payments/line-pay.md"
            text = payment.read_text(encoding="utf-8").replace(
                "| 第一銀行 iLEO 卡 |", "| 不存在的產品 |", 1
            )
            payment.write_text(text, encoding="utf-8")

            with self.assertRaisesRegex(BuildError, "payment product.*不存在的產品"):
                build_dataset(fixture)

    def test_missing_required_card_section_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "repo"
            shutil.copytree(ROOT / "docs", fixture / "docs")
            card = fixture / "docs/card-rewards/2026-h2/cards/first-ileo.md"
            text = card.read_text(encoding="utf-8").replace("## 排除交易", "## 其他事項", 1)
            card.write_text(text, encoding="utf-8")

            with self.assertRaisesRegex(BuildError, "排除交易"):
                build_dataset(fixture)
```

Add `import shutil` at the top. Expected errors must include the affected relative path and contract name.

- [ ] **Step 5: Run parser tests and Phase 1 regression**

Run:

```powershell
& $py -m unittest tests.test_card_rewards_tool.CardRewardsDatasetTests -v
& $py -m unittest tests.test_card_rewards_docs -v
& $py scripts/validate_card_rewards_docs.py --root docs/card-rewards/2026-h2
```

Expected: all tests PASS; validator prints `card rewards corpus: OK`.

- [ ] **Step 6: Commit the parser**

```powershell
git add -- scripts/build_card_rewards_tool.py tests/test_card_rewards_tool.py
git diff --cached --check
git commit -m "feat: build card rewards dataset"
```

Expected staged scope: exactly the two listed files.

---

### Task 2: Atomic HTML Data Injection and Drift Check

**Files:**
- Modify: `scripts/build_card_rewards_tool.py`
- Modify: `tests/test_card_rewards_tool.py`
- Create: `tool/card-rewards.html`

**Interfaces:**
- Consumes: `build_dataset()` and `serialize_dataset()` from Task 1.
- Produces: `DATA_START`, `DATA_END`, `read_embedded_dataset()`, `replace_embedded_dataset()`, `build_output()`, and `main()` from Shared Interfaces.
- CLI defaults: repo root is `Path(__file__).parents[1]`; output is `<repo>/tool/card-rewards.html`; `--check` performs no writes.

- [ ] **Step 1: Write failing marker, CLI, and drift tests**

Append a new test class:

```python
import os
import subprocess
import sys

from scripts.build_card_rewards_tool import (
    DATA_END,
    DATA_START,
    read_embedded_dataset,
    replace_embedded_dataset,
)


UTF8_ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}


class CardRewardsBuildTests(unittest.TestCase):
    def test_replace_embedded_dataset_changes_only_marked_block(self) -> None:
        source = f"before\n{DATA_START}\nold\n{DATA_END}\nafter\n"
        updated = replace_embedded_dataset(source, '{"schemaVersion": "1"}\n')

        self.assertTrue(updated.startswith(f"before\n{DATA_START}\n"))
        self.assertTrue(updated.endswith(f"{DATA_END}\nafter\n"))
        self.assertEqual('{"schemaVersion": "1"}\n', read_embedded_dataset(updated))

    def test_replace_rejects_missing_or_duplicate_markers(self) -> None:
        with self.assertRaisesRegex(BuildError, "exactly one data marker pair"):
            replace_embedded_dataset("<html></html>", "{}\n")
        duplicate = f"{DATA_START}x{DATA_END}{DATA_START}y{DATA_END}"
        with self.assertRaisesRegex(BuildError, "exactly one data marker pair"):
            replace_embedded_dataset(duplicate, "{}\n")

    def test_checked_in_html_matches_generated_dataset(self) -> None:
        expected = serialize_dataset(build_dataset(ROOT))
        actual = read_embedded_dataset((ROOT / "tool/card-rewards.html").read_text(encoding="utf-8"))
        self.assertEqual(expected, actual)

    def test_cli_check_detects_one_byte_of_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "card-rewards.html"
            output.write_text((ROOT / "tool/card-rewards.html").read_text(encoding="utf-8"), encoding="utf-8")
            output.write_text(output.read_text(encoding="utf-8").replace('"schemaVersion": "1"', '"schemaVersion": "9"', 1), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_card_rewards_tool.py"), "--check", "--output", str(output)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                env=UTF8_ENV,
                check=False,
            )

        self.assertEqual(1, result.returncode)
        self.assertIn("embedded dataset drift", result.stderr)
```

- [ ] **Step 2: Run build tests and verify missing-interface failures**

Run:

```powershell
& $py -m unittest tests.test_card_rewards_tool.CardRewardsBuildTests -v
```

Expected: FAIL because marker functions and `tool/card-rewards.html` do not exist.

- [ ] **Step 3: Implement marker replacement, atomic write, and CLI**

Add these rules to the builder:

```python
DATA_START = "<!-- CARD_REWARDS_DATA_START -->"
DATA_END = "<!-- CARD_REWARDS_DATA_END -->"


def _marker_bounds(html_text: str) -> tuple[int, int]:
    if html_text.count(DATA_START) != 1 or html_text.count(DATA_END) != 1:
        raise BuildError("HTML must contain exactly one data marker pair")
    start = html_text.index(DATA_START) + len(DATA_START)
    end = html_text.index(DATA_END)
    if start >= end:
        raise BuildError("HTML data markers are out of order")
    return start, end


def read_embedded_dataset(html_text: str) -> str:
    start, end = _marker_bounds(html_text)
    block = html_text[start:end].strip("\r\n")
    match = re.fullmatch(
        r'<script id="card-rewards-data" type="application/json">\n(.*)\n</script>',
        block,
        flags=re.DOTALL,
    )
    if match is None:
        raise BuildError("marked block must contain exactly one card-rewards-data JSON script")
    return match.group(1) + "\n"


def replace_embedded_dataset(html_text: str, json_text: str) -> str:
    start, end = _marker_bounds(html_text)
    safe_json = json_text.replace("</", "<\\/")
    block = (
        "\n<script id=\"card-rewards-data\" type=\"application/json\">\n"
        + safe_json.rstrip("\n")
        + "\n</script>\n"
    )
    return html_text[:start] + block + html_text[end:]
```

`build_output()` must read the existing template, compare serialized JSON in check mode, and otherwise write through a sibling temporary file before `Path.replace()` so failed writes cannot leave a partial HTML. Add CLI arguments `--check`, `--repo-root`, and `--output`; catch `BuildError` and print `card rewards build: <message>` to stderr.

- [ ] **Step 4: Create the initial semantic HTML template and generate its data**

Create `tool/card-rewards.html` with `lang="zh-TW"`, UTF-8, viewport metadata, one semantic `<main id="app">`, a visible `<noscript>` notice, and exactly one marker block:

```html
<!-- CARD_REWARDS_DATA_START -->
<script id="card-rewards-data" type="application/json">{}</script>
<!-- CARD_REWARDS_DATA_END -->
```

Do not add any external `src`, stylesheet, font, image, iframe, or fetch call. Then run:

```powershell
& $py scripts/build_card_rewards_tool.py
& $py scripts/build_card_rewards_tool.py --check
```

Expected: first command updates only the marker block; second prints `card rewards tool: OK` and exits 0.

- [ ] **Step 5: Run Task 1–2 tests and compile check**

```powershell
& $py -m unittest tests.test_card_rewards_tool -v
& $py -m py_compile scripts/build_card_rewards_tool.py
& $py scripts/validate_card_rewards_docs.py --root docs/card-rewards/2026-h2
```

Expected: all tests PASS, compile exits 0, corpus validator prints OK.

- [ ] **Step 6: Commit deterministic artifact generation**

```powershell
git add -- scripts/build_card_rewards_tool.py tests/test_card_rewards_tool.py tool/card-rewards.html
git diff --cached --check
git commit -m "feat: add deterministic card rewards artifact build"
```

Expected staged scope: exactly the three listed files.

---

### Task 3: Search, Facets, and Responsive Product Cards

**Files:**
- Modify: `tool/card-rewards.html`
- Modify: `tests/test_card_rewards_tool.py`

**Interfaces:**
- Consumes: embedded `CardRewardsDataset` from Task 2.
- Produces: `globalThis.CardRewardsCore` pure functions from Shared Interfaces.
- Produces DOM IDs: `app`, `fatal-error`, `search`, `result-count`, `clear-filters`, `facet-controls`, `coverage-controls`, `type-controls`, `card-grid`, `empty-state`, `compare-tray`.

- [ ] **Step 1: Write failing static-contract and pure JavaScript tests**

Add an `HTMLParser` helper that records element IDs, external assets, and the text of `<script id="card-rewards-core">`. Add a Node `vm` helper matching existing repository test style. Then add:

```python
class CardRewardsInterfaceTests(unittest.TestCase):
    def test_page_has_required_discovery_controls(self) -> None:
        parser = parse_tool_page()
        for element_id in (
            "app", "fatal-error", "search", "result-count", "clear-filters", "facet-controls",
            "coverage-controls", "type-controls", "card-grid", "empty-state", "compare-tray",
        ):
            self.assertIn(element_id, parser.elements)
        self.assertEqual("search", parser.elements["search"]["type"])

    def test_page_has_no_runtime_asset_or_network_dependency(self) -> None:
        parser = parse_tool_page()
        self.assertEqual([], parser.external_assets)
        source = (ROOT / "tool/card-rewards.html").read_text(encoding="utf-8")
        self.assertNotRegex(source, r"\bfetch\s*\(")
        self.assertNotIn("XMLHttpRequest", source)

    def test_core_search_matches_bank_alias_merchant_and_payment(self) -> None:
        self.assertTrue(run_core("cardMatchesQuery(CARDS.find(c => c.id === 'taishin-richart-gogo'), '@gogo')"))
        self.assertTrue(run_core("cardMatchesQuery(CARDS.find(c => c.id === 'sinopac-daway'), '路易莎')"))
        self.assertTrue(run_core("cardMatchesQuery(CARDS.find(c => c.id === 'esun-unicard'), '全支付')"))
        self.assertFalse(run_core("cardMatchesQuery(CARDS.find(c => c.id === 'esun-pi'), 'Costco')"))

    def test_filter_groups_are_or_within_group_and_and_across_groups(self) -> None:
        expression = """
        filterCards(CARDS, {
          query: '',
          facets: new Set(['line-pay', 'ipass-money']),
          coverage: new Set(['complete']),
          productTypes: new Set()
        }).map(card => card.id)
        """
        result = run_core(expression)
        self.assertIn("esun-unicard", result)
        self.assertNotIn("esun-pi", result)
```

The Node helper must inject the parsed dataset as `CARDS` and convert JSON-compatible filter fixtures to JavaScript `Set` objects before evaluating the expression.

- [ ] **Step 2: Run the focused interface tests and verify missing-control failures**

```powershell
& $py -m unittest tests.test_card_rewards_tool.CardRewardsInterfaceTests -v
```

Expected: FAIL because discovery controls and `CardRewardsCore` do not exist.

- [ ] **Step 3: Implement the visual shell and pure state functions**

In `tool/card-rewards.html`, define CSS custom properties and responsive layout:

```css
:root {
  color-scheme: light;
  --navy-950: #0a1f33;
  --navy-800: #153a5b;
  --navy-650: #285b82;
  --warm-50: #fbfaf6;
  --warm-100: #f4f0e7;
  --ink: #17212b;
  --muted: #5f6b76;
  --line: #d9d5ca;
  --ok: #2f6b52;
  --warn: #9a6418;
  --danger: #9b3a32;
  --focus: #1677bd;
  --radius: 16px;
}
```

Use system fonts, `font-variant-numeric: tabular-nums`, a three-column `.card-grid`, two columns below 900px, and one column below 620px. Add visible `:focus-visible` styles, 44px minimum touch targets, reduced-motion rules, and a deep-navy header on warm-white content.

Implement exact pure functions in `<script id="card-rewards-core">`:

```javascript
function normalizeText(value) {
  return String(value ?? "").normalize("NFKC").trim().toLocaleLowerCase("zh-TW");
}

function collectText(value, output = []) {
  if (typeof value === "string") output.push(value);
  else if (Array.isArray(value)) value.forEach(item => collectText(item, output));
  else if (value && typeof value === "object") Object.values(value).forEach(item => collectText(item, output));
  return output;
}

function cardMatchesQuery(card, query) {
  const needle = normalizeText(query);
  return !needle || normalizeText(collectText(card).join(" ")).includes(needle);
}

function cardMatchesFilters(card, filters) {
  const inGroup = (selected, values) => !selected.size || values.some(value => selected.has(value));
  return inGroup(filters.facets, card.facetIds)
    && inGroup(filters.coverage, [card.coverageStatus])
    && inGroup(filters.productTypes, [card.productType]);
}

function filterCards(cards, filters) {
  return cards.filter(card => cardMatchesQuery(card, filters.query) && cardMatchesFilters(card, filters));
}
```

Render all corpus strings with element creation plus `textContent`. Product cards must include issuer, product, type, domestic, overseas, best special, cap/condition text, status badges, `查看詳情`, and `加入比較`. Keep Phase 1 order; do not sort by percentage.

Bootstrap by parsing only `#card-rewards-data`. Require `schemaVersion === "1"`, 15 cards, and 3 payments before rendering. Wrap bootstrap in `try/catch`; on invalid or missing JSON, hide the interactive controls and reveal `#fatal-error` with `資料無法載入；請重新產生 card-rewards.html。` plus the escaped error message. Never attempt a network fallback.

- [ ] **Step 4: Implement query, filter, count, and empty-state behavior**

Use one in-memory state object:

```javascript
const state = {
  query: "",
  facets: new Set(),
  coverage: new Set(),
  productTypes: new Set(),
  selectedIds: [],
  detailId: null
};
```

Facet buttons use `aria-pressed`; within-group selections are OR and different groups are AND. On every state change, update `#result-count`, rebuild `#card-grid`, toggle `#empty-state`, and update `#clear-filters`. The empty state must say no product matched and provide the same clear operation.

- [ ] **Step 5: Run interface, drift, and Phase 1 tests**

```powershell
& $py -m unittest tests.test_card_rewards_tool.CardRewardsInterfaceTests -v
& $py -m unittest tests.test_card_rewards_tool.CardRewardsBuildTests -v
& $py scripts/build_card_rewards_tool.py --check
& $py -m unittest tests.test_card_rewards_docs -v
```

Expected: all tests PASS; `--check` still passes because UI edits remain outside the marked data block.

- [ ] **Step 6: Commit the discovery interface**

```powershell
git add -- tool/card-rewards.html tests/test_card_rewards_tool.py
git diff --cached --check
git commit -m "feat: add card rewards discovery interface"
```

Expected staged scope: exactly the two listed files.

---

### Task 4: Three-Card Comparison, Evidence Detail, and Accessibility

**Files:**
- Modify: `tool/card-rewards.html`
- Modify: `tests/test_card_rewards_tool.py`

**Interfaces:**
- Consumes: Task 3 state and `CardRewardsCore` functions.
- Produces: `toggleSelection()` in `CardRewardsCore`.
- Produces DOM IDs: `compare-count`, `compare-open`, `compare-dialog`, `comparison-content`, `detail-dialog`, `detail-title`, `detail-content`, `detail-close`.

- [ ] **Step 1: Write failing selection and semantic-dialog tests**

Add exact tests:

```python
    def test_selection_stops_at_three_without_mutating_input(self) -> None:
        expression = """
        (() => {
          const original = ['first-ileo', 'first-green', 'sinopac-dawho'];
          const result = toggleSelection(original, 'sinopac-daway');
          return { original, result };
        })()
        """
        value = run_core(expression)
        self.assertEqual(["first-ileo", "first-green", "sinopac-dawho"], value["original"])
        self.assertEqual(value["original"], value["result"]["ids"])
        self.assertTrue(value["result"]["limitReached"])

    def test_selection_can_remove_and_readd_a_product(self) -> None:
        value = run_core("toggleSelection(['first-ileo', 'first-green'], 'first-ileo')")
        self.assertEqual(["first-green"], value["ids"])
        self.assertFalse(value["limitReached"])

    def test_compare_and_detail_use_native_dialogs_with_labels(self) -> None:
        parser = parse_tool_page()
        self.assertEqual("dialog", parser.elements["compare-dialog"]["tag"])
        self.assertEqual("dialog", parser.elements["detail-dialog"]["tag"])
        self.assertEqual("detail-title", parser.elements["detail-dialog"]["aria-labelledby"])
        self.assertIn("aria-live", parser.elements["compare-count"])
```

Update the parser to preserve element tag names and ARIA attributes.

- [ ] **Step 2: Run focused tests and verify expected failures**

```powershell
& $py -m unittest tests.test_card_rewards_tool.CardRewardsInterfaceTests.test_selection_stops_at_three_without_mutating_input tests.test_card_rewards_tool.CardRewardsInterfaceTests.test_compare_and_detail_use_native_dialogs_with_labels -v
```

Expected: FAIL because selection and dialog interfaces are missing.

- [ ] **Step 3: Implement immutable three-card selection and compare tray**

Add to the core script:

```javascript
function toggleSelection(selectedIds, productId, limit = 3) {
  const ids = [...selectedIds];
  const existing = ids.indexOf(productId);
  if (existing >= 0) {
    ids.splice(existing, 1);
    return { ids, limitReached: false };
  }
  if (ids.length >= limit) return { ids, limitReached: true };
  ids.push(productId);
  return { ids, limitReached: false };
}
```

The fixed compare tray lists selected names, lets users remove each item, and enables `開啟比較` only for at least two selections. At three selections, disable other add buttons and expose the explanation `最多比較 3 項產品` as visible text and an accessible description.

Render comparison rows for product, domestic, overseas, best special, conditions, cap/derived spend, LINE Pay, iPASS MONEY, 全支付, and coverage. Use original text, no winner classes, no numeric sorting, and no cross-currency totals.

- [ ] **Step 4: Implement detail dialog with structured evidence blocks**

Use native `<dialog>` for both desktop and mobile. CSS positions `#detail-dialog` as a right drawer above 720px and a near-full-screen bottom sheet at or below 720px. Build every paragraph, list, table, badge, and source link with DOM APIs. Source links must use `target="_blank"` and `rel="noopener noreferrer"`; the evidence Markdown link is relative to `../docs/card-rewards/2026-h2/cards/<id>.md`.

Render detail sections in this fixed order:

```javascript
const DETAIL_SECTION_ORDER = [
  ["summary", "結論摘要"],
  ["generalRewards", "一般回饋"],
  ["specialRewards", "特殊回饋"],
  ["paymentCompatibility", "行動支付相容性"],
  ["exclusions", "排除交易"],
  ["uncertainties", "不確定事項"]
];
```

Use `showModal()`; store the opener before opening, close on native Esc or explicit button, and restore focus to the opener on `close`. Do not attach a click-to-close handler to dialog content; only a click whose target is the dialog backdrop may close it.

- [ ] **Step 5: Add a headless browser interaction probe**

Add a helper that copies the HTML to a temporary file, inserts a probe immediately before `</body>`, launches Chrome or Edge with `--headless=new --disable-gpu --disable-extensions --no-first-run --dump-dom`, and reads `<pre id="e2e-result">` JSON. The probe must:

1. Search `路易莎` and assert only matching cards remain.
2. Clear filters.
3. Select three cards and attempt a fourth; assert count stays 3 and the fourth add button is disabled.
4. Open comparison and assert domestic/overseas rows exist.
5. Close comparison, open CUBE detail, and assert `部分期間`, `不確定事項`, and at least one HTTPS official source are visible.

Use a 1200×900 viewport and a unique temporary `--user-data-dir`.

- [ ] **Step 6: Run core, headless interaction, and build checks**

```powershell
& $py -m unittest tests.test_card_rewards_tool.CardRewardsInterfaceTests -v
& $py scripts/build_card_rewards_tool.py --check
& $py -m py_compile scripts/build_card_rewards_tool.py tests/test_card_rewards_tool.py
```

Expected: all interface tests PASS, headless probe PASS, drift check exits 0.

- [ ] **Step 7: Commit comparison and evidence detail**

```powershell
git add -- tool/card-rewards.html tests/test_card_rewards_tool.py
git diff --cached --check
git commit -m "feat: add card rewards comparison and evidence details"
```

Expected staged scope: exactly the two listed files.

---

### Task 5: Repo Navigation and Date-Scoped Documentation

**Files:**
- Modify: `index.html`
- Modify: `README.md`
- Modify: `tests/test_index_navigation.py`

**Interfaces:**
- Consumes: checked-in `tool/card-rewards.html` from Tasks 2–4.
- Produces: one relative repo homepage link and one README relative link to `tool/card-rewards.html`.

- [ ] **Step 1: Write the failing local-navigation regression test**

Append to `IndexNavigationTests`:

```python
    def test_index_links_to_local_card_rewards_tool(self) -> None:
        parser = LinkParser()
        parser.feed((ROOT / "index.html").read_text(encoding="utf-8"))

        self.assertIn(("tool/card-rewards.html", "2026 下半年舊戶卡片回饋查詢"), parser.links)
        self.assertNotIn(
            "https://claude.ai/public/artifacts/aa39410d-a1c4-4e5d-8259-df094c2238b8",
            (ROOT / "index.html").read_text(encoding="utf-8"),
        )
        self.assertTrue((ROOT / "tool/card-rewards.html").is_file())

    def test_readme_links_to_local_card_rewards_snapshot(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("[2026 下半年舊戶卡片回饋查詢](tool/card-rewards.html)", readme)
        self.assertIn("查證基準日 2026-08-18", readme)
```

- [ ] **Step 2: Run navigation tests and verify the old external-link failure**

```powershell
& $py -m unittest tests.test_index_navigation -v
```

Expected: the existing image-stack test passes; the two new card-reward tests FAIL because the external Claude link is still present.

- [ ] **Step 3: Replace only the card-tool links and add scope copy**

In `index.html`, replace the existing card entry with:

```html
<li><a href="tool/card-rewards.html">2026 下半年舊戶卡片回饋查詢</a></li>
```

In the README Web Tools table, replace the card row with:

```markdown
| [2026 下半年舊戶卡片回饋查詢](tool/card-rewards.html) | 既有持卡人／既有帳戶的 2026-08-01 至 12-31 離線回饋快照；查證基準日 2026-08-18，非即時銀行資料 |
```

Do not change other GitHub Pages or Claude artifact links.

- [ ] **Step 4: Run navigation, tool, and corpus regression tests**

```powershell
& $py -m unittest tests.test_index_navigation tests.test_card_rewards_tool tests.test_card_rewards_docs -v
& $py scripts/build_card_rewards_tool.py --check
```

Expected: all tests PASS; tool drift check exits 0.

- [ ] **Step 5: Commit local navigation integration**

```powershell
git add -- index.html README.md tests/test_index_navigation.py
git diff --cached --check
git commit -m "docs: link local card rewards tool"
```

Expected staged scope: exactly the three listed files.

---

### Task 6: Offline, Mobile, and Security Acceptance Tests

**Files:**
- Modify: `tests/test_card_rewards_tool.py`
- Modify: `tool/card-rewards.html` only if a failing acceptance test reveals an implementation defect

**Interfaces:**
- Consumes: complete artifact and test helpers from Tasks 1–5.
- Produces: repeatable desktop/mobile/offline/security acceptance coverage.

- [ ] **Step 1: Add failing offline and source-link security assertions**

Add tests that parse all tags and attributes:

```python
class CardRewardsAcceptanceTests(unittest.TestCase):
    def test_offline_page_has_no_automatic_network_surface(self) -> None:
        parser = parse_tool_page()
        self.assertEqual([], parser.external_assets)
        self.assertEqual([], parser.iframes)
        source = (ROOT / "tool/card-rewards.html").read_text(encoding="utf-8")
        for forbidden in ("fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket", "localStorage"):
            self.assertNotIn(forbidden, source)

    def test_all_generated_official_links_are_https_and_safe(self) -> None:
        result = run_browser_probe("source-links", width=1200, height=900)
        self.assertGreater(result["sourceCount"], 0)
        self.assertTrue(result["allHttps"])
        self.assertTrue(result["allNoopenerNoreferrer"])

    def test_corpus_text_is_not_executed_as_html(self) -> None:
        source = (ROOT / "tool/card-rewards.html").read_text(encoding="utf-8")
        self.assertNotRegex(source, r"\.innerHTML\s*=.*(?:card|section|source|dataset)")

    def test_invalid_schema_shows_visible_failure_without_network_fallback(self) -> None:
        result = run_browser_probe(
            "invalid-schema",
            width=1200,
            height=900,
            source_transform=lambda source: source.replace(
                '"schemaVersion": "1"', '"schemaVersion": "unsupported"', 1
            ),
        )
        self.assertTrue(result["fatalVisible"])
        self.assertIn("資料無法載入", result["fatalText"])
        self.assertTrue(result["controlsHidden"])
```

The parser treats `href` as an external asset only for `<link>`; ordinary official `<a>` links are inspected separately by the browser probe. Extend `run_browser_probe()` with an optional `source_transform` callable used only on its temporary HTML copy; the checked-in artifact remains unchanged.

- [ ] **Step 2: Add a 390×844 mobile browser probe**

The mobile probe must open the generated file and record:

```javascript
{
  viewportWidth: document.documentElement.clientWidth,
  cardColumns: getComputedStyle(document.getElementById("card-grid")).gridTemplateColumns,
  bodyOverflow: document.documentElement.scrollWidth <= document.documentElement.clientWidth,
  touchTargetHeight: document.querySelector("[data-action='detail']").getBoundingClientRect().height,
  detailOpen: document.getElementById("detail-dialog").open,
  detailMode: getComputedStyle(document.getElementById("detail-dialog")).getPropertyValue("--detail-mode").trim(),
  closeVisible: document.getElementById("detail-close").getBoundingClientRect().top >= 0
}
```

Assert one card-grid column, no whole-page horizontal overflow, touch target height at least 44 CSS px, open detail mode equals `bottom-sheet`, and the close control remains visible.

- [ ] **Step 3: Run acceptance tests and record the RED causes**

```powershell
& $py -m unittest tests.test_card_rewards_tool.CardRewardsAcceptanceTests -v
```

Expected: any missing security attribute, mobile CSS variable, or parser distinction fails with a precise assertion. Record the failing test names in the task report before editing the implementation.

- [ ] **Step 4: Apply the minimum HTML fixes required by the acceptance tests**

Allowed fixes are limited to:

- adding `rel="noopener noreferrer"` to generated external anchors;
- replacing corpus-driven `innerHTML` with DOM construction and `textContent`;
- setting `--detail-mode: drawer` and the mobile override `--detail-mode: bottom-sheet`;
- preventing page-level horizontal overflow while leaving detail tables locally scrollable;
- increasing interactive controls to at least 44px height.

Do not alter embedded reward data or Phase 1 Markdown in this task.

- [ ] **Step 5: Run the full Phase 2 and Phase 1 suites**

```powershell
& $py -m unittest tests.test_card_rewards_tool tests.test_card_rewards_docs tests.test_index_navigation -v
& $py -m py_compile scripts/build_card_rewards_tool.py tests/test_card_rewards_tool.py tests/test_card_rewards_docs.py tests/test_index_navigation.py
& $py scripts/build_card_rewards_tool.py --check
& $py scripts/validate_card_rewards_docs.py --root docs/card-rewards/2026-h2
```

Expected: all tests PASS, both scripts exit 0, corpus validator prints `card rewards corpus: OK`.

- [ ] **Step 6: Commit the acceptance coverage**

If only tests changed:

```powershell
git add -- tests/test_card_rewards_tool.py
git diff --cached --check
git commit -m "test: verify card rewards artifact acceptance"
```

If an HTML defect was fixed:

```powershell
git add -- tests/test_card_rewards_tool.py tool/card-rewards.html
git diff --cached --check
git commit -m "fix: satisfy card rewards artifact acceptance"
```

Expected staged scope: tests plus the HTML only when directly justified by a failing acceptance test.

---

### Task 7: Fresh Browser Read-Back and Final Scope Audit

**Files:**
- Verify only; do not edit unless a check fails and the failure is returned to the responsible task.

**Interfaces:**
- Consumes: all prior task commits.
- Produces: final evidence for completion; no deployable artifact beyond the committed files.

- [ ] **Step 1: Verify the Git scope before testing**

```powershell
git status --short --branch
git diff e1d929a..HEAD --name-only
git diff e1d929a..HEAD --check
```

Expected changed implementation paths are limited to:

```text
README.md
index.html
scripts/build_card_rewards_tool.py
tests/test_card_rewards_tool.py
tests/test_index_navigation.py
tool/card-rewards.html
```

The plan document itself predates the implementation range and is not included in this list. Worktree status must be clean.

- [ ] **Step 2: Run one fresh complete automated verification**

```powershell
& $py -m unittest tests.test_card_rewards_tool tests.test_card_rewards_docs tests.test_index_navigation -v
& $py -m py_compile scripts/build_card_rewards_tool.py tests/test_card_rewards_tool.py tests/test_card_rewards_docs.py tests/test_index_navigation.py
& $py scripts/build_card_rewards_tool.py --check
& $py scripts/validate_card_rewards_docs.py --root docs/card-rewards/2026-h2 --json-report tmp/card-rewards-final-validation.json
```

Expected: zero test failures, py_compile exit 0, build check exit 0, and JSON `issue_count` equals 0.

- [ ] **Step 3: Perform actual in-app browser desktop read-back**

Open the absolute `file://` URI for `tool/card-rewards.html` at a desktop viewport and verify:

1. Header states existing customers, 2026-08-01 to 12-31, and audit date 2026-08-18.
2. Initial count is 15 and initial order matches comparison.md.
3. `@GoGo` finds Richart, `路易莎` finds DAWAY, and `全支付` includes explicitly supported entries without converting unknown to unsupported.
4. Domestic plus complete filters combine correctly and clear restores 15.
5. Three-card compare works; a fourth cannot be added; no winner or cross-currency total is shown.
6. CUBE detail visibly shows partial coverage, uncertainty, full sections, safe official links, and evidence path.
7. Browser console contains no uncaught exception or failed automatic network request.

- [ ] **Step 4: Perform actual in-app browser mobile read-back**

At approximately 390×844 verify:

1. Cards are one column and the page has no whole-page horizontal overflow.
2. Filter chips and buttons are comfortably tappable.
3. Detail opens as a bottom sheet, close control remains visible, Esc closes when a keyboard is present, and focus returns to the opener.
4. Comparison remains readable through its local scroll container.
5. With network disabled, all embedded data, search, filters, compare, and detail still work.

- [ ] **Step 5: Confirm artifact-data equivalence and no hidden drift**

```powershell
$expected = & $py scripts/build_card_rewards_tool.py --check
if ($LASTEXITCODE -ne 0) { throw 'embedded dataset drift' }
git status --short
git diff --check
```

Expected: build prints OK, worktree stays clean, and diff check reports no issue.

- [ ] **Step 6: Request fresh-context review before completion**

Reviewer scope:

- Compare implementation against every acceptance criterion in `docs/superpowers/specs/2026-08-18-card-rewards-tool-design.md`.
- Inspect generated data against at least CUBE (`partial`), DAWAY (limited merchant promotions), Rakuten (unconfirmed merchant function), and Unicard (different reward currency).
- Confirm no Phase 1 fact changed only inside HTML.
- Confirm search/filter mappings do not turn `not officially confirmed` into zero or unsupported.
- Confirm no external runtime dependency, cross-currency ranking, publication, push, merge, or unrelated staged change.

Any Important or Critical finding returns to the owning task for a test-first fix and a new focused commit. Re-run Steps 1–5 after the final fix.

## Completion Evidence to Report

The final handoff must state:

- implementation commit range and exact changed paths;
- total automated tests run, failures, and skipped tests;
- Phase 1 validator `issue_count`;
- generator `--check` result;
- desktop and mobile viewport results;
- offline/network and console results;
- remaining evidence limitations inherited from Phase 1;
- explicit confirmation that no push, merge, deploy, publication, or unrelated main-worktree edit occurred.
