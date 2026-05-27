#!/usr/bin/env python3
"""報告單位時間產值分析（pt/hr）— 全模態，真實 CSV 簽發間隔計時。

回答「哪種報告單位時間最賺錢」。

計時方法（2026-05-27 改版，取代舊估算模型）：
  - 依 case_id 分組，取最早簽發時間（report_date+report_time）
  - 全 case 依簽發時間排序，每件的「讀片時間」= 與前一件的簽發間隔
  - 間隔 = 0：批次簽發（同分鐘多件）→ 剔除
  - 間隔 > break-min（預設 30）：中間休息 → 剔除
  - 其餘間隔視為該件耗時；用中位數（robust）算 pt/hr = 平均點值 × 60/中位min

分類粒度：
  - 全模態（XR/CT/US/Mammo/MR/BMD/IVP）
  - CT 子分類（LDCT/Brain/Neck/Chest-Abd）；US（一般/困難）
  - XR 依部位；Spine 再依 protocol（AP/Lat、Flex/Ext、4view）拆分

限制：
  - report_time 僅到「分」→ 次分鐘讀片被 floor 到 1 min（同分鐘者當批次剔除）
  - 間隔含 think/dictation 時間，是 throughput 代理，非純看片秒數
  - 建議餵多週 CSV 以累積足夠計時樣本（單週每類別 n 太少）

用法：
    python xr_value.py --csv csv_input/1150510_CL.csv csv_input/1150517_CL.csv ...
    python xr_value.py --csv ... --json output/xr_value_2026-05.json
    python xr_value.py --csv ... --break-min 30 --min-n 15
"""
import argparse
import csv
import io
import json
import statistics
import sys
from collections import defaultdict
from datetime import datetime


