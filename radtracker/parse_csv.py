#!/usr/bin/env python3
"""
parse_csv.py — 解析醫院匯出 CSV，產出標準化週報中間 JSON

Usage:
    python parse_csv.py 202602.csv --week 2026-W09 --output parsed_W09.json
    python parse_csv.py 202602.csv --yk 202602YK.csv --week 2026-W09 --output parsed_W09.json

CSV 格式：cp950 (Big5) 編碼，Tab 分隔，31 欄
"""

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

# ── Column mapping (0-indexed) ────────────────────────────────────────────
COL_CASE_ID = 0       # 案號
COL_CHART_NO = 1      # 病歷號
COL_ORDER_DATE = 3    # 開單日 (MM/DD/YYYY)
COL_SOURCE = 4        # 來源: 1=急診, 2=門診, 3=住院, 4=健檢
COL_DEPT = 5          # 科別 (S101, S103, etc.)
COL_ORDER_CODE = 6    # 醫令代碼
COL_QTY = 7           # 次數
COL_EXAM_NAME = 8     # 項目 (exam name)
COL_REPORT_DATE = 13  # 報告日期 (MM/DD/YYYY)
COL_REPORT_TIME = 14  # 報告時間 (HH:MM)
COL_REPORTER_ID = 17  # 報告醫師ID
COL_WORK_POINTS = 24  # 工作點值
COL_WEIGHTED_PTS = 28 # 加權點值

# ── Constants ─────────────────────────────────────────────────────────────
WEEKDAY_NAMES = ['一', '二', '三', '四', '五', '六', '日']
DAY_ORDER = ['一', '二', '三', '四', '五', '六', '日']
TRACKED_MODS = ['XR', 'CT', 'US', 'Mammo']
ALL_MODS = ['XR', 'CT', 'US', 'Mammo', 'MR', 'BMD', 'IVP', 'Other']

# US sub-types considered 困難
HARD_US = {
    'US-Breast', 'US-Prostate', 'US-Extremity',
    'US-Lower Extremity A.', 'US-Lower Extremity V.',
    'US-Scrotum', 'US-Parotid Gland', 'US-Other',
}

# Baselines from claude.md (for efficiency comparison)
BASELINES = {
    'XR(普通)': 50, 'XR(急打)': 35, 'XR(中等)': 30, 'XR(困難)': 20,
    'CT(Chest/Abd)': 3.5, 'CT(Brain)': 7, 'CT(Neck/CTA)': 3.5, 'CT(Brain-C)': 3,
    'US(一般)': 18, 'US(困難)': 4,
    'Mammo': 22, 'MR': 2, 'IVP': 12, 'BMD': 60,
}


# ── CSV Reading ───────────────────────────────────────────────────────────

def read_csv(path: str) -> list[dict]:
    """Read a cp950-encoded TSV file and return list of row dicts."""
    rows = []
    with open(path, 'rb') as f:
        raw = f.read()
    text = raw.decode('cp950', errors='replace')
    lines = text.strip().split('\n')

    for line in lines[1:]:  # skip header
        cols = line.strip('\r').split('\t')
        if len(cols) < 25:
            continue
        rows.append({
            'case_id': cols[COL_CASE_ID].strip(),
            'chart_no': cols[COL_CHART_NO].strip(),
            'order_date': cols[COL_ORDER_DATE].strip(),
            'source': cols[COL_SOURCE].strip(),
            'dept': cols[COL_DEPT].strip(),
            'order_code': cols[COL_ORDER_CODE].strip(),
            'qty': cols[COL_QTY].strip(),
            'exam_name': cols[COL_EXAM_NAME].strip(),
            'report_date': cols[COL_REPORT_DATE].strip(),
            'report_time': cols[COL_REPORT_TIME].strip(),
            'reporter_id': cols[COL_REPORTER_ID].strip(),
            'work_points': cols[COL_WORK_POINTS].strip(),
            'weighted_pts': cols[COL_WEIGHTED_PTS].strip() if len(cols) > COL_WEIGHTED_PTS else '0',
        })
    return rows


# ── Filtering ─────────────────────────────────────────────────────────────

