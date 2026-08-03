#!/usr/bin/env python3
"""build_course_hub.py — 把一個資料夾裡的多場 viewer 串成一頁課程首頁。

十場講座就是十個 viewer 檔，沒有首頁就只能靠檔名找。這頁做兩件單一 viewer 做不到的事：
  1. 十場的卡片一覽（講者、題目、時長、段數、投影片數、縮圖、一句摘要）
  2. ==跨場搜尋==：把每場的段落標題、重點、投影片 OCR 建成一個索引，搜尋結果直接帶
     `?t=<秒>` 開到那一場的那個時間點。想找「哪一場講過 stereotactic」時，這是唯一的辦法。

用法
  python build_course_hub.py "<課程資料夾>"
  python build_course_hub.py "<資料夾>" --title "2026 乳房影像系列" -o "課程首頁.html"

會略過沒有 viewer 的講座（先跑 batch_course.py）。
"""
from __future__ import annotations
import argparse
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote

VIDEO_EXT = (".mp4", ".mkv", ".mov", ".webm", ".m4v")


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8-sig"))


def parse_name(stem: str) -> tuple[str, str, str]:
    """`11506-09-陳詩華醫師-乳房攝影於乳房切片之應用` -> (09, 陳詩華醫師, 題目)。
    抓不到就整串當題目，不要為了排版硬猜。"""
    m = re.match(r"^(\d+)-(\d+)-([^-]+?醫師|[^-]+?主任|[^-]+?部長|[^-]+?教授)-(.+)$", stem)
    if m:
        return m.group(2), m.group(3), m.group(4)
    m = re.match(r"^\d+-(\d+)-(.+)$", stem)
    if m:
        return m.group(1), "", m.group(2)
    return "", "", stem


def collect(folder: Path) -> list[dict]:
    out = []
    for j in sorted(folder.glob("*.json")):
        if j.name.startswith("_") or j.name.endswith((".frames.json", ".frames_ocr.json")):
            continue
        viewer = folder / f"{j.stem}.viewer.html"
        if not viewer.exists():
            continue
        try:
            data = load(j)
        except json.JSONDecodeError:
            continue
        segs = data.get("segments") or []
        if not segs:
            continue
        no, speaker, topic = parse_name(j.stem)
        frames = [f for s in segs for f in (s.get("frames") or [])]
        out.append({
            "no": no, "speaker": speaker, "topic": topic, "stem": j.stem,
            "viewer": viewer.name, "segments": segs, "frames": frames,
            "thumb": frames[0] if frames else None,
            "minutes": round(float(segs[-1].get("end_sec") or 0) / 60),
            "summary": (data.get("overall_summary_zh") or "")[:150],
            "takeaways": data.get("takeaways_zh") or [],
        })
    return sorted(out, key=lambda x: (x["no"] or "zz", x["stem"]))


def build_index(items: list[dict]) -> list[dict]:
    """跨場搜尋索引：段落標題／重點／投影片 OCR，各自帶回到哪一場的哪一秒。"""
    idx = []
    for it in items:
        for t in it["takeaways"]:
            idx.append({"v": it["viewer"], "no": it["no"], "t": 0,
                        "k": "重點", "x": str(t)})
        for s in it["segments"]:
            sec = int(float(s.get("start_sec") or 0))
            idx.append({"v": it["viewer"], "no": it["no"], "t": sec,
                        "k": "段落", "x": str(s.get("title") or "")})
            for b in s.get("bullets_zh") or []:
                idx.append({"v": it["viewer"], "no": it["no"], "t": sec,
                            "k": "摘要", "x": str(b)})
            for e in s.get("frame_ocr") or []:
                m = re.search(r"-(\d{2})(\d{2})\.\w+$", str(e.get("frame", "")))
                ts = int(m.group(1)) * 60 + int(m.group(2)) if m else sec
                text = (e.get("text") or "").strip()
                if text:
                    idx.append({"v": it["viewer"], "no": it["no"], "t": ts,
                                "k": "投影片", "x": text})
    return idx


