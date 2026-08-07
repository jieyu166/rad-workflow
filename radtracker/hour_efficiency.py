#!/usr/bin/env python3
"""Time-of-day efficiency analysis from raw CSV logs (W12-W25).

Per-hour and per-period stats:
- cases/hr (effective time = sum of intervals capped at 20min)
- median raw interval (minutes)
- interruption rate (% intervals > 20min)
- modality composition
- weekday vs weekend
"""
import csv, glob, os, sys, io, json
from collections import defaultdict
from datetime import datetime, timedelta
from statistics import median

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

REPORTER = 'A80748'
CSV_DIR = 'csv_input'
INTERVAL_CAP_MIN = 20  # > 20min counted as 20 (effective time cap)
INTERVAL_DROP_ZERO = True  # drop batch-signed (interval=0)
SAMPLE_WARN_THRESHOLD = 30

def classify(exam):
    e = exam.strip()
    if 'Bone densit' in e: return 'BMD'
    if 'I.V.P.' in e or 'IVP' in e: return 'IVP'
    if e.startswith(('CT-', 'CTA-')) or 'Low Dose CT' in e or 'LDCT' in e or 'HRCT' in e: return 'CT'
    if e.startswith('MR') or 'MRI' in e: return 'MR'
    if 'Mammography' in e: return 'Mammo'
    if e.startswith('US-'): return 'US'
    return 'XR'

def parse_ts(date_s, time_s):
    try:
        return datetime.strptime(date_s.strip() + ' ' + time_s.strip(), '%m/%d/%Y %H:%M')
    except (ValueError, AttributeError):
        return None

# --- Step 1: Load all cases ---
files = []
for fn in sorted(glob.glob(os.path.join(CSV_DIR, '*.csv'))):
    base = os.path.basename(fn).lower()
    if 'legacy' in base: continue
    files.append(fn)
print(f'[Loading {len(files)} CSVs from {CSV_DIR}/]')

cases = {}  # case_id -> {'ts': earliest dt, 'mod': str, 'src': str}
excluded = {'no_ts': 0, 'future': 0, 'wrong_reporter': 0, 'dup_case': 0}
now = datetime(2026, 6, 22, 23, 59)  # known current date

for fn in files:
    try:
        with open(fn, encoding='cp950', errors='replace') as f:
            for row in csv.reader(f, delimiter='\t'):
                if len(row) < 29: continue
                if row[17].strip() != REPORTER:
                    excluded['wrong_reporter'] += 1
                    continue
                cid = row[0].strip()
                if not cid: continue
                ts = parse_ts(row[13], row[14])
                if ts is None:
                    excluded['no_ts'] += 1
                    continue
                if ts > now:
                    excluded['future'] += 1
                    continue
                mod = classify(row[8])
                src = row[4].strip()
                if cid in cases:
                    if ts < cases[cid]['ts']:
                        cases[cid] = {'ts': ts, 'mod': mod, 'src': src}
                    else:
                        excluded['dup_case'] += 1
                else:
                    cases[cid] = {'ts': ts, 'mod': mod, 'src': src}
    except Exception as e:
        print(f'  ERR {fn}: {e}', file=sys.stderr)

print(f'[Loaded {len(cases)} unique cases]')
print(f'[Excluded: no_ts={excluded["no_ts"]}, future={excluded["future"]}, dup_case_rows={excluded["dup_case"]}]')

# --- Step 2: Group by workday (deep-night attribution 00-05:59 to prev day) ---
def workday(ts):
    if ts.hour < 6:
        return (ts - timedelta(days=1)).date()
    return ts.date()

by_day = defaultdict(list)
for cid, c in cases.items():
    by_day[workday(c['ts'])].append((c['ts'], c['mod'], c['src']))

# Filter to W12-W25 (2026-03-16 to 2026-06-21)
START = datetime(2026, 3, 16).date()
END = datetime(2026, 6, 21).date()
by_day_filt = {d: v for d, v in by_day.items() if START <= d <= END}
print(f'[Filtered to {START} ~ {END}: {len(by_day_filt)} workdays, {sum(len(v) for v in by_day_filt.values())} cases]')

