#!/usr/bin/env python3
"""Build multi-week trends HTML from history.json + per-week daily data.

Visualizes:
  1. Weekly added per modality (line chart)
  2. Weekly work points (bar)
  3. Weekly completed per modality (stacked bar)
  4. GitHub-style daily intensity heatmap
  5. Backlog (end-of-week remaining) trend
  6. Weekly active hours
  7. Weekly cases/hr (productivity)
  8. Weekly net change (delta)
"""
import json
import re
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).parent
HISTORY = ROOT / "history.json"
DAILY_GLOB = "output/W*/weekly_report.json"
OUT_HTML = ROOT / "output" / "trends.html"

DAY_TO_OFFSET = {"一": 0, "二": 1, "三": 2, "四": 3, "五": 4, "六": 5, "日": 6}


def iso_week_monday(year, week):
    """Get Monday date for given ISO year/week."""
    return date.fromisocalendar(year, week, 1)


def parse_week(week_id):
    """'2026-W18' -> (2026, 18)."""
    m = re.match(r"(\d{4})-W(\d+)", week_id)
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)


def num(s):
    """'>=449' -> 449, 449 -> 449, None -> 0."""
    if s is None:
        return 0
    if isinstance(s, str):
        s = s.replace(">=", "").strip()
        try:
            return int(s)
        except ValueError:
            return 0
    return int(s)


def load_history():
    return json.loads(HISTORY.read_text(encoding="utf-8"))["weeks"]


def load_daily():
    """Map: date_str (YYYY-MM-DD) -> {points, total, modalities, hr}."""
    out = {}
    for fp in sorted(ROOT.glob(DAILY_GLOB)):
        try:
            d = json.loads(fp.read_text(encoding="utf-8"))
        except Exception:
            continue
        meta = d.get("metadata", {})
        wid = meta.get("week", "")
        year, week = parse_week(wid)
        if not year:
            continue
        monday = iso_week_monday(year, week)
        daily = d.get("daily", {})
        for day_ch, info in daily.items():
            if day_ch not in DAY_TO_OFFSET:
                continue
            dt = monday + timedelta(days=DAY_TO_OFFSET[day_ch])
            out[dt.isoformat()] = {
                "total": info.get("total", 0),
                "points": info.get("points", 0),
                "active_hr": info.get("active_hr", 0),
                "xr": info.get("X光", 0),
                "ct": info.get("CT", 0),
                "us": info.get("US", 0),
                "mammo": info.get("Mammo", 0),
                "week_id": wid,
                "day": day_ch,
            }
    return out


def build_weekly_summary(weeks):
    """Normalize per-week summary."""
    rows = []
    for w in weeks:
        wid = w.get("week_id", "?")
        end = w.get("tracking", {}).get("end", {})
        comp = w.get("completed", {}) or w.get("completed_csv", {})
        add = w.get("added_estimated", {}) or {}
        net = w.get("tracking", {}).get("net_change", {})
        time = w.get("time", {}) or {}
        totals = w.get("totals", {}) or {}
        rows.append({
            "week": wid,
            "end_xr": end.get("xr", 0),
            "end_ct": end.get("ct", 0),
            "end_us": end.get("us", 0),
            "end_mm": end.get("mammo", 0),
            "comp_xr": comp.get("xr", 0),
            "comp_ct": comp.get("ct", 0),
            "comp_us": comp.get("us", 0),
            "comp_mm": comp.get("mammo", 0),
            "comp_bmd": comp.get("bmd", 0),
            "comp_ivp": comp.get("ivp", 0),
            "add_xr": num(add.get("xr")),
            "add_ct": num(add.get("ct")),
            "add_us": num(add.get("us")),
            "add_mm": num(add.get("mammo")),
            "net_xr": net.get("xr", 0),
            "net_ct": net.get("ct", 0),
            "net_us": net.get("us", 0),
            "net_mm": net.get("mammo", 0),
            "report_hr": time.get("report_hr") or 0,
            "points": totals.get("points") or 0,
            "grand_total": totals.get("grand_total") or 0,
        })
    return rows


