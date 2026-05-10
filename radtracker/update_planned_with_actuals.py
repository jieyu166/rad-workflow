#!/usr/bin/env python3
"""Generate per-day actual-vs-planned summary for a week's schedule.

Reads:
  - output/w{nn}_schedule.json (planned daily slots)
  - CSV input for the matching week

Produces:
  - output/w{nn}_actuals.json with per-day per-modality actual completion
  - Per-event description blocks ready to paste into GCal

Why day-level not slot-level:
  CSV report_time = batch sign-off time, not actual read time (~60% batch signed).
  Slot-time matching catches only ~15% of cases. Day-level aggregation is honest.

Usage:
    python update_planned_with_actuals.py W19
    python update_planned_with_actuals.py W19 --csv csv_input/1150510_CL.csv [csv_input/1150510_YK.csv]
"""
import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
OUTPUT_DIR = ROOT / "output"
CSV_DIR = ROOT / "csv_input"


def classify_modality(exam_name):
    n = exam_name or ""
    if n.startswith("CT-") or n.startswith("CTA-") or "Low Dose CT" in n or "LDCT" in n or "HRCT" in n:
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


CN_WEEKDAY = ["一", "二", "三", "四", "五", "六", "日"]


def get_work_date(dt):
    """Map 00:00-05:59 to previous day."""
    if dt.hour < 6:
        return (dt.replace(hour=12) - datetime.timedelta(days=1)).date() if False else dt.date()
    return dt.date()


def load_csv(csv_files):
    """Group cases by case_id; return list of {case_id, work_date, modality, work_points}."""
    by_case = {}
    for fp in csv_files:
        with open(fp, encoding="cp950", errors="replace") as f:
            reader = csv.reader(f, delimiter="\t")
            next(reader, None)
            for row in reader:
                if len(row) < 25:
                    continue
                case_id = row[0]
                report_date, report_time = row[13], row[14]
                exam_name = row[8]
                work_points = row[24]
                if "Contrast" in exam_name and work_points in ("0", "0.0", ""):
                    continue
                if not (report_date and report_time):
                    continue
                try:
                    dt = datetime.strptime(f"{report_date} {report_time}", "%m/%d/%Y %H:%M")
                except ValueError:
                    continue
                # work_date: 00-05:59 → previous day
                from datetime import timedelta
                wd = (dt - timedelta(hours=6)).date()
                mod = classify_modality(exam_name)
                wp = float(work_points) if work_points else 0.0
                if case_id not in by_case:
                    by_case[case_id] = {"case_id": case_id, "work_date": wd,
                                        "modality": mod, "work_points": wp, "dt": dt}
                else:
                    by_case[case_id]["work_points"] += wp
    return list(by_case.values())


def aggregate_daily(cases):
    """Return {(work_date, modality): {count, work_points, first_dt, last_dt}}."""
    agg = defaultdict(lambda: {"count": 0, "work_points": 0.0, "first_dt": None, "last_dt": None})
    for c in cases:
        key = (c["work_date"], c["modality"])
        a = agg[key]
        a["count"] += 1
        a["work_points"] += c["work_points"]
        if a["first_dt"] is None or c["dt"] < a["first_dt"]:
            a["first_dt"] = c["dt"]
        if a["last_dt"] is None or c["dt"] > a["last_dt"]:
            a["last_dt"] = c["dt"]
    return agg


def build_summary(schedule, daily_actuals):
    """For each planned day, compute actual vs planned."""
    out = []
    for day in schedule.get("daily", []):
        date = datetime.strptime(day["date"], "%Y-%m-%d").date()
        planned_by_mod = defaultdict(lambda: {"count": 0, "slots": []})
        for slot in day.get("slots", []):
            if slot.get("type") != "report":
                continue
            mod = slot["modality"]
            planned_by_mod[mod]["count"] += slot["count"]
            planned_by_mod[mod]["slots"].append(slot)

        # Collect actuals for that day
        actual_by_mod = {}
        for mod in set(list(planned_by_mod.keys()) + ["XR", "CT", "US", "Mammo", "IVP", "BMD", "MR"]):
            key = (date, mod)
            if key in daily_actuals:
                actual_by_mod[mod] = daily_actuals[key]

        # Compose day summary
        day_planned = sum(p["count"] for p in planned_by_mod.values())
        day_actual = sum(a["count"] for a in actual_by_mod.values())
        day_wp = sum(a["work_points"] for a in actual_by_mod.values())
        mod_compare = []
        for mod in sorted(set(list(planned_by_mod.keys()) + list(actual_by_mod.keys()))):
            p = planned_by_mod.get(mod, {}).get("count", 0)
            a = actual_by_mod.get(mod, {}).get("count", 0)
            mod_compare.append({"modality": mod, "planned": p, "actual": a, "delta": a - p})

        out.append({
            "date": day["date"],
            "weekday": day.get("day", ""),
            "planned_total": day_planned,
            "actual_total": day_actual,
            "actual_work_points": round(day_wp, 1),
            "deviation_pct": round((day_actual - day_planned) / day_planned * 100, 0) if day_planned else 0,
            "by_modality": mod_compare,
            "slot_event_ids": [s["slots"] for s in planned_by_mod.values()],  # for ref
        })
    return out


