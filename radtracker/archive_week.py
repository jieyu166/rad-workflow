#!/usr/bin/env python3
"""Archive current week's output files into output/W{nn}/ folder.

Usage:
    python archive_week.py                  # auto-detect from weekly_report.json
    python archive_week.py --week W12       # explicit week number
    python archive_week.py --dry-run        # show what would be moved
"""
import json
import re
import shutil
import argparse
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / 'output'

# Files to archive (glob patterns)
ARCHIVE_PATTERNS = [
    'weekly_report.json',
    'weekly_report.html',
    'w*_midweek*.json',
    'w*_midweek*.html',
    'w*_schedule*.html',
    'contribution_heatmap.html',
    'csv_report.json',
]


def detect_week():
    """Auto-detect week number from weekly_report.json."""
    report_file = OUTPUT_DIR / 'weekly_report.json'
    if report_file.exists():
        with open(report_file, encoding='utf-8') as f:
            data = json.load(f)
        week = data.get('metadata', {}).get('week', '')
        m = re.search(r'W(\d+)', week)
        if m:
            return int(m.group(1))

    # Fallback: check midweek files
    for p in OUTPUT_DIR.glob('w*_midweek*.json'):
        with open(p, encoding='utf-8') as f:
            data = json.load(f)
        week = data.get('metadata', {}).get('week', '')
        m = re.search(r'W(\d+)', week)
        if m:
            return int(m.group(1))

    return None


def archive(week_num, dry_run=False):
    """Move matching files to output/W{nn}/."""
    target = OUTPUT_DIR / f'W{week_num:02d}'

    # Collect files to move
    files_to_move = []
    for pattern in ARCHIVE_PATTERNS:
        for f in OUTPUT_DIR.glob(pattern):
            if f.is_file():
                files_to_move.append(f)

    if not files_to_move:
        print(f"No files to archive in {OUTPUT_DIR}")
        return

    if not dry_run:
        target.mkdir(parents=True, exist_ok=True)

    for f in files_to_move:
        dest = target / f.name
        if dry_run:
            print(f"  [dry-run] {f.name} -> W{week_num:02d}/{f.name}")
        else:
            if dest.exists():
                print(f"  [skip] {f.name} (already exists in W{week_num:02d}/)")
            else:
                shutil.move(str(f), str(dest))
                print(f"  [moved] {f.name} -> W{week_num:02d}/{f.name}")

    if not dry_run:
        print(f"Archived {len(files_to_move)} file(s) to {target}")


def main():
    parser = argparse.ArgumentParser(description='Archive weekly output files')
    parser.add_argument('--week', help='Week number (e.g., W12 or 12)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be moved')
    args = parser.parse_args()

    if args.week:
        m = re.search(r'(\d+)', args.week)
        week_num = int(m.group(1)) if m else None
    else:
        week_num = detect_week()

    if week_num is None:
        print("Error: cannot detect week number. Use --week W12", file=sys.stderr)
        import sys; sys.exit(1)

    print(f"Archiving to W{week_num:02d}/ {'(dry-run)' if args.dry_run else ''}")
    archive(week_num, args.dry_run)


if __name__ == '__main__':
    main()