# --- Step 3: Compute per-case intervals (within each workday) ---
# Each "record" = (timestamp, mod, interval_min_from_prev, is_weekend)
records = []
for day, items in by_day_filt.items():
    items.sort(key=lambda x: x[0])
    is_weekend = day.weekday() >= 5  # Sat=5, Sun=6
    prev_ts = None
    for ts, mod, src in items:
        interval_min = None
        if prev_ts is not None:
            interval_min = (ts - prev_ts).total_seconds() / 60.0
        records.append({'ts': ts, 'mod': mod, 'src': src,
                        'interval': interval_min, 'is_weekend': is_weekend,
                        'workday': day})
        prev_ts = ts

# Drop interval=0 (batch sign) per user
records_intervals = [r for r in records if r['interval'] is not None]
n_zero = sum(1 for r in records_intervals if r['interval'] == 0)
print(f'[Intervals: {len(records_intervals)} pairs, {n_zero} (={n_zero*100/len(records_intervals):.1f}%) are interval=0 (batch sign) — dropped]')
records_intervals = [r for r in records_intervals if r['interval'] > 0]

# --- Step 4: Bucket by hour-of-day ---
def hour_bucket(ts):
    h = ts.hour
    return h  # 0-23

def period_bucket(ts):
    h = ts.hour
    if 0 <= h <= 2: return '深夜 (00-02)'
    if 3 <= h <= 5: return '凌晨 (03-05)'  # edge case
    if 6 <= h <= 7: return '清晨 (06-07)'
    if 8 <= h <= 11: return '上午 (08-11)'
    if 12 <= h <= 12: return '午餐 (12)'
    if 13 <= h <= 16: return '午後 (13-16)'
    if 17 <= h <= 18: return '傍晚 (17-18)'
    if 19 <= h <= 22: return '晚間 (19-22)'
    if h == 23: return '夜深 (23)'
    return f'其他 ({h})'

def compute_stats(recs, label):
    if not recs:
        return None
    intervals = [r['interval'] for r in recs]
    capped = [min(i, INTERVAL_CAP_MIN) for i in intervals]
    eff_hr = sum(capped) / 60.0
    n = len(recs)
    rate = n / eff_hr if eff_hr > 0 else None
    med = median(intervals) if intervals else None
    interruption = sum(1 for i in intervals if i > INTERVAL_CAP_MIN)
    interruption_rate = interruption / n * 100 if n else 0
    mod_dist = defaultdict(int)
    for r in recs:
        mod_dist[r['mod']] += 1
    return {'label': label, 'n': n, 'eff_hr': eff_hr, 'cases_per_hr': rate,
            'median_interval': med, 'interruption_rate': interruption_rate,
            'mod_dist': dict(mod_dist)}

# --- per-hour stats ---
print('\n=== Per-hour statistics ===')
print(f'{"Hour":<6} {"n":<6} {"eff_hr":<8} {"c/hr":<8} {"med_min":<9} {"intr%":<7} {"主要模態 (top3)":<30}')
for h in range(24):
    recs = [r for r in records_intervals if r['ts'].hour == h]
    s = compute_stats(recs, f'{h:02d}')
    if not s:
        print(f'{h:02d}:00  {"--":<6}')
        continue
    top_mods = sorted(s['mod_dist'].items(), key=lambda x: -x[1])[:3]
    mods_str = ' '.join(f'{m}:{c}' for m, c in top_mods)
    rate_str = f'{s["cases_per_hr"]:.1f}' if s['cases_per_hr'] else '--'
    med_str = f'{s["median_interval"]:.1f}' if s['median_interval'] is not None else '--'
    warn = ' ⚠' if s['n'] < SAMPLE_WARN_THRESHOLD else ''
    print(f'{h:02d}:00  {s["n"]:<6} {s["eff_hr"]:<8.1f} {rate_str:<8} {med_str:<9} {s["interruption_rate"]:<7.1f} {mods_str:<30}{warn}')

