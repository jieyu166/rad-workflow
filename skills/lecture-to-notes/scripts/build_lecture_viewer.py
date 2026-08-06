#!/usr/bin/env python3
"""build_lecture_viewer.py — 由 Task 6 分段 JSON + SRT + 影片產生單檔雙向同步 viewer。

和 tool/jsonvideo.htm 的差別：jsonvideo 是「通用載入器」，每次開啟要重新指定影片與字幕，
右側只有段落卡片；這支是「每場講座產生一頁」，把摘要層與逐字稿層當成同一條時間軸的兩個
圖層並排，播放時兩層同時高亮跟隨，點任何一行都能跳播。

同步精度（誠實說明）
  逐字稿層：每句都有 SRT 的真實時間碼 -> 句級精準同步。
  摘要層  ：Task 6 的 bullets 沒有各自的時間碼，只有段落起訖，所以 bullet 的時間是在
            段落區間內平均插補的「推估值」，頁面上會標示。要句級精準就得讓 Task 6 在
            產生 bullets 時附上時間碼（lecture-to-notes 的做法是每點都帶 (Vn MM:SS)）。

用法
  python build_lecture_viewer.py "<分段.json>"                    # 同層自動找同名 .srt / 影片
  python build_lecture_viewer.py "<分段.json>" --video "<a.mp4>" --srt "<a.srt>"
  python build_lecture_viewer.py "<分段.json>" -o "<輸出.html>"

產物是單一 .html（CSS/JS 內嵌），影片與截圖用相對路徑引用——把 html 跟影片放同層即可離線看。
"""
from __future__ import annotations
import argparse
import html
import json
import re
import sys
from pathlib import Path

VIDEO_EXT = (".mp4", ".m4v", ".webm", ".mov", ".mkv")


def frame_seconds(name: str, fallback: float = 0.0) -> float:
    """由檔名末尾的時間戳推秒數。`<stem>-MMSS.png`，但片長超過 99 分鐘時
    分鐘會變成三位數（`-14901.png` = 149:01），所以不能寫死四位數——
    固定取最後兩位當秒、其餘當分。"""
    m = re.search(r"-(\d+)\.\w+$", str(name))
    if not m:
        return fallback
    s = m.group(1)
    if len(s) < 3:
        return fallback
    return int(s[:-2]) * 60 + int(s[-2:])
SRT_TIME = re.compile(
    r"(\d{1,2}):(\d{2}):(\d{2})[,.](\d{1,3})\s*-->\s*(\d{1,2}):(\d{2}):(\d{2})[,.](\d{1,3})")


def read_text(p: Path) -> str:
    raw = p.read_bytes()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16")
    if raw[:3] == b"\xef\xbb\xbf":
        return raw.decode("utf-8-sig")
    return raw.decode("utf-8", "replace")


def parse_srt(path: Path) -> list[dict]:
    """回傳 [{start, end, text}]。只認時間碼行；序號行靠「下一行是不是時間碼」判斷——
    純數字行出現在字幕文字之後也可能是下一段的序號，不能只看是不是第一行。"""
    lines = read_text(path).replace("\r", "").split("\n")
    cues, cur = [], None
    for i, line in enumerate(lines):
        m = SRT_TIME.search(line)
        if m:
            g = [int(x) for x in m.groups()]
            start = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
            end = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
            cur = {"start": start, "end": end, "lines": []}
            cues.append(cur)
            continue
        text = line.strip()
        if cur is None or not text:
            continue
        if text.isdigit() and any(SRT_TIME.search(nxt) for nxt in lines[i + 1:i + 2]):
            continue  # 序號行（下一行就是時間碼）
        cur["lines"].append(text)
    out = []
    for c in cues:
        text = " ".join(c["lines"]).strip()
        if text:
            out.append({"start": round(c["start"], 3), "end": round(c["end"], 3), "text": text})
    return out


def find_sibling(base: Path, stem: str, exts) -> Path | None:
    """同名優先，再退同前綴。==排除 .raw.srt==：那是 correct_srt.py 留下的未校正原始檔，
    字面排序會讓 `.raw.srt` 排在 `.srt` 前面，不排除就會拿到錯字版。"""
    def ok(p: Path) -> bool:
        return p.exists() and ".raw." not in p.name.lower()

    for ext in exts:
        if ok(base / f"{stem}{ext}"):
            return base / f"{stem}{ext}"
        for cand in sorted(base.glob(f"{stem}*{ext}")):
            if ok(cand):
                return cand
    hits = [p for p in sorted(base.iterdir()) if p.suffix.lower() in exts and ok(p)]
    return hits[0] if len(hits) == 1 else None


