#!/usr/bin/env python3
"""Categorize cases by clinical priority bucket (P1-P4).

Priority hierarchy (Jieyu's 2026-05-14 triage policy):
  P1 急打：source=1(急診) or 3(住院) → ASAP (<24hr target)
  P2 健檢：source=4 → within 10 days
  P3 門診新：source=2 AND order_date age < 3 days → still active
  P4 門診舊：source=2 AND order_date age ≥ 3 days → may de-prioritize/skip

Two modes:
  --pending mode: input CSV has open cases (no report_date) → backlog analysis
  --completed mode (default): input CSV has reported cases → turnaround analysis

Usage:
  python priority_breakdown.py --csv csv_input/1150514_CL.csv
  python priority_breakdown.py --csv csv_input/pending.csv --pending --today 2026-05-14
  python priority_breakdown.py --csv ... --modality XR --json output/priority.json
"""
import argparse
import csv
import io
import json
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

SOURCE_NAMES = {"1": "急診", "2": "門診", "3": "住院", "4": "健檢"}


def is_ldct(exam_name: str, order_code: str) -> bool:
    """Detect LDCT screening cases regardless of source."""
    n = exam_name or ""
    oc = order_code or ""
    if "LDCT" in n or "Low Dose CT" in n or "Low Dose" in n:
        return True
    if oc.startswith("33904"):  # 33904-1 through 33904-9 are all LDCT variants
        return True
    return False


def classify_modality(exam_name: str) -> str:
    n = exam_name or ""
    if n.startswith("CT-") or n.startswith("CTA-") or "LDCT" in n or "Low Dose CT" in n or "HRCT" in n:
        return "CT"
    if n.startswith("US-"):
        return "US"
    if "Mammography" in n:
        return "Mammo"
    if n.startswith("MR") or "MRI" in n:
        return "MR"
    if "Bone densitometry" in n:
        return "BMD"
    if "I.V.P." in n or "IVP" in n:
        return "IVP"
    return "XR"


def ct_subtype(exam_name: str, order_code: str) -> str:
    """CT subtype for finer-grained tracking. Only valid if modality==CT."""
    if is_ldct(exam_name, order_code):
        return "LDCT"
    n = exam_name or ""
    oc = order_code or ""
    if "Brain" in n or "Head" in n:
        if any(c in oc for c in ["33072", "33090"]):
            return "Brain-C"
        return "Brain"
    if "Neck" in n or "C-Spine" in n or "C Spine" in n or n.startswith("CTA-"):
        return "Neck/CTA"
    return "Chest/Abd"


def priority_bucket(source: str, age_days: int, exam_name: str = "", order_code: str = ""):
    """Return (priority_code, label, sla_threshold_days).

    Special: LDCT cases override source-based logic and go P2 (10d SLA),
    because clinically they are screening exams regardless of arriving via 門診/健檢.
    """
    if is_ldct(exam_name, order_code):
        return "P2", "LDCT健檢", 10
    if source in ("1", "3"):
        return "P1", "急打", 1
    if source == "4":
        return "P2", "健檢", 10
    if source == "2":
        if age_days < 3:
            return "P3", "門診新", 3
        return "P4", "門診舊", None  # may skip
    return "P5", f"其他({source})", None


def load_cases(csv_path: str, today: date):
    """Load cases from CSV, group by case_id. Returns list of dicts."""
    by_case = {}
    with open(csv_path, encoding="cp950", errors="replace") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader, None)  # skip header
        for row in reader:
            if len(row) < 25:
                continue
            cid = row[0]
            chart_no = row[1]
            order_date_str = row[3]
            source = row[4]
            order_code = row[6]
            exam = row[8]
            report_date = row[13]
            wp = row[24]
            # exclude contrast billing rows
            if "Contrast" in exam and wp in ("0", "0.0", ""):
                continue
            try:
                order_date = datetime.strptime(order_date_str, "%m/%d/%Y").date()
            except (ValueError, TypeError):
                continue
            age = (today - order_date).days
            mod = classify_modality(exam)
            sub = ct_subtype(exam, order_code) if mod == "CT" else None
            completed = bool(report_date and report_date.strip())

            # case_id grouping: first row wins; if any row in case is "different" exam, keep first
            if cid not in by_case:
                # Display modality: show CT-LDCT separately for visibility
                display_mod = "CT-LDCT" if (mod == "CT" and sub == "LDCT") else mod
                by_case[cid] = {
                    "case_id": cid,
                    "chart_no": chart_no,
                    "source": source,
                    "source_name": SOURCE_NAMES.get(source, f"src={source}"),
                    "order_code": order_code,
                    "order_date": order_date.isoformat(),
                    "age_days": age,
                    "modality": mod,
                    "display_modality": display_mod,
                    "ct_subtype": sub,
                    "exam_name": exam,
                    "completed": completed,
                    "report_date": report_date if completed else None,
                }
    return list(by_case.values())


def aggregate(cases, only_modality=None, pending_only=False):
    """Group by (priority, modality)."""
    filtered = cases
    if only_modality:
        filtered = [c for c in filtered if c["modality"] == only_modality]
    if pending_only:
        filtered = [c for c in filtered if not c["completed"]]
    buckets = defaultdict(list)
    for c in filtered:
        prio, label, sla = priority_bucket(
            c["source"], c["age_days"],
            exam_name=c.get("exam_name", ""),
            order_code=c.get("order_code", ""),
        )
        c["priority"] = prio
        c["priority_label"] = label
        c["sla_days"] = sla
        c["sla_overdue"] = (sla is not None and c["age_days"] > sla)
        buckets[(prio, label)].append(c)
    return buckets, filtered


