#!/usr/bin/env python3
"""Extract chest CT (CT-Chest) case numbers from hospital CSV exports.

Groups rows by case_id (檢查單號) for the given reporter, keeps only studies
whose exam list contains "CT-Chest" (excludes CT-Biopsy Chest), and flags
contrast vs non-contrast from the order codes.

Output: output/ct_chest_<scope>_cases.json  (gitignored — contains chart_no).
Reuses biopsy_tracker._load_all_cases for the CP950/tab parsing + grouping.
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

from biopsy_tracker import _load_all_cases, REPORTER

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"

# order code prefixes that indicate IV contrast enhancement for chest CT
CONTRAST_PREFIXES = ("33072", "33090")
# CT-Biopsy uses this order; such cases are NOT diagnostic chest CT
BIOPSY_ORDER = "33103-1"


def _has_contrast(orders: set) -> bool:
    return any(o.startswith(CONTRAST_PREFIXES) for o in orders)


def extract(csv_dir: str, reporter: str) -> dict:
    all_cases = _load_all_cases(csv_dir, reporter)
    rows = []
    for case_id, c in all_cases.items():
        if "CT-Chest" not in c["exams"]:
            continue
        if BIOPSY_ORDER in c["orders"]:
            continue  # CT-Biopsy, not a diagnostic chest CT
        rows.append({
            "case_id": case_id,
            "chart_no": c["chart_no"],
            "report_date": c["report_date"].strftime("%Y-%m-%d") if c["report_date"] else None,
            "contrast": _has_contrast(c["orders"]),
            "combined_with": sorted(e for e in c["exams"] if e != "CT-Chest"),
            "orders": sorted(c["orders"]),
        })
    rows.sort(key=lambda r: (r["report_date"] or "", r["case_id"]))
    n_contrast = sum(1 for r in rows if r["contrast"])
    return {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "reporter": reporter,
        "total": len(rows),
        "contrast": n_contrast,
        "noncontrast": len(rows) - n_contrast,
        "cases": rows,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Extract chest CT case numbers from CSV.")
    ap.add_argument("--csv-dir", default=str(BASE_DIR / "csv_input"))
    ap.add_argument("--reporter", default=REPORTER)
    ap.add_argument("--scope", default="all", help="label for the output filename")
    args = ap.parse_args()

    data = extract(args.csv_dir, args.reporter)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUTPUT_DIR / f"ct_chest_{args.scope}_cases.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"CT-Chest cases (reporter {data['reporter']}): {data['total']}")
    print(f"  contrast    : {data['contrast']}")
    print(f"  non-contrast: {data['noncontrast']}")
    print(f"  -> {out}")
    print("  sample (first 5 case_id | date | contrast):")
    for r in data["cases"][:5]:
        print(f"    {r['case_id']:<18} {r['report_date'] or '?':<12} "
              f"{'contrast' if r['contrast'] else 'non-contrast'}")


if __name__ == "__main__":
    main()
