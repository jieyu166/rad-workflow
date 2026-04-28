#!/usr/bin/env python3
"""Aggregate typing patterns across multiple keylog files."""
import csv
import re
import sys
from collections import Counter
from pathlib import Path

REPORT_CLASSES = {'ThunderRT6FormDC'}
REPORT_TITLE_KEYWORD = 'chk060'
LONG_MIN = 12   # 連續可印字元 >= N
HOTSTRING_MAXLEN = 8  # 長度小於此且以 ; 結尾的視為 hotstring 觸發


def load(filepath):
    with open(filepath, encoding='utf-8-sig') as f:
        return [r for r in csv.DictReader(f, delimiter='\t') if r.get('timestamp')]


def in_report(row):
    return (row.get('window_class', '') in REPORT_CLASSES
            and REPORT_TITLE_KEYWORD in row.get('window_title', ''))


def extract_typings(rows):
    """Yield (timestamp, text) for each contiguous printable run >= LONG_MIN chars."""
    buf = ''
    buf_start = None
    for r in rows:
        k = r['key']
        if len(k) == 1 and k.isprintable():
            if not buf:
                buf_start = r['timestamp']
            buf += k
            if k == ';' and len(buf) <= HOTSTRING_MAXLEN:
                buf = ''
                buf_start = None
        else:
            if len(buf.strip()) >= LONG_MIN:
                yield buf_start, buf.strip()
            buf = ''
            buf_start = None
    if len(buf.strip()) >= LONG_MIN:
        yield buf_start, buf.strip()


def normalize(text):
    """Normalize for grouping: lowercase, collapse whitespace, strip surrounding punctuation."""
    s = re.sub(r'\s+', ' ', text.strip().lower())
    s = re.sub(r'^[^\w]+|[^\w.]+$', '', s)
    return s


def looks_like_chart_no(text):
    return bool(re.fullmatch(r'\d{12,16}', text.strip()))


def main():
    files = sys.argv[1:] or sorted(Path('logs').glob('keylog_*.log'))
    all_typings = []
    for fp in files:
        rows = [r for r in load(fp) if in_report(r)]
        for ts, text in extract_typings(rows):
            all_typings.append((ts, text, str(fp)))

    print(f"Files analyzed: {len(files)}")
    print(f"Total typings >= {LONG_MIN} chars: {len(all_typings)}")

    # Bucket: chart_no vs text
    chart_typings = [t for t in all_typings if looks_like_chart_no(t[1])]
    text_typings = [t for t in all_typings if not looks_like_chart_no(t[1])]
    print(f"  chart-number typings: {len(chart_typings)} (Mammo MCA flow)")
    print(f"  text typings: {len(text_typings)}")

    # Frequency by normalized text
    freq = Counter(normalize(t[1]) for t in text_typings)

    print(f"\n[Recurring text fragments (>=2x across files)]")
    for text, count in freq.most_common(30):
        if count < 2:
            break
        print(f"  x{count:3d}  {text[:140]}")

    print(f"\n[Top 20 longest unique text typings (any frequency)]")
    seen = set()
    longest = sorted(text_typings, key=lambda t: -len(t[1]))
    for ts, text, fp in longest:
        n = normalize(text)
        if n in seen:
            continue
        seen.add(n)
        if len(seen) > 20:
            break
        date = Path(fp).stem.replace('keylog_', '')
        print(f"  {date} {ts[11:19]} ({len(text):3d}) {text[:140]}")

    # Count chart_no typing per day (manual MCA / case input)
    chart_per_day = Counter()
    for ts, text, fp in chart_typings:
        chart_per_day[Path(fp).stem.replace('keylog_', '')] += 1
    print(f"\n[Chart number manual typing per day]")
    for d in sorted(chart_per_day):
        print(f"  {d}: x{chart_per_day[d]}")


if __name__ == '__main__':
    main()
