#!/usr/bin/env python3
"""Draft clock-in/out times from report timestamps (for manual 刷卡補登).

Reads hospital CSV, filters by reporter ID, groups report timestamps by date,
then derives a draft check-in (earliest - buffer) and check-out (latest + buffer).

Output is a review table only -- no web submission. The user manually enters
each row into the 刷卡補登作業 page.
"""

import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

ENCODING = "cp950"
REPORTER = "A80748"
BASE_DIR = Path(__file__).resolve().parent

# 0-indexed CSV columns (see claude.md)
COL_CASE_ID = 0
COL_EXEC_DATE = 11
COL_EXEC_TIME = 12
COL_REPORT_DATE = 13
COL_REPORT_TIME = 14
COL_REPORTER_ID = 17

WEEKDAY_TW = ["一", "二", "三", "四", "五", "六", "日"]
NIGHT_END_HOUR = 6  # 00:00-05:59 counts as deep night


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


def load_records(paths, reporter):
    """Return {date: {'stamps': [datetime], 'cases': set, 'exec': [datetime]}}."""
    days = defaultdict(lambda: {"stamps": [], "cases": set(), "exec": []})
    total_rows = 0
    for path in paths:
        raw = Path(path).read_bytes().decode(ENCODING, errors="replace")
        reader = csv.reader(raw.splitlines(), delimiter="\t")
        next(reader, None)  # header
        for row in reader:
            if len(row) <= COL_REPORTER_ID:
                continue
            if row[COL_REPORTER_ID].strip() != reporter:
                continue
            stamp = _parse_dt(row[COL_REPORT_DATE], row[COL_REPORT_TIME])
            if stamp is None:
                continue
            total_rows += 1
            bucket = days[stamp.date()]
            bucket["stamps"].append(stamp)
            bucket["cases"].add(row[COL_CASE_ID].strip())
            ex = _parse_dt(row[COL_EXEC_DATE], row[COL_EXEC_TIME])
            if ex is not None:
                bucket["exec"].append(ex)
    return days, total_rows


def build_rows(days, checkin_buf, checkout_buf, exclude_night, date_from, date_to):
    rows = []
    for day in sorted(days):
        if date_from and day < date_from:
            continue
        if date_to and day > date_to:
            continue
        data = days[day]
        stamps = sorted(data["stamps"])
        night = [s for s in stamps if s.hour < NIGHT_END_HOUR]

        considered = stamps
        if exclude_night and night and len(night) < len(stamps):
            considered = [s for s in stamps if s.hour >= NIGHT_END_HOUR]

        first, last = considered[0], considered[-1]
        checkin = first - timedelta(minutes=checkin_buf)
        checkout = last + timedelta(minutes=checkout_buf)

        flags = []
        # clamp inside the calendar day (the punch page books one date at a time)
        if checkin.date() < day:
            checkin = datetime.combine(day, datetime.min.time())
            flags.append("簽到已夾到00:00")
        if checkout.date() > day:
            checkout = datetime.combine(day, datetime.max.time()).replace(
                second=0, microsecond=0
            )
            flags.append("簽退已夾到23:59")
        if night:
            flags.append(f"深夜{len(night)}筆")
        if len(stamps) == 1:
            flags.append("僅1筆")
        if day.weekday() >= 5:
            flags.append("假日")

        rows.append(
            {
                "date": day.isoformat(),
                "weekday": WEEKDAY_TW[day.weekday()],
                "cases": len(data["cases"]),
                "rows": len(stamps),
                "first_report": first.strftime("%H:%M"),
                "last_report": last.strftime("%H:%M"),
                "checkin": checkin.strftime("%H:%M"),
                "checkout": checkout.strftime("%H:%M"),
                "span_hr": round((checkout - checkin).total_seconds() / 3600, 1),
                "notes": "/".join(flags),
            }
        )
    return rows


def _w(text):
    """Display width: CJK chars take 2 columns."""
    return sum(2 if ord(ch) > 0x2E80 else 1 for ch in str(text))


