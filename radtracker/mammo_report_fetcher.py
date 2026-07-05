#!/usr/bin/env python3
"""Fetch monthly mammography reports and maintain BI-RADS 0 follow-up state."""

import argparse
import configparser
import html
import json
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode

FETCH_INTERVAL = 1.0
ALLOWED_START = 21
ALLOWED_END = 3
REPORTER = "A80748"

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
BIRADS0_PATH = OUTPUT_DIR / "mammo_birads0.json"
SETTINGS_PATH = BASE_DIR.parent / "ahk-scripts" / "radiologist_settings.ini"


def cases_path(month_str: str) -> Path:
    return OUTPUT_DIR / f"mammo_{month_str.replace('-', '')}_cases.json"


def reports_path(month_str: str) -> Path:
    return OUTPUT_DIR / f"mammo_{month_str.replace('-', '')}_reports.json"


def read_iuser(default: str = REPORTER) -> str:
    for encoding in ("utf-8-sig", "utf-16", "cp950"):
        config = configparser.ConfigParser()
        try:
            config.read(SETTINGS_PATH, encoding=encoding)
        except UnicodeError:
            continue
        if config.has_section("Login"):
            return config.get("Login", "Username", fallback=default).strip() or default
    return default


def in_allowed_window() -> bool:
    import os
    start = int(os.environ.get("MAMMO_WINDOW_START", ALLOWED_START))
    end = int(os.environ.get("MAMMO_WINDOW_END", ALLOWED_END))
    h = datetime.now().hour
    return h >= start or h < end


def _report_url(case_id: str, iuser: str, ihost: int = 14) -> str:
    query = urlencode({
        "ihost": ihost,
        "ichkcode": case_id[:15],
        "iitemseq": "01",
        "iuser": iuser,
    })
    return f"http://intranet.chimei.org.tw/intranet/chilin/rptdiff/demo_diff.asp?{query}"


def _clean_text(text: str | None) -> str | None:
    if text is None:
        return None
    cleaned = html.unescape(text).replace("\xa0", " ").strip()
    return cleaned or None


def fetch_report_requests(case_id: str, iuser: str, ihost: int = 14) -> str | None:
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        return None

    try:
        response = requests.get(_report_url(case_id, iuser, ihost), timeout=15)
        response.raise_for_status()
    except Exception:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    node = soup.find(id="text2")
    if node is None:
        return None
    return _clean_text(node.get_text("\n"))


def fetch_report_playwright(case_id: str, iuser: str, ihost: int = 14) -> str | None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None

    browser = None
    playwright = None
    try:
        playwright = sync_playwright().start()
        browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
        page = browser.contexts[0].pages[0] if browser.contexts and browser.contexts[0].pages else browser.new_page()
        page.goto(_report_url(case_id, iuser, ihost), wait_until="domcontentloaded")
        return _clean_text(page.locator("#text2").inner_text(timeout=10000))
    except Exception:
        return None
    finally:
        if browser is not None:
            browser.close()
        if playwright is not None:
            playwright.stop()


def _playwright_available() -> bool:
    try:
        import playwright.sync_api  # noqa: F401
    except ImportError:
        return False
    return True


def parse_birads(report_text: str | None) -> int | None:
    if not report_text:
        return None
    match = re.search(r"BI-RADS[^\n]*Category\s*:?\s*(\d)", report_text, re.IGNORECASE)
    if not match:
        match = re.search(
            r"BI-RADS\s+assessment\s*:\s*[\r\n]+\s*Category\s*:?\s*(\d)",
            report_text,
            re.IGNORECASE,
        )
    return int(match.group(1)) if match else None


def fetch_report(case_id: str, iuser: str) -> dict:
    text = fetch_report_requests(case_id, iuser)
    if text is None:
        text = fetch_report_playwright(case_id, iuser)

    if text:
        return {
            "status": "fetched",
            "report_text": text,
            "birads_category": parse_birads(text),
            "error": None,
        }

    return {
        "status": "fetch_failed",
        "report_text": None,
        "birads_category": None,
        "error": "playwright_unavailable" if not _playwright_available() else "empty_content",
    }


def _load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def _write_json(path: Path, data: dict) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _summarize_reports(reports: list[dict]) -> tuple[int, int]:
    total_fetched = sum(1 for item in reports if item.get("status") == "fetched")
    total_failed = sum(1 for item in reports if item.get("status") == "fetch_failed")
    return total_fetched, total_failed


