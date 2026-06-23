#!/usr/bin/env python3
"""Time-of-day (hour-of-day) reporting efficiency analysis — reusable module.

Used by:
  - build_trends.py  -> monthly 0-23 heatmap section (all / weekday / weekend)
  - generate_report.py -> per-week weekday 24-point cases/hr line (weekly summary)
  - CLI standalone    -> regenerate output/tod_efficiency.html

Method (per user spec):
  - completion timestamp = report_date (col 13) + report_time (col 14), minute precision
  - 00:00-05:59 attributed to previous work-day ("深夜" bucket, not mixed with morning)
  - effective working minutes per bucket = sum of adjacent intervals, single interval
    capped at 20 min (long gap = interruption/leave, not work)
  - cases/hr = cases / effective-hours ; median interval = secondary indicator
  - interruption rate = % of adjacent intervals > 20 min
  - de-dup by case_id across overlapping CSV exports

Known limitation: report_time precision is 1 min -> median interval floored ~1 min;
~60% batch sign-off compresses intervals (interval=0) -> use cases/hr + interruption
rate as primary, median interval as weak secondary.
"""
import csv
import glob
import statistics
import sys
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from pathlib import Path

ROOT = Path(__file__).parent
REPORTER = "A80748"
ENCODING = "cp950"

MODCOLOR = {"XR": "#5b8af0", "CT": "#e8923a", "US": "#4caf7d", "Mm": "#e06090",
            "IVP": "#d4a94a", "BMD": "#6b7088", "MR": "#9b72e0", "-": "#2a2d3a"}


def classify(exam: str) -> str:
    e = exam
    if "Bone densit" in e:
        return "BMD"
    if "I.V.P." in e or "IVP" in e:
        return "IVP"
    if e.startswith(("CT-", "CTA-")) or "Low Dose CT" in e or "LDCT" in e or "HRCT" in e:
        return "CT"
    if "Mammography" in e:
        return "Mm"
    if e.startswith("US-"):
        return "US"
    if e.startswith("MR") or "MRI" in e:
        return "MR"
    return "XR"


def _workdate(dt: datetime):
    """00:00-05:59 belongs to the previous work-day."""
    return (dt - timedelta(days=1)).date() if dt.hour < 6 else dt.date()


def load_records(csv_paths, reporter=REPORTER, now=None):
    """Merge CSVs, de-dup by case_id, return (records, excluded_counts).

    Each record: {dt, mod, hour, wdate, weekend}.
    """
    cases = {}
    for fp in csv_paths:
        try:
            with open(fp, encoding=ENCODING, errors="replace") as f:
                for r in csv.reader(f, delimiter="\t"):
                    if len(r) < 29 or r[17].strip() != reporter:
                        continue
                    cid = r[0].strip()
                    if not cid:
                        continue
                    rd, rt = r[13].strip(), r[14].strip()
                    if cid not in cases:
                        cases[cid] = {"rd": rd, "rt": rt, "exam": r[8].strip()}
                    elif not cases[cid]["rt"] and rt:
                        cases[cid]["rt"], cases[cid]["rd"] = rt, rd
        except FileNotFoundError:
            continue
    recs = []
    excl_notime = excl_bad = 0
    for c in cases.values():
        if not c["rd"] or not c["rt"]:
            excl_notime += 1
            continue
        try:
            dt = datetime.strptime(c["rd"] + " " + c["rt"], "%m/%d/%Y %H:%M")
        except ValueError:
            excl_bad += 1
            continue
        if now and dt > now:
            excl_bad += 1
            continue
        recs.append({"dt": dt, "mod": classify(c["exam"]),
                     "hour": dt.hour, "wdate": _workdate(dt),
                     "weekend": _workdate(dt).weekday() >= 5})
    return recs, {"no_timestamp": excl_notime, "bad_or_future": excl_bad}


def hour_table(records):
    """Per integer-hour bucket: n, cph (effective), irate, top modality, median interval."""
    g = defaultdict(list)
    for x in records:
        g[x["wdate"]].append(x)
    for d in g:
        g[d].sort(key=lambda x: x["dt"])
    n = Counter()
    eff = defaultdict(float)
    ints = defaultdict(list)
    mods = defaultdict(Counter)
    for lst in g.values():
        for i, x in enumerate(lst):
            n[x["hour"]] += 1
            mods[x["hour"]][x["mod"]] += 1
            if i > 0:
                gap = (x["dt"] - lst[i - 1]["dt"]).total_seconds() / 60.0
                hb = lst[i - 1]["hour"]
                eff[hb] += min(gap, 20.0)
                ints[hb].append(gap)
    out = {}
    for h in range(24):
        cnt = n.get(h, 0)
        eh = eff.get(h, 0) / 60.0
        ii = ints.get(h, [])
        out[h] = {
            "n": cnt,
            "cph": round(cnt / eh, 1) if eh > 0.05 else None,
            "irate": round(100 * sum(1 for v in ii if v > 20) / len(ii)) if ii else 0,
            "med": round(statistics.median(ii), 1) if ii else 0,
            "top": mods[h].most_common(1)[0][0] if mods[h] else "-",
        }
    return out


