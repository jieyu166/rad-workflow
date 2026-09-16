#!/usr/bin/env python3
"""Extract 國健 LDCT (order_code 33904-*) case numbers from hospital CSV exports.

33904-8 is the 國健署 lung-cancer-screening LDCT order; 33904-3 is the other
LDCT variant. Default selects 33904-8 only.

Output: output/ldct_<scope>_cases.json  (gitignored — contains chart_no).
Feed it to ldct_report_fetcher.py.

Usage:
  python ldct_cases.py                       # 33904-8, all CSVs
  python ldct_cases.py --order 33904-3
  python ldct_cases.py --order any           # every 33904-*
"""

import argparse
import csv
import glob
import io
import json
import os
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
REPORTER = "A80748"


def extract(csv_dir: str, reporter: str, order: str) -> dict:
    pats = [os.path.join(csv_dir, p) for p in ("115*_CL*.csv", "115*_YK*.csv", "2026*.csv")]
    files = sorted({f for pat in pats for f in glob.glob(pat) if "_attr" not in f})

    cases: dict[str, dict] = {}
    for f in files:
        for r in csv.reader(io.open(f, encoding="cp950", errors="replace"), delimiter="\t"):
            if len(r) < 25 or r[17] != reporter:
                continue
            code = (r[6] or "").strip()
            if not code.startswith("33904"):
                continue
            if order != "any" and code != order:
                continue
            cid = r[0]
            if cid in cases:
                cases[cid]["orders"].append(code)
                continue
            cases[cid] = {
                "case_id": cid,
                "chart_no": r[1],
                "exec_date": r[11] or None,
                "report_date": r[13] or None,
                "exam": r[8],
                "orders": [code],
            }

    for c in cases.values():
        c["orders"] = sorted(set(c["orders"]))

    def key(c):
        try:
            return datetime.strptime(c["exec_date"], "%m/%d/%Y")
        except (TypeError, ValueError):
            return datetime(1900, 1, 1)

    ordered = sorted(cases.values(), key=key)
    return {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "reporter": reporter,
        "order_filter": order,
        "source_files": len(files),
        "total": len(ordered),
        "cases": ordered,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Extract 國健 LDCT case numbers.")
    ap.add_argument("--csv-dir", default=str(BASE_DIR / "csv_input"))
    ap.add_argument("--reporter", default=REPORTER)
    ap.add_argument("--order", default="33904-8",
                    help="33904-8 (default) / 33904-3 / any")
    ap.add_argument("--scope", default=None, help="output filename label")
    args = ap.parse_args()

    data = extract(args.csv_dir, args.reporter, args.order)
    scope = args.scope or args.order.replace("-", "_")
    OUTPUT_DIR.mkdir(exist_ok=True)
    out = OUTPUT_DIR / f"ldct_{scope}_cases.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    months: dict[str, int] = {}
    for c in data["cases"]:
        if c["exec_date"]:
            try:
                d = datetime.strptime(c["exec_date"], "%m/%d/%Y")
                months[f"{d.year}-{d.month:02d}"] = months.get(f"{d.year}-{d.month:02d}", 0) + 1
            except ValueError:
                pass
    print(f"LDCT cases (order {args.order}, reporter {data['reporter']}): {data['total']}")
    for k in sorted(months):
        print(f"  {k}  {months[k]}")
    print(f"Saved -> {out}")


if __name__ == "__main__":
    main()