def filter_rows(rows: list[dict], reporter_id: str,
                date_start: datetime, date_end: datetime) -> list[dict]:
    """Filter rows by reporter, date range, and exclude contrast-only."""
    filtered = []
    for r in rows:
        # Reporter filter
        if r['reporter_id'] != reporter_id:
            continue
        # Exclude contrast-only rows (work_points == 0 and name contains Contrast)
        if 'Contrast' in r['exam_name']:
            try:
                pts = float(r['work_points'])
                if pts == 0:
                    continue
            except ValueError:
                continue
        # Date range filter
        try:
            rpt_date = datetime.strptime(r['report_date'], '%m/%d/%Y')
        except ValueError:
            continue
        if rpt_date < date_start or rpt_date > date_end:
            continue
        filtered.append(r)
    return filtered


# ── Modality Classification ───────────────────────────────────────────────

def classify_modality(exam_name: str) -> str:
    """Classify exam_name into modality."""
    e = exam_name.strip()
    if e.startswith('CT-') or e.startswith('CTA-'):
        return 'CT'
    if 'Low Dose CT' in e or 'LDCT' in e:
        return 'CT'
    if 'HRCT' in e:
        return 'CT'
    if e.startswith('US-'):
        return 'US'
    if 'Mammography' in e:
        return 'Mammo'
    if e.startswith('MR') or 'MRI' in e:
        return 'MR'
    if 'Bone densitometry' in e:
        return 'BMD'
    if 'I.V.P.' in e or 'IVP' in e:
        return 'IVP'
    if 'Contrast' in e:
        return '_contrast'  # should be filtered already
    return 'XR'


def classify_ct_subtype(exam_name: str, order_code: str) -> str:
    """Classify CT sub-type."""
    e = exam_name.strip()
    if 'Brain' in e or 'Head' in e:
        # Check if contrast study (order code 33072 = with contrast)
        if '33072' in order_code or '33090' in order_code:
            return 'Brain-C'
        return 'Brain'
    if 'Neck' in e or 'C-Spine' in e or 'C Spine' in e:
        return 'Neck/CTA'
    if e.startswith('CTA-'):
        return 'Neck/CTA'
    return 'Chest/Abd'


def classify_us_subtype(exam_name: str) -> str:
    """Classify US difficulty."""
    if exam_name.strip() in HARD_US:
        return '困難'
    return '一般'


# ── Case Grouping ─────────────────────────────────────────────────────────

def group_cases(rows: list[dict]) -> list[dict]:
    """Group rows by case_id into logical exam cases."""
    groups = defaultdict(list)
    for r in rows:
        groups[r['case_id']].append(r)

    cases = []
    for case_id, case_rows in groups.items():
        # Skip if no rows (shouldn't happen after filtering)
        if not case_rows:
            continue

        # Determine modality from first non-contrast row
        modality = classify_modality(case_rows[0]['exam_name'])
        if modality == '_contrast':
            continue

        # Unique exam body parts (for difficulty classification)
        unique_exams = set()
        for r in case_rows:
            m = classify_modality(r['exam_name'])
            if m != '_contrast':
                unique_exams.add(r['exam_name'])

        # Sum work points
        total_points = 0
        for r in case_rows:
            try:
                total_points += float(r['work_points'])
            except ValueError:
                pass

        # CT sub-type (from first CT row)
        ct_subtype = None
        if modality == 'CT':
            ct_subtype = classify_ct_subtype(
                case_rows[0]['exam_name'], case_rows[0]['order_code'])

        # US sub-type
        us_subtype = None
        if modality == 'US':
            us_subtype = classify_us_subtype(case_rows[0]['exam_name'])

        cases.append({
            'case_id': case_id,
            'modality': modality,
            'unique_exam_count': len(unique_exams),
            'unique_exams': sorted(unique_exams),
            'report_date': case_rows[0]['report_date'],
            'report_time': case_rows[0]['report_time'],
            'source': case_rows[0]['source'],
            'dept': case_rows[0]['dept'],
            'total_points': round(total_points, 2),
            'primary_exam': case_rows[0]['exam_name'],
            'ct_subtype': ct_subtype,
            'us_subtype': us_subtype,
            'row_count': len(case_rows),
        })

    return cases


# ── Difficulty Classification ─────────────────────────────────────────────

def classify_difficulty(case: dict) -> str:
    """Classify XR difficulty. Returns 普通/急打/中等/困難."""
    if case['modality'] != 'XR':
        return None

    # 急打: source 1(急診) or 3(住院)
    if case['source'] in ('1', '3'):
        return '急打'

    # Non-urgent: by unique exam count
    n = case['unique_exam_count']
    if n >= 3:
        return '困難'
    if n == 2:
        return '中等'
    return '普通'


