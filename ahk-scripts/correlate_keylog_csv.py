#!/usr/bin/env python3
"""把 keylog 時間點對應到 CSV 的報告（exam_name / chart_no）。

用途：找出哪些報告有「手打 chart_no、方向鍵猛按、貼上後大改、注音漏切換」等行為。
"""
import csv
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

# repo root resolved relative to this script
REPO = Path(__file__).resolve().parent.parent
CSV_DIR = REPO / "radtracker" / "csv_input"
LOG_DIR = REPO / "ahk-scripts" / "logs"

REPORT_CLASSES = {'ThunderRT6FormDC'}
REPORT_KW = 'chk060'
REPORTER = 'A80748'
ENCODING = 'cp950'
MATCH_WINDOW_MIN = 5  # 報告 timestamp ± N 分鐘視為同一份


def load_csv_reports(csv_paths):
    """Load minimal report fields from hospital CSV(s).

    Returns list of dicts: case_id, chart_no, exam_name, modality, report_dt
    Multiple rows under one case_id are merged (kept exam_name list).
    """
    by_case = {}
    for fp in csv_paths:
        try:
            with open(fp, encoding=ENCODING, errors='replace') as f:
                reader = csv.reader(f, delimiter='\t')
                for row in reader:
                    if len(row) < 18 or row[17].strip() != REPORTER:
                        continue
                    case_id = row[0].strip()
                    if not case_id:
                        continue
                    rd = row[13].strip()
                    rt = row[14].strip()
                    try:
                        dt = datetime.strptime(f"{rd} {rt}", "%m/%d/%Y %H:%M")
                    except ValueError:
                        continue
                    rec = by_case.setdefault(case_id, {
                        'case_id': case_id,
                        'chart_no': row[1].strip(),
                        'exams': set(),
                        'orders': set(),
                        'report_dt': dt,
                    })
                    rec['exams'].add(row[8].strip())
                    rec['orders'].add(row[6].strip())
                    if dt < rec['report_dt']:
                        rec['report_dt'] = dt
        except Exception as e:
            print(f"[warn] failed to read {fp}: {e}", file=sys.stderr)

    reports = list(by_case.values())
    reports.sort(key=lambda r: r['report_dt'])
    return reports


def classify_modality(exams):
    """Rough modality from exam_name list."""
    s = " ".join(exams).lower()
    if 'mammography' in s:
        return 'Mammo'
    if any(x in s for x in ['ct-', 'cta-', 'low dose ct', 'ldct', 'hrct']):
        return 'CT'
    if 'us-' in s or 'sonography' in s or 'ultraso' in s:
        return 'US'
    if s.startswith('mr') or 'mri' in s or 'magnetic' in s:
        return 'MR'
    if 'bone densitometry' in s:
        return 'BMD'
    if 'i.v.p' in s or 'ivp' in s:
        return 'IVP'
    return 'XR'


def load_keylog(filepath):
    with open(filepath, encoding='utf-8-sig') as f:
        return [r for r in csv.DictReader(f, delimiter='\t') if r.get('timestamp')]


def in_report(row):
    return (row.get('window_class', '') in REPORT_CLASSES
            and REPORT_KW in row.get('window_title', ''))


def find_match(reports, target_dt, window_min=MATCH_WINDOW_MIN):
    """Find the report whose report_dt is within ±window_min of target_dt."""
    delta = timedelta(minutes=window_min)
    candidates = [r for r in reports
                  if abs(r['report_dt'] - target_dt) <= delta]
    if not candidates:
        # try a wider window for 注音 / arrow key bursts (typing during pre-finalize)
        delta2 = timedelta(minutes=15)
        candidates = [r for r in reports
                      if -timedelta(minutes=2) <= (r['report_dt'] - target_dt) <= delta2]
    if not candidates:
        return None
    return min(candidates, key=lambda r: abs(r['report_dt'] - target_dt))


# ── Detectors ────────────────────────────────────────────────────────────

