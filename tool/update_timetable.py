"""Refresh the train data embedded in tool/timetable.html from the TRA website.

Scrapes the per-station weekday timetable for the tracked stations, joins the
rows by train number, and rewrites the block between the TRAIN DATA markers in
timetable.html. Everything outside those markers is left untouched.

Usage:
    python update_timetable.py                 # next weekday
    python update_timetable.py --date 2026/09/07
    python update_timetable.py --dry-run       # scrape and report, write nothing
"""

import argparse
import datetime as dt
import json
import re
import ssl
import sys
import urllib.parse
import urllib.request
from pathlib import Path

HTML = Path(__file__).with_name("timetable.html")
BASE = "https://www.railway.gov.tw/tra-tip-web/tip/tip001/tip112/querybystationblank"

# Tracked stations, ordered north to south. The query name is what the site
# expects in the URL (it uses the formal form for a few stations).
STATIONS = [
    ("4120", "新營", "新營"),
    ("4170", "善化", "善化"),
    ("4210", "大橋", "大橋"),
    ("4220", "台南", "臺南"),
    ("4340", "新左營", "新左營"),
    ("4370", "美術館", "美術館"),
    ("4400", "高雄", "高雄"),
]
NORTH_TO_SOUTH = [s[1] for s in STATIONS]
NORTHBOUND = list(reversed(NORTH_TO_SOUTH))  # 高雄 first
WEEKDAYS = "一二三四五六日"

ROW_RE = re.compile(r"<tr>(.*?)</tr>", re.S)
TRAIN_RE = re.compile(r"trainNo=(\d+)[^>]*>([^<]+)</a>(.*?)</li>", re.S)
SPAN_RE = re.compile(r"<span>([^<]*)</span>")
TIME_RE = re.compile(r">(\d{2}:\d{2})<")
NUM_RE = re.compile(r"(\d+)$")


def next_weekday(today=None):
    d = today or dt.date.today()
    while d.weekday() >= 5:  # Sat/Sun -> roll forward to Monday
        d += dt.timedelta(days=1)
    return d


def ssl_context():
    """Verify the certificate, but without Python 3.13+ strict X509 checks.

    The TRA certificate chain lacks a Subject Key Identifier, which strict mode
    rejects even though the chain itself is valid (curl and browsers accept it).
    """
    ctx = ssl.create_default_context()
    ctx.verify_flags &= ~ssl.VERIFY_X509_STRICT
    return ctx


def fetch(code, query_name, ride_date, ctx):
    url = "%s?rideDate=%s&station=%s-%s" % (
        BASE, ride_date, code, urllib.parse.quote(query_name))
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
        return resp.read().decode("utf-8", "replace")


def parse_station(html, station, trains):
    """Merge one station page into the train dict keyed by train number."""
    found = 0
    for row in ROW_RE.findall(html):
        m = TRAIN_RE.search(row)
        if not m:
            continue
        no, label, tail = m.group(1), m.group(2).strip(), m.group(3)
        time = TIME_RE.search(row)
        if not time:
            continue
        spans = [s.strip() for s in SPAN_RE.findall(tail)]
        od = [s for s in spans if s not in ("(", ")", "→", "->")]
        rec = trains.setdefault(no, {"label": label, "od": [], "times": {}})
        if len(od) == 2 and len(rec["od"]) != 2:
            rec["od"] = od
        rec["times"][station] = time.group(1)
        found += 1
    return found


def to_minutes(t):
    h, m = t.split(":")
    return int(h) * 60 + int(m)