CSS = """
:root{--bg:#0f1115;--panel:#171a21;--line:#272c37;--fg:#e6e9ef;--dim:#9aa3b2;--accent:#4da3ff;--hit:#f5c451}
*{box-sizing:border-box}
body{margin:0;font:16px/1.7 "Noto Sans TC","Microsoft JhengHei",system-ui,sans-serif;background:var(--bg);color:var(--fg)}
header{padding:1.4rem 1.6rem .8rem;border-bottom:1px solid var(--line);background:var(--panel)}
h1{margin:0 0 .2rem;font-size:1.5rem}
.meta{color:var(--dim);font-size:.85rem}
.searchwrap{margin-top:.9rem;position:relative;max-width:44rem}
#q{width:100%;background:#0d1016;border:1px solid var(--line);color:var(--fg);border-radius:8px;padding:.55rem .8rem;font-size:.95rem}
#results{position:absolute;top:108%;left:0;right:0;max-height:66vh;overflow:auto;background:var(--panel);border:1px solid var(--line);border-radius:10px;display:none;z-index:20;box-shadow:0 10px 40px #000a}
#results.open{display:block}
.sr{display:grid;grid-template-columns:3rem 4.5rem 1fr 3.5rem;gap:.5rem;align-items:baseline;width:100%;text-align:left;background:none;border:0;border-bottom:1px solid var(--line);padding:.45rem .7rem;color:var(--fg);cursor:pointer;font:inherit;font-size:.85rem}
.sr:hover{background:#1e2530}
.sr .no{color:var(--accent);font-weight:600}
.sr .k{color:var(--dim);font-size:.75rem}
.sr .ts{color:var(--accent);font-size:.78rem;text-align:right}
.count{padding:.4rem .7rem;color:var(--dim);font-size:.78rem}
main{display:grid;grid-template-columns:repeat(auto-fill,minmax(21rem,1fr));gap:1rem;padding:1.3rem 1.6rem 3rem}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;overflow:hidden;text-decoration:none;color:inherit;display:flex;flex-direction:column;transition:border-color .12s}
.card:hover{border-color:var(--accent)}
.card img{width:100%;aspect-ratio:16/9;object-fit:cover;background:#000;border-bottom:1px solid var(--line)}
.card .body{padding:.7rem .9rem 1rem}
.card .no{color:var(--accent);font-weight:700;margin-right:.4rem}
.card h2{font-size:1rem;margin:0 0 .3rem;line-height:1.45}
.card .who{color:var(--dim);font-size:.82rem;margin-bottom:.4rem}
.card .sum{color:var(--dim);font-size:.8rem;line-height:1.6;
  display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.card .stat{margin-top:.6rem;color:var(--dim);font-size:.75rem;border-top:1px solid var(--line);padding-top:.5rem}
mark{background:var(--hit);color:#111}
footer{padding:0 1.6rem 2rem;color:var(--dim);font-size:.75rem}
"""

JS = """
const IDX=INDEX;
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const fmt=t=>{t=Math.max(0,Math.floor(t||0));return String(Math.floor(t/60)).padStart(2,'0')+':'+String(t%60).padStart(2,'0')};
const box=document.getElementById('results');
function run(qs){
  const terms=(qs||'').trim().toLowerCase().split(/\\s+/).filter(Boolean);
  if(!terms.length){box.classList.remove('open');box.innerHTML='';return;}
  const hits=IDX.filter(r=>terms.every(t=>r.x.toLowerCase().includes(t))).slice(0,120);
  if(!hits.length){box.innerHTML='<div class="count">無符合結果</div>';box.classList.add('open');return;}
  const perLecture={}; hits.forEach(h=>perLecture[h.no]=(perLecture[h.no]||0)+1);
  const spread=Object.keys(perLecture).sort().map(n=>n+'('+perLecture[n]+')').join('　');
  box.innerHTML='<div class="count">'+hits.length+' 筆，分布：'+spread+'</div>'+hits.map(h=>{
    const pos=Math.max(0,h.x.toLowerCase().indexOf(terms[0])-24);
    let frag=esc((pos?'…':'')+h.x.slice(pos,pos+120));
    for(const t of terms) frag=frag.replace(new RegExp('('+t.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\\\$&')+')','ig'),'<mark>$1</mark>');
    return '<button class="sr" data-v="'+esc(h.v)+'" data-t="'+h.t+'"><span class="no">'+esc(h.no)
      +'</span><span class="k">'+esc(h.k)+'</span><span>'+frag+'</span><span class="ts">'+fmt(h.t)+'</span></button>';
  }).join('');
  box.classList.add('open');
}
let tmr;
document.getElementById('q').addEventListener('input',e=>{clearTimeout(tmr);tmr=setTimeout(()=>run(e.target.value),120);});
document.addEventListener('click',e=>{
  const sr=e.target.closest('.sr');
  if(sr){ location.href=encodeURI(sr.dataset.v)+'?t='+sr.dataset.t; return; }
  if(!e.target.closest('.searchwrap')) box.classList.remove('open');
});
document.addEventListener('keydown',e=>{
  if(e.key==='/'&&!/^(INPUT|TEXTAREA)$/.test(e.target.tagName)){e.preventDefault();document.getElementById('q').focus();}
  if(e.key==='Escape') box.classList.remove('open');
});
"""