def build_blocks(data: dict, cues: list[dict]) -> tuple[list[dict], list[dict]]:
    """摘要 bullets（時間插補）+ 逐字稿 cue（真實時間），都掛到所屬 segment。"""
    segs, blocks = [], []
    for seg in data.get("segments", []):
        sid = f"s{seg.get('index')}"
        s0 = float(seg.get("start_sec") or 0)
        s1 = float(seg.get("end_sec") or s0)
        segs.append({
            "id": sid,
            "index": seg.get("index"),
            "title": seg.get("title") or "",
            "start": s0,
            "end": s1,
            "summary": seg.get("summary_zh") or "",
            "frames": seg.get("frames") or ([seg["frame"]] if seg.get("frame") else []),
        })
        # 每張投影片的 OCR 各自成一個可點的 block：檔名末四碼就是 MMSS，
        # 所以點 OCR 文字能直接跳到那張投影片出現的時間點。
        for e in seg.get("frame_ocr") or []:
            text = (e.get("text") or "").strip()
            if not text:
                continue
            t = frame_seconds(e.get("frame", ""), s0)
            blocks.append({"id": f"{sid}f{len(blocks)}", "seg": sid, "kind": "slide",
                           "start": float(t), "end": float(t) + 1,
                           "text": text, "est": False,
                           "frame": str(e.get("frame", ""))})
        bullets = [b for b in (seg.get("bullets_zh") or []) if str(b).strip()]
        span = max(s1 - s0, 0.001)
        # bullets 沒有自己的時間碼 -> 在段落內平均插補，並標記 estimated
        for j, b in enumerate(bullets):
            bs = s0 + span * j / max(len(bullets), 1)
            be = s0 + span * (j + 1) / max(len(bullets), 1)
            blocks.append({"id": f"{sid}b{j}", "seg": sid, "kind": "summary",
                           "start": round(bs, 2), "end": round(be, 2),
                           "text": str(b), "est": True})
    for i, c in enumerate(cues):
        seg = next((s for s in segs if s["start"] <= c["start"] < s["end"]), None)
        if seg is None:
            seg = min(segs, key=lambda s: abs(s["start"] - c["start"])) if segs else None
        blocks.append({"id": f"t{i}", "seg": seg["id"] if seg else "", "kind": "transcript",
                       "start": c["start"], "end": c["end"], "text": c["text"], "est": False})
    return segs, blocks