def _pad(text, width, align="<"):
    pad = max(0, width - _w(text))
    return (" " * pad + str(text)) if align == ">" else (str(text) + " " * pad)


def print_table(rows, checkin_buf, checkout_buf, exclude_night):
    if not rows:
        print("No records matched.")
        return
    headers = [
        ("date", "日期", 10, "<"),
        ("weekday", "週", 4, "<"),
        ("cases", "件數", 6, ">"),
        ("first_report", "最早報告", 10, ">"),
        ("last_report", "最晚報告", 10, ">"),
        ("checkin", "草稿簽到", 10, ">"),
        ("checkout", "草稿簽退", 10, ">"),
        ("span_hr", "時數", 6, ">"),
        ("notes", "備註", 20, "<"),
    ]
    print(
        f"簽到緩衝 -{checkin_buf}min / 簽退緩衝 +{checkout_buf}min"
        + ("  (已排除深夜報告)" if exclude_night else "")
    )
    print("-" * 92)
    print("".join(_pad(h[1], h[2], h[3]) + " " for h in headers))
    print("-" * 92)
    for r in rows:
        print("".join(_pad(r[h[0]], h[2], h[3]) + " " for h in headers))
    print("-" * 92)
    print(f"共 {len(rows)} 天；件數合計 {sum(r['cases'] for r in rows)}")
    print("此表為草稿，請人工檢視後再手動補登（有備註者務必確認）")


def main():
    p = argparse.ArgumentParser(
        description="從報告時間戳推算每日草稿簽到/簽退（供人工補登）"
    )
    p.add_argument("--csv", nargs="+", required=True, help="CSV 檔（可多個）")
    p.add_argument("--reporter", default=REPORTER, help=f"報告醫師工號（預設 {REPORTER}）")
    p.add_argument("--checkin-buffer", type=int, default=45,
                   help="簽到往前推的分鐘數（預設 45）")
    p.add_argument("--checkout-buffer", type=int, default=20,
                   help="簽退往後推的分鐘數（預設 20）")
    p.add_argument("--exclude-night", action="store_true",
                   help="計算最早報告時忽略 00:00-05:59 的深夜簽發（避免簽到被拉到凌晨）")
    p.add_argument("--from", dest="date_from", help="起始日 YYYY-MM-DD")
    p.add_argument("--to", dest="date_to", help="結束日 YYYY-MM-DD")
    p.add_argument("--json", help="另存 JSON 路徑")
    p.add_argument("--out-csv", help="另存 CSV 路徑（utf-8-sig，可用 Excel 開）")
    args = p.parse_args()

    def _d(v):
        return datetime.strptime(v, "%Y-%m-%d").date() if v else None

    days, total = load_records(args.csv, args.reporter)
    if not days:
        print(f"找不到報告醫師 {args.reporter} 的紀錄，請確認 CSV 與工號。")
        return 1

    rows = build_rows(days, args.checkin_buffer, args.checkout_buffer,
                      args.exclude_night, _d(args.date_from), _d(args.date_to))
    print_table(rows, args.checkin_buffer, args.checkout_buffer, args.exclude_night)

    if args.json:
        out = {
            "reporter": args.reporter,
            "generated": datetime.now().isoformat(),
            "checkin_buffer_min": args.checkin_buffer,
            "checkout_buffer_min": args.checkout_buffer,
            "exclude_night": args.exclude_night,
            "source_csv": list(args.csv),
            "total_report_rows": total,
            "days": rows,
        }
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json).write_text(
            json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"JSON saved: {args.json}")

    if args.out_csv:
        Path(args.out_csv).parent.mkdir(parents=True, exist_ok=True)
        with open(args.out_csv, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["日期", "週", "件數", "最早報告", "最晚報告",
                        "草稿簽到", "草稿簽退", "時數", "備註"])
            for r in rows:
                w.writerow([r["date"], r["weekday"], r["cases"], r["first_report"],
                            r["last_report"], r["checkin"], r["checkout"],
                            r["span_hr"], r["notes"]])
        print(f"CSV saved: {args.out_csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