# ── Date Attribution ──────────────────────────────────────────────────────

def get_work_date(report_date_str: str, report_time_str: str) -> tuple[str, str]:
    """Apply late-night rule: 00:00-05:59 → previous day.
    Returns (work_date as YYYY/MM/DD, weekday name)."""
    try:
        dt = datetime.strptime(report_date_str, '%m/%d/%Y')
    except ValueError:
        return report_date_str, '?'

    # Parse time
    try:
        parts = report_time_str.split(':')
        hour = int(parts[0])
    except (ValueError, IndexError):
        hour = 12  # default to noon if unparseable

    if hour < 6:
        dt = dt - timedelta(days=1)

    weekday_name = WEEKDAY_NAMES[dt.weekday()]
    return dt.strftime('%Y/%m/%d'), weekday_name


# ── Time Estimation ───────────────────────────────────────────────────────

def estimate_daily_hours(timestamps: list[str]) -> dict:
    """Estimate active reporting hours from sorted HH:MM timestamps."""
    if not timestamps:
        return {'span_hr': 0, 'active_hr': 0, 'sessions': 0}

    times = []
    for ts in timestamps:
        try:
            parts = ts.split(':')
            h, m = int(parts[0]), int(parts[1])
            times.append(h * 60 + m)  # minutes since midnight
        except (ValueError, IndexError):
            continue

    if not times:
        return {'span_hr': 0, 'active_hr': 0, 'sessions': 0}

    times.sort()

    # Handle day-crossing: if we have both early morning (< 360 = 6:00)
    # and late night (> 1200 = 20:00) timestamps, the early ones are
    # already attributed to previous day by get_work_date, so we should
    # not see this case. But just in case, handle gracefully.

    # Total span
    span_min = times[-1] - times[0]

    # Session detection: gaps > 30 min
    sessions = 1
    active_min = 0
    session_start = times[0]

    for i in range(1, len(times)):
        gap = times[i] - times[i - 1]
        if gap > 30:
            # End current session
            active_min += times[i - 1] - session_start
            session_start = times[i]
            sessions += 1

    # Last session
    active_min += times[-1] - session_start

    # Minimum: at least 0.5 min per report
    active_min = max(active_min, len(times) * 0.5)

    return {
        'span_hr': round(span_min / 60, 1),
        'active_hr': round(active_min / 60, 1),
        'sessions': sessions,
    }


# ── Week Date Range ───────────────────────────────────────────────────────

def parse_week_range(week_str: str) -> tuple[datetime, datetime]:
    """Parse ISO week string like '2026-W09' into (Monday, Sunday) dates."""
    # Python's %G-%V-%u format: %G=ISO year, %V=ISO week, %u=weekday (1=Mon)
    monday = datetime.strptime(f'{week_str}-1', '%G-W%V-%u')
    sunday = monday + timedelta(days=6)
    return monday, sunday


# ── Main Processing ───────────────────────────────────────────────────────

