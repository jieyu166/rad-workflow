#!/usr/bin/env python3
"""Fetch LDCT report texts and parse Lung-RADS categories.

Reuses the generic report-fetch layer from mammo_report_fetcher (demo_diff.asp
+ #text2 scrape). Case list comes from ldct_<scope>_cases.json (ldct_cases.py).

Must run on the hospital intranet. Output contains report text + chart_no ->
output/ is gitignored. Never commit or share.

Usage:
  python ldct_report_fetcher.py --scope 33904_8 --limit 3   # small test first
  python ldct_report_fetcher.py --scope 33904_8             # full run
  python ldct_report_fetcher.py --scope 33904_8 --stats     # count only, no fetch
"""

import argparse
import json
import re
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

from mammo_report_fetcher import fetch_report, read_iuser, REPORTER

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
FETCH_INTERVAL = 1.0

CHECKED = "■"    # ■ 已勾選
UNCHECKED = "□"  # □ 未勾選

# 報告是 Big5，抓下來常是 latin-1 誤解碼的亂碼，先還原
def fix_encoding(text: str | None) -> str | None:
    if not text or CHECKED in text or UNCHECKED in text:
        return text
    try:
        return text.encode("latin-1").decode("cp950")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


# 「Overall recommendation」區塊內，被勾選的 Category 行才是結論。
# 下方 Airway nodule / Atypical pulmonary cyst 也有 (Category 2/3/4A/4B)，
# 那是子選項，不可當作整體判讀。
_CAT_LINE = re.compile(
    rf"^\s*([{CHECKED}{UNCHECKED}])\s*Category\s*(\d)\s*([AB](?:/4X)?)?\s*:",
    re.MULTILINE,
)
_MOD_S = re.compile(rf"^\s*([{CHECKED}{UNCHECKED}])\s*Modifier\s*S\b", re.MULTILINE)


def _overall_block(text: str) -> str:
    """只取 Overall recommendation ~ LDCT Quality 之間。"""
    lo = text.find("Overall recommendation")
    if lo < 0:
        return ""
    hi = text.find("LDCT Quality", lo)
    return text[lo: hi if hi > 0 else len(text)]


def parse_lungrads(text: str | None) -> dict:
    """依勾選框判讀。回傳 main(0-4) / full('4A','4B/4X') / modifier_s / issue。

    issue 不是 None 就代表這份需要人工確認，數字不可直接採用。
    """
    empty = {"main": None, "full": None, "modifier_s": None, "checked": [], "issue": None}
    text = fix_encoding(text)
    if not text:
        return {**empty, "issue": "no_text"}
    blk = _overall_block(text)
    if not blk:
        return {**empty, "issue": "no_overall_block"}

    checked = [(int(n), (suf or "").strip()) for mark, n, suf in _CAT_LINE.findall(blk)
               if mark == CHECKED]
    ms = _MOD_S.findall(blk)
    modifier_s = (ms[0] == CHECKED) if ms else None

    if not checked:
        return {**empty, "modifier_s": modifier_s, "issue": "no_category_checked"}
    if len(checked) > 1:
        return {"main": max(n for n, _ in checked),
                "full": None, "modifier_s": modifier_s,
                "checked": [f"{n}{s}" for n, s in checked],
                "issue": "multiple_categories_checked"}

    n, suf = checked[0]
    return {"main": n, "full": f"{n}{suf}" if suf else str(n),
            "modifier_s": modifier_s, "checked": [f"{n}{suf}" if suf else str(n)],
            "issue": None}


def cases_path(scope: str) -> Path:
    return OUTPUT_DIR / f"ldct_{scope}_cases.json"


def reports_path(scope: str) -> Path:
    return OUTPUT_DIR / f"ldct_{scope}_reports.json"


def _load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def summarize(reports: list[dict]) -> dict:
    cat = Counter()
    full = Counter()
    for r in reports:
        if r.get("status") != "fetched":
            cat["fetch_failed"] += 1
            continue
        m = r.get("lungrads_main")
        cat[m if m is not None else "unparsed"] += 1
        if r.get("lungrads_full"):
            full[r["lungrads_full"]] += 1
    return {"by_main": dict(cat), "by_full": dict(full)}


def run(scope: str, limit: int | None, reporter: str) -> dict:
    cases = _load_json(cases_path(scope), {}).get("cases", [])
    if not cases:
        raise SystemExit(f"no cases in {cases_path(scope)} — run ldct_cases.py first")

    existing = {r["case_id"]: r for r in _load_json(reports_path(scope), {}).get("reports", [])}
    iuser = read_iuser(reporter)

    todo = [c for c in cases if existing.get(c["case_id"], {}).get("status") != "fetched"]
    if limit:
        todo = todo[:limit]
    print(f"cases={len(cases)}  already fetched={len(cases) - len([c for c in cases if existing.get(c['case_id'], {}).get('status') != 'fetched'])}  to fetch={len(todo)}")

    for i, c in enumerate(todo, 1):
        res = fetch_report(c["case_id"], iuser)
        lr = parse_lungrads(res.get("report_text"))
        existing[c["case_id"]] = {
            **{k: c.get(k) for k in ("case_id", "chart_no", "exec_date", "report_date")},
            "status": res["status"],
            "report_text": res.get("report_text"),
            "lungrads_main": lr["main"],
            "lungrads_full": lr["full"],
            "lungrads_modifier_s": lr["modifier_s"],
            "lungrads_checked": lr["checked"],
            "lungrads_issue": lr["issue"],
            "error": res.get("error"),
        }
        if i % 10 == 0 or i == len(todo):
            print(f"  {i}/{len(todo)}")
        if i < len(todo):
            time.sleep(FETCH_INTERVAL)

    # 舊檔可能是用先前版本的 parser 存的 -> 一律用現行規則重新判讀一次
    for r in existing.values():
        lr = parse_lungrads(r.get("report_text"))
        r.update(lungrads_main=lr["main"], lungrads_full=lr["full"],
                 lungrads_modifier_s=lr["modifier_s"],
                 lungrads_checked=lr["checked"], lungrads_issue=lr["issue"])
        r.pop("lungrads_all", None)
        r.pop("lungrads_conflict", None)

    reports = [existing[c["case_id"]] for c in cases if c["case_id"] in existing]
    data = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "scope": scope,
        "total": len(reports),
        "summary": summarize(reports),
        "reports": reports,
    }
    reports_path(scope).write_text(json.dumps(data, ensure_ascii=False, indent=2),
                                   encoding="utf-8")
    return data


def main() -> None:
    ap = argparse.ArgumentParser(description="Fetch LDCT reports and parse Lung-RADS.")
    ap.add_argument("--scope", default="33904_8")
    ap.add_argument("--limit", type=int, default=None, help="fetch at most N new reports")
    ap.add_argument("--reporter", default=REPORTER)
    ap.add_argument("--stats", action="store_true", help="re-summarize existing file, no fetch")
    args = ap.parse_args()

    if args.stats:
        d = _load_json(reports_path(args.scope), {})
        reps = d.get("reports", [])
        if not reps:
            raise SystemExit("no fetched reports yet")
        s = summarize(reps)
        print(json.dumps(s, ensure_ascii=False, indent=2))
        return

    data = run(args.scope, args.limit, args.reporter)
    print(json.dumps(data["summary"], ensure_ascii=False, indent=2))
    print(f"Saved -> {reports_path(args.scope)}")


if __name__ == "__main__":
    main()
