"""Validate the structure and provenance contract for the 2026 H2 card corpus."""

from __future__ import annotations

import argparse
import json
import posixpath
import re
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

EXPECTED_CARD_FILES = {
    "cards/first-ileo.md",
    "cards/first-green.md",
    "cards/taishin-richart-gogo.md",
    "cards/sinopac-dawho.md",
    "cards/sinopac-coin.md",
    "cards/sinopac-daway.md",
    "cards/cathay-cube.md",
    "cards/ctbc-line-pay.md",
    "cards/rakuten-bank-card.md",
    "cards/obank-debit.md",
    "cards/line-bank-debit.md",
    "cards/esun-pi.md",
    "cards/esun-unicard.md",
    "cards/esun-ubear.md",
    "cards/fubon-costco.md",
}
EXPECTED_PAYMENT_FILES = {
    "payments/line-pay.md",
    "payments/ipass-money.md",
    "payments/px-pay.md",
}
EXPECTED_CARD_IDS = {Path(relative).stem for relative in EXPECTED_CARD_FILES}
REQUIRED_METADATA = {
    "product",
    "issuer",
    "product_type",
    "customer_scope",
    "target_from",
    "target_to",
    "verified_at",
    "coverage_status",
}
REQUIRED_HEADINGS = (
    "## 結論摘要",
    "## 一般回饋",
    "## 特殊回饋",
    "## 行動支付相容性",
    "## 排除交易",
    "## 來源證據",
    "## 不確定事項",
)
ALLOWED_PRODUCT_TYPES = {"credit", "debit", "atm", "payment"}
ALLOWED_COVERAGE = {"complete", "partial", "unavailable"}
OFFICIAL_HOST_SUFFIXES = (
    "firstbank.com.tw",
    "taishinbank.com.tw",
    "bank.sinopac.com",
    "cathaybk.com.tw",
    "ctbcbank.com",
    "ctbcbank.com.tw",
    "rakuten-bank.com.tw",
    "o-bank.com",
    "linebank.com.tw",
    "esunbank.com",
    "fubon.com",
    "linepay.com",
    "line.me",
    "i-pass.com.tw",
    "ipassmoney.com.tw",
    "pxpayplus.com",
)

_KEY_VALUE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):(?:[ \t]*)(.*)$")
_URL = re.compile(r"https?://[^\s<>\)\]]+")
_PARTIAL_GAP = re.compile(
    r"未覆蓋期間：\d{4}-\d{2}-\d{2} 至 \d{4}-\d{2}-\d{2}"
)
_PERCENTAGE = re.compile(r"(?<!\d)\d+(?:\.\d+)?\s*[%％]")
_PRODUCT_ID_COMMENT = re.compile(
    r"<!--\s*product-id:\s*([a-z0-9][a-z0-9-]*)\s*-->"
)
_FOOTNOTE_REF = re.compile(r"\[\^([A-Za-z0-9_-]+)\]")
_FOOTNOTE_DEFINITION = re.compile(
    r"(?m)^\[\^([A-Za-z0-9_-]+)\]:\s*\[[^\]\n]*\]\(([^)\n]+)\)\s*$"
)


@dataclass(frozen=True)
class Issue:
    code: str
    path: str
    message: str


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Parse the contract's deliberately small, single-line YAML subset."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise ValueError("frontmatter must start with ---")
    end = next((i for i, line in enumerate(lines[1:], 1) if line.strip() == "---"), None)
    if end is None:
        raise ValueError("frontmatter closing --- is missing")
    metadata: dict[str, str] = {}
    for line in lines[1:end]:
        raw = line.rstrip("\r\n")
        match = _KEY_VALUE.match(raw)
        if not match or not match.group(2).strip():
            raise ValueError(f"invalid frontmatter line: {raw!r}")
        key, value = match.groups()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if any(char in value for char in "[]{}"):
            raise ValueError(f"only scalar frontmatter values are supported: {key}")
        metadata[key] = value
    return metadata, "".join(lines[end + 1 :])