CSS = """
:root{--bg:#0f1115;--panel:#171a21;--line:#272c37;--fg:#e6e9ef;--dim:#9aa3b2;--accent:#4da3ff;--hit:#f5c451}
*{box-sizing:border-box}
body{margin:0;font:16px/1.65 "Noto Sans TC","Microsoft JhengHei",system-ui,sans-serif;background:var(--bg);color:var(--fg);height:100vh;display:flex;flex-direction:column;overflow:hidden}
header{flex:0 0 auto;display:flex;gap:.5rem;align-items:center;flex-wrap:wrap;padding:.5rem .8rem;background:var(--panel);border-bottom:1px solid var(--line);z-index:40}
header h1{font-size:1rem;margin:0 .6rem 0 0;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:34vw}
button{background:#222833;color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:.25rem .6rem;cursor:pointer;font-size:.85rem}
button:hover{border-color:var(--accent)}
button.active{background:var(--accent);color:#08101c;border-color:var(--accent);font-weight:600}
.spacer{flex:1}
.search{position:relative}
.search input{background:#0d1016;border:1px solid var(--line);color:var(--fg);border-radius:6px;padding:.3rem .6rem;width:15rem;font-size:.85rem}
#results{position:absolute;top:110%;right:0;width:34rem;max-height:60vh;overflow:auto;background:var(--panel);border:1px solid var(--line);border-radius:8px;display:none;z-index:50}
#results.open{display:block}
.sr{display:grid;grid-template-columns:5.5rem 1fr 3.5rem;gap:.4rem;width:100%;text-align:left;background:none;border:0;border-bottom:1px solid var(--line);padding:.4rem .6rem;border-radius:0}
.sr:hover{background:#1e2530}
.sr .k{color:var(--dim);font-size:.72rem}
.sr .t{font-size:.82rem}
.sr .ts{color:var(--accent);font-size:.75rem;text-align:right}
.count{padding:.3rem .6rem;color:var(--dim);font-size:.75rem}
html{height:100%;overflow:hidden}
main{flex:1 1 auto;min-height:0;overflow:hidden;display:grid;grid-template-columns:var(--vcol,44%) 6px 1fr}
#vpane{padding:.6rem;min-height:0;overflow:hidden;display:flex;flex-direction:column}
#vhead{flex:0 0 auto}
video{width:100%;background:#000;border-radius:8px}
#now{font-size:.8rem;color:var(--dim);margin-top:.4rem;min-height:1.4em}
#segnav{flex:1 1 auto;min-height:0;overflow:auto;margin-top:.7rem;display:flex;flex-direction:column;gap:.3rem}
.segcard{text-align:left;padding:.4rem .6rem;font-size:.85rem;line-height:1.4}
.segcard.on{border-color:var(--accent);background:#1b2635}
.segcard b{color:var(--accent);margin-right:.4rem;font-weight:600}
#vsplit,#hsplit{background:var(--line);cursor:col-resize}
#hsplit{cursor:row-resize;height:6px}
#notes{display:grid;grid-template-rows:var(--srow,45%) 6px 1fr;min-width:0;min-height:0;overflow:hidden}
.pane{overflow:auto;min-height:0;padding:.6rem .9rem}
.pane h2{font-size:.8rem;color:var(--dim);margin:.2rem 0 .6rem;font-weight:600;letter-spacing:.05em}
body.only-sum #hsplit,body.only-sum #tpane{display:none}
body.only-sum #notes{grid-template-rows:1fr}
body.only-tr #hsplit,body.only-tr #spane{display:none}
body.only-tr #notes{grid-template-rows:1fr}
.seg{margin-bottom:1.1rem}
.seg>h3{font-size:.95rem;margin:.2rem 0 .3rem}
.seg>h3 .no{color:var(--accent)}
.sum{color:var(--dim);font-size:.85rem;margin:0 0 .4rem}
.blk{display:block;width:100%;text-align:left;background:none;border:0;border-left:3px solid transparent;border-radius:0;padding:.18rem .5rem;color:var(--fg);font-size:.9rem;line-height:1.6}
.blk:hover{background:#1c222c;border-left-color:var(--dim)}
.blk.on{background:#233246;border-left-color:var(--hit)}
.blk .ts{color:var(--accent);font-size:.75rem;margin-right:.45rem;font-variant-numeric:tabular-nums}
.blk.est .ts::after{content:"~";color:var(--dim)}
#tpane .blk{font-size:.86rem;padding:.1rem .5rem}
.thumbs{display:flex;gap:.3rem;flex-wrap:wrap;margin:.3rem 0 .5rem}
.ocr{margin:.3rem 0 .2rem}
.ocr>summary{cursor:pointer;color:var(--dim);font-size:.78rem;padding:.15rem .5rem}
.blk.slide{white-space:pre-wrap;font-size:.8rem;color:var(--dim);border-left-color:#3a4557}
.blk.slide:hover{color:var(--fg)}
.thumbs img{height:72px;border-radius:4px;border:1px solid var(--line);cursor:zoom-in}
.note{flex:0 0 auto;font-size:.72rem;color:var(--dim);padding:.25rem .9rem;background:var(--panel);border-top:1px solid var(--line);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
mark{background:var(--hit);color:#111}
body.float #vpane{position:fixed;right:1rem;bottom:1rem;width:var(--fw,26rem);z-index:60;background:var(--panel);border:1px solid var(--line);border-radius:10px;box-shadow:0 8px 30px #0009;resize:both;overflow:auto;max-height:80vh}
body.float #segnav{display:none}
body.float main{grid-template-columns:0 0 1fr}
@media(max-width:900px){main{grid-template-columns:1fr;grid-template-rows:auto 0 1fr}#vsplit{display:none}}
"""