def main():
    ap = argparse.ArgumentParser(description="多場 viewer -> 一頁課程首頁（含跨場搜尋）")
    ap.add_argument("folder")
    ap.add_argument("--title", help="課程名稱（預設用資料夾名）")
    ap.add_argument("-o", "--out", help="輸出檔名（預設 課程首頁.html）")
    args = ap.parse_args()

    folder = Path(args.folder)
    if not folder.is_dir():
        print(f"[錯誤] 不是資料夾：{folder}", file=sys.stderr)
        sys.exit(2)
    items = collect(folder)
    if not items:
        print("[錯誤] 找不到任何 *.viewer.html（先跑 batch_course.py）", file=sys.stderr)
        sys.exit(2)

    title = args.title or folder.name
    idx = build_index(items)
    total_min = sum(i["minutes"] for i in items)
    total_frames = sum(len(i["frames"]) for i in items)

    cards = []
    for it in items:
        thumb = (f'<img src="{html.escape(quote(it["thumb"]))}" loading="lazy" alt="">'
                 if it["thumb"] else "")
        cards.append(
            f'<a class="card" href="{html.escape(quote(it["viewer"]))}">{thumb}'
            f'<div class="body"><h2><span class="no">{html.escape(it["no"])}</span>'
            f'{html.escape(it["topic"])}</h2>'
            f'<div class="who">{html.escape(it["speaker"])}</div>'
            f'<div class="sum">{html.escape(it["summary"])}</div>'
            f'<div class="stat">{it["minutes"]} 分　·　{len(it["segments"])} 段　·　'
            f'{len(it["frames"])} 張投影片</div></div></a>')

    page = f"""<!DOCTYPE html>
<html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><style>{CSS}</style></head><body>
<header>
  <h1>{html.escape(title)}</h1>
  <div class="meta">{len(items)} 場　·　共 {total_min} 分（{total_min/60:.1f} 小時）　·
    {sum(len(i["segments"]) for i in items)} 段　·　{total_frames} 張投影片</div>
  <div class="searchwrap">
    <input id="q" placeholder="跨場搜尋：段落標題／摘要／投影片文字（按 / 聚焦）">
    <div id="results"></div>
  </div>
</header>
<main>{"".join(cards)}</main>
<footer>搜尋結果會直接開到該場的那個時間點。投影片文字為 OCR，有辨識誤差，僅供定位。</footer>
<script>const INDEX={json.dumps(idx, ensure_ascii=False)};</script>
<script>{JS}</script></body></html>
"""
    out = Path(args.out) if args.out else folder / "課程首頁.html"
    out.write_text(page, encoding="utf-8", newline="\n")
    print(f"{len(items)} 場｜{total_min} 分｜搜尋索引 {len(idx)} 筆")
    for it in items:
        print(f"  {it['no']} {it['speaker']:8s} {it['topic'][:30]:32s} "
              f"{it['minutes']:2d}分 {len(it['segments']):2d}段 {len(it['frames']):3d}圖")
    print(f"輸出 -> {out}  ({out.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