def _official_url(url: str) -> bool:
    parsed = urlsplit(url)
    host = (parsed.hostname or "").lower().rstrip(".")
    return parsed.scheme in {"http", "https"} and any(
        host == suffix or host.endswith("." + suffix) for suffix in OFFICIAL_HOST_SUFFIXES
    )


def _section_body(body: str, heading: str) -> str:
    """Return one level-two section, excluding its heading."""
    match = re.search(
        rf"(?ms)^\s*{re.escape(heading)}\s*$\n?(.*?)(?=^##\s|\Z)",
        body,
    )
    return match.group(1).strip() if match else ""


def _issue(code: str, path: str, message: str) -> Issue:
    return Issue(code=code, path=path, message=message)


def _split_markdown_row(line: str) -> list[str] | None:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return None
    return [cell.strip() for cell in stripped[1:-1].split("|")]


def _comparison_table_rows(text: str) -> list[list[str]]:
    section = _section_body(text, "## 15 項產品總表")
    lines = section.splitlines()
    table_start = next(
        (index for index, line in enumerate(lines) if _split_markdown_row(line) is not None),
        None,
    )
    if table_start is None or table_start + 1 >= len(lines):
        return []
    rows: list[list[str]] = []
    for line in lines[table_start + 2 :]:
        cells = _split_markdown_row(line)
        if cells is None:
            if rows:
                break
            continue
        rows.append(cells)
    return rows


def _payment_matrix_rows(body: str) -> list[list[str]]:
    section = _section_body(body, "## 行動支付相容性")
    lines = section.splitlines()
    table_start = next(
        (index for index, line in enumerate(lines) if _split_markdown_row(line) is not None),
        None,
    )
    if table_start is None or table_start + 1 >= len(lines):
        return []
    rows: list[list[str]] = []
    for line in lines[table_start + 2 :]:
        cells = _split_markdown_row(line)
        if cells is None:
            if rows:
                break
            continue
        rows.append(cells)
    return rows


def _validate_comparison(text: str) -> list[Issue]:
    relative = "comparison.md"
    issues: list[Issue] = []
    rows = _comparison_table_rows(text)
    if len(rows) != 15:
        issues.append(
            _issue(
                "comparison_row_count",
                relative,
                f"15 項產品總表 must contain exactly 15 data rows; found {len(rows)}",
            )
        )

    definitions: dict[str, list[str]] = defaultdict(list)
    for footnote_id, target in _FOOTNOTE_DEFINITION.findall(text):
        definitions[footnote_id].append(target)

    bound_ids: list[str] = []
    footnote_uses: Counter[str] = Counter()
    for row_number, cells in enumerate(rows, start=1):
        if len(cells) != 10:
            issues.append(
                _issue(
                    "comparison_column_count",
                    relative,
                    f"data row {row_number} must contain exactly 10 columns; found {len(cells)}",
                )
            )
        product_cell = cells[0] if cells else ""
        row_ids = _PRODUCT_ID_COMMENT.findall(product_cell)
        bound_ids.extend(row_ids)
        if len(row_ids) != 1:
            issues.append(
                _issue(
                    "comparison_row_product_id",
                    relative,
                    f"data row {row_number} product cell must contain exactly one product-id; found {len(row_ids)}",
                )
            )
            continue
        product_id = row_ids[0]
        if product_id not in EXPECTED_CARD_IDS:
            issues.append(
                _issue(
                    "comparison_unknown_product",
                    relative,
                    f"data row {row_number} contains unknown product-id {product_id}",
                )
            )
            continue

        footnote_refs = _FOOTNOTE_REF.findall(product_cell)
        if len(footnote_refs) != 1:
            issues.append(
                _issue(
                    "comparison_footnote_mismatch",
                    relative,
                    f"product-id {product_id} must have exactly one product footnote; found {len(footnote_refs)}",
                )
            )
            continue
        footnote_id = footnote_refs[0]
        footnote_uses[footnote_id] += 1
        expected_target = f"cards/{product_id}.md"
        targets = definitions.get(footnote_id, [])
        if targets != [expected_target]:
            issues.append(
                _issue(
                    "comparison_footnote_mismatch",
                    relative,
                    f"product-id {product_id} footnote {footnote_id} must uniquely target {expected_target}",
                )
            )

    for footnote_id, count in sorted(footnote_uses.items()):
        if count != 1:
            issues.append(
                _issue(
                    "comparison_footnote_mismatch",
                    relative,
                    f"product footnote {footnote_id} must be used by exactly one data row; found {count}",
                )
            )

    bound_counts = Counter(bound_ids)
    for product_id in sorted(EXPECTED_CARD_IDS):
        count = bound_counts[product_id]
        if count != 1:
            issues.append(
                _issue(
                    "comparison_missing_product",
                    relative,
                    f"product-id {product_id} must appear in exactly one product cell; found {count}",
                )
            )
        if count > 1:
            issues.append(
                _issue(
                    "comparison_duplicate_product",
                    relative,
                    f"product-id {product_id} appears in {count} data rows",
                )
            )

    all_counts = Counter(_PRODUCT_ID_COMMENT.findall(text))
    for product_id in sorted(all_counts):
        detached_count = all_counts[product_id] - bound_counts[product_id]
        if detached_count > 0:
            issues.append(
                _issue(
                    "comparison_detached_product",
                    relative,
                    f"product-id {product_id} appears {detached_count} time(s) outside a product cell",
                )
            )
        if product_id not in EXPECTED_CARD_IDS and bound_counts[product_id] == 0:
            issues.append(
                _issue(
                    "comparison_unknown_product",
                    relative,
                    f"unknown product-id {product_id}",
                )
            )
    return issues