def process_csvs(csv_paths: list[str], week_str: str,
                 reporter_id: str = 'A80748') -> dict:
    """Main processing: read CSVs → filter → group → classify → aggregate."""

    # Parse week range
    week_start, week_end = parse_week_range(week_str)
    # Extend end to include the full Sunday (plus early morning of next Monday)
    date_filter_end = week_end + timedelta(days=1, hours=6)

    # Read and merge all CSV files
    all_rows = []
    for path in csv_paths:
        rows = read_csv(path)
        all_rows.extend(rows)

    # Filter
    filtered = filter_rows(all_rows, reporter_id, week_start, date_filter_end)

    # Group by case_id
    cases = group_cases(filtered)

    # Add difficulty and work_date
    for c in cases:
        c['difficulty'] = classify_difficulty(c)
        work_date, weekday = get_work_date(c['report_date'], c['report_time'])
        c['work_date'] = work_date
        c['weekday'] = weekday

    # Filter to only cases whose work_date falls within the week
    week_cases = []
    for c in cases:
        try:
            wd = datetime.strptime(c['work_date'], '%Y/%m/%d')
            if week_start <= wd <= week_end:
                week_cases.append(c)
        except ValueError:
            pass

    # ── Aggregate daily ──────────────────────────────────────────────
    daily = {}
    for wd in DAY_ORDER:
        daily[wd] = {
            'cases': 0,
            'points': 0,
            'timestamps': [],
            **{m: 0 for m in ALL_MODS},
            'xr_sub': defaultdict(int),
            'ct_sub': defaultdict(int),
            'us_sub': defaultdict(int),
        }

    for c in week_cases:
        wd = c['weekday']
        if wd not in daily:
            continue
        d = daily[wd]
        mod = c['modality']

        d['cases'] += 1
        d['points'] += c['total_points']
        d['timestamps'].append(c['report_time'])

        if mod in d:
            d[mod] += 1

        if mod == 'XR' and c['difficulty']:
            d['xr_sub'][c['difficulty']] += 1
        elif mod == 'CT' and c['ct_subtype']:
            d['ct_sub'][c['ct_subtype']] += 1
        elif mod == 'US' and c['us_subtype']:
            d['us_sub'][c['us_subtype']] += 1

    # Estimate daily hours
    for wd in DAY_ORDER:
        d = daily[wd]
        time_est = estimate_daily_hours(d['timestamps'])
        d['active_hr'] = time_est['active_hr']
        d['span_hr'] = time_est['span_hr']
        d['session_count'] = time_est['sessions']
        d['report_count'] = len(d['timestamps'])
        # Clean up non-serializable
        del d['timestamps']

    # ── Totals ───────────────────────────────────────────────────────
    totals = {m: 0 for m in ALL_MODS}
    total_cases = 0
    total_points = 0
    total_active_hr = 0

    for wd in DAY_ORDER:
        d = daily[wd]
        for m in ALL_MODS:
            totals[m] += d[m]
        total_cases += d['cases']
        total_points += d['points']
        total_active_hr += d['active_hr']

    # ── Efficiency (per sub-category, daily-level) ───────────────────
    # Aggregate sub-category counts across all days
    sub_counts = defaultdict(lambda: {'count': 0, 'points': 0})
    for wd in DAY_ORDER:
        d = daily[wd]
        for diff, cnt in d['xr_sub'].items():
            sub_counts[f'XR({diff})']['count'] += cnt
        for sub, cnt in d['ct_sub'].items():
            sub_counts[f'CT({sub})']['count'] += cnt
        for sub, cnt in d['us_sub'].items():
            sub_counts[f'US({sub})']['count'] += cnt
        if d['Mammo'] > 0:
            sub_counts['Mammo']['count'] += d['Mammo']
        if d['MR'] > 0:
            sub_counts['MR']['count'] += d['MR']
        if d['BMD'] > 0:
            sub_counts['BMD']['count'] += d['BMD']
        if d['IVP'] > 0:
            sub_counts['IVP']['count'] += d['IVP']

    # Daily-level efficiency (total cases / total active hours)
    efficiency_daily = {}
    for wd in DAY_ORDER:
        d = daily[wd]
        if d['active_hr'] > 0 and d['cases'] > 0:
            efficiency_daily[wd] = {
                'cases': d['cases'],
                'active_hr': d['active_hr'],
                'rate': round(d['cases'] / d['active_hr'], 1),
                'estimated': True,
            }

    # ── Build output ─────────────────────────────────────────────────
    # Convert defaultdicts to regular dicts for JSON serialization
    daily_out = {}
    for wd in DAY_ORDER:
        d = daily[wd]
        day_data = {
            'cases': d['cases'],
            'points': round(d['points'], 1),
            'active_hr': d['active_hr'],
            'span_hr': d['span_hr'],
            'sessions': d['session_count'],
            'report_count': d['report_count'],
        }
        for m in ALL_MODS:
            if d[m] > 0:
                day_data[m] = d[m]
        if d['xr_sub']:
            day_data['xr_sub'] = dict(d['xr_sub'])
        if d['ct_sub']:
            day_data['ct_sub'] = dict(d['ct_sub'])
        if d['us_sub']:
            day_data['us_sub'] = dict(d['us_sub'])
        daily_out[wd] = day_data

    output = {
        'metadata': {
            'week': week_str,
            'date_range': f"{week_start.strftime('%m/%d')} ~ {week_end.strftime('%m/%d')}",
            'source': 'csv',
            'csv_files': csv_paths,
            'reporter_id': reporter_id,
            'total_csv_rows': len(all_rows),
            'filtered_rows': len(filtered),
            'total_cases': len(week_cases),
        },
        'daily': daily_out,
        'totals': {
            'mods': {m: totals[m] for m in ALL_MODS if totals[m] > 0},
            'cases': total_cases,
            'points': round(total_points, 1),
            'active_hr': round(total_active_hr, 1),
            'grand_total': sum(totals[m] for m in TRACKED_MODS),
        },
        'sub_counts': {k: dict(v) for k, v in sub_counts.items() if v['count'] > 0},
        'efficiency_daily': efficiency_daily,
    }

    return output