def render_event_description_block(date_str, mod, planned_total, actual_total, actual_wp, deviation_pct):
    """The standardized description block to paste into all GCal events of same day+modality."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    return (
        f"\n\n—— 實際（自動回填 {ts}）——\n"
        f"當日 {mod} 計畫共：{planned_total} 件\n"
        f"當日 {mod} 實際共：{actual_total} 件\n"
        f"工作點值：{actual_wp:.0f}pt\n"
        f"偏差％：{deviation_pct:+.0f}％\n"
        f"註：CSV 簽發時間為 batch sign-off，無法精細對應單一 slot，僅顯示日總計"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("week", help="W19 / W20 etc")
    ap.add_argument("--csv", nargs="+", help="CSV files (auto-detect if not given)")
    ap.add_argument("--output", help="Output JSON path")
    args = ap.parse_args()

    wlow = args.week.lower()
    sched_path = OUTPUT_DIR / f"{wlow}_schedule.json"
    if not sched_path.exists():
        archived = OUTPUT_DIR / args.week.upper() / f"{wlow}_schedule.json"
        if archived.exists():
            sched_path = archived
        else:
            print(f"ERROR: {sched_path} not found", file=sys.stderr)
            sys.exit(1)

    with open(sched_path, encoding="utf-8") as f:
        schedule = json.load(f)

    if args.csv:
        csv_files = args.csv
    else:
        csv_files = sorted(str(p) for p in CSV_DIR.glob("115*_CL.csv"))[-1:]
        yk = sorted(str(p) for p in CSV_DIR.glob("115*_YK.csv"))[-1:]
        csv_files = csv_files + yk

    print(f"Schedule: {sched_path}")
    print(f"CSV: {csv_files}\n")

    cases = load_csv(csv_files)
    daily_actuals = aggregate_daily(cases)
    summary = build_summary(schedule, daily_actuals)

    # Print summary
    print(f"{'Date':12s}{'Day':5s}{'Plan':>6s}{'Actual':>8s}{'Pt':>10s}{'Dev%':>7s}  By Modality")
    print("-" * 90)
    for s in summary:
        mods_str = " | ".join(f"{m['modality']}:{m['actual']}/{m['planned']}({m['delta']:+d})"
                              for m in s["by_modality"] if m["planned"] > 0 or m["actual"] > 0)
        print(f"{s['date']:12s}{s['weekday']:5s}{s['planned_total']:>6d}"
              f"{s['actual_total']:>8d}{s['actual_work_points']:>10.0f}{s['deviation_pct']:>+7.0f}  {mods_str}")

    # Write output
    out_path = args.output or str(OUTPUT_DIR / f"{wlow}_actuals.json")
    out = {
        "week": schedule.get("week"),
        "computed_at": datetime.now().isoformat(),
        "csv_files": csv_files,
        "summary_by_day": summary,
        "gcal_description_blocks": [
            {
                "date": s["date"],
                "modalities": [
                    {
                        "modality": m["modality"],
                        "block_text": render_event_description_block(
                            s["date"], m["modality"], m["planned"], m["actual"],
                            next((mod_act["work_points"]
                                  for (d, mod), mod_act in daily_actuals.items()
                                  if d.isoformat() == s["date"] and mod == m["modality"]), 0),
                            (m["actual"] - m["planned"]) / m["planned"] * 100 if m["planned"] else 0
                        )
                    }
                    for m in s["by_modality"] if m["planned"] > 0
                ]
            }
            for s in summary
        ],
        "synced_event_ids": schedule.get("gcal", {}).get("synced_event_ids", []),
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nWrote: {out_path}")
    print(f"\nNext step: pass {out_path} to Claude Code and ask to update each GCal event's description.")
    print("Each event in synced_event_ids gets appended its corresponding day+modality block.")


if __name__ == "__main__":
    main()
