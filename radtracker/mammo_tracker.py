#!/usr/bin/env python3
"""Monthly mammography BI-RADS 0 quality tracker."""

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path

from biopsy_tracker import ENCODING, _load_all_cases, _parse_date

MAMMO_FOLLOWUP_ORDER = "91"
REPORTER = "A80748"

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
BIRADS0_PATH = OUTPUT_DIR / "mammo_birads0.json"


def cases_path(month_str: str) -> Path:
    return OUTPUT_DIR / f"mammo_{month_str.replace('-', '')}_cases.json"


def reports_path(month_str: str) -> Path:
    return OUTPUT_DIR / f"mammo_{month_str.replace('-', '')}_reports.json"


def _format_date(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")
    parsed = _parse_date(str(value))
    return parsed.strftime("%Y-%m-%d") if parsed else None


def _is_mammo_case(case: dict, month_str: str) -> bool:
    report_date = case.get("report_date")
    if report_date is None or report_date.strftime("%Y-%m") != month_str:
        return False
    if MAMMO_FOLLOWUP_ORDER not in case.get("orders", set()):
        return False
    exams = " ".join(case.get("exams", set())).lower()
    return "mammography" in exams


def _load_order_dates(csv_dir: str, reporter: str) -> dict[str, str]:
    order_dates = {}
    for fp in sorted(Path(csv_dir).glob("*.csv")):
        if "legacy" in fp.name.lower():
            continue
        try:
            with fp.open(encoding=ENCODING, errors="replace") as f:
                reader = csv.reader(f, delimiter="\t")
                for row in reader:
                    if len(row) < 18 or row[17].strip() != reporter:
                        continue
                    parsed = _parse_date(row[3])
                    if parsed is None:
                        continue
                    case_id = row[0].strip()
                    formatted = parsed.strftime("%Y-%m-%d")
                    current = order_dates.get(case_id)
                    if current is None or formatted < current:
                        order_dates[case_id] = formatted
        except Exception:
            continue
    return order_dates


def get_mammo_cases(csv_dir: str, month_str: str, reporter: str = REPORTER) -> dict:
    all_cases = _load_all_cases(csv_dir, reporter)
    order_dates = _load_order_dates(csv_dir, reporter)
    entries = []
    seen_case_ids = set()

    for case_id, case in sorted(all_cases.items()):
        if case_id in seen_case_ids or not _is_mammo_case(case, month_str):
            continue
        seen_case_ids.add(case_id)
        report_date = _format_date(case.get("report_date"))
        entries.append({
            "case_id": case.get("case_id") or case_id,
            "chart_no": case.get("chart_no", ""),
            "report_date": report_date,
            "order_date": order_dates.get(case_id, report_date),
            "work_points": float(case.get("pts_total", 0.0)),
        })

    result = {
        "month": month_str,
        "generated": datetime.now().isoformat(),
        "reporter": reporter,
        "total_cases": len(entries),
        "cases": entries,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    cases_path(month_str).write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return result


def _load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def calculate_metrics(month_str: str) -> dict:
    cases_data = _load_json(cases_path(month_str), {"total_cases": 0, "cases": []})
    reports_file = reports_path(month_str)
    reports_data = _load_json(reports_file, None)
    tracker_data = _load_json(BIRADS0_PATH, {"cases": []})

    total_cases = int(cases_data.get("total_cases", len(cases_data.get("cases", []))))
    if reports_data is None or reports_data.get("total_fetched", 0) == 0:
        birads0_count = None
        recall_rate = None
    else:
        reports = reports_data.get("reports", [])
        birads0_count = sum(1 for item in reports if item.get("birads_category") == 0)
        recall_rate = (birads0_count / total_cases * 100.0) if total_cases else 0.0

    resolved_outcomes = {"benign", "malignant", "inadequate", "lost_to_followup"}
    month_cases = [
        item for item in tracker_data.get("cases", [])
        if item.get("recall_month") == month_str
    ]
    resolved = [
        item for item in month_cases
        if item.get("outcome") in resolved_outcomes
    ]
    malignant_count = sum(1 for item in resolved if item.get("outcome") == "malignant")
    pending_count = len(month_cases) - len(resolved)
    ppv1 = (malignant_count / len(resolved) * 100.0) if resolved else None

    return {
        "month": month_str,
        "total_cases": total_cases,
        "birads0_count": birads0_count,
        "recall_rate": recall_rate,
        "resolved_count": len(resolved),
        "malignant_count": malignant_count,
        "ppv1": ppv1,
        "pending_count": pending_count,
        "generated": datetime.now().isoformat(),
    }


def print_metrics(metrics: dict) -> None:
    print(f"Month: {metrics['month']}")
    print(f"Total cases: {metrics['total_cases']}")
    if metrics["recall_rate"] is None:
        print("BI-RADS 0 recall count: N/A (no reports fetched)")
        print("Recall rate: N/A (no reports fetched)")
    else:
        print(f"BI-RADS 0 recall count: {metrics['birads0_count']}")
        print(f"Recall rate: {metrics['recall_rate']:.1f}%")
    print(f"Resolved count: {metrics['resolved_count']}")
    print(f"Malignant count: {metrics['malignant_count']}")
    if metrics["ppv1"] is None:
        print("PPV1: N/A")
    else:
        print(f"PPV1: {metrics['ppv1']:.1f}%")
    print(f"Pending count: {metrics['pending_count']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan monthly mammography cases.")
    parser.add_argument("--month", required=True, help="Month in YYYY-MM format")
    parser.add_argument("--csv-dir", default=str(BASE_DIR / "csv_input"))
    parser.add_argument("--reporter", default=REPORTER)
    parser.add_argument("--stats", action="store_true")
    parser.add_argument("--output", help="Optional metrics JSON output path")
    args = parser.parse_args()

    if args.stats:
        metrics = calculate_metrics(args.month)
        print_metrics(metrics)
        if args.output:
            out_path = Path(args.output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(
                json.dumps(metrics, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        return

    result = get_mammo_cases(args.csv_dir, args.month, args.reporter)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