def detect_chart_typing(rows):
    """Find episodes of typing 12-16 consecutive digits."""
    out = []
    buf = ''
    buf_start = None
    for r in rows:
        k = r['key']
        if len(k) == 1 and k.isdigit():
            if not buf:
                buf_start = r['timestamp']
            buf += k
        else:
            if 12 <= len(buf) <= 16:
                out.append({'time': buf_start, 'chart': buf})
            buf = ''
            buf_start = None
    if 12 <= len(buf) <= 16:
        out.append({'time': buf_start, 'chart': buf})
    return out


def detect_arrow_clusters(rows, min_count=10):
    """Find consecutive same-key clusters of arrow keys."""
    out = []
    if not rows:
        return out
    cur = rows[0]
    cur_count = 1
    cur_start = rows[0]['timestamp']
    for r in rows[1:]:
        if r['key'] == cur['key']:
            cur_count += 1
        else:
            if cur['key'] in ('Up', 'Down', 'Left', 'Right') and cur_count >= min_count:
                out.append({'time': cur_start, 'key': cur['key'],
                            'count': cur_count})
            cur = r
            cur_count = 1
            cur_start = r['timestamp']
    if cur['key'] in ('Up', 'Down', 'Left', 'Right') and cur_count >= min_count:
        out.append({'time': cur_start, 'key': cur['key'], 'count': cur_count})
    return out