# ── CLI ───────────────────────────────────────────────────────────────────

def infer_week_from_filename(filepath):
    """Infer ISO week from ROC calendar filename like 1150319_JL.csv.
    ROC year 115 = 2026, so 1150319 = 2026/03/19 -> that date's ISO week."""
    name = Path(filepath).stem  # e.g., "1150319_JL"
    m = re.match(r'^(\d{3})(\d{2})(\d{2})', name)
    if m:
        roc_year = int(m.group(1))
        month = int(m.group(2))
        day = int(m.group(3))
        west_year = roc_year + 1911
        try:
            dt = datetime(west_year, month, day)
            iso_cal = dt.isocalendar()
            return f"{iso_cal[0]}-W{iso_cal[1]:02d}"
        except ValueError:
            pass
    # Also handle YYYYMM.csv -> use last day of month to get latest week
    m2 = re.match(r'^(\d{4})(\d{2})', name)
    if m2:
        year = int(m2.group(1))
        month = int(m2.group(2))
        # Last day of month
        if month == 12:
            last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = datetime(year, month + 1, 1) - timedelta(days=1)
        iso_cal = last_day.isocalendar()
        return f"{iso_cal[0]}-W{iso_cal[1]:02d}"
    return None


def main():
    parser = argparse.ArgumentParser(
        description='Parse hospital CSV exports for radiology weekly report')
    parser.add_argument('csv', nargs='+', help='CSV file(s) to parse (main + optional YK)')
    parser.add_argument('--week', default=None,
                        help='ISO week string, e.g., 2026-W09 (auto-inferred from ROC filename if omitted)')
    parser.add_argument('--reporter', default='A80748',
                        help='Reporter ID to filter (default: A80748)')
    parser.add_argument('-o', '--output', default=None,
                        help='Output JSON path (default: stdout)')

    args = parser.parse_args()

    # Auto-infer week from filename if not provided
    week = args.week
    if not week:
        for csv_path in args.csv:
            week = infer_week_from_filename(csv_path)
            if week:
                print(f"Auto-detected week: {week} (from {Path(csv_path).name})", file=sys.stderr)
                break
    if not week:
        print("Error: --week is required when week cannot be inferred from filename", file=sys.stderr)
        sys.exit(1)

    result = process_csvs(args.csv, week, args.reporter)

    # Print summary to stderr
    t = result['totals']
    print(f"=== parse_csv.py 結果摘要 ===", file=sys.stderr)
    print(f"週次: {result['metadata']['week']}", file=sys.stderr)
    print(f"日期: {result['metadata']['date_range']}", file=sys.stderr)
    print(f"CSV 總行數: {result['metadata']['total_csv_rows']}", file=sys.stderr)
    print(f"篩選後: {result['metadata']['filtered_rows']} 行", file=sys.stderr)
    print(f"分組後: {result['metadata']['total_cases']} 案件", file=sys.stderr)
    print(f"", file=sys.stderr)
    for m, cnt in t['mods'].items():
        print(f"  {m}: {cnt}", file=sys.stderr)
    print(f"  合計(四大模態): {t['grand_total']}", file=sys.stderr)
    print(f"  工作點值: {t['points']}", file=sys.stderr)
    print(f"  推估活躍時數: {t['active_hr']}hr", file=sys.stderr)
    print(f"", file=sys.stderr)

    print(f"── 每日 ──", file=sys.stderr)
    for wd in DAY_ORDER:
        d = result['daily'][wd]
        if d['cases'] > 0:
            mods_str = ' '.join(f"{m}={d[m]}" for m in ALL_MODS if d.get(m, 0) > 0)
            print(f"  {wd}: {d['cases']}案 / {d['active_hr']}hr "
                  f"/ {d['points']}pt  [{mods_str}]", file=sys.stderr)

    # Output JSON
    json_str = json.dumps(result, ensure_ascii=False, indent=2, default=str)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json_str, encoding='utf-8')
        print(f"\nJSON 已儲存: {args.output}", file=sys.stderr)
    else:
        print(json_str)


if __name__ == '__main__':
    main()