JS = """
const S=DATA.segments, B=DATA.blocks.slice().sort((a,b)=>a.start-b.start);
let auto=true, suspend=0, progScroll=false, activeSeg=S[0]?S[0].id:'';
const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];
const fmt=t=>{t=Math.max(0,Math.floor(t||0));const h=Math.floor(t/3600),m=Math.floor(t%3600/60),s=t%60;
  return (h?h+':'+String(m).padStart(2,'0'):String(m))+':'+String(s).padStart(2,'0');};
const V=$('#player');

function seek(t,play){
  // preload="metadata" 尚未載完時設 currentTime 會被忽略，得等 loadedmetadata 再設
  const go=()=>{ try{V.currentTime=t;}catch(e){} if(play!==false) V.play().catch(()=>{}); };
  if(V.readyState===0){ V.addEventListener('loadedmetadata',go,{once:true}); V.load(); }
  else go();
  sync(t,true);
}

/* 播放 -> 兩個圖層同時高亮並捲到視窗 42% 高度處 */
function sync(t,force){
  const hits=B.filter(b=>b.start-0.15<=t && t<b.end+0.15);
  if(!hits.length) return;
  $$('.blk.on').forEach(e=>e.classList.remove('on'));
  const seg=(hits.find(b=>b.kind==='summary')||hits[0]).seg;
  if(seg!==activeSeg){ activeSeg=seg;
    $$('.segcard').forEach(e=>e.classList.toggle('on',e.dataset.seg===seg));
    // 段落清單自己會捲，換段時要把新卡片帶進視野，否則播到後段就看不到自己在哪
    const c=$('.segcard.on'); if(c&&(force||follow())) scrollInto(c); }
  const lead=hits.find(b=>b.kind==='summary')||hits[0];
  $('#now').textContent='▶ '+fmt(lead.start)+' — '+lead.text.slice(0,60);
  for(const h of hits){
    const el=document.getElementById('b-'+h.id); if(!el) continue;
    el.classList.add('on');
    if((force||follow()) ) scrollInto(el);
  }
}
function follow(){ return auto && Date.now()>suspend && !V.paused; }
function scrollInto(el){
  const pane=el.closest('.pane, #segnav'); if(!pane) return;
  const target=pane.scrollTop+(el.getBoundingClientRect().top-pane.getBoundingClientRect().top)-pane.clientHeight*0.42;
  progScroll=true; pane.scrollTo({top:Math.max(0,target),behavior:'auto'});
  setTimeout(()=>progScroll=false,80);
}
/* 手動捲動時暫停自動跟隨 5 秒——否則使用者往回看一眼就被拉回去 */
$$('.pane, #segnav').forEach(p=>p.addEventListener('wheel',()=>{ if(!progScroll&&auto&&!V.paused){ suspend=Date.now()+5000; paint(); } },{passive:true}));
function paint(){ const b=$('#autoscroll');
  b.textContent='自動捲動：'+(!auto?'關':(Date.now()<suspend?'暫停':'開'));
  b.classList.toggle('active',auto&&Date.now()>=suspend); }
setInterval(paint,1000);

V.addEventListener('timeupdate',()=>{ if(!V.paused) sync(V.currentTime,false); });
document.addEventListener('click',e=>{
  const blk=e.target.closest('.blk'); if(blk){ seek(Number(blk.dataset.t)); return; }
  const card=e.target.closest('.segcard'); if(card){ seek(Number(card.dataset.t)); return; }
  const m=e.target.closest('[data-mode]'); if(m){ setMode(m.dataset.mode); return; }
  const img=e.target.closest('.thumbs img'); if(img){ window.open(img.src,'_blank'); return; }
  if(!e.target.closest('.search')) $('#results').classList.remove('open');
});
function setMode(m){ document.body.classList.toggle('only-sum',m==='sum');
  document.body.classList.toggle('only-tr',m==='tr');
  $$('[data-mode]').forEach(b=>b.classList.toggle('active',b.dataset.mode===m)); }
$('#autoscroll').addEventListener('click',()=>{auto=!auto;suspend=0;paint();});
$('#float').addEventListener('click',e=>{document.body.classList.toggle('float');e.target.classList.toggle('active');});
let fs=1; const zoom=d=>{fs=Math.min(1.7,Math.max(.85,fs+d));document.documentElement.style.fontSize=(16*fs)+'px';};
$('#zin').addEventListener('click',()=>zoom(.1)); $('#zout').addEventListener('click',()=>zoom(-.1));

/* 全文搜尋：摘要 + 逐字稿一起找，點結果直接跳播 */
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function search(qs){
  const box=$('#results'), terms=(qs||'').trim().toLowerCase().split(/\\s+/).filter(Boolean);
  if(!terms.length){ box.classList.remove('open'); box.innerHTML=''; return; }
  const hits=B.filter(b=>terms.every(t=>b.text.toLowerCase().includes(t))).slice(0,80);
  if(!hits.length){ box.innerHTML='<div class="count">無符合結果</div>'; box.classList.add('open'); return; }
  box.innerHTML='<div class="count">'+hits.length+' 筆</div>'+hits.map(b=>{
    const pos=Math.max(0,b.text.toLowerCase().indexOf(terms[0])-20);
    let t=esc((pos?'…':'')+b.text.slice(pos,pos+110));
    for(const q of terms) t=t.replace(new RegExp('('+q.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\\\$&')+')','ig'),'<mark>$1</mark>');
    return '<button class="sr" data-t="'+b.start+'"><span class="k">'+({summary:'摘要',transcript:'逐字',slide:'投影片'}[b.kind]||b.kind)+'</span>'
      +'<span class="t">'+t+'</span><span class="ts">'+fmt(b.start)+'</span></button>';
  }).join('');
  box.classList.add('open');
  $$('.sr',box).forEach(el=>el.addEventListener('click',()=>{ box.classList.remove('open'); seek(Number(el.dataset.t)); }));
}
let tmr; $('#q').addEventListener('input',e=>{clearTimeout(tmr);tmr=setTimeout(()=>search(e.target.value),120);});
document.addEventListener('keydown',e=>{ if(e.key==='/'&&!/^(INPUT|TEXTAREA)$/.test(e.target.tagName)){e.preventDefault();$('#q').focus();}
  if(e.key==='Escape'){$('#results').classList.remove('open');} });
/* 分隔線拖曳 */
function drag(handle,apply){ handle.addEventListener('pointerdown',e=>{e.preventDefault();handle.setPointerCapture(e.pointerId);
  const mv=m=>apply(m); const up=()=>{handle.removeEventListener('pointermove',mv);handle.removeEventListener('pointerup',up);};
  handle.addEventListener('pointermove',mv);handle.addEventListener('pointerup',up);}); }
drag($('#vsplit'),m=>document.body.style.setProperty('--vcol',Math.min(Math.max(m.clientX,280),window.innerWidth-380)+'px'));
drag($('#hsplit'),m=>{const r=$('#notes').getBoundingClientRect();
  document.body.style.setProperty('--srow',Math.min(Math.max(m.clientY-r.top,100),r.height-120)+'px');});
setMode('split'); paint();
/* ?t=<秒> 深連結：課程首頁的搜尋結果可直接指到某一場的某個時間點 */
(function(){ const t=Number(new URLSearchParams(location.search).get('t'));
  if(!isNaN(t)&&t>0){ V.addEventListener('loadedmetadata',()=>{try{V.currentTime=t;}catch(e){} sync(t,true);},{once:true});
    if(V.readyState) { try{V.currentTime=t;}catch(e){} sync(t,true); } } })();
"""


