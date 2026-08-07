# -*- coding: utf-8 -*-
"""Parse every captured DICOM header in work/raw/ into work/result.csv.

Run this at home. The hospital PC only captures raw headers (no Python there),
so this is the step that turns them into sheet columns. Re-running is safe and
is the right thing to do after any change to the parsing rules - result.csv is
rebuilt from scratch each time, the raw files stay untouched.

Console output is cp950-safe: no arrows, no check marks.

Usage:
    python parse_all_raw.py
    python parse_all_raw.py --problems-only    # list just the ones needing attention
"""
import argparse
import csv
import glob
import os
import sys

from parse_dicom_header import OUTPUT_COLUMNS, RESULT_CSV, WORK_DIR, parse_header, to_row

RAW_GLOB = os.path.join(WORK_DIR, "raw", "*.txt")


def main():
    ap = argparse.ArgumentParser(description="Parse all captured headers into result.csv")
    ap.add_argument("--problems-only", action="store_true",
                    help="print only the files with missing fields")
    args = ap.parse_args()

    paths = sorted(glob.glob(RAW_GLOB))
    if not paths:
        print("work/raw/ 底下沒有任何檔頭，還沒開始擷取？")
        return 0

    rows = []
    problem_files = []
    mismatched = []

    for path in paths:
        name = os.path.splitext(os.path.basename(path))[0]
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        row, problems = to_row(parse_header(text)[0])

        # The file is named after the accession the capture asked for. If the header
        # says something else, the capture grabbed the wrong study - do not trust it.
        if row["AccessionNumber"] and name.isdigit() and row["AccessionNumber"] != name:
            mismatched.append((name, row["AccessionNumber"]))
            continue
        if not row["AccessionNumber"] and name.isdigit():
            row["AccessionNumber"] = name

        rows.append(row)
        if problems:
            problem_files.append((name, problems))

    os.makedirs(WORK_DIR, exist_ok=True)
    with open(RESULT_CSV, "w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print("檔頭檔案      %d" % len(paths))
    print("解析成功      %d" % len(rows))
    print("完全無缺漏    %d" % (len(rows) - len(problem_files)))

    if mismatched:
        print("")
        print("單號不符（已排除，建議重抓）%d 筆：" % len(mismatched))
        for name, got in mismatched[:10]:
            print("  檔名 %s 但檔頭是 %s" % (name, got))

    if problem_files:
        print("")
        print("有缺漏欄位 %d 筆：" % len(problem_files))
        for name, problems in problem_files[:20]:
            print("  %s: %s" % (name, "；".join(problems)))
        if len(problem_files) > 20:
            print("  ...另外 %d 筆" % (len(problem_files) - 20))

    if not args.problems_only:
        print("")
        print("已寫出 %s" % RESULT_CSV)
    return 0


if __name__ == "__main__":
    sys.exit(main())
