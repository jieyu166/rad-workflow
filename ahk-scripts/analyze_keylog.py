#!/usr/bin/env python3
"""Analyze AHK keylog files and output structured JSON report.

Usage:
    python analyze_keylog.py logs/keylog_20260321.log
    python analyze_keylog.py logs/keylog_20260321.log -o keylog_report.json
    python analyze_keylog.py logs/keylog_20260321.log --summary   # console only
"""
import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path


# --- Constants ---
WORK_CLASSES = {'ThunderRT6FormDC', '#32770', 'AutoHotkeyGUI'}
WORK_TITLE_KEYWORDS = {'chk060', 'Mammo', 'BMD', 'INFINITT', 'qrylab'}
STUDY_TITLE_KEYWORDS = {'Obsidian'}
REPORT_CLASSES = {'ThunderRT6FormDC'}
REPORT_TITLE_KEYWORD = 'chk060'
SESSION_GAP_SEC = 30
HEAVY_SESSION_THRESHOLD = 50


def load_keylog(filepath):
    """Load keylog TSV file, return list of dicts."""
    rows = []
    with open(filepath, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for r in reader:
            if 'timestamp' in r and r['timestamp']:
                rows.append(r)
    return rows


def classify_window(row):
    """Classify a keystroke as work, study, or nonwork."""
    wc = row.get('window_class', '')
    wt = row.get('window_title', '')
    if wc in WORK_CLASSES:
        return 'work'
    for kw in WORK_TITLE_KEYWORDS:
        if kw in wt:
            return 'work'
    for kw in STUDY_TITLE_KEYWORDS:
        if kw in wt:
            return 'study'
    return 'nonwork'


def is_report_window(row):
    """Check if keystroke is in chk060 report window."""
    return (row.get('window_class', '') in REPORT_CLASSES and
            REPORT_TITLE_KEYWORD in row.get('window_title', ''))


def extract_hotstrings(rows):
    """Extract hotstring triggers (sequences ending with ;) from report rows."""
    hotstrings = Counter()
    buf = ''
    for r in rows:
        k = r['key']
        if len(k) == 1 and k.isprintable():
            buf += k
            if k == ';':
                if len(buf) >= 2:
                    hotstrings[buf.upper()] += 1
                buf = ''
        else:
            buf = ''
    return hotstrings


def extract_typed_words(keys):
    """Extract typed words from a sequence of keys."""
    buf = ''
    words = []
    for k in keys:
        if len(k) == 1 and k.isprintable():
            buf += k
        else:
            if len(buf) >= 3:
                words.append(buf)
            buf = ''
    if len(buf) >= 3:
        words.append(buf)
    return words


def split_sessions(rows, gap_sec=SESSION_GAP_SEC):
    """Split rows into sessions based on time gaps."""
    if not rows:
        return []
    sessions = []
    cur = [rows[0]]
    for i in range(1, len(rows)):
        t1 = datetime.strptime(cur[-1]['timestamp'], '%Y-%m-%d %H:%M:%S')
        t2 = datetime.strptime(rows[i]['timestamp'], '%Y-%m-%d %H:%M:%S')
        if (t2 - t1).total_seconds() > gap_sec:
            sessions.append(cur)
            cur = [rows[i]]
        else:
            cur.append(rows[i])
    if cur:
        sessions.append(cur)
    return sessions


def analyze_sessions(sessions):
    """Analyze report sessions for heavy typing and patterns."""
    results = []
    for i, sess in enumerate(sessions):
        keys = [r['key'] for r in sess]
        t_start = sess[0]['timestamp']
        t_end = sess[-1]['timestamp']
        char_keys = sum(1 for k in keys if len(k) == 1)
        f4_count = keys.count('F4')
        paste_count = keys.count('^V')
        up_count = keys.count('Up')
        down_count = keys.count('Down')
        del_count = keys.count('Delete')
        words = extract_typed_words(keys)

        results.append({
            'index': i + 1,
            'start': t_start,
            'end': t_end,
            'total_keys': len(keys),
            'char_keys': char_keys,
            'f4': f4_count,
            'paste': paste_count,
            'up': up_count,
            'down': down_count,
            'delete': del_count,
            'heavy': len(keys) > HEAVY_SESSION_THRESHOLD,
            'typed_preview': ' '.join(words[:12]),
        })
    return results


def analyze_keylog(filepath):
    """Main analysis function. Returns structured dict."""
    rows = load_keylog(filepath)
    if not rows:
        return {'error': 'No data found'}

    date = Path(filepath).stem.replace('keylog_', '')

    # --- Time range ---
    t_first = rows[0]['timestamp']
    t_last = rows[-1]['timestamp']

    # --- Hourly distribution ---
    hourly = Counter()
    for r in rows:
        h = r['timestamp'].split(' ')[1].split(':')[0]
        hourly[h] += 1

    # --- Window distribution ---
    window_counts = Counter()
    for r in rows:
        wt = r.get('window_title', '').split(' ')[0][:30]
        wc = r.get('window_class', '')
        window_counts[f'{wt} ({wc})'] += 1

    # --- Work vs study vs non-work ---
    classifications = Counter(classify_window(r) for r in rows)
    work_count = classifications.get('work', 0)
    study_count = classifications.get('study', 0)
    nonwork_count = classifications.get('nonwork', 0)

    # --- Report window analysis ---
    report_rows = [r for r in rows if is_report_window(r)]

    # --- Hotstrings ---
    hotstrings = extract_hotstrings(report_rows)

    # --- Sessions ---
    sessions = split_sessions(report_rows)
    session_analysis = analyze_sessions(sessions)
    heavy_sessions = [s for s in session_analysis if s['heavy']]

    # --- Key frequency in report window ---
    report_keys = Counter(r['key'] for r in report_rows)

    # --- Typing stats ---
    total_chars = sum(1 for r in report_rows if len(r['key']) == 1)
    total_special = len(report_rows) - total_chars

    # --- Build output ---
    result = {
        'file': str(filepath),
        'date': date,
        'total_keystrokes': len(rows),
        'time_range': {'start': t_first, 'end': t_last},

        'hourly': {h: hourly[h] for h in sorted(hourly.keys())},

        'windows': {w: c for w, c in window_counts.most_common(10)},

        'work_ratio': {
            'work': work_count,
            'study': study_count,
            'nonwork': nonwork_count,
            'work_pct': round(work_count * 100 / len(rows), 1) if rows else 0,
            'study_pct': round(study_count * 100 / len(rows), 1) if rows else 0,
            'nonwork_pct': round(nonwork_count * 100 / len(rows), 1) if rows else 0,
        },

        'report_window': {
            'total_keys': len(report_rows),
            'char_keys': total_chars,
            'special_keys': total_special,
            'char_pct': round(total_chars * 100 / len(report_rows), 1) if report_rows else 0,
        },

        'hotstrings': {hs: c for hs, c in hotstrings.most_common(20)},

        'sessions': {
            'total': len(sessions),
            'heavy_count': len(heavy_sessions),
            'heavy_sessions': heavy_sessions[:10],
        },

        'top_keys': {k: c for k, c in report_keys.most_common(30)},
    }

    return result


def print_summary(data):
    """Print human-readable summary to console (cp950-safe)."""
    print(f"===== {data['date']} ({data['total_keystrokes']} keystrokes) =====")
    print(f"Time: {data['time_range']['start']} ~ {data['time_range']['end']}")

    print("\nHourly:")
    for h, c in sorted(data['hourly'].items()):
        bar = '#' * (c // 20)
        print(f"  {h}:00 {c:5d} {bar}")

    wr = data['work_ratio']
    print(f"\nWork: {wr['work']} ({wr['work_pct']}%) / Study: {wr['study']} ({wr['study_pct']}%) / Other: {wr['nonwork']} ({wr['nonwork_pct']}%)")

    rw = data['report_window']
    print(f"\nReport window: {rw['total_keys']} keys (char {rw['char_pct']}%)")

    print("\nHotstrings:")
    for hs, c in list(data['hotstrings'].items())[:15]:
        print(f"  {hs:15s} x{c}")

    ss = data['sessions']
    print(f"\nSessions: {ss['total']} total, {ss['heavy_count']} heavy (>{HEAVY_SESSION_THRESHOLD} keys)")
    for s in ss['heavy_sessions'][:5]:
        t = s['start'].split(' ')[1]
        print(f"  #{s['index']} {t} keys={s['total_keys']} typed: {s['typed_preview']}")


def main():
    parser = argparse.ArgumentParser(description='Analyze AHK keylog files')
    parser.add_argument('logfile', help='Path to keylog TSV file')
    parser.add_argument('-o', '--output', help='Output JSON path (default: stdout summary)')
    parser.add_argument('--summary', action='store_true', help='Print console summary')
    args = parser.parse_args()

    data = analyze_keylog(args.logfile)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Report saved to {args.output}")

    if args.summary or not args.output:
        print_summary(data)


if __name__ == '__main__':
    main()