def _validate_document(root: Path, relative: str) -> list[Issue]:
    path = root / relative
    issues: list[Issue] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return [_issue("unreadable", relative, str(exc))]
    try:
        metadata, body = parse_frontmatter(text)
    except ValueError as exc:
        return [_issue("frontmatter", relative, str(exc))]
    missing = sorted(REQUIRED_METADATA - metadata.keys())
    if missing:
        issues.append(_issue("missing_metadata", relative, ", ".join(missing)))
    if metadata.get("product_type") not in ALLOWED_PRODUCT_TYPES:
        issues.append(_issue("invalid_enum", relative, "product_type must be credit, debit, atm, or payment"))
    if metadata.get("coverage_status") not in ALLOWED_COVERAGE:
        issues.append(_issue("invalid_enum", relative, "coverage_status must be complete, partial, or unavailable"))
    if metadata.get("customer_scope") != "existing":
        issues.append(_issue("wrong_scope", relative, "customer_scope must be existing"))
    for key in ("target_from", "target_to", "verified_at"):
        value = metadata.get(key)
        try:
            if value is None or date.fromisoformat(value).isoformat() != value:
                raise ValueError
        except ValueError:
            issues.append(_issue("invalid_date", relative, f"{key} must be YYYY-MM-DD"))
    if metadata.get("target_from") != "2026-08-01" or metadata.get("target_to") != "2026-12-31":
        issues.append(_issue("wrong_scope", relative, "target window must be 2026-08-01 through 2026-12-31"))
    for heading in REQUIRED_HEADINGS:
        if not re.search(rf"(?m)^{re.escape(heading)}\s*$", body):
            issues.append(_issue("missing_heading", relative, heading))
    if relative in EXPECTED_PAYMENT_FILES:
        payment_rows = _payment_matrix_rows(body)
        if len(payment_rows) != 15:
            issues.append(
                _issue(
                    "payment_matrix_row_count",
                    relative,
                    "行動支付相容性 must contain exactly 15 product rows; "
                    f"found {len(payment_rows)}",
                )
            )
    source_body = _section_body(body, "## 來源證據")
    coverage = metadata.get("coverage_status")
    if coverage == "partial" and not _PARTIAL_GAP.search(body):
        issues.append(
            _issue(
                "partial_without_gap",
                relative,
                "partial coverage requires 未覆蓋期間：YYYY-MM-DD 至 YYYY-MM-DD",
            )
        )
    conclusion_body = _section_body(body, "## 結論摘要")
    if coverage == "unavailable" and _PERCENTAGE.search(conclusion_body):
        issues.append(
            _issue(
                "unavailable_numeric_claim",
                relative,
                "unavailable documents cannot recommend a percentage in 結論摘要",
            )
        )
    urls = _URL.findall(source_body)
    if not any(_official_url(url.rstrip(".,;")) for url in urls):
        uncertainty_body = _section_body(body, "## 不確定事項")
        has_query_scope = bool(re.search(r"(?m)^\s*查詢範圍：\s*\S.+$", source_body))
        has_concrete_uncertainty = bool(
            uncertainty_body
            and uncertainty_body.strip() not in {"無", "無。", "N/A", "待確認", "待確認。"}
        )
        unavailable = (
            metadata.get("coverage_status") == "unavailable"
            and has_query_scope
            and has_concrete_uncertainty
        )
        if not unavailable:
            issues.append(
                _issue(
                    "missing_official_url",
                    relative,
                    "an official URL is required in 來源證據; unavailable requires 查詢範圍 and concrete 不確定事項",
                )
            )
    return issues