def _write_reports(month_str: str, report_map: dict[str, dict]) -> dict:
    reports = list(report_map.values())
    total_fetched, total_failed = _summarize_reports(reports)
    data = {
        "month": month_str,
        "generated": datetime.now().isoformat(),
        "total_fetched": total_fetched,
        "total_failed": total_failed,
        "reports": reports,
    }
    _write_json(reports_path(month_str), data)
    return data


def run_batch(month_str: str, csv_dir: str | None = None, reporter: str = REPORTER) -> dict | None:
    if not in_allowed_window():
        print("Outside allowed window (21:00-03:00)")
        return None

    case_data = _load_json(cases_path(month_str), None)
    if case_data is None:
        if csv_dir is None:
            csv_dir = str(BASE_DIR / "csv_input")
        from mammo_tracker import get_mammo_cases
        case_data = get_mammo_cases(csv_dir, month_str, reporter)

    existing = _load_json(reports_path(month_str), {"reports": []})
    report_map = {
        item["case_id"]: item
        for item in existing.get("reports", [])
        if item.get("case_id")
    }
    iuser = read_iuser(reporter)

    for case in case_data.get("cases", []):
        case_id = case["case_id"]
        if report_map.get(case_id, {}).get("status") == "fetched":
            continue
        if not in_allowed_window():
            break

        fetched = fetch_report(case_id, iuser)
        report_map[case_id] = {
            "case_id": case_id,
            "chart_no": case.get("chart_no", ""),
            "report_date": case.get("report_date"),
            "status": fetched["status"],
            "birads_category": fetched["birads_category"],
            "report_text": fetched["report_text"],
            "error": fetched["error"],
        }
        _write_reports(month_str, report_map)
        time.sleep(FETCH_INTERVAL)

    return _write_reports(month_str, report_map)


def update_birads0_tracker(month_str: str) -> dict:
    reports_data = _load_json(reports_path(month_str), {"reports": []})
    tracker = _load_json(BIRADS0_PATH, {"cases": []})
    existing = {
        item.get("case_id"): item
        for item in tracker.get("cases", [])
        if item.get("case_id")
    }

    for report in reports_data.get("reports", []):
        if report.get("birads_category") != 0:
            continue
        case_id = report.get("case_id")
        if not case_id or case_id in existing:
            continue
        report_date = datetime.strptime(report["report_date"], "%Y-%m-%d")
        existing[case_id] = {
            "case_id": case_id,
            "chart_no": report.get("chart_no", ""),
            "report_date": report.get("report_date"),
            "recall_month": month_str,
            "followup_due": (report_date + timedelta(days=90)).strftime("%Y-%m-%d"),
            "status": "pending",
            "outcome": None,
            "notes": "",
        }

    data = {"cases": list(existing.values()), "generated": datetime.now().isoformat()}
    data["cases"].sort(key=lambda item: (item.get("followup_due") or "", item.get("case_id") or ""))
    _write_json(BIRADS0_PATH, data)
    return data


def list_birads0() -> None:
    tracker = _load_json(BIRADS0_PATH, {"cases": []})
    rows = [item for item in tracker.get("cases", []) if item.get("status") == "pending"]
    print(f"{'case_id':<18} {'chart_no':<12} {'report_date':<12} {'followup_due':<12} {'outcome':<16} notes")
    print("-" * 104)
    for item in rows:
        print(
            f"{item.get('case_id', ''):<18} "
            f"{item.get('chart_no', ''):<12} "
            f"{item.get('report_date', ''):<12} "
            f"{item.get('followup_due', ''):<12} "
            f"{item.get('outcome') or '':<16} "
            f"{item.get('notes') or ''}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch mammography reports.")
    parser.add_argument("--month", help="Month in YYYY-MM format")
    parser.add_argument("--csv-dir", default=str(BASE_DIR / "csv_input"))
    parser.add_argument("--reporter", default=REPORTER)
    parser.add_argument("--list-birads0", action="store_true")
    args = parser.parse_args()

    if args.list_birads0:
        list_birads0()
        return
    if not args.month:
        parser.error("--month is required unless --list-birads0 is used")

    run_batch(args.month, args.csv_dir, args.reporter)
    update_birads0_tracker(args.month)


if __name__ == "__main__":
    main()