def detect_paste_then_edit(rows, min_edits=12):
    """Paste followed by >= min_edits navigation/edit keys within 30s."""
    out = []
    edit_keys = {'Backspace', 'Delete', 'Up', 'Down', 'Left', 'Right'}
    for i, r in enumerate(rows):
        if r['key'] != '^V':
            continue
        try:
            t0 = datetime.strptime(r['timestamp'], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            continue
        edits = 0
        for j in range(i + 1, min(i + 300, len(rows))):
            try:
                t = datetime.strptime(rows[j]['timestamp'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue
            if (t - t0).total_seconds() > 30:
                break
            if rows[j]['key'] in edit_keys:
                edits += 1
        if edits >= min_edits:
            out.append({'time': r['timestamp'], 'edits': edits})
    return out


def detect_zhuyin_leak(rows, min_len=12):
    """Detect Bopomofo-keycode leaks: long bursts dominated by digits 0-7
    mixed with letter keys (no normal English words)."""
    out = []
    buf = ''
    buf_start = None
    digit_count = 0
    for r in rows:
        k = r['key']
        if len(k) == 1 and k.isprintable() and k != ' ':
            if not buf:
                buf_start = r['timestamp']
                digit_count = 0
            buf += k
            if k.isdigit():
                digit_count += 1
        else:
            if len(buf) >= min_len:
                # heuristic: >=30% digits AND no recognizable word > 3 letters
                if digit_count / len(buf) >= 0.3:
                    has_word = False
                    cur_word = ''
                    for ch in buf:
                        if ch.isalpha():
                            cur_word += ch
                        else:
                            if len(cur_word) >= 4:
                                has_word = True
                                break
                            cur_word = ''
                    if len(cur_word) >= 4:
                        has_word = True
                    if not has_word:
                        out.append({'time': buf_start, 'text': buf})
            buf = ''
            buf_start = None
            digit_count = 0
    return out


# ── Main ─────────────────────────────────────────────────────────────────

def analyze(date_yyyymmdd):
    """Cross-reference one keylog date against CSVs."""
    log_path = LOG_DIR / f"keylog_{date_yyyymmdd}.log"
    if not log_path.exists():
        # try with (2) suffix
        candidates = list(LOG_DIR.glob(f"keylog_{date_yyyymmdd}*.log"))
        if not candidates:
            print(f"[warn] no keylog for {date_yyyymmdd}")
            return
        log_path = candidates[0]

    csv_paths = sorted(CSV_DIR.glob("*.csv"))
    csv_paths = [p for p in csv_paths
                 if 'legacy' not in p.name.lower()
                 and 'archive' not in str(p).lower()]
    reports = load_csv_reports(csv_paths)

    rows = load_keylog(log_path)
    rep_rows = [r for r in rows if in_report(r)]

    print(f"\n========== {date_yyyymmdd}  ({log_path.name}) ==========")
    print(f"Reports loaded from CSVs: {len(reports)}")
    print(f"Report-window keystrokes: {len(rep_rows)}")

    target_date = datetime.strptime(date_yyyymmdd, '%Y%m%d').date()
    same_day = [r for r in reports if r['report_dt'].date() == target_date]
    print(f"Reports signed on {target_date}: {len(same_day)}")

    # ── C: chart_no 手打 ──
    chart_episodes = detect_chart_typing(rep_rows)
    print(f"\n[C] Chart-number manual typing: {len(chart_episodes)} episodes")
    for ep in chart_episodes:
        try:
            tdt = datetime.strptime(ep['time'], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            continue
        m = find_match(reports, tdt)
        if m:
            mod = classify_modality(m['exams'])
            exam = list(m['exams'])[0][:60]
            print(f"  {ep['time'][11:19]} typed {ep['chart']:16s} -> "
                  f"[{mod}] {exam} (chart {m['chart_no']})")
        else:
            print(f"  {ep['time'][11:19]} typed {ep['chart']:16s} -> (no CSV match)")

    # ── D: 方向鍵連按簇 ──
    clusters = detect_arrow_clusters(rep_rows, min_count=10)
    print(f"\n[D] Arrow-key clusters >= 10 keys: {len(clusters)} bursts")
    for c in clusters[:15]:
        try:
            tdt = datetime.strptime(c['time'], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            continue
        m = find_match(reports, tdt)
        if m:
            mod = classify_modality(m['exams'])
            exam = list(m['exams'])[0][:60]
            print(f"  {c['time'][11:19]} {c['key']:6s} x{c['count']:3d} -> "
                  f"[{mod}] {exam}")
        else:
            print(f"  {c['time'][11:19]} {c['key']:6s} x{c['count']:3d} -> (no CSV match)")

    # ── E: paste-then-edit ──
    edits = detect_paste_then_edit(rep_rows, min_edits=12)
    print(f"\n[E] Paste-then-edit episodes (>=12 edits in 30s): {len(edits)}")
    for e in edits[:15]:
        try:
            tdt = datetime.strptime(e['time'], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            continue
        m = find_match(reports, tdt)
        if m:
            mod = classify_modality(m['exams'])
            exam = list(m['exams'])[0][:60]
            print(f"  {e['time'][11:19]} +{e['edits']:2d} edits -> "
                  f"[{mod}] {exam}")
        else:
            print(f"  {e['time'][11:19]} +{e['edits']:2d} edits -> (no CSV match)")

    # ── 注音漏切換 ──
    zh = detect_zhuyin_leak(rep_rows, min_len=12)
    print(f"\n[Z] Possible Bopomofo-leak episodes: {len(zh)}")
    for z in zh[:15]:
        try:
            tdt = datetime.strptime(z['time'], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            continue
        m = find_match(reports, tdt)
        snippet = z['text'][:50]
        if m:
            mod = classify_modality(m['exams'])
            exam = list(m['exams'])[0][:60]
            print(f"  {z['time'][11:19]} {snippet:50s} -> [{mod}] {exam}")
        else:
            print(f"  {z['time'][11:19]} {snippet:50s} -> (no CSV match)")

    # 模態分布總結
    if same_day:
        mod_counter = Counter(classify_modality(r['exams']) for r in same_day)
        print(f"\n[Modality distribution on {target_date}]")
        for mod, count in mod_counter.most_common():
            print(f"  {mod}: {count}")


def main():
    if len(sys.argv) > 1:
        for d in sys.argv[1:]:
            analyze(d)
    else:
        # default: last 2 days
        for d in ['20260427', '20260428']:
            analyze(d)


if __name__ == '__main__':
    main()
