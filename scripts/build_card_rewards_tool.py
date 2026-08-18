"""Build the deterministic dataset consumed by the card-rewards tool."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).parents[1]))

from scripts.validate_card_rewards_docs import parse_frontmatter, validate_corpus


CORPUS_RELATIVE = Path("docs/card-rewards/2026-h2")
DATA_START = "<!-- CARD_REWARDS_DATA_START -->"
DATA_END = "<!-- CARD_REWARDS_DATA_END -->"
COMPARISON_HEADERS = [
    "產品", "國內一般", "國外一般", "最佳特殊回饋", "條件",
    "上限／推導可刷額", "LINE Pay", "iPASS MONEY", "全支付", "覆蓋狀態",
]
COMPARISON_KEYS = [
    "product", "domestic", "overseas", "bestSpecial", "conditions",
    "capAndDerivedSpend", "linePay", "ipassMoney", "pxPay", "coverage",
]
PAYMENT_IDS = {
    "line-pay.md": "line-pay",
    "ipass-money.md": "ipass-money",
    "px-pay.md": "px-pay",
}
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
FOOTNOTE_DEFINITION_RE = re.compile(
    r"(?m)^\[\^([^\]]+)\]:\s*\[[^\]]+\]\((cards/([a-z0-9-]+)\.md)\)\s*$"
)
SOURCE_RE = re.compile(r"(?m)^(\d+)\.\s+(.+?)\s+(https://\S+)\s*$")
CTBC_SPECIAL_HEADERS = (
    "有效期間", "場景／通路", "總回饋", "組成", "舊戶條件", "回饋上限／推導可刷額", "登錄／名額",
)
CTBC_SPECIAL_SHORT_ROW = (
    "2026-01-01 至 2026-12-31",
    "Hotels.com 臺灣網站指定「LINE Pay卡」網頁，代碼 `CTBCLP16`",
    "16% LINE POINTS",
    "已含一般 1%；不與 Hotels.com Rewards™ 併用 [來源 6]",
    "線上以 LINE Pay 卡付款、新臺幣，1-28 晚；2026 年預訂、2027-06-30 前完成入住，僅線上付款飯店，Pay at hotel 不適用；每筆 1,800 點 [來源 6]",
    "詳細頁稱每月首 450 次預訂；但官方總表稱每月 400 組，兩頁衝突，不選一方為完整名額 [來源 3][來源 6]",
)


class BuildError(ValueError):
    """A deterministic corpus or generated-artifact contract failure."""


def _relative(path: Path, corpus_root: Path) -> str:
    return path.relative_to(corpus_root).as_posix()


def _split_row(line: str) -> list[str] | None:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return None
    return [cell.strip() for cell in stripped[1:-1].split("|")]


def _is_separator(row: list[str]) -> bool:
    return bool(row) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in row)


def parse_markdown_table(text: str, *, context: str = "markdown table") -> tuple[list[str], list[list[str]]]:
    """Parse one pipe table, rejecting ambiguous or malformed table contracts."""
    lines = [line for line in text.splitlines() if line.strip()]
    if len(lines) < 3:
        raise BuildError(f"{context}: requires a header, separator, and data row")
    header = _split_row(lines[0])
    separator = _split_row(lines[1])
    if header is None or separator is None:
        raise BuildError(f"{context}: requires a header row and separator row")
    if not header or len(separator) != len(header) or not _is_separator(separator):
        raise BuildError(f"{context}: invalid separator row")
    rows: list[list[str]] = []
    for line in lines[2:]:
        row = _split_row(line)
        if row is None:
            raise BuildError(f"{context}: non-table content appears inside table")
        if len(row) != len(header):
            raise BuildError(f"{context}: fixed row width is {len(header)}; found {len(row)}")
        rows.append(row)
    if not rows:
        raise BuildError(f"{context}: requires at least one data row")
    return header, rows


def _section(body: str, title: str, *, relative: str) -> str:
    pattern = re.compile(rf"(?m)^##\s+{re.escape(title)}\s*$")
    matches = list(pattern.finditer(body))
    if len(matches) != 1:
        state = "missing" if not matches else "duplicate"
        raise BuildError(f"{relative}: required section {title} is {state}")
    start = matches[0].end()
    next_heading = re.search(r"(?m)^##\s+", body[start:])
    end = start + next_heading.start() if next_heading else len(body)
    return body[start:end].strip()


def _clean_text(text: str) -> str:
    text = html.unescape(text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    text = text.replace("**", "")
    return re.sub(r"[ \t]+", " ", text).strip()


def _safe_table_block(
    lines: list[str], *, relative: str, section: str
) -> dict[str, object]:
    """Use a marked fallback only for the ruled CTBC source table and row."""
    context = f"{relative}: {section}"
    try:
        headers, rows = parse_markdown_table("\n".join(lines), context=context)
    except BuildError:
        header = _split_row(lines[0])
        separator = _split_row(lines[1]) if len(lines) > 1 else None
        source_rows = [_split_row(line) for line in lines[2:]]
        if (
            header is None
            or separator is None
            or len(separator) != len(header)
            or not _is_separator(separator)
            or not source_rows
            or any(row is None for row in source_rows)
            or relative != "cards/ctbc-line-pay.md"
            or section != "特殊回饋"
            or tuple(header) != CTBC_SPECIAL_HEADERS
            or len([row for row in source_rows if row is not None and len(row) != len(header)]) != 1
            or tuple(next(row for row in source_rows if row is not None and len(row) != len(header)))
            != CTBC_SPECIAL_SHORT_ROW
        ):
            raise
        return {
            "type": "table-fallback",
            "headers": [_clean_text(cell) for cell in header],
            "rows": [
                {"cells": [_clean_text(cell) for cell in row]}
                for row in source_rows
                if row is not None
            ],
            "sourceRowWidthMismatch": True,
        }
    return {
        "type": "table",
        "headers": [_clean_text(header) for header in headers],
        "rows": [[_clean_text(cell) for cell in row] for row in rows],
    }


def _blocks(text: str, *, relative: str, section: str) -> list[dict[str, object]]:
    """Represent Markdown using only safe paragraph, list, and table records."""
    lines = text.splitlines()
    blocks: list[dict[str, object]] = []
    index = 0
    while index < len(lines):
        if not lines[index].strip():
            index += 1
            continue
        if _split_row(lines[index]) is not None:
            end = index
            while end < len(lines) and _split_row(lines[end]) is not None:
                end += 1
            blocks.append(_safe_table_block(lines[index:end], relative=relative, section=section))
            index = end
            continue
        if re.match(r"^\s*(?:[-*+]\s+|\d+\.\s+)", lines[index]):
            items: list[str] = []
            while index < len(lines) and re.match(r"^\s*(?:[-*+]\s+|\d+\.\s+)", lines[index]):
                items.append(_clean_text(re.sub(r"^\s*(?:[-*+]\s+|\d+\.\s+)", "", lines[index])))
                index += 1
            blocks.append({"type": "list", "items": items})
            continue
        paragraph: list[str] = []
        while index < len(lines) and lines[index].strip() and _split_row(lines[index]) is None:
            if re.match(r"^\s*(?:[-*+]\s+|\d+\.\s+)", lines[index]):
                break
            paragraph.append(re.sub(r"^#{3,}\s+", "", lines[index]).strip())
            index += 1
        if paragraph:
            blocks.append({"type": "paragraph", "text": _clean_text(" ".join(paragraph))})
    return blocks


def _sources(section: str, *, relative: str) -> list[dict[str, str]]:
    sources: list[dict[str, str]] = []
    normalized = re.sub(r"(?<!\s)(https://)", r" \1", section)
    for label, description, url in SOURCE_RE.findall(normalized):
        if not url.startswith("https://"):
            raise BuildError(f"{relative}: source {label} must use an HTTPS URL")
        sources.append({"label": label, "description": _clean_text(description), "url": url})
    if not sources:
        raise BuildError(f"{relative}: sourceEvidence requires numbered HTTPS sources")
    return sources


def parse_document(path: Path, *, corpus_root: Path) -> dict[str, object]:
    """Parse one validated card or payment Markdown document into safe records."""
    relative = _relative(path, corpus_root)
    try:
        metadata, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise BuildError(f"{relative}: cannot parse document: {exc}") from exc
    sections: dict[str, dict[str, object]] = {}
    for title, key in SECTION_KEYS.items():
        content = _section(body, title, relative=relative)
        sections[key] = {"blocks": _blocks(content, relative=relative, section=title)}
    return {
        "metadata": metadata,
        "body": body,
        "sections": sections,
        "sources": _sources(_section(body, "來源證據", relative=relative), relative=relative),
    }


def _comparison(corpus_root: Path) -> tuple[list[dict[str, str]], dict[str, str], dict[str, str]]:
    relative = "comparison.md"
    text = (corpus_root / relative).read_text(encoding="utf-8")
    section = _section(text, "15 項產品總表", relative=relative)
    table_lines = [line for line in section.splitlines() if _split_row(line) is not None]
    headers, rows = parse_markdown_table("\n".join(table_lines), context=f"{relative}: 15 項產品總表")
    if headers != COMPARISON_HEADERS:
        raise BuildError(f"{relative}: comparison headers do not match the dataset contract")
    result: list[dict[str, str]] = []
    labels: dict[str, str] = {}
    footnotes: dict[str, str] = {}
    definitions: dict[str, tuple[str, str]] = {}
    for footnote, _, product_id in FOOTNOTE_DEFINITION_RE.findall(text):
        if footnote in definitions:
            raise BuildError(f"{relative}: duplicate comparison footnote {footnote}")
        definitions[footnote] = (f"cards/{product_id}.md", product_id)
    for index, row in enumerate(rows, start=1):
        product_cell = row[0]
        ids = PRODUCT_ID_RE.findall(product_cell)
        uses = FOOTNOTE_USE_RE.findall(product_cell)
        if len(ids) != 1 or len(uses) != 1:
            raise BuildError(f"{relative}: comparison row {index} requires one product-id and one footnote")
        product_id, footnote = ids[0], uses[0]
        definition = definitions.get(footnote)
        if definition != (f"cards/{product_id}.md", product_id):
            raise BuildError(f"{relative}: comparison footnote {footnote} does not map to {product_id}")
        if product_id in labels:
            raise BuildError(f"{relative}: duplicate comparison product-id {product_id}")
        label = _clean_text(FOOTNOTE_USE_RE.sub("", PRODUCT_ID_RE.sub("", product_cell)))
        labels[product_id] = label
        footnotes[footnote] = product_id
        record = {key: _clean_text(value) for key, value in zip(COMPARISON_KEYS, row, strict=True)}
        record["product"] = label
        record["productId"] = product_id
        result.append(record)
    return result, labels, footnotes


def _payment_rows(
    path: Path,
    *,
    corpus_root: Path,
    labels: dict[str, str],
) -> dict[str, object]:
    parsed = parse_document(path, corpus_root=corpus_root)
    relative = _relative(path, corpus_root)
    section = _section(str(parsed["body"]), "行動支付相容性", relative=relative)
    table_lines = [line for line in section.splitlines() if _split_row(line) is not None]
    headers, rows = parse_markdown_table("\n".join(table_lines), context=f"{relative}: 行動支付相容性")
    expected = ["使用者產品", "可綁／可連結", "支付方式", "原卡／帳戶回饋", "支付服務加碼", "可否疊加", "官方證據"]
    if headers != expected:
        raise BuildError(f"{relative}: payment matrix headers do not match the dataset contract")
    label_to_ids: dict[str, list[str]] = {}
    for product_id, label in labels.items():
        label_to_ids.setdefault(label, []).append(product_id)
    output_rows: list[dict[str, str]] = []
    used_ids: Counter[str] = Counter()
    for row in rows:
        product_name = _clean_text(row[0])
        matching = label_to_ids.get(product_name, [])
        if len(matching) != 1:
            state = "zero" if not matching else "multiple"
            raise BuildError(f"{relative}: payment product {product_name!r} has {state} comparison matches")
        product_id = matching[0]
        used_ids[product_id] += 1
        if used_ids[product_id] != 1:
            raise BuildError(f"{relative}: payment product {product_name!r} has duplicate matrix rows")
        output_rows.append(
            {
                "productId": product_id,
                "product": product_name,
                "supported": _clean_text(row[1]),
                "method": _clean_text(row[2]),
                "cardRewards": _clean_text(row[3]),
                "serviceBonus": _clean_text(row[4]),
                "stacking": _clean_text(row[5]),
                "sourceEvidence": _clean_text(row[6]),
            }
        )
    missing = [label for product_id, label in labels.items() if used_ids[product_id] != 1]
    if missing:
        raise BuildError(f"{relative}: payment matrix is missing products: {', '.join(missing)}")
    payment_id = PAYMENT_IDS[path.name]
    metadata = parsed["metadata"]
    return {
        "id": payment_id,
        "product": metadata["product"],
        "issuer": metadata["issuer"],
        "coverageStatus": metadata["coverage_status"],
        "rows": output_rows,
    }


def _aliases(*values: str) -> list[str]:
    aliases: list[str] = []
    for value in values:
        if value and value not in aliases:
            aliases.append(value)
        for parenthetical in re.findall(r"[（(]([^）)]+)[）)]", value):
            parenthetical = _clean_text(parenthetical)
            if parenthetical and parenthetical not in aliases:
                aliases.append(parenthetical)
        for token in re.findall(r"[A-Za-z][A-Za-z0-9+@!._-]*", value):
            if token not in aliases:
                aliases.append(token)
    return aliases


def _badges(*texts: str) -> list[str]:
    content = "\n".join(texts)
    checks = (
        ("partial", "partial" in content),
        ("registration", "登錄" in content),
        ("limited", any(value in content for value in ("限量", "名額", "額滿"))),
        ("derived", "推導" in content),
        ("non-guaranteed", "非保證" in content),
        ("conflict", "衝突" in content),
        ("unconfirmed", any(value in content for value in ("not officially confirmed", "未確認"))),
    )
    return [badge for badge, present in checks if present]


def _scenarios(
    corpus_root: Path,
    *,
    footnotes: dict[str, str],
    labels: dict[str, str],
) -> tuple[list[dict[str, object]], dict[str, set[str]]]:
    text = (corpus_root / "comparison.md").read_text(encoding="utf-8")
    section = _section(text, "情境選擇", relative="comparison.md")
    headings = list(re.finditer(r"(?m)^###\s+(.+?)\s*$", section))
    if not headings:
        raise BuildError("comparison.md: 情境選擇 requires scenario headings")
    scenarios: list[dict[str, object]] = []
    product_facets: dict[str, set[str]] = {product_id: set() for product_id in labels}
    for index, match in enumerate(headings, start=1):
        start = match.end()
        end = headings[index].start() if index < len(headings) else len(section)
        content = section[start:end].strip()
        entries: list[dict[str, object]] = []
        for block in _blocks(content, relative="comparison.md", section=f"scenario {match.group(1)}"):
            if block["type"] == "list":
                for item in block["items"]:
                    product_ids = [footnotes[footnote] for footnote in FOOTNOTE_USE_RE.findall(str(item)) if footnote in footnotes]
                    entries.append({"text": item, "productIds": product_ids})
            elif block["type"] == "paragraph":
                item = str(block["text"])
                product_ids = [footnotes[footnote] for footnote in FOOTNOTE_USE_RE.findall(item) if footnote in footnotes]
                entries.append({"text": item, "productIds": product_ids})
        title = _clean_text(match.group(1))
        for entry in entries:
            for product_id in entry["productIds"]:
                product_facets[product_id].update(SCENARIO_FACETS.get(title, ()))
        referenced = [product_id for entry in entries for product_id in entry["productIds"]]
        terms = [title]
        for product_id in referenced:
            for alias in _aliases(labels[product_id]):
                if alias not in terms:
                    terms.append(alias)
        scenarios.append(
            {
                "id": f"scenario-{index}",
                "title": title,
                "entries": entries,
                "searchTerms": terms,
            }
        )
    return scenarios, product_facets


def build_dataset(root: Path) -> dict[str, object]:
    """Build a fully deterministic dataset from the validated Phase 1 corpus."""
    root = Path(root)
    corpus_root = root / CORPUS_RELATIVE
    issues = validate_corpus(corpus_root)
    if issues:
        raise BuildError("\n".join(f"{issue.code}: {issue.path}: {issue.message}" for issue in issues))
    comparison, labels, footnotes = _comparison(corpus_root)
    payment_documents = [
        _payment_rows(corpus_root / "payments" / filename, corpus_root=corpus_root, labels=labels)
        for filename in PAYMENT_IDS
    ]
    scenarios, scenario_facets = _scenarios(corpus_root, footnotes=footnotes, labels=labels)
    payment_facets: dict[str, set[str]] = {product_id: set() for product_id in labels}
    for payment in payment_documents:
        for row in payment["rows"]:
            if str(row["supported"]).startswith("supported"):
                payment_facets[str(row["productId"])].add(str(payment["id"]))
    cards: list[dict[str, object]] = []
    coverage: Counter[str] = Counter()
    audit_dates: set[str] = set()
    target_from: set[str] = set()
    target_to: set[str] = set()
    for comparison_row in comparison:
        product_id = comparison_row["productId"]
        parsed = parse_document(corpus_root / "cards" / f"{product_id}.md", corpus_root=corpus_root)
        metadata = parsed["metadata"]
        coverage[str(metadata["coverage_status"])] += 1
        audit_dates.add(str(metadata["verified_at"]))
        target_from.add(str(metadata["target_from"]))
        target_to.add(str(metadata["target_to"]))
        facets = sorted(scenario_facets[str(product_id)] | payment_facets[str(product_id)])
        source_text = "\n".join(
            f"{source['description']} {source['url']}" for source in parsed["sources"]
        )
        card_text = "\n".join(
            block.get("text", "") if isinstance(block, dict) else ""
            for section in parsed["sections"].values()
            for block in section["blocks"]
        )
        cards.append(
            {
                "id": product_id,
                "product": labels[str(product_id)],
                "issuer": metadata["issuer"],
                "productType": metadata["product_type"],
                "coverageStatus": metadata["coverage_status"],
                "comparison": {key: value for key, value in comparison_row.items() if key not in {"product", "productId"}},
                "sections": parsed["sections"],
                "sources": parsed["sources"],
                "badges": _badges(str(metadata["coverage_status"]), source_text, card_text, *comparison_row.values()),
                "facetIds": facets,
                "searchAliases": _aliases(str(metadata["product"]), labels[str(product_id)], str(metadata["issuer"])),
            }
        )
    for payment in payment_documents:
        coverage[str(payment["coverageStatus"])] += 1
        parsed = parse_document(corpus_root / "payments" / f"{payment['id']}.md", corpus_root=corpus_root)
        metadata = parsed["metadata"]
        audit_dates.add(str(metadata["verified_at"]))
        target_from.add(str(metadata["target_from"]))
        target_to.add(str(metadata["target_to"]))
    expected_coverage = {"complete": 9, "partial": 9, "unavailable": 0}
    coverage_counts = {key: coverage[key] for key in expected_coverage}
    if coverage_counts != expected_coverage:
        raise BuildError(f"coverage baseline mismatch: expected {expected_coverage}; found {coverage_counts}")
    if len(target_from) != 1 or len(target_to) != 1:
        raise BuildError("corpus metadata must have one target window")
    return {
        "schemaVersion": "1",
        "auditDate": max(audit_dates),
        "targetFrom": next(iter(target_from)),
        "targetTo": next(iter(target_to)),
        "baselineCommit": BASELINE_COMMIT,
        "coverageCounts": coverage_counts,
        "cards": cards,
        "payments": payment_documents,
        "scenarios": scenarios,
    }


def serialize_dataset(dataset: dict[str, object]) -> str:
    return json.dumps(
        dataset,
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
        separators=(",", ": "),
    ) + "\n"


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
    payload = match.group(1)
    if re.search(r"</\s*script\s*>\s*<script\b", payload, flags=re.IGNORECASE):
        raise BuildError("marked block must contain exactly one card-rewards-data JSON script")
    if re.search(r"</\s*script\b", payload, flags=re.IGNORECASE):
        raise BuildError("marked block payload must not contain a raw closing script token")
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise BuildError("marked block must contain valid JSON") from exc
    return json.dumps(
        parsed,
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
        separators=(",", ": "),
    ) + "\n"


def replace_embedded_dataset(html_text: str, json_text: str) -> str:
    start, end = _marker_bounds(html_text)
    safe_json = json_text.replace("</", "<\\/")
    block = (
        "\n<script id=\"card-rewards-data\" type=\"application/json\">\n"
        + safe_json.rstrip("\n")
        + "\n</script>\n"
    )
    return html_text[:start] + block + html_text[end:]


def build_output(repo_root: Path, output_path: Path, *, check: bool) -> bool:
    expected = serialize_dataset(build_dataset(repo_root))
    try:
        template = output_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise BuildError(f"cannot read HTML template: {output_path}") from exc
    if check:
        if read_embedded_dataset(template) != expected:
            raise BuildError("embedded dataset drift")
        return True
    updated = replace_embedded_dataset(template, expected)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            newline="\n",
            dir=output_path.parent,
            prefix=f".{output_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary.write(updated)
            temporary_path = Path(temporary.name)
        temporary_path.replace(output_path)
    except OSError as exc:
        if temporary_path is not None:
            try:
                if temporary_path.exists():
                    temporary_path.unlink()
            except OSError:
                pass
        raise BuildError(f"cannot write HTML output: {output_path}") from exc
    finally:
        if temporary_path is not None:
            try:
                if temporary_path.exists():
                    temporary_path.unlink()
            except OSError as exc:
                raise BuildError(f"cannot clean temporary HTML output: {output_path}") from exc
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).parents[1])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    output_path = args.output or args.repo_root / "tool/card-rewards.html"
    try:
        build_output(args.repo_root, output_path, check=args.check)
    except BuildError as exc:
        print(f"card rewards build: {exc}", file=sys.stderr)
        return 1
    if args.check:
        print("card rewards tool: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