# --- period stats (overall) ---
print('\n=== Period buckets (ALL days) ===')
print(f'{"Period":<18} {"n":<6} {"eff_hr":<8} {"c/hr":<8} {"med_min":<9} {"intr%":<7} {"主要模態":<35}')
period_order = ['深夜 (00-02)', '凌晨 (03-05)', '清晨 (06-07)', '上午 (08-11)', '午餐 (12)',
                '午後 (13-16)', '傍晚 (17-18)', '晚間 (19-22)', '夜深 (23)']
period_recs = defaultdict(list)
for r in records_intervals:
    period_recs[period_bucket(r['ts'])].append(r)
period_results = {}
for p in period_order:
    s = compute_stats(period_recs.get(p, []), p)
    if not s: continue
    period_results[p] = s
    top = sorted(s['mod_dist'].items(), key=lambda x: -x[1])[:4]
    mods_str = ' '.join(f'{m}:{c}' for m, c in top)
    warn = ' ⚠樣本不足' if s['n'] < SAMPLE_WARN_THRESHOLD else ''
    rate = f'{s["cases_per_hr"]:.1f}' if s['cases_per_hr'] else '--'
    med = f'{s["median_interval"]:.1f}' if s['median_interval'] is not None else '--'
    print(f'{p:<18} {s["n"]:<6} {s["eff_hr"]:<8.1f} {rate:<8} {med:<9} {s["interruption_rate"]:<7.1f} {mods_str:<35}{warn}')

# --- weekday vs weekend ---
for tag, recs in [('平日 (Mon-Fri)', [r for r in records_intervals if not r['is_weekend']]),
                   ('假日 (Sat-Sun)', [r for r in records_intervals if r['is_weekend']])]:
    print(f'\n=== Period buckets — {tag} ===')
    print(f'{"Period":<18} {"n":<6} {"eff_hr":<8} {"c/hr":<8} {"med_min":<9} {"intr%":<7} {"主要模態":<35}')
    pr = defaultdict(list)
    for r in recs:
        pr[period_bucket(r['ts'])].append(r)
    for p in period_order:
        s = compute_stats(pr.get(p, []), p)
        if not s: continue
        top = sorted(s['mod_dist'].items(), key=lambda x: -x[1])[:4]
        mods_str = ' '.join(f'{m}:{c}' for m, c in top)
        warn = ' ⚠' if s['n'] < SAMPLE_WARN_THRESHOLD else ''
        rate = f'{s["cases_per_hr"]:.1f}' if s['cases_per_hr'] else '--'
        med = f'{s["median_interval"]:.1f}' if s['median_interval'] is not None else '--'
        print(f'{p:<18} {s["n"]:<6} {s["eff_hr"]:<8.1f} {rate:<8} {med:<9} {s["interruption_rate"]:<7.1f} {mods_str:<35}{warn}')

# --- key comparison: afternoon vs evening ---
print('\n=== 關鍵對決：午後 (13-16, 17-18) vs 晚間 (19-22) ===')
keys = ['午後 (13-16)', '傍晚 (17-18)', '晚間 (19-22)']
for k in keys:
    s = period_results.get(k)
    if not s: continue
    print(f'  {k}: {s["cases_per_hr"]:.1f} cases/hr | 中位間隔 {s["median_interval"]:.1f}min | 中斷率 {s["interruption_rate"]:.1f}%')

# Save JSON
out = {'window': f'{START} ~ {END}', 'total_cases': len(cases),
       'analyzed_pairs': len(records_intervals),
       'excluded': excluded, 'periods': {k: {kk: vv for kk, vv in v.items() if kk != 'label'} for k, v in period_results.items()}}
with open('output/hour_efficiency.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2, default=str)
print('\n[Saved output/hour_efficiency.json]')
