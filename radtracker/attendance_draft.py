#!/usr/bin/env python3
"""Draft clock-in/out times from report timestamps (for manual 刷卡補登).

Work-session model (2026-07-23, per user):
  - 深夜報告視為前一天的延續：00:00 - (night-cutoff) 的簽發歸前一個工作日
  - 收工通常不超過 04:00，早上最早 06:00 開始 -> cutoff 預設 05:00 落在兩者之間
  - 簽到不早於 06:00（早上最早開始時間）
  - 簽退可跨日（例：工作日 07/19 的簽退落在 07/20 02:34）

補登頁是「日期+時間」逐筆送出、由系統依打卡狀態自動判定簽到/簽退，
所以跨日的簽退直接用它自己的日期補登即可。

Output is a review table only -- no web submission.
"""

import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta, time
from pathlib import Path

ENCODING = "cp950"
REPORTER = "A80748"

# 0-indexed CSV columns (see claude.md)
COL_CASE_ID = 0
COL_REPORT_DATE = 13
COL_REPORT_TIME = 14
COL_REPORTER_ID = 17

WEEKDAY_TW = ["一", "二", "三", "四", "五", "六", "日"]


def _parse_dt(date_str, time_str):
    date_str, time_str = date_str.strip(), time_str.strip()
    if not date_str or not time_str:
        return None
    for fmt in ("%m/%d/%Y %H:%M", "%Y/%m/%d %H:%M", "%m/%d/%Y %H:%M:%S"):
        try:
            return datetime.strptime(f"{date_str} {time_str}", fmt)
        except ValueError:
            continue
    return None


def load_sessions(paths, reporter, night_cutoff):
    """Group report timestamps into work days (night reports -> previous day)."""
    days = defaultdict(lambda: {"stamps": [], "cases": set(), "night": 0})
    total = 0
    for path in paths:
        raw = Path(path).read_bytes().decode(ENCODING, errors="replace")
        reader = csv.reader(raw.splitlines(), delimiter="\t")
        next(reader, None)
        for row in reader:
            if len(row) <= COL_REPORTER_ID:
                continue
            if row[COL_REPORTER_ID].strip() != reporter:
                continue
            stamp = _parse_dt(row[COL_REPORT_DATE], row[COL_REPORT_TIME])
            if stamp is None:
                continue
            total += 1
            is_night = stamp.hour < night_cutoff
            work_day = stamp.date() - timedelta(days=1) if is_night else stamp.date()
            b = days[work_day]
            b["stamps"].append(stamp)
            b["cases"].add(row[COL_CASE_ID].strip())
            if is_night:
                b["night"] += 1
    return days, total


def build_rows(days, checkin_buf, checkout_buf, earliest_start,
               date_from, date_to, night_cutoff):
    rows = []
    for day in sorted(days):
        if date_from and day < date_from:
            continue
        if date_to and day > date_to:
            continue
        d = days[day]
        stamps = sorted(d["stamps"])
        first, last = stamps[0], stamps[-1]

        checkin = first - timedelta(minutes=checkin_buf)
        floor = datetime.combine(day, earliest_start)
        flags = []
        if checkin < floor:
            checkin = floor
            flags.append(f"簽到夾到{earliest_start.strftime('%H:%M')}")
        checkout = last + timedelta(minutes=checkout_buf)

        cross = checkout.date() > day
        if cross:
            flags.append("簽退跨日")
        # 只反映「簽報告」時間；若當天上午在做臨床卻沒簽報告，簽到會被低估
        if checkin.hour >= 12:
            flags.append("簽到偏晚需確認")
        if d["night"]:
            flags.append(f"深夜{d['night']}筆")
        if len(stamps) == 1:
            flags.append("僅1筆")
        if day.weekday() >= 5:
            flags.append("假日")

        rows.append({
            "work_day": day.isoformat(),
            "weekday": WEEKDAY_TW[day.weekday()],
            "cases": len(d["cases"]),
            "reports": len(stamps),
            "first_report": first.strftime("%H:%M"),
            "last_report": (last.strftime("%m/%d %H:%M") if cross
                            else last.strftime("%H:%M")),
            "checkin_date": checkin.date().isoformat(),
            "checkin": checkin.strftime("%H:%M"),
            "checkout_date": checkout.date().isoformat(),
            "checkout": checkout.strftime("%H:%M"),
            "checkout_cross_day": cross,
            "span_hr": round((checkout - checkin).total_seconds() / 3600, 1),
            "night_reports": d["night"],
            "notes": "/".join(flags),
        })
    return rows


