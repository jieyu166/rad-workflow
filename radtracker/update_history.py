#!/usr/bin/env python3
"""Update history.json with data from a weekly report JSON.

Usage:
    python update_history.py output/weekly_report.json
    python update_history.py output/w12_midweek.json --notes "mid-week snapshot"
"""
import json
import sys
import argparse
from pathlib import Path

HISTORY_FILE = Path(__file__).parent / 'history.json'

# Map display names to history keys
MOD_MAP = {'X光': 'xr', 'CT': 'ct', 'US': 'us', 'Mammo': 'mammo',
           'MR': 'mr', 'BMD': 'bmd', 'IVP': 'ivp'}
DAY_MAP = {'一': 'mon', '二': 'tue', '三': 'wed', '四': 'thu',
           '五': 'fri', '六': 'sat', '日': 'sun'}


def load_history():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, encoding='utf-8') as f:
            return json.load(f)
    return {'weeks': []}


def save_history(data):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Updated: {HISTORY_FILE}")


def extract_from_report(report, notes=''):
    """Extract history entry from generate_report.py output."""
    meta = report.get('metadata', {})
    week_id = meta.get('week', '')
    source = report.get('source', 'csv')

    # Tracking
    tracking_raw = report.get('tracking', {})
    tracking = {
        'start': {}, 'end': {}, 'net_change': {}
    }
    total_net = 0
    for mod_display, data in tracking_raw.items():
        key = MOD_MAP.get(mod_display, mod_display.lower())
        if isinstance(data, dict):
            tracking['start'][key] = data.get('start', 0)
            tracking['end'][key] = data.get('end', 0)
            tracking['net_change'][key] = data.get('net', 0)
            total_net += data.get('net', 0)
    tracking['total_net'] = total_net

    # Completed
    totals = report.get('totals', {})
    mods = totals.get('mods', {})
    completed = {}
    for mod_display, count in mods.items():
        key = MOD_MAP.get(mod_display, mod_display.lower())
        completed[key] = count

    # Added (estimated)
    added = {}
    for mod_display, data in tracking_raw.items():
        key = MOD_MAP.get(mod_display, mod_display.lower())
        if isinstance(data, dict) and 'added' in data:
            added[key] = f">={data['added']}"

    # Time
    time_data = {
        'report_hr': totals.get('active_hr', None),
        'clinical_hr': None,
        'study_hr': 0,
    }

    # Totals
    totals_out = {
        'grand_total': totals.get('grand_total', totals.get('cases', 0)),
        'points': totals.get('points', None),
    }

    # Efficiency daily avg
    eff_daily = report.get('efficiency_daily', {})
    if eff_daily:
        total_cases = sum(d.get('cases', 0) for d in eff_daily.values())
        total_hr = sum(d.get('active_hr', 0) for d in eff_daily.values())
        eff_avg = {
            'cases_per_hr': round(total_cases / total_hr, 1) if total_hr > 0 else 0,
        }
        if totals.get('points'):
            eff_avg['points_per_hr'] = round(totals['points'] / total_hr, 1) if total_hr > 0 else 0
    else:
        eff_avg = {}

    # Daily breakdown
    daily_raw = report.get('daily', {})
    daily = {}
    for day_zh, data in daily_raw.items():
        day_en = DAY_MAP.get(day_zh, day_zh)
        if isinstance(data, dict) and data.get('cases', 0) > 0:
            entry = {'total': data['cases']}
            if data.get('active_hr'):
                entry['active_hr'] = data['active_hr']
            if data.get('points'):
                entry['points'] = data['points']
            # Modality counts
            for mod in ('XR', 'CT', 'US', 'Mammo', 'BMD', 'IVP', 'MR'):
                if data.get(mod, 0) > 0:
                    entry[mod.lower()] = data[mod]
            daily[day_en] = entry

    entry = {
        'week_id': week_id,
        'date_range': meta.get('date_range', ''),
        'source': f"{', '.join(meta.get('csv_files', []))} ({source} mode)",
        'tracking': tracking,
        'completed': completed,
        'added_estimated': added,
        'time': time_data,
        'totals': totals_out,
    }
    if eff_avg:
        entry['efficiency_daily_avg'] = eff_avg
    if daily:
        entry['daily'] = daily
    if notes:
        entry['notes'] = notes

    return entry


def extract_from_midweek(report, notes=''):
    """Extract from parse_csv.py midweek output (different format)."""
    meta = report.get('metadata', {})
    week_id = meta.get('week', '')

    totals = report.get('totals', {})
    mods = totals.get('mods', {})
    completed = {}
    for mod, count in mods.items():
        completed[mod.lower()] = count

    daily_raw = report.get('daily', {})
    daily = {}
    for day_zh, data in daily_raw.items():
        day_en = DAY_MAP.get(day_zh, day_zh)
        if isinstance(data, dict) and data.get('cases', 0) > 0:
            entry = {'total': data['cases']}
            if data.get('active_hr'):
                entry['active_hr'] = data['active_hr']
            if data.get('points'):
                entry['points'] = data['points']
            for mod in ('XR', 'CT', 'US', 'Mammo', 'BMD', 'IVP', 'MR'):
                if data.get(mod, 0) > 0:
                    entry[mod.lower()] = data[mod]
            daily[day_en] = entry

    entry = {
        'week_id': week_id,
        'date_range': meta.get('date_range', ''),
        'source': f"{', '.join(meta.get('csv_files', []))} (midweek)",
        'completed': completed,
        'time': {
            'report_hr': totals.get('active_hr'),
            'clinical_hr': None,
            'study_hr': 0,
        },
        'totals': {
            'grand_total': totals.get('grand_total', totals.get('cases', 0)),
            'points': totals.get('points'),
        },
    }
    if daily:
        entry['daily'] = daily
    if notes:
        entry['notes'] = notes
    return entry


def main():
    parser = argparse.ArgumentParser(description='Update history.json from report JSON')
    parser.add_argument('report', help='Path to weekly_report.json or midweek JSON')
    parser.add_argument('--notes', default='', help='Optional notes for this entry')
    parser.add_argument('--force', action='store_true', help='Overwrite existing week entry')
    args = parser.parse_args()

    with open(args.report, encoding='utf-8') as f:
        report = json.load(f)

    # Detect format: generate_report output has "source" key at top level
    if 'source' in report and 'tracking' in report:
        entry = extract_from_report(report, args.notes)
    else:
        entry = extract_from_midweek(report, args.notes)

    week_id = entry['week_id']
    if not week_id:
        print("Error: cannot determine week_id from report", file=sys.stderr)
        sys.exit(1)

    history = load_history()

    # Check for duplicates
    existing_idx = None
    for i, w in enumerate(history['weeks']):
        if w.get('week_id') == week_id:
            existing_idx = i
            break

    if existing_idx is not None:
        if args.force:
            history['weeks'][existing_idx] = entry
            print(f"Replaced: {week_id}")
        else:
            print(f"Week {week_id} already exists. Use --force to overwrite.")
            sys.exit(1)
    else:
        history['weeks'].append(entry)
        print(f"Appended: {week_id}")

    save_history(history)


if __name__ == '__main__':
    main()
