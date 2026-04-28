#!/usr/bin/env python3
"""Find long typed sentences and repetitive key clusters in AHK keylog.

目的：找出可以做成 hotstring 的長句、以及高頻重複按鍵簇（編輯/捲動熱點）。
"""
import csv
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

REPORT_CLASSES = {'ThunderRT6FormDC'}
REPORT_TITLE_KEYWORD = 'chk060'
LONG_TYPING_MIN = 15          # 連續可印字元 >= N 視為長段打字
REPEAT_CLUSTER_MIN = 5        # 同一鍵連按 >= N 視為連按簇
SESSION_GAP_SEC = 30


def load(filepath):
    with open(filepath, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter='\t')
        return [r for r in reader if r.get('timestamp')]


def in_report(row):
    return (row.get('window_class', '') in REPORT_CLASSES
            and REPORT_TITLE_KEYWORD in row.get('window_title', ''))


def find_long_typings(rows):
    """連續可印字元（含空白），切分點：非可印鍵或 ; 結尾。"""
    out = []
    buf = ''
    buf_start = None
    for r in rows:
        k = r['key']
        if len(k) == 1 and k.isprintable():
            if not buf:
                buf_start = r['timestamp']
            buf += k
            # ; 視為 hotstring 觸發點，先暫存後重啟（讓長段不被 ; 切碎）
            if k == ';' and len(buf) >= 2:
                # 短於 8 字（如 BOW;）視為 hotstring，從緩衝中移除
                if len(buf) <= 8:
                    buf = ''
                    buf_start = None
        elif len(k) == 1 and k == ' ':
            buf += ' '
        else:
            if len(buf.strip()) >= LONG_TYPING_MIN:
                out.append({'start': buf_start, 'text': buf.strip(),
                            'len': len(buf.strip())})
            buf = ''
            buf_start = None
    if len(buf.strip()) >= LONG_TYPING_MIN:
        out.append({'start': buf_start, 'text': buf.strip(),
                    'len': len(buf.strip())})
    return out


def find_repeat_clusters(rows):
    """連按同一鍵 >= REPEAT_CLUSTER_MIN 次。"""
    out = []
    if not rows:
        return out
    cur_key = rows[0]['key']
    cur_count = 1
    cur_start = rows[0]['timestamp']
    for r in rows[1:]:
        if r['key'] == cur_key:
            cur_count += 1
        else:
            if cur_count >= REPEAT_CLUSTER_MIN:
                out.append({'key': cur_key, 'count': cur_count,
                            'start': cur_start})
            cur_key = r['key']
            cur_count = 1
            cur_start = r['timestamp']
    if cur_count >= REPEAT_CLUSTER_MIN:
        out.append({'key': cur_key, 'count': cur_count,
                    'start': cur_start})
    return out


def find_paste_then_edit(rows):
    """偵測『貼上後立刻大量修改』模式：^V 後 30 秒內出現 >= 10 次 Backspace/Delete/Up/Down。"""
    hits = []
    for i, r in enumerate(rows):
        if r['key'] != '^V':
            continue
        t0 = datetime.strptime(r['timestamp'], '%Y-%m-%d %H:%M:%S')
        edits = 0
        last_t = t0
        for j in range(i + 1, min(i + 200, len(rows))):
            t = datetime.strptime(rows[j]['timestamp'], '%Y-%m-%d %H:%M:%S')
            if (t - t0).total_seconds() > 30:
                break
            if rows[j]['key'] in ('Backspace', 'Delete', 'Up', 'Down', 'Left', 'Right'):
                edits += 1
                last_t = t
        if edits >= 10:
            hits.append({'paste_at': r['timestamp'], 'edits_in_30s': edits})
    return hits


def find_phrase_frequencies(typings):
    """從長段打字中找出重複出現的子片語（>=10 字、>=2 次）。"""
    phrases = Counter()
    norm = lambda s: re.sub(r'\s+', ' ', s.strip()).lower()
    for t in typings:
        text = norm(t['text'])
        # 切句：以 . ! ? 切，再保留 >=10 字的段落
        for sentence in re.split(r'[.!?]\s*', text):
            s = sentence.strip()
            if 10 <= len(s) <= 200:
                phrases[s] += 1
    return Counter({p: c for p, c in phrases.items() if c >= 2})


def analyze_file(filepath):
    rows = load(filepath)
    report_rows = [r for r in rows if in_report(r)]

    typings = find_long_typings(report_rows)
    typings.sort(key=lambda x: -x['len'])

    clusters = find_repeat_clusters(report_rows)
    cluster_summary = Counter(c['key'] for c in clusters)

    paste_edits = find_paste_then_edit(report_rows)

    phrases = find_phrase_frequencies(typings)

    return {
        'file': str(filepath),
        'date': Path(filepath).stem.replace('keylog_', ''),
        'report_keystrokes': len(report_rows),
        'long_typings': typings[:20],
        'long_typings_total': len(typings),
        'clusters': clusters,
        'cluster_summary': dict(cluster_summary.most_common()),
        'paste_then_edit_count': len(paste_edits),
        'paste_then_edit_samples': paste_edits[:10],
        'recurring_phrases': phrases.most_common(15),
    }


def print_report(data):
    print(f"\n===== {data['date']} =====")
    print(f"Report-window keystrokes: {data['report_keystrokes']}")

    print(f"\n[Top 10 long typings ({data['long_typings_total']} total >= {LONG_TYPING_MIN} chars)]")
    for t in data['long_typings'][:10]:
        snippet = t['text'][:120].replace('\n', ' ')
        print(f"  {t['start'][11:19]} ({t['len']:3d}) {snippet}")

    print(f"\n[Repeat key clusters >= {REPEAT_CLUSTER_MIN} consecutive]")
    for k, c in list(data['cluster_summary'].items())[:10]:
        print(f"  {k:12s} x{c} clusters")
    if data['clusters']:
        worst = sorted(data['clusters'], key=lambda x: -x['count'])[:5]
        print(f"  Top 5 worst clusters:")
        for w in worst:
            print(f"    {w['start'][11:19]} {w['key']:10s} x{w['count']}")

    print(f"\n[Paste-then-edit episodes: {data['paste_then_edit_count']}]")
    for p in data['paste_then_edit_samples'][:5]:
        print(f"  {p['paste_at'][11:19]} -> {p['edits_in_30s']} edit keys in 30s")

    print(f"\n[Recurring phrases (>=2x in long typings)]")
    for phrase, count in data['recurring_phrases'][:10]:
        snippet = phrase[:100]
        print(f"  x{count} {snippet}")


if __name__ == '__main__':
    files = sys.argv[1:] or sorted(Path('logs').glob('keylog_*.log'))
    for fp in files:
        print_report(analyze_file(fp))
