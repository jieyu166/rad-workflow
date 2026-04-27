#!/usr/bin/env python3
"""Biopsy/FNA and selected interventional procedure tracker.

This module provides shared CSV parsing helpers used by other radtracker tools:

- `_parse_date()`
- `_load_all_cases()`

It also exposes `get_biopsy_summary()` for weekly biopsy/FNA follow-up reminders.
Hospital CSV exports are CP950 encoded tab-separated files.
"""

import csv
import glob
import json
import os
from collections import defaultdict
from datetime import datetime, timedelta

REPORTER = "A80748"
ENCODING = "cp950"

BIOPSY_DEFS = [
    {
        "label": "Thyroid FNA",
        "orders": {"29011-1", "19007-12"},
        "require_all": True,
        "exam_contains": None,
        "followup_days": 7,
        "color": "cyan",
    },
    {
        "label": "US-Neck FNA",
        "orders": {"19007-12"},
        "require_all": False,
        "exam_contains": "Neck",
        "followup_days": 7,
        "color": "cyan",
    },
    {
        "label": "Breast CNB",
        "orders": {"19007-1", "29035-1"},
        "require_all": True,
        "exam_contains": "Breast",
        "followup_days": 7,
        "color": "pink",
    },
    {
        "label": "Mammo Stereotactic Bx",
        "orders": {"33125"},
        "require_all": False,
        "exam_contains": None,
        "followup_days": 7,
        "color": "pink",
    },
    {
        "label": "CT-Biopsy",
        "orders": {"33103-1"},
        "require_all": False,
        "exam_contains": None,
        "followup_days": 7,
        "color": "orange",
    },
]

INTERVENTIONAL_ORDERS = {
    "33026-X": "Drainage/Puncture",
    "33095": "PCN Revision",
    "33106": "P.T.G.B.D.",
    "33063": "Arthrography",
    "33096": "Swallowing Video",
    "33029": "H.S.G.",
}