def validate_document(path: Path, root: Path) -> list[Issue]:
    """Validate one document addressed by an absolute or root-relative path."""
    root = Path(root).resolve()
    document = Path(path)
    if not document.is_absolute():
        document = root / document
    document = document.resolve()
    try:
        relative = document.relative_to(root).as_posix()
    except ValueError:
        return [_issue("unreadable", document.as_posix(), "document is outside corpus root")]
    expected = EXPECTED_CARD_FILES | EXPECTED_PAYMENT_FILES
    if relative not in expected:
        return [_issue("unreadable", relative, "document is not an expected product or payment path")]
    if not document.is_file():
        return [_issue("missing_file", relative, "expected product document is missing")]
    return _validate_document(root, relative)


def validate_corpus(root: Path, only: set[str] | None = None) -> list[Issue]:
    """Return deterministic structural issues for the expected corpus."""
    root = Path(root)
    issues: list[Issue] = []
    expected = (
        EXPECTED_CARD_FILES | EXPECTED_PAYMENT_FILES
        if only is None
        else {relative.replace("\\", "/") for relative in only}
    )
    for relative in sorted(expected):
        issues.extend(validate_document(Path(relative), root))
    if only is not None:
        return issues
    comparison_text = ""
    comparison = root / "comparison.md"
    if comparison.is_file():
        try:
            comparison_text = comparison.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            issues.append(_issue("unreadable", "comparison.md", str(exc)))
    issues.extend(_validate_comparison(comparison_text))
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("docs/card-rewards/2026-h2"))
    parser.add_argument("--json-report", type=Path)
    parser.add_argument("--only", help="comma-separated expected product/payment paths")
    args = parser.parse_args(argv)
    if not args.root.is_dir():
        parser.error(f"--root must be an existing readable directory: {args.root}")
    try:
        next(args.root.iterdir(), None)
    except OSError as exc:
        parser.error(f"--root is not readable: {exc}")
    only: set[str] | None = None
    if args.only is not None:
        raw_items = args.only.split(",")
        if any(not item.strip() for item in raw_items):
            parser.error("--only cannot contain empty paths")
        expected = EXPECTED_CARD_FILES | EXPECTED_PAYMENT_FILES
        only = set()
        for item in raw_items:
            normalized = item.strip().replace("\\", "/")
            if any(part == ".." for part in normalized.split("/")):
                parser.error(f"--only path escapes corpus root: {item}")
            normalized = posixpath.normpath(normalized)
            if normalized.startswith("/") or normalized not in expected:
                parser.error(f"--only path is not an expected product/payment file: {item}")
            only.add(normalized)
    issues = validate_corpus(args.root, only)
    report = {"root": str(args.root), "issue_count": len(issues), "issues": [asdict(issue) for issue in issues]}
    if args.json_report:
        args.json_report.parent.mkdir(parents=True, exist_ok=True)
        args.json_report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for issue in issues:
        print(f"{issue.code}: {issue.path}: {issue.message}")
    if not issues:
        print("card rewards corpus: OK")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