def compute(csv_paths, reporter=REPORTER, now=None):
    recs, excl = load_records(csv_paths, reporter, now)
    if not recs:
        return None
    span = "%s ~ %s" % (min(x["wdate"] for x in recs), max(x["wdate"] for x in recs))
    return {
        "all": hour_table(recs),
        "weekday": hour_table([x for x in recs if not x["weekend"]]),
        "weekend": hour_table([x for x in recs if x["weekend"]]),
        "meta": {"total": len(recs), "span": span, "files": len(csv_paths), "excluded": excl},
    }


# ──────────────────────────── rendering ────────────────────────────
def _color(cph):
    if cph is None:
        return "#1a1d28"
    t = max(0.0, min(1.0, (cph - 10.0) / 16.0))
    return "hsl(%d,70%%,42%%)" % round(210 - 210 * t)


def heatmap_html(data):
    """Return an HTML fragment (heatmap table + legend) for embedding in trends.html."""
    def _get(tbl, h):
        return tbl[h] if h in tbl else tbl[str(h)]

    def hrow(label, tbl, note=""):
        cells = []
        for h in range(24):
            c = _get(tbl, h)
            cph, nn = c["cph"], c["n"]
            cph_s = ("%.0f" % cph) if cph is not None else "-"
            op = "1" if nn >= 30 else "0.4"
            ti = "%02d:00  %s c/hr  n=%d  interrupt %d%%  %s" % (h, cph_s, nn, c["irate"], c["top"])
            cells.append('<td style="background:%s;opacity:%s" title="%s"><div class="tcph">%s</div><div class="tnn">%d</div></td>'
                         % (_color(cph), op, ti, cph_s, nn))
        sp = ('<br><span>%s</span>' % note) if note else ""
        return '<tr><th class="trl">%s%s</th>%s</tr>' % (label, sp, "".join(cells))

    def mrow(tbl):
        cells = []
        for h in range(24):
            m = _get(tbl, h)["top"]
            cells.append('<td style="background:%s" title="%02d:00 %s"><div class="tmm">%s</div></td>'
                         % (MODCOLOR.get(m, "#2a2d3a"), h, m, m))
        return '<tr><th class="trl">主要模態<br><span>(全部)</span></th>%s</tr>' % "".join(cells)

    hdr = "".join('<th class="thh%s">%d</th>' % (" dn" if h < 6 else "", h) for h in range(24))
    css = """<style>
table.todheat{border-collapse:collapse;width:100%;min-width:780px;}
table.todheat th.thh{font-family:'JetBrains Mono',monospace;font-size:11px;color:#6b7088;padding:2px;text-align:center;font-weight:400;}
table.todheat th.thh.dn{color:#5b8af0;}
table.todheat th.trl{font-size:12px;color:#c8ccd8;text-align:right;padding:4px 8px;white-space:nowrap;font-weight:600;}
table.todheat th.trl span{font-size:10px;color:#6b7088;font-weight:400;}
table.todheat td{text-align:center;padding:0;height:44px;border:1px solid #0c0e14;border-radius:3px;}
table.todheat td .tcph{font-family:'JetBrains Mono',monospace;font-size:13px;font-weight:700;color:#fff;}
table.todheat td .tnn{font-size:9px;color:rgba(255,255,255,.7);}
table.todheat td .tmm{font-size:10px;font-weight:700;color:#fff;}
.todscale{display:inline-flex;height:12px;width:150px;border-radius:3px;background:linear-gradient(90deg,hsl(210,70%,42%),hsl(105,70%,42%),hsl(0,70%,42%));}
.todleg{display:flex;gap:12px;flex-wrap:wrap;margin-top:10px;font-size:11px;color:#6b7088;align-items:center;}
</style>"""
    body = ['<div class="card" style="overflow-x:auto">', css, '<table class="todheat">',
            '<tr><th class="trl"></th>%s</tr>' % hdr,
            hrow("全部資料", data["all"]),
            hrow("平日", data["weekday"], "Mon-Fri"),
            hrow("假日", data["weekend"], "Sat-Sun"),
            mrow(data["all"]), '</table>',
            '<div class="todleg"><span>低</span><span class="todscale"></span><span>高 cases/hr</span>'
            '<span style="margin-left:10px">藍字=深夜(0-5)</span><span>· 淡格=樣本&lt;30</span>'
            '<span>· 樣本 %d 份 / %s</span></div>' % (data["meta"]["total"], data["meta"]["span"]),
            '<div style="background:rgba(208,127,20,.1);border:1px solid rgba(208,127,20,.3);border-radius:6px;'
            'padding:10px 14px;margin-top:10px;font-size:12px;color:#d4a94a">⚠ cases/hr 由相鄰簽發間隔推估'
            '（&gt;20min 截斷）；假日上午紅格為週末值班 XR 批次簽章假象，請對照主要模態列。</div>',
            '</div>']
    return "".join(body)