def _w(t):
    return sum(2 if ord(c) > 0x2E80 else 1 for c in str(t))


def _pad(t, w, a="<"):
    p = max(0, w - _w(t))
    return (" " * p + str(t)) if a == ">" else (str(t) + " " * p)


def print_table(rows, checkin_buf, checkout_buf, earliest_start, night_cutoff):
    if not rows:
        print("No records matched.")
        return
    print(f"簽到 = 最早報告 -{checkin_buf}min（不早於 {earliest_start.strftime('%H:%M')}）"
          f"｜簽退 = 最晚報告 +{checkout_buf}min")
    print(f"深夜規則：00:00-{night_cutoff:02d}:00 的簽發歸前一工作日（簽退跨日）")
    print("-" * 100)
    hdr = [("work_day", "工作日", 11, "<"), ("weekday", "週", 4, "<"),
           ("cases", "件數", 6, ">"), ("first_report", "最早報告", 10, ">"),
           ("last_report", "最晚報告", 13, ">"), ("checkin", "簽到", 8, ">"),
           ("checkout_disp", "簽退", 13, ">"), ("span_hr", "時數", 6, ">"),
           ("notes", "備註", 24, "<")]
    print("".join(_pad(h[1], h[2], h[3]) + " " for h in hdr))
    print("-" * 100)
    for r in rows:
        r = dict(r)
        r["checkout_disp"] = (f"{r['checkout_date'][5:]} {r['checkout']}"
                              if r["checkout_cross_day"] else r["checkout"])
        print("".join(_pad(r[h[0]], h[2], h[3]) + " " for h in hdr))
    print("-" * 100)
    print(f"共 {len(rows)} 個工作日；件數合計 {sum(r['cases'] for r in rows)}")
    print("此表為草稿，請人工檢視後再手動補登（跨日簽退用它自己的日期送出）")


def main():
    p = argparse.ArgumentParser(
        description="從報告時間戳推算每日草稿簽到/簽退（供人工補登，不碰網頁）")
    p.add_argument("--csv", nargs="+", required=True)
    p.add_argument("--reporter", default=REPORTER)
    p.add_argument("--checkin-buffer", type=int, default=45,
                   help="簽到往前推分鐘數（預設 45）")
    p.add_argument("--checkout-buffer", type=int, default=20,
                   help="簽退往後推分鐘數（預設 20）")
    p.add_argument("--night-cutoff", type=int, default=5,
                   help="00:00 到此小時的簽發歸前一工作日（預設 5，即 <05:00）")
    p.add_argument("--earliest-start", default="06:00",
                   help="簽到不早於此時刻（預設 06:00）")
    p.add_argument("--from", dest="date_from")
    p.add_argument("--to", dest="date_to")
    p.add_argument("--json")
    p.add_argument("--out-csv")
    a = p.parse_args()

    def _d(v):
        return datetime.strptime(v, "%Y-%m-%d").date() if v else None

    es = datetime.strptime(a.earliest_start, "%H:%M").time()
    days, total = load_sessions(a.csv, a.reporter, a.night_cutoff)
    if not days:
        print(f"找不到報告醫師 {a.reporter} 的紀錄，請確認 CSV 與工號。")
        return 1

    rows = build_rows(days, a.checkin_buffer, a.checkout_buffer, es,
                      _d(a.date_from), _d(a.date_to), a.night_cutoff)
    print_table(rows, a.checkin_buffer, a.checkout_buffer, es, a.night_cutoff)

    if a.json:
        Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        Path(a.json).write_text(json.dumps({
            "reporter": a.reporter,
            "generated": datetime.now().isoformat(),
            "checkin_buffer_min": a.checkin_buffer,
            "checkout_buffer_min": a.checkout_buffer,
            "night_cutoff_hour": a.night_cutoff,
            "earliest_start": a.earliest_start,
            "source_csv": list(a.csv),
            "total_report_rows": total,
            "days": rows,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"JSON saved: {a.json}")

    if a.out_csv:
        Path(a.out_csv).parent.mkdir(parents=True, exist_ok=True)
        with open(a.out_csv, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["工作日", "週", "件數", "最早報告", "最晚報告",
                        "簽到日期", "簽到", "簽退日期", "簽退", "時數", "備註"])
            for r in rows:
                w.writerow([r["work_day"], r["weekday"], r["cases"],
                            r["first_report"], r["last_report"],
                            r["checkin_date"], r["checkin"],
                            r["checkout_date"], r["checkout"],
                            r["span_hr"], r["notes"]])
        print(f"CSV saved: {a.out_csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