def split_by_direction(trains):
    """Northbound = even train number; verified against the actual times."""
    north, south, flipped = [], [], []
    for no, v in trains.items():
        num = int(NUM_RE.search(v["label"]).group(1))
        is_north = num % 2 == 0
        times = v["times"]
        if len(times) >= 2:
            stops = sorted(times, key=NORTH_TO_SOUTH.index)
            diff = to_minutes(times[stops[0]]) - to_minutes(times[stops[-1]])
            if diff < -720:
                diff += 1440
            elif diff > 720:
                diff -= 1440
            if (diff > 0) != is_north:
                flipped.append(v["label"])
                is_north = diff > 0
        od = v["od"] if len(v["od"]) == 2 else ["", ""]
        rec = {
            "id": v["label"],
            "type": re.match(r"^(.*?)\d+$", v["label"]).group(1),
            "from": od[0],
            "to": od[1],
            "times": times,
        }
        (north if is_north else south).append(rec)
    return north, south, flipped


def sort_key(rec, order):
    """Sort by the first available departure; train number breaks ties so that
    re-running the scrape produces a stable diff."""
    num = int(NUM_RE.search(rec["id"]).group(1))
    for s in order:
        if s in rec["times"]:
            return (to_minutes(rec["times"][s]), num)
    return (0, num)


def emit(name, recs, order):
    lines = ["const %s = [" % name]
    for r in recs:
        times = ", ".join(
            "%s: %s" % (s, '"%s"' % r["times"][s] if s in r["times"] else "null")
            for s in order)
        lines.append('  { id: "%s", type: "%s", from: "%s", to: "%s", times: { %s } },'
                     % (r["id"], r["type"], r["from"], r["to"], times))
    lines.append("];")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--date", help="ride date as YYYY/MM/DD (default: next weekday)")
    ap.add_argument("--dry-run", action="store_true", help="scrape only, do not write")
    args = ap.parse_args()

    if args.date:
        day = dt.datetime.strptime(args.date, "%Y/%m/%d").date()
    else:
        day = next_weekday()
    ride_date = day.strftime("%Y/%m/%d")
    if day.weekday() >= 5:
        print("WARNING: %s is a weekend; the page will show holiday services." % ride_date)
    print("Ride date: %s (%s)" % (ride_date, WEEKDAYS[day.weekday()]))

    trains = {}
    ctx = ssl_context()
    for code, station, query_name in STATIONS:
        try:
            html = fetch(code, query_name, ride_date, ctx)
        except Exception as exc:
            print("ERROR: failed to fetch %s (%s): %s" % (station, code, exc))
            return 1
        n = parse_station(html, station, trains)
        print("  %-4s %-4s %4d rows" % (code, station, n))
        if n == 0:
            print("ERROR: no rows parsed for %s -- the page layout may have changed." % station)
            return 1

    north, south, flipped = split_by_direction(trains)
    north.sort(key=lambda r: sort_key(r, NORTHBOUND))
    south.sort(key=lambda r: sort_key(r, NORTH_TO_SOUTH))
    shalun = sum(1 for r in north + south if "沙崙" in r["from"] + r["to"])
    print("Trains: %d total, %d northbound, %d southbound, %d via Shalun branch"
          % (len(trains), len(north), len(south), shalun))
    if flipped:
        print("NOTE: train number parity disagreed with the timetable for %d train(s); "
              "used the timetable: %s" % (len(flipped), ", ".join(flipped)))

    block = ('// ==== TRAIN DATA START (generated by update_timetable.py -- do not edit by hand) ====\n'
             'const dataDate = "%s (週%s)";\n\n%s\n\n%s\n'
             '// ==== TRAIN DATA END ===='
             % (ride_date, WEEKDAYS[day.weekday()],
                emit("northTrains", north, NORTHBOUND),
                emit("southTrains", south, NORTH_TO_SOUTH)))

    page = HTML.read_text(encoding="utf-8")
    new_page, count = re.subn(
        r"// ==== TRAIN DATA START.*?// ==== TRAIN DATA END ====",
        lambda _: block, page, flags=re.S)
    if count != 1:
        print("ERROR: expected 1 TRAIN DATA block in timetable.html, found %d." % count)
        return 1

    if args.dry_run:
        print("Dry run: timetable.html not modified.")
        return 0
    HTML.write_text(new_page, encoding="utf-8", newline="\n")
    print("Updated %s" % HTML.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