def _parse_date(s: str):
    """Parse common hospital date formats, returning datetime or None."""
    for fmt in ("%m/%d/%Y", "%Y/%m/%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(s.strip(), fmt)
        except (AttributeError, ValueError):
            continue
    return None


def _week_range(week_str: str):
    """Return (Monday, Sunday) for an ISO week string like '2026-W17'."""
    year, wk = int(week_str[:4]), int(week_str[6:])
    monday = datetime.fromisocalendar(year, wk, 1)
    sunday = monday + timedelta(days=6)
    return monday, sunday


def _load_all_cases(csv_dir: str, reporter: str) -> dict:
    """Scan CSV files and group rows by case_id for the given reporter.

    Returns a dict keyed by case_id. Each case contains:
    case_id, chart_no, report_date, orders, exams, pts_total, seen_files.
    Files whose names contain "legacy" are skipped.
    """
    cases = defaultdict(lambda: {
        "case_id": "",
        "chart_no": "",
        "report_date": None,
        "orders": set(),
        "exams": set(),
        "pts_total": 0.0,
        "seen_files": set(),
    })

    csv_files = sorted(glob.glob(os.path.join(csv_dir, "*.csv")))
    for fp in csv_files:
        fname = os.path.basename(fp)
        if "legacy" in fname.lower():
            continue
        try:
            with open(fp, encoding=ENCODING, errors="replace") as f:
                reader = csv.reader(f, delimiter="\t")
                for row in reader:
                    if len(row) < 29:
                        continue
                    if row[17].strip() != reporter:
                        continue

                    case_id = row[0].strip()
                    if not case_id:
                        continue
                    chart_no = row[1].strip()
                    order = row[6].strip()
                    exam = row[8].strip()
                    rdate = _parse_date(row[13])
                    try:
                        pts = float(row[24].strip() or 0)
                    except ValueError:
                        pts = 0.0

                    case = cases[case_id]
                    case["case_id"] = case_id
                    case["chart_no"] = chart_no
                    case["orders"].add(order)
                    case["exams"].add(exam)
                    case["pts_total"] += pts
                    case["seen_files"].add(fname)
                    if rdate and (case["report_date"] is None or rdate < case["report_date"]):
                        case["report_date"] = rdate
        except Exception:
            continue

    return dict(cases)


def _classify_case(case: dict):
    """Return the first matching biopsy definition, or None."""
    orders = case["orders"]
    exams = " ".join(case["exams"])

    for defn in BIOPSY_DEFS:
        required = defn["orders"]
        exam_kw = defn.get("exam_contains")

        if defn["require_all"]:
            if not required.issubset(orders):
                continue
        elif not (required & orders):
            continue

        if exam_kw and exam_kw.lower() not in exams.lower():
            continue

        return defn
    return None


def _is_interventional(case: dict):
    """Return (order, label) for selected interventional procedures, or None."""
    for order, label in INTERVENTIONAL_ORDERS.items():
        if order in case["orders"]:
            return order, label
    return None


def get_biopsy_summary(csv_dir: str, week_str: str, reporter: str = REPORTER) -> dict:
    """Return biopsy/FNA and selected interventional procedure summary.

    `biopsy_this_week` contains procedures performed this week.
    `biopsy_due_now` contains procedures performed the previous week whose
    follow-up is due this week.
    """
    week_mon, week_sun = _week_range(week_str)
    prev_mon = week_mon - timedelta(days=7)
    prev_sun = week_sun - timedelta(days=7)

    all_cases = _load_all_cases(csv_dir, reporter)
    biopsy_this_week = []
    biopsy_due_now = []
    interventional = []
    seen_keys = set()

    for case_id, case in all_cases.items():
        rdate = case["report_date"]
        if rdate is None:
            continue

        defn = _classify_case(case)
        if defn:
            followup_date = rdate + timedelta(days=defn["followup_days"])
            dedup_key = (case["chart_no"], rdate.strftime("%Y-%m-%d"), defn["label"])
            record = {
                "label": defn["label"],
                "color": defn["color"],
                "chart_no": case["chart_no"],
                "case_id": case_id,
                "procedure_date": rdate.strftime("%m/%d"),
                "followup_date": followup_date.strftime("%m/%d"),
                "orders": sorted(case["orders"]),
            }

            if week_mon <= rdate <= week_sun and dedup_key not in seen_keys:
                seen_keys.add(dedup_key)
                biopsy_this_week.append(record)
            elif prev_mon <= rdate <= prev_sun and dedup_key not in seen_keys:
                seen_keys.add(dedup_key)
                biopsy_due_now.append(record)

        interventional_match = _is_interventional(case)
        if interventional_match and week_mon <= rdate <= week_sun:
            order, label = interventional_match
            dedup_key = (case["chart_no"], rdate.strftime("%Y-%m-%d"), order)
            if dedup_key not in seen_keys:
                seen_keys.add(dedup_key)
                interventional.append({
                    "label": label,
                    "order": order,
                    "chart_no": case["chart_no"],
                    "case_id": case_id,
                    "date": rdate.strftime("%m/%d"),
                })

    biopsy_this_week.sort(key=lambda item: item["procedure_date"])
    biopsy_due_now.sort(key=lambda item: item["followup_date"])
    interventional.sort(key=lambda item: item["date"])

    return {
        "week": week_str,
        "biopsy_this_week": biopsy_this_week,
        "biopsy_due_now": biopsy_due_now,
        "interventional": interventional,
        "summary": {
            "biopsy_this_week_count": len(biopsy_this_week),
            "biopsy_due_now_count": len(biopsy_due_now),
            "interventional_count": len(interventional),
        },
    }


if __name__ == "__main__":
    import sys

    week = sys.argv[1] if len(sys.argv) > 1 else "2026-W17"
    csv_dir = sys.argv[2] if len(sys.argv) > 2 else "csv_input"
    result = get_biopsy_summary(csv_dir, week)
    print(json.dumps(result, ensure_ascii=False, indent=2))