def render(data: dict, segs: list[dict], blocks: list[dict], title: str,
           video_rel: str, media_dir: str) -> str:
    def blk_html(b: dict) -> str:
        cls = "blk est" if b["est"] else "blk"
        return (f'<button class="{cls}" id="b-{b["id"]}" data-t="{b["start"]}">'
                f'<span class="ts">{int(b["start"])//60:02d}:{int(b["start"])%60:02d}</span>'
                f'{html.escape(b["text"])}</button>')

    by_seg: dict[str, list[dict]] = {}
    for b in blocks:
        by_seg.setdefault(b["seg"], []).append(b)

    sum_html, tr_html, nav_html = [], [], []
    for s in segs:
        mine = by_seg.get(s["id"], [])
        nav_html.append(
            f'<button class="segcard" data-seg="{s["id"]}" data-t="{s["start"]}">'
            f'<b>{s["index"]:02d}</b>{html.escape(s["title"])}'
            f'<div style="color:var(--dim);font-size:.75rem">'
            f'{int(s["start"])//60:02d}:{int(s["start"])%60:02d}–'
            f'{int(s["end"])//60:02d}:{int(s["end"])%60:02d}</div></button>')
        thumbs = "".join(
            f'<img src="{html.escape(media_dir + f)}" loading="lazy" alt="">'
            for f in s["frames"])
        slides = [b for b in mine if b["kind"] == "slide"]
        ocr_html = ""
        if slides:
            rows = "".join(
                f'<button class="blk slide" id="b-{b["id"]}" data-t="{b["start"]}">'
                f'<span class="ts">{int(b["start"])//60:02d}:{int(b["start"])%60:02d}</span>'
                f'{html.escape(b["text"])}</button>' for b in slides)
            ocr_html = ('<details class="ocr"><summary>投影片文字 '
                        f'{len(slides)} 張（OCR，有誤差，僅供定位／搜尋）</summary>{rows}</details>')
        sum_html.append(
            f'<section class="seg"><h3><span class="no">{s["index"]:02d}</span> '
            f'{html.escape(s["title"])}</h3>'
            + (f'<div class="thumbs">{thumbs}</div>' if thumbs else "")
            + f'<p class="sum">{html.escape(s["summary"])}</p>'
            + "".join(blk_html(b) for b in mine if b["kind"] == "summary")
            + ocr_html
            + "</section>")
        cues = [b for b in mine if b["kind"] == "transcript"]
        if cues:
            tr_html.append(
                f'<section class="seg"><h3><span class="no">{s["index"]:02d}</span> '
                f'{html.escape(s["title"])}</h3>'
                + "".join(blk_html(b) for b in cues) + "</section>")

    takeaways = "".join(f"<li>{html.escape(str(t))}</li>"
                        for t in data.get("takeaways_zh") or [])
    payload = json.dumps({"segments": segs, "blocks": blocks}, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><style>{CSS}</style></head><body>
<header>
  <h1>{html.escape(title)}</h1>
  <button data-mode="sum">整理稿</button>
  <button data-mode="split">兩欄</button>
  <button data-mode="tr">逐字稿</button>
  <button id="autoscroll">自動捲動：開</button>
  <button id="float">浮動播放器</button>
  <span class="spacer"></span>
  <button id="zout">A−</button><button id="zin">A＋</button>
  <span class="search"><input id="q" placeholder="搜尋摘要與逐字稿（按 / 聚焦）"><div id="results"></div></span>
</header>
<main>
  <div id="vpane">
    <div id="vhead">
      <video id="player" controls preload="metadata" src="{html.escape(video_rel)}"></video>
      <div id="now">尚未播放</div>
    </div>
    <div id="segnav">{"".join(nav_html)}</div>
  </div>
  <div id="vsplit"></div>
  <div id="notes">
    <div class="pane" id="spane"><h2>整理稿（摘要層）</h2>{"".join(sum_html)}
      <section class="seg"><h3>全片重點</h3><ul>{takeaways}</ul></section></div>
    <div id="hsplit"></div>
    <div class="pane" id="tpane"><h2>逐字稿（時間層）</h2>{"".join(tr_html)}</div>
  </div>
</main>
<div class="note">點任一行跳播，播放時兩層同時高亮跟隨　·　摘要層時間標「~」＝段落內插補的推估值，逐字稿與投影片為真實時間碼</div>
<script>const DATA={payload};</script><script>{JS}</script></body></html>
"""


def main():
    ap = argparse.ArgumentParser(description="Task 6 JSON + SRT + 影片 -> 單檔雙向同步 viewer")
    ap.add_argument("json_path", help="Task 6 分段 JSON")
    ap.add_argument("--srt", help="字幕檔（預設同層同名）")
    ap.add_argument("--video", help="影片檔（預設同層同名）")
    ap.add_argument("-o", "--out", help="輸出 HTML（預設 <stem>.viewer.html）")
    ap.add_argument("--title", help="頁面標題（預設用檔名）")
    args = ap.parse_args()

    jp = Path(args.json_path)
    if not jp.exists():
        print(f"[錯誤] 找不到 {jp}", file=sys.stderr)
        sys.exit(2)
    data = json.loads(read_text(jp))
    base, stem = jp.parent, jp.stem

    video = Path(args.video) if args.video else find_sibling(base, stem, VIDEO_EXT)
    srt = Path(args.srt) if args.srt else find_sibling(base, stem, (".srt", ".vtt"))
    if not video:
        print("[錯誤] 找不到影片檔，請用 --video 指定", file=sys.stderr)
        sys.exit(2)
    cues = parse_srt(srt) if srt and srt.exists() else []
    if not cues:
        print("  (沒有字幕 -> 只產生摘要層，逐字稿層會是空的)", file=sys.stderr)

    segs, blocks = build_blocks(data, cues)
    if not segs:
        print("[錯誤] JSON 沒有 segments", file=sys.stderr)
        sys.exit(2)

    out = Path(args.out) if args.out else base / f"{stem}.viewer.html"
    title = args.title or stem
    page = render(data, segs, blocks, title,
                  video_rel=video.name, media_dir="")
    out.write_text(page, encoding="utf-8", newline="\n")
    n_sum = sum(1 for b in blocks if b["kind"] == "summary")
    n_tr = len(blocks) - n_sum
    print(f"段落 {len(segs)}｜摘要 block {n_sum}（時間為推估）｜逐字 cue {n_tr}（真實時間碼）")
    print(f"影片 {video.name}｜字幕 {srt.name if srt else '無'}")
    print(f"輸出 -> {out}  ({out.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