def print_summary(buckets, mode_label: str, today: date, output_json: str = None):
    """Console output."""
    print(f"\n=== Priority Breakdown — mode: {mode_label} ===")
    print(f"Today: {today}\n")

    json_out = {"mode": mode_label, "today": today.isoformat(), "buckets": []}

    # Stable order
    order = ["P1", "P2", "P3", "P4", "P5"]
    sla_label = {"P1": ">24hr", "P2": ">10d", "P3": ">3d (應升 P4)", "P4": "(可放棄)", "P5": "—"}

    print(f"{'Prio':5s}{'Label':10s}{'Count':>7s}{'Median age':>13s}{'Max age':>10s}{'Overdue':>10s}  Modality breakdown")
    print("-" * 95)

    for prio in order:
        items_all = []
        for key, items in buckets.items():
            if key[0] == prio:
                items_all.extend(items)
        if not items_all:
            continue
        ages = sorted(c["age_days"] for c in items_all)
        med = ages[len(ages) // 2] if ages else 0
        mx = max(ages) if ages else 0
        overdue = sum(1 for c in items_all if c["sla_overdue"])
        mod_breakdown = defaultdict(int)
        for c in items_all:
            mod_breakdown[c.get("display_modality", c["modality"])] += 1
        mod_str = " ".join(f"{m}:{n}" for m, n in sorted(mod_breakdown.items()))

        label = items_all[0]["priority_label"]
        print(f"{prio:5s}{label:10s}{len(items_all):>7d}{med:>11d}d{mx:>8d}d{overdue:>10d}  {mod_str}")

        json_out["buckets"].append({
            "priority": prio,
            "label": label,
            "count": len(items_all),
            "median_age_days": med,
            "max_age_days": mx,
            "overdue_count": overdue,
            "overdue_sla": sla_label[prio],
            "by_modality": dict(mod_breakdown),
        })

    print()

    # Show oldest 5 in P1 and P2 (most actionable)
    for prio in ("P1", "P2"):
        items_all = []
        for key, items in buckets.items():
            if key[0] == prio:
                items_all.extend(items)
        if not items_all:
            continue
        print(f"[{prio} {items_all[0]['priority_label']} — 最舊 5 件]")
        for c in sorted(items_all, key=lambda x: -x["age_days"])[:5]:
            flag = " ⚠ 逾期" if c["sla_overdue"] else ""
            disp_mod = c.get("display_modality", c["modality"])
            print(f"  chart {c['chart_no']:10s}  {disp_mod:8s}  age {c['age_days']:3d}d  "
                  f"{c['source_name']:5s}  {c['exam_name'][:50]}{flag}")
        print()

    # SLA summary box
    p1_total = sum(b["count"] for b in json_out["buckets"] if b["priority"] == "P1")
    p1_over = sum(b["overdue_count"] for b in json_out["buckets"] if b["priority"] == "P1")
    p2_total = sum(b["count"] for b in json_out["buckets"] if b["priority"] == "P2")
    p2_over = sum(b["overdue_count"] for b in json_out["buckets"] if b["priority"] == "P2")

    print("=== KPI ===")
    print(f"  P1 急打 SLA (≤24hr):  {p1_total - p1_over} / {p1_total} 達成"
          + (f"  ⚠ 逾期 {p1_over}" if p1_over else "  ✓"))
    print(f"  P2 健檢 SLA (≤10d):   {p2_total - p2_over} / {p2_total} 達成"
          + (f"  ⚠ 逾期 {p2_over}" if p2_over else "  ✓"))
    json_out["kpi"] = {
        "p1_total": p1_total, "p1_overdue": p1_over,
        "p2_total": p2_total, "p2_overdue": p2_over,
    }

    if output_json:
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(json_out, f, ensure_ascii=False, indent=2)
        print(f"\nJSON saved: {output_json}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", required=True, help="Input CSV (cp950, TSV)")
    ap.add_argument("--pending", action="store_true",
                    help="Filter pending cases only (no report_date). Default: all cases.")
    ap.add_argument("--modality", help="Filter modality (XR/CT/US/Mammo)")
    ap.add_argument("--today", help="Override today date (YYYY-MM-DD)")
    ap.add_argument("--json", help="Output JSON path")
    args = ap.parse_args()

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    today = date.fromisoformat(args.today) if args.today else date.today()
    cases = load_cases(args.csv, today=today)
    n_pending = sum(1 for c in cases if not c["completed"])
    n_completed = sum(1 for c in cases if c["completed"])
    print(f"CSV loaded: {len(cases)} 案件（pending {n_pending} / completed {n_completed}）")

    buckets, filtered = aggregate(cases, only_modality=args.modality, pending_only=args.pending)
    mode = []
    if args.pending: mode.append("pending only")
    else: mode.append("all (含 completed)")
    if args.modality: mode.append(f"modality={args.modality}")
    mode_label = ", ".join(mode)

    print_summary(buckets, mode_label, today, output_json=args.json)


if __name__ == "__main__":
    main()