def linechart_svg(htable, hours=range(8, 24), width=720, height=180, color="#4caf7d", label="平日 cases/hr"):
    """24-point (default 08-23) cases/hr line for weekly summary. htable keys int 0-23."""
    hrs = list(hours)
    vals = [(htable[h]["cph"] if htable[h]["cph"] is not None else 0) for h in hrs]
    ns = [htable[h]["n"] for h in hrs]
    vmax = max([v for v in vals if v] + [20]) * 1.15
    PADL, PADR, PADT, PADB = 38, 12, 16, 26
    iw = width - PADL - PADR
    ih = height - PADT - PADB
    def xa(i):
        return PADL + (iw * i / (len(hrs) - 1)) if len(hrs) > 1 else PADL
    def ya(v):
        return PADT + ih * (1 - v / vmax)
    out = ['<svg viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg" style="width:100%%;height:auto;font-family:JetBrains Mono,monospace">' % (width, height)]
    # y gridlines
    for k in range(5):
        v = vmax * k / 4
        y = ya(v)
        out.append('<line x1="%d" x2="%d" y1="%.1f" y2="%.1f" stroke="#2a2d3a" stroke-width="1"/>' % (PADL, width - PADR, y, y))
        out.append('<text x="%d" y="%.1f" fill="#6b7088" font-size="10" text-anchor="end">%.0f</text>' % (PADL - 4, y + 3, v))
    # path (skip zero-n hours to avoid fake dips)
    pts = []
    for i, h in enumerate(hrs):
        if ns[i] > 0:
            pts.append("%.1f,%.1f" % (xa(i), ya(vals[i])))
    if pts:
        out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2"/>' % (" ".join(pts), color))
    for i, h in enumerate(hrs):
        if ns[i] > 0:
            r = 3 if ns[i] >= 30 else 2
            op = "1" if ns[i] >= 30 else "0.4"
            out.append('<circle cx="%.1f" cy="%.1f" r="%d" fill="%s" opacity="%s"><title>%02d:00  %.0f c/hr  n=%d</title></circle>'
                       % (xa(i), ya(vals[i]), r, color, op, h, vals[i], ns[i]))
        out.append('<text x="%.1f" y="%d" fill="#6b7088" font-size="9" text-anchor="middle">%d</text>' % (xa(i), height - 8, h))
    out.append('<text x="%d" y="11" fill="#c8ccd8" font-size="11">%s</text>' % (PADL, label))
    out.append('</svg>')
    return "".join(out)


def all_csv_paths():
    return sorted(glob.glob(str(ROOT / "csv_input" / "115*_CL.csv")) +
                  glob.glob(str(ROOT / "csv_input" / "115*_YK.csv")))


def _standalone_html(data):
    periods = _period_table(data_records=None, data=data)
    H = ['<!DOCTYPE html><html lang="zh-TW"><head><meta charset="UTF-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
         '<title>時段效率分析 — 每整點熱力圖</title>',
         '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">',
         '<style>body{background:#0c0e14;color:#c8ccd8;font-family:Noto Sans TC,sans-serif;padding:0 0 60px;margin:0;}'
         '.header{background:linear-gradient(135deg,#131a2e,#0c0e14);border-bottom:2px solid #5b8af0;padding:26px 24px;text-align:center;}'
         '.header h1{font-size:21px;color:#fff;margin:0;}.header .meta{font-size:12px;color:#6b7088;margin-top:6px;font-family:JetBrains Mono,monospace;}'
         '.container{max-width:1080px;margin:0 auto;padding:0 14px;}.section{margin:26px 0;}'
         '.st{font-size:15px;font-weight:700;color:#fff;border-left:3px solid #5b8af0;padding:6px 0 6px 12px;margin-bottom:14px;}'
         '.card{background:#13161f;border:1px solid #2a2d3a;border-radius:8px;padding:16px;}'
         '.mono{font-family:JetBrains Mono,monospace;}</style></head><body>',
         '<div class="header"><h1>時段效率分析 — 每整點 0–23 熱力圖</h1>',
         '<div class="meta">樣本 %d 份 · %s · %d 個 CSV 去重 · A80748</div></div>' % (data["meta"]["total"], data["meta"]["span"], data["meta"]["files"]),
         '<div class="container">',
         '<div class="section"><h3 class="st">🔥 每整點熱力圖（顏色 = cases/hr；格內上=cases/hr 下=件數）</h3>',
         heatmap_html(data), '</div>',
         '<div class="section"><h3 class="st">📈 平日 cases/hr 折線（08–23）</h3><div class="card">',
         linechart_svg(data["weekday"]), '</div></div>',
         '</div></body></html>']
    return "".join(H)


def _period_table(data_records=None, data=None):
    return None  # placeholder (standalone uses heatmap+line; period table lives in weekly)


def main():
    paths = all_csv_paths()
    data = compute(paths, now=datetime(2026, 12, 31, 23, 59))
    if not data:
        print("No records found.", file=sys.stderr)
        sys.exit(1)
    out = ROOT / "output" / "tod_efficiency.html"
    out.write_text(_standalone_html(data), encoding="utf-8")
    print("written %s (samples=%d, span=%s, files=%d)" %
          (out, data["meta"]["total"], data["meta"]["span"], data["meta"]["files"]))


if __name__ == "__main__":
    main()