def categorize(exams):
    """exams: list of exam_name for one case_id → 分類字串。"""
    joined = " | ".join(exams)
    n = joined.lower()
    e0 = exams[0]
    # CT
    if e0.startswith("CT-") or e0.startswith("CTA-") or "ldct" in n or "low dose" in n or "hrct" in n:
        if "ldct" in n or "low dose" in n:
            return "CT-LDCT"
        if "brain" in n or "head" in n:
            return "CT-Brain"
        if e0.startswith("CTA-") or "neck" in n:
            return "CT-Neck/CTA"
        return "CT-Chest/Abd"
    if e0.startswith("US-"):
        return ("US-困難" if any(k in joined for k in
                ["Breast", "Prostate", "Extremity", "Scrotum", "Parotid", "Lower Extremity"])
                else "US-一般")
    if "Mammography" in joined:
        return "Mammo"
    if e0.startswith("MR") or "MRI" in joined:
        return "MR"
    if "Bone densitometry" in joined:
        return "BMD"
    if "I.V.P." in joined or "IVP" in joined:
        return "IVP"
    # XR — spine split by protocol
    if "c-spine" in n or "cervical" in n:
        if "flex" in n:
            return "XR C-spine Flex/Ext"
        if "4 view" in n:
            return "XR C-spine 4view"
        return "XR C-spine AP/Lat"
    if "l-spine" in n or "lumbar" in n or "l-s spine" in n:
        if "flex" in n:
            return "XR L-spine Flex/Ext"
        if "4 view" in n:
            return "XR L-spine 4view"
        return "XR L-spine AP/Lat"
    if "t-l spine" in n or "t-spine" in n or "thoracic" in n:
        return "XR T/TL-spine"
    if "whole spine" in n:
        return "XR Whole-spine"
    for kw, lbl in [("chest", "Chest"), ("knee", "Knee"), ("ankle", "Ankle"), ("foot", "Foot"),
                    ("hand", "Hand"), ("wrist", "Wrist"), ("shoulder", "Shoulder"), ("clavic", "Clavicle"),
                    ("pelvis", "Pelvis"), ("hip", "Hip"), ("kub", "KUB"), ("elbow", "Elbow"),
                    ("humer", "Humerus"), ("forearm", "Forearm"), ("femur", "Femur"), ("tibia", "Tibia"),
                    ("skull", "Skull"), ("finger", "Finger"), ("toe", "Toe"), ("rib", "Rib"),
                    ("scapula", "Scapula"), ("calcaneus", "Calcaneus"), ("nasal", "Nasal")]:
        if kw in n:
            return "XR " + lbl
    return "XR Other"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", nargs="+", required=True, help="CSV 檔（建議多週累積）")
    ap.add_argument("--break-min", type=float, default=30, help="間隔 > 此分鐘視為休息剔除（預設 30）")
    ap.add_argument("--min-n", type=int, default=15, help="計時樣本 >= 此數才視為可信（預設 15）")
    ap.add_argument("--json", help="輸出 JSON 路徑")
    args = ap.parse_args()
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    cases = {}
    for fp in args.csv:
        try:
            f = open(fp, encoding="cp950", errors="replace")
        except FileNotFoundError:
            print(f"WARN: {fp} not found", file=sys.stderr)
            continue
        r = csv.reader(f, delimiter="\t")
        next(r, None)
        for row in r:
            if len(row) < 25:
                continue
            cid, exam, wp, rd, rt = row[0], row[8], row[24], row[13], row[14]
            if not (rd and rt):
                continue
            if "Contrast" in exam and wp in ("0", "0.0", ""):
                continue
            try:
                dt = datetime.strptime(f"{rd} {rt}", "%m/%d/%Y %H:%M")
            except ValueError:
                continue
            try:
                wpv = float(wp) if wp else 0.0
            except ValueError:
                wpv = 0.0
            c = cases.setdefault(cid, {"dt": dt, "wp": 0.0, "exams": []})
            c["wp"] += wpv
            c["exams"].append(exam)
            if dt < c["dt"]:
                c["dt"] = dt
        f.close()

    for c in cases.values():
        c["cat"] = categorize(c["exams"])

    # sort by sign time, compute intervals
    recs = sorted(cases.values(), key=lambda c: c["dt"])
    intervals = defaultdict(list)
    skip_batch = skip_break = used = 0
    for i in range(1, len(recs)):
        gap = (recs[i]["dt"] - recs[i - 1]["dt"]).total_seconds() / 60
        if gap <= 0:
            skip_batch += 1
            continue
        if gap > args.break_min:
            skip_break += 1
            continue
        intervals[recs[i]["cat"]].append(gap)
        used += 1

    pts = defaultdict(lambda: {"n": 0, "wp": 0.0})
    for c in cases.values():
        pts[c["cat"]]["n"] += 1
        pts[c["cat"]]["wp"] += c["wp"]

    rows = []
    for cat in pts:
        timed = intervals.get(cat, [])
        n_all = pts[cat]["n"]
        avg_pt = pts[cat]["wp"] / n_all if n_all else 0
        med = statistics.median(timed) if timed else None
        pph = (avg_pt * 60 / med) if med else None
        rows.append({
            "category": cat, "n_cases": n_all, "n_timed": len(timed),
            "avg_points": round(avg_pt, 1),
            "median_min": round(med, 1) if med else None,
            "points_per_hr": round(pph) if pph else None,
            "reliable": len(timed) >= args.min_n,
        })
    # rank: reliable first by pt/hr desc, then low-sample
    ranked = sorted([r for r in rows if r["points_per_hr"] is not None],
                    key=lambda x: (-(x["reliable"]), -x["points_per_hr"]))

    print(f"\n=== 報告單位時間產值（真實 CSV 計時）===")
    print(f"unique case {len(recs)}；可用間隔 {used}；批次(0)剔 {skip_batch}；休息(>{args.break_min:.0f}min)剔 {skip_break}")
    print(f"可信門檻：計時樣本 >= {args.min_n}\n")
    print("{:22s}{:>6s}{:>6s}{:>9s}{:>8s}{:>9s}".format(
        "category", "n件", "n計時", "中位min", "平均pt", "pt/hr"))
    print("-" * 62)
    for r in ranked:
        flag = "" if r["reliable"] else " ⚠少"
        print("{:22s}{:>6d}{:>6d}{:>9.1f}{:>8.1f}{:>9d}{}".format(
            r["category"], r["n_cases"], r["n_timed"],
            r["median_min"], r["avg_points"], r["points_per_hr"], flag))

    reliable = [r for r in ranked if r["reliable"]]
    if reliable:
        print(f"\n最高（可信）：{reliable[0]['category']} ~{reliable[0]['points_per_hr']} pt/hr"
              f"（中位 {reliable[0]['median_min']}min, {reliable[0]['avg_points']}pt/件）")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fo:
            json.dump({"method": "csv_signoff_interval", "break_min": args.break_min,
                       "min_n": args.min_n, "total_cases": len(recs),
                       "used_intervals": used, "ranking": ranked},
                      fo, ensure_ascii=False, indent=2)
        print(f"\nJSON saved: {args.json}")
    print("\n註：pt/hr 用真實簽發間隔中位數；report_time 僅到分→次分鐘讀片 floor 1min；建議餵多週累積樣本。")


if __name__ == "__main__":
    main()
