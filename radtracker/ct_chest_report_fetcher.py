#!/usr/bin/env python3
"""Fetch chest CT report texts for the case numbers found by ct_chest_cases.py.

Reuses the generic report-fetch layer from mammo_report_fetcher (demo_diff.asp
+ #text2 scrape). Mammo-specific case selection is NOT used here; the case list
comes from ct_chest_<scope>_cases.json.

Must run on the hospital intranet. Output (contains report text / chart_no) goes
to output/ and is gitignored.

Usage:
  python ct_chest_report_fetcher.py --scope all --limit 3   # small test
  python ct_chest_report_fetcher.py --scope all             # full run
"""

import argparse
import json
import time
from datetime import datetime
from pathlib import Path

from mammo_report_fetcher import fetch_report, read_iuser, REPORTER

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
FETCH_INTERVAL = 1.0


def cases_path(scope: str) -> Path:
    return OUTPUT_DIR / f"ct_chest_{scope}_cases.json"


def reports_path(scope: str) -> Path:
    return OUTPUT_DIR / f"ct_chest_{scope}_reports.json"


def _load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def run(scope: str, limit: int | None, reporter: str) -> dict:
    case_data = _load_json(cases_path(scope), None)
    if case_data is None:
        raise SystemExit(f"missing {cases_path(scope)} — run ct_chest_cases.py first")

    existing = _load_json(reports_path(scope), {"reports": []})
    report_map = {r["case_id"]: r for r in existing.get("reports", []) if r.get("case_id")}
    iuser = read_iuser(reporter)

    todo = [c for c in case_data["cases"]
            if report_map.get(c["case_id"], {}).get("status") != "fetched"]
    if limit:
        todo = todo[:limit]
    print(f"fetching {len(todo)} report(s) (iuser={iuser[:3]}***)...")

    for i, case in enumerate(todo, 1):
        cid = case["case_id"]
        fetched = fetch_report(cid, iuser)
        report_map[cid] = {
            "case_id": cid,
            "chart_no": case.get("chart_no", ""),
            "report_date": case.get("report_date"),
            "contrast": case.get("contrast"),
            "status": fetched["status"],
            "report_text": fetched["report_text"],
            "error": fetched["error"],
        }
        ok = fetched["status"] == "fetched"
        print(f"  [{i}/{len(todo)}] {cid} {'OK' if ok else 'FAIL: ' + str(fetched['error'])}")
        time.sleep(FETCH_INTERVAL)

    reports = list(report_map.values())
    data = {
        "scope": scope,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "total_fetched": sum(1 for r in reports if r["status"] == "fetched"),
        "total_failed": sum(1 for r in reports if r["status"] == "fetch_failed"),
        "reports": reports,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    reports_path(scope).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"fetched={data['total_fetched']} failed={data['total_failed']} -> {reports_path(scope)}")
    return data


def main() -> None:
    ap = argparse.ArgumentParser(description="Fetch chest CT report texts.")
    ap.add_argument("--scope", default="all")
    ap.add_argument("--limit", type=int, default=None, help="fetch at most N new reports (test)")
    ap.add_argument("--reporter", default=REPORTER)
    args = ap.parse_args()
    run(args.scope, args.limit, args.reporter)


if __name__ == "__main__":
    main()