def build_heatmap_grid(daily):
    """Build calendar grid (Mon-Sun rows, weeks as columns)."""
    if not daily:
        return [], None, None
    dates = sorted(daily.keys())
    first = date.fromisoformat(dates[0])
    last = date.fromisoformat(dates[-1])
    # Snap to Monday before/at first
    start = first - timedelta(days=first.weekday())
    cells = []
    cur = start
    while cur <= last:
        info = daily.get(cur.isoformat())
        cells.append({"date": cur.isoformat(), "info": info, "weekday": cur.weekday()})
        cur += timedelta(days=1)
    return cells, start, last


def points_intensity(p):
    """0-4 intensity level, returns CSS class suffix."""
    if not p or p <= 0:
        return 0
    if p < 200:
        return 1
    if p < 400:
        return 2
    if p < 600:
        return 3
    return 4


def render():
    weeks_raw = load_history()
    weekly = build_weekly_summary(weeks_raw)
    daily = load_daily()
    cells, start, last = build_heatmap_grid(daily)

    # Build SVG line chart for added
    weeks_lbl = [w["week"][-3:] for w in weekly]  # W08, W09 ...
    n = len(weekly)

    # Compute max for scaling
    # XR is ~10x larger than CT/US/Mammo, so use separate scales/charts
    max_added = max(max(w["add_xr"] for w in weekly), 1)
    max_comp = max(w["comp_xr"] + w["comp_ct"] + w["comp_us"] + w["comp_mm"] for w in weekly)
    max_pts = max((w["points"] for w in weekly), default=1)
    max_hr = max((w["report_hr"] for w in weekly), default=1)
    max_end = max(w["end_xr"] for w in weekly)

    # --- Non-XR (CT/US/Mammo) separate scales so small modalities are readable ---
    max_added_oth = max((max(w["add_ct"], w["add_us"], w["add_mm"]) for w in weekly), default=1) or 1
    max_comp_oth = max((w["comp_ct"] + w["comp_us"] + w["comp_mm"] for w in weekly), default=1) or 1
    max_end_oth = max((max(w["end_ct"], w["end_us"], w["end_mm"]) for w in weekly), default=1) or 1

    # SVG dimensions
    W = 760
    H = 220
    PADL, PADR, PADT, PADB = 50, 20, 20, 30
    PW = W - PADL - PADR
    PH = H - PADT - PADB

    def x_at(i):
        return PADL + (PW * i / max(n - 1, 1))

    def y_at(v, vmax):
        return PADT + PH - (PH * v / max(vmax, 1))

    def line_path(values, vmax):
        pts = []
        for i, v in enumerate(values):
            pts.append(f"{x_at(i):.1f},{y_at(v, vmax):.1f}")
        return "M " + " L ".join(pts)

    def axis_x_labels():
        return "".join(
            f'<text x="{x_at(i):.1f}" y="{H - PADB + 14}" text-anchor="middle" '
            f'fill="#6b7088" font-size="10" font-family="JetBrains Mono">{lbl}</text>'
            for i, lbl in enumerate(weeks_lbl)
        )

    def axis_y_labels(vmax, count=4):
        out = []
        for k in range(count + 1):
            v = vmax * k / count
            y = y_at(v, vmax)
            out.append(
                f'<text x="{PADL - 6}" y="{y + 3:.1f}" text-anchor="end" '
                f'fill="#6b7088" font-size="10" font-family="JetBrains Mono">{int(v)}</text>'
            )
            out.append(f'<line x1="{PADL}" x2="{W - PADR}" y1="{y:.1f}" y2="{y:.1f}" '
                       f'stroke="#2a2d3a" stroke-width="0.5"/>')
        return "".join(out)

    def render_line_chart(series_list, vmax, height=H):
        """series_list = [(label, color, [values])]"""
        out = [f'<svg viewBox="0 0 {W} {height}" preserveAspectRatio="xMinYMid meet" '
               f'style="width:100%;height:auto">']
        out.append(axis_y_labels(vmax))
        for label, color, values in series_list:
            path = line_path(values, vmax)
            out.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="2"/>')
            for i, v in enumerate(values):
                out.append(f'<circle cx="{x_at(i):.1f}" cy="{y_at(v, vmax):.1f}" r="3" '
                           f'fill="{color}"><title>{label} {weeks_lbl[i]}: {v}</title></circle>')
        out.append(axis_x_labels())
        out.append('</svg>')
        return "".join(out)

    def render_stacked_bar(series_list, vmax, bar_w=36):
        """series_list = [(label, color, [values])] — stacked vertically per week."""
        out = [f'<svg viewBox="0 0 {W} {H}" preserveAspectRatio="xMinYMid meet" '
               f'style="width:100%;height:auto">']
        out.append(axis_y_labels(vmax))
        for i in range(n):
            cx = x_at(i)
            cumulative = 0
            for label, color, values in series_list:
                v = values[i]
                if v <= 0:
                    continue
                y_top = y_at(cumulative + v, vmax)
                y_bot = y_at(cumulative, vmax)
                h = max(y_bot - y_top, 0.5)
                out.append(f'<rect x="{cx - bar_w/2:.1f}" y="{y_top:.1f}" '
                           f'width="{bar_w}" height="{h:.1f}" fill="{color}">'
                           f'<title>{label} {weeks_lbl[i]}: {v}</title></rect>')
                cumulative += v
        out.append(axis_x_labels())
        out.append('</svg>')
        return "".join(out)

    def render_bar(values, vmax, color, label, bar_w=36):
        out = [f'<svg viewBox="0 0 {W} {H}" preserveAspectRatio="xMinYMid meet" '
               f'style="width:100%;height:auto">']
        out.append(axis_y_labels(vmax))
        for i, v in enumerate(values):
            if v <= 0:
                continue
            cx = x_at(i)
            y_top = y_at(v, vmax)
            y_bot = y_at(0, vmax)
            h = y_bot - y_top
            out.append(f'<rect x="{cx - bar_w/2:.1f}" y="{y_top:.1f}" '
                       f'width="{bar_w}" height="{h:.1f}" fill="{color}" rx="2">'
                       f'<title>{label} {weeks_lbl[i]}: {v}</title></rect>')
            out.append(f'<text x="{cx:.1f}" y="{y_top - 4:.1f}" text-anchor="middle" '
                       f'fill="#c8ccd8" font-size="10" font-family="JetBrains Mono">{v}</text>')
        out.append(axis_x_labels())
        out.append('</svg>')
        return "".join(out)

    # Series — XR separated from CT/US/Mammo (XR ~10x larger)
    add_series_xr = [("XR", "#5b8af0", [w["add_xr"] for w in weekly])]
    add_series_oth = [
        ("CT", "#e8923a", [w["add_ct"] for w in weekly]),
        ("US", "#4caf7d", [w["add_us"] for w in weekly]),
        ("Mammo", "#e06090", [w["add_mm"] for w in weekly]),
    ]
    comp_series_xr = [("XR", "#5b8af0", [w["comp_xr"] for w in weekly])]
    comp_series_oth = [
        ("CT", "#e8923a", [w["comp_ct"] for w in weekly]),
        ("US", "#4caf7d", [w["comp_us"] for w in weekly]),
        ("Mammo", "#e06090", [w["comp_mm"] for w in weekly]),
    ]
    end_series_xr = [("XR", "#5b8af0", [w["end_xr"] for w in weekly])]
    end_series_oth = [
        ("CT", "#e8923a", [w["end_ct"] for w in weekly]),
        ("US", "#4caf7d", [w["end_us"] for w in weekly]),
        ("Mammo", "#e06090", [w["end_mm"] for w in weekly]),
    ]
    max_comp_xr = max((w["comp_xr"] for w in weekly), default=1) or 1
    pts_vals = [round(w["points"]) for w in weekly]
    hr_vals = [w["report_hr"] for w in weekly]
    grand_total_vals = [w["grand_total"] or sum(
        w[k] for k in ("comp_xr", "comp_ct", "comp_us", "comp_mm", "comp_bmd", "comp_ivp")
    ) for w in weekly]

    # Cases per hour productivity
    prod_vals = [round(g / h, 1) if h else 0 for g, h in zip(grand_total_vals, hr_vals)]
    max_prod = max(prod_vals) if prod_vals else 1

    # Heatmap (Mon-Sun rows, weeks columns)
    days_per_row = 7
    if cells:
        nweeks = (len(cells) + days_per_row - 1) // days_per_row
    else:
        nweeks = 0
    cell_size = 13
    cell_gap = 3
    hm_w = (cell_size + cell_gap) * nweeks
    hm_h = (cell_size + cell_gap) * 7

    hm_svg = [f'<svg viewBox="0 -16 {hm_w + 60} {hm_h + 30}" '
              f'style="width:100%;max-width:{hm_w + 80}px;height:auto">']
    # Day labels
    for di, dch in enumerate(["一", "二", "三", "四", "五", "六", "日"]):
        hm_svg.append(f'<text x="{hm_w + 4}" y="{di*(cell_size+cell_gap)+10}" '
                      f'fill="#6b7088" font-size="10" font-family="Noto Sans TC">{dch}</text>')
    # Cells
    for i, c in enumerate(cells):
        wcol = i // 7
        wd = c["weekday"]
        x = wcol * (cell_size + cell_gap)
        y = wd * (cell_size + cell_gap)
        info = c["info"]
        if info:
            lvl = points_intensity(info["points"])
            color = ["#13161f", "#244731", "#2f6c47", "#3a915c", "#4caf7d"][lvl]
            tooltip = f"{c['date']} ({info['day']}) — {info['total']}件 / {info['points']:.0f}pt / {info['active_hr']}hr"
        else:
            color = "#0c0e14"
            tooltip = c["date"]
        hm_svg.append(f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" '
                      f'rx="2" fill="{color}"><title>{tooltip}</title></rect>')
    # Month labels
    seen_months = set()
    for i, c in enumerate(cells):
        wcol = i // 7
        wd = c["weekday"]
        if wd != 0:
            continue
        m = c["date"][:7]  # YYYY-MM
        if m in seen_months:
            continue
        seen_months.add(m)
        x = wcol * (cell_size + cell_gap)
        mm = int(m.split("-")[1])
        hm_svg.append(f'<text x="{x}" y="-4" fill="#6b7088" font-size="10" '
                      f'font-family="JetBrains Mono">{mm}月</text>')
    hm_svg.append('</svg>')
    hm_html = "".join(hm_svg)

    # Stats summary
    total_completed = sum(grand_total_vals)
    total_points = sum(pts_vals)
    total_hr = sum(hr_vals)
    avg_per_week = total_completed // max(n, 1)

    # Build HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>放射科多週趨勢 — W08~W18</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #0c0e14; --bg2: #13161f; --bg3: #1a1d28;
    --border: #2a2d3a; --text: #c8ccd8; --text-dim: #6b7088;
    --accent: #5b8af0;
    --xr: #5b8af0; --ct: #e8923a; --us: #4caf7d; --mm: #e06090;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); font-family: 'Noto Sans TC', sans-serif; font-size: 14px; line-height: 1.5; padding: 0 0 60px; }}
  .header {{ background: linear-gradient(135deg, #131a2e, #0c0e14); border-bottom: 2px solid var(--accent); padding: 28px 24px 22px; text-align: center; }}
  .header h1 {{ font-size: 22px; color: #fff; }}
  .header .meta {{ font-size: 13px; color: var(--text-dim); margin-top: 6px; font-family: 'JetBrains Mono', monospace; }}
  .container {{ max-width: 1100px; margin: 0 auto; padding: 0 16px; }}
  .section {{ margin: 24px 0; }}
  .section-title {{ font-size: 15px; font-weight: 700; color: #fff; border-left: 3px solid var(--accent); padding: 6px 0 6px 14px; margin-bottom: 14px; display: flex; gap: 8px; align-items: center; }}
  .section-title .num {{ background: var(--accent); color: #fff; border-radius: 50%; width: 22px; height: 22px; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; }}
  .card {{ background: var(--bg2); border: 1px solid var(--border); border-radius: 8px; padding: 16px; }}
  .mono {{ font-family: 'JetBrains Mono', monospace; }}
  .legend {{ display: flex; gap: 14px; flex-wrap: wrap; margin-bottom: 10px; font-size: 12px; }}
  .legend-item {{ display: flex; align-items: center; gap: 5px; }}
  .legend-dot {{ width: 12px; height: 12px; border-radius: 2px; }}
  .stat-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 16px; }}
  .stat-card {{ background: var(--bg2); border: 1px solid var(--border); border-radius: 8px; padding: 14px; text-align: center; }}
  .stat-num {{ font-size: 26px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }}
  .stat-label {{ font-size: 11px; color: var(--text-dim); margin-top: 4px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
  th {{ background: var(--bg3); color: var(--text-dim); font-weight: 500; padding: 6px 8px; text-align: right; border-bottom: 1px solid var(--border); }}
  td {{ padding: 5px 8px; border-bottom: 1px solid var(--border); text-align: right; }}
  td:first-child, th:first-child {{ text-align: left; }}
  tr:last-child td {{ border-bottom: none; }}
  .heatmap-legend {{ display: flex; gap: 4px; align-items: center; font-size: 11px; color: var(--text-dim); margin-top: 12px; }}
  .heatmap-legend .swatch {{ width: 13px; height: 13px; border-radius: 2px; }}
  .delta-pos {{ color: #e05c5c; font-weight: 600; }}
  .delta-neg {{ color: #4caf7d; font-weight: 600; }}
</style>
</head>
<body>

<div class="header">
  <h1>放射科多週趨勢分析</h1>
  <div class="meta">{weekly[0]['week']} ~ {weekly[-1]['week']} · {n} 週 · {total_completed} 件 · {round(total_points):,} pt · {total_hr:.1f}hr</div>
</div>

<div class="container">

<!-- Stats summary -->
<div class="section">
  <div class="stat-grid">
    <div class="stat-card"><div class="stat-num" style="color:var(--accent)">{n}</div><div class="stat-label">統計週數</div></div>
    <div class="stat-card"><div class="stat-num" style="color:var(--xr)">{total_completed:,}</div><div class="stat-label">累計完成件數</div></div>
    <div class="stat-card"><div class="stat-num" style="color:var(--mm)">{round(total_points):,}</div><div class="stat-label">累計工作點值</div></div>
    <div class="stat-card"><div class="stat-num" style="color:var(--ct)">{total_hr:.0f}hr</div><div class="stat-label">累計報告時數</div></div>
    <div class="stat-card"><div class="stat-num" style="color:var(--us)">{avg_per_week}</div><div class="stat-label">週均件數</div></div>
  </div>
</div>

<!-- 1. 各檢查每週新增 -->
<div class="section">
  <div class="section-title"><span class="num">1</span>各檢查每週新增份數變化（推算值，&gt;= 期末-期初+完成）</div>
  <div class="card">
    <div style="font-size:12px;color:var(--text-dim);margin-bottom:6px">① X光（單獨刻度，量大）</div>
    <div class="legend">
      <div class="legend-item"><span class="legend-dot" style="background:var(--xr)"></span>X光（峰值 {max_added}）</div>
    </div>
    {render_line_chart(add_series_xr, max_added)}
    <div style="font-size:12px;color:var(--text-dim);margin:14px 0 6px">② CT / US / Mammo（放大刻度，峰值 {max_added_oth}）</div>
    <div class="legend">
      <div class="legend-item"><span class="legend-dot" style="background:var(--ct)"></span>CT</div>
      <div class="legend-item"><span class="legend-dot" style="background:var(--us)"></span>US</div>
      <div class="legend-item"><span class="legend-dot" style="background:var(--mm)"></span>Mammo</div>
    </div>
    {render_line_chart(add_series_oth, max_added_oth)}
  </div>
</div>

<!-- 2. 每週點值 -->
<div class="section">
  <div class="section-title"><span class="num">2</span>每週工作點值（pt）</div>
  <div class="card">
    {render_bar(pts_vals, max_pts, "#d4a94a", "Points")}
    <div style="font-size:12px;color:var(--text-dim);margin-top:8px">
      W08-W10 為 GPT 對話手動整理，無 work_points 欄位（顯示 0）；W11+ 為 CSV 模式。
    </div>
  </div>
</div>

<!-- 3. 每週完成件數 -->
<div class="section">
  <div class="section-title"><span class="num">3</span>每週完成件數變化</div>
  <div class="card">
    <div style="font-size:12px;color:var(--text-dim);margin-bottom:6px">① X光完成（單獨刻度，峰值 {max_comp_xr}）</div>
    <div class="legend">
      <div class="legend-item"><span class="legend-dot" style="background:var(--xr)"></span>X光</div>
    </div>
    {render_bar([w["comp_xr"] for w in weekly], max_comp_xr, "#5b8af0", "XR")}
    <div style="font-size:12px;color:var(--text-dim);margin:14px 0 6px">② CT / US / Mammo 完成（堆疊，放大刻度，峰值 {max_comp_oth}）</div>
    <div class="legend">
      <div class="legend-item"><span class="legend-dot" style="background:var(--ct)"></span>CT</div>
      <div class="legend-item"><span class="legend-dot" style="background:var(--us)"></span>US</div>
      <div class="legend-item"><span class="legend-dot" style="background:var(--mm)"></span>Mammo</div>
    </div>
    {render_stacked_bar(comp_series_oth, max_comp_oth)}
  </div>
</div>

<!-- 4. GitHub-style heatmap -->
<div class="section">
  <div class="section-title"><span class="num">4</span>每日工作強度熱力圖（GitHub 風格，色階＝點值）</div>
  <div class="card" style="overflow-x:auto">
    {hm_html}
    <div class="heatmap-legend" style="margin-top:14px">
      Less
      <span class="swatch" style="background:#13161f"></span>
      <span class="swatch" style="background:#244731"></span>
      <span class="swatch" style="background:#2f6c47"></span>
      <span class="swatch" style="background:#3a915c"></span>
      <span class="swatch" style="background:#4caf7d"></span>
      More
      <span style="margin-left:14px">|  色階：&lt;200pt / 200-400 / 400-600 / 600-800 / 800+</span>
    </div>
    <div style="font-size:12px;color:var(--text-dim);margin-top:8px">
      資料來源：W11~W18 每日 work_points（W08-W10 無 daily breakdown）。滑鼠移至格子可看詳情。
    </div>
  </div>
</div>

<!-- 5. 期末剩餘量趨勢 -->
<div class="section">
  <div class="section-title"><span class="num">5</span>期末剩餘量趨勢（積案壓力指標）</div>
  <div class="card">
    <div style="font-size:12px;color:var(--text-dim);margin-bottom:6px">① X光剩餘（單獨刻度，峰值 {max_end}）— 主要壓力源</div>
    <div class="legend">
      <div class="legend-item"><span class="legend-dot" style="background:var(--xr)"></span>X光</div>
    </div>
    {render_line_chart(end_series_xr, max_end)}
    <div style="font-size:12px;color:var(--text-dim);margin:14px 0 6px">② CT / US / Mammo 剩餘（放大刻度，峰值 {max_end_oth}）</div>
    <div class="legend">
      <div class="legend-item"><span class="legend-dot" style="background:var(--ct)"></span>CT</div>
      <div class="legend-item"><span class="legend-dot" style="background:var(--us)"></span>US</div>
      <div class="legend-item"><span class="legend-dot" style="background:var(--mm)"></span>Mammo</div>
    </div>
    {render_line_chart(end_series_oth, max_end_oth)}
    <div style="font-size:12px;color:var(--text-dim);margin-top:8px">
      X光剩餘量持續累積（W08 518 → W17 731 → W18 720），仍是主要壓力源。
    </div>
  </div>
</div>

<!-- 6. 每週活躍時數 + 7. cases/hr -->
<div class="section">
  <div class="section-title"><span class="num">6</span>每週報告時數 vs 件數產出比</div>
  <div class="card">
    <h4 style="font-size:13px;color:#fff;margin-bottom:10px">報告活躍時數 (hr)</h4>
    {render_bar([round(v,1) for v in hr_vals], max(max_hr, 1), "#9b72e0", "Hours")}
    <h4 style="font-size:13px;color:#fff;margin:16px 0 10px">每小時件數產出 (cases/hr)</h4>
    {render_bar(prod_vals, max(max_prod, 1), "#3ab8c8", "cases/hr")}
  </div>
</div>

<!-- 8. 數據總表 -->
<div class="section">
  <div class="section-title"><span class="num">7</span>每週數據總表</div>
  <div class="card" style="overflow-x:auto">
    <table>
      <thead>
        <tr>
          <th>週次</th>
          <th>新增 XR</th><th>新增 CT</th><th>新增 US</th><th>新增 Mm</th>
          <th>完成 XR</th><th>完成 CT</th><th>完成 US</th><th>完成 Mm</th>
          <th>總件數</th>
          <th>點值</th>
          <th>時數</th>
          <th>件/hr</th>
          <th>期末 XR</th>
        </tr>
      </thead>
      <tbody>
"""
    for i, w in enumerate(weekly):
        gt = grand_total_vals[i]
        prod = prod_vals[i]
        html += (
            f"<tr><td><strong>{w['week']}</strong></td>"
            f"<td class='mono'>{w['add_xr']}</td>"
            f"<td class='mono'>{w['add_ct']}</td>"
            f"<td class='mono'>{w['add_us']}</td>"
            f"<td class='mono'>{w['add_mm']}</td>"
            f"<td class='mono'>{w['comp_xr']}</td>"
            f"<td class='mono'>{w['comp_ct']}</td>"
            f"<td class='mono'>{w['comp_us']}</td>"
            f"<td class='mono'>{w['comp_mm']}</td>"
            f"<td class='mono'><strong>{gt}</strong></td>"
            f"<td class='mono'>{round(w['points']) if w['points'] else '-'}</td>"
            f"<td class='mono'>{w['report_hr']:.1f}</td>"
            f"<td class='mono'>{prod}</td>"
            f"<td class='mono'>{w['end_xr']}</td></tr>\n"
        )
    html += """
      </tbody>
    </table>
  </div>
</div>

<div style="text-align:center;color:var(--text-dim);font-size:11px;margin-top:30px;padding:20px 0;border-top:1px solid var(--border)">
  Generated by build_trends.py · radtracker · 純 SVG/CSS，無 JS 依賴
</div>

</div>
</body>
</html>
"""
    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"Wrote: {OUT_HTML}")
    print(f"Weeks: {n}, Daily cells: {len(daily)}, Heatmap span: {start} -> {last}")


if __name__ == "__main__":
    render()
