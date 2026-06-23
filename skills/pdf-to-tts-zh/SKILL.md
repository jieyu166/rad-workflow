---
name: pdf-to-tts-zh
description: Turn a PDF (slides, case reports, handouts) into a single narrated Traditional Chinese audiobook MP3. Rasterize each page to an image, read it, write a natural spoken 繁體中文逐字稿 per page, synthesize each with edge-tts, then concatenate into one mp3. Use when asked to make a Chinese voiceover/audio/podcast/audiobook from a PDF or slide deck, "把 PDF 轉成語音/逐字稿/有聲書", or "用 edge-tts 唸投影片".
---

# pdf-to-tts-zh

Convert any PDF into one continuous Traditional Chinese narration MP3 — page by page.

## When to use

- "把這份投影片/PDF 轉成繁中語音 / 有聲書 / podcast"
- "幫每一頁寫逐字稿再用 edge-tts 唸出來，合併成一個 mp3"
- Turning slide decks, case reports, or handouts into an audio walkthrough.

## Requirements

Check these are installed before starting; install whatever is missing.

| Tool | Purpose | Install |
|------|---------|---------|
| `pdftoppm` | Rasterize PDF pages to PNG | `brew install poppler` |
| `edge-tts` | Microsoft Edge neural TTS (free, no key) | `pip install edge-tts` / `uv tool install edge-tts` |
| `ffmpeg` | Concatenate per-page mp3s | `brew install ffmpeg` |

## Workflow

Work inside a project directory holding the source PDF (referred to as `INPUT.pdf`).

### 1. Rasterize every page

```bash
mkdir -p pages audio scripts
pdftoppm -png -r 150 INPUT.pdf pages/page
```

Produces `pages/page-01.png … page-NN.png` (zero-padded). 150 dpi is a good
legibility/size balance; bump to 200 for dense small text.

### 2. Read each page and write a 繁中逐字稿

For **every** PNG, use the Read tool to view the image, then write a natural
spoken-Chinese narration to `scripts/page-NN.txt` (one file per page, plain text).

Writing rules:
- **Speak, don't list.** Narrate the page like a presenter, not by reading bullets verbatim.
- **Keep technical tokens in English** — drug names, abbreviations, gene/protein names
  (e.g. `rituximab`, `MALT`, `AIHA`) stay in English so the voice pronounces them correctly.
- **Verbalize numbers/dates** in Chinese reading order (e.g. `2026/05/25` → 「2026 年 5 月 25 日」).
- **No meta narration** — never write 「這一頁顯示」「投影片上」; just deliver the content.
- Section/title pages can be one short sentence; data-heavy pages get a fuller paragraph.
- Plain text only — no markdown, no bullet glyphs.

**Scale tip:** for long decks, dispatch parallel subagents, each owning a page
range, reading its PNGs and writing the `scripts/page-NN.txt` files. Keep the
voice/style instructions identical across agents for a consistent narrator.

### 3. Synthesize each page with edge-tts

```bash
for f in scripts/page-*.txt; do
  n=$(basename "$f" .txt)
  edge-tts --voice zh-TW-HsiaoChenNeural --file "$f" --write-media "audio/$n.mp3"
done
```

Voice options (all key-free):
- `zh-TW-HsiaoChenNeural` — Taiwan female (default, warm)
- `zh-TW-YunJheNeural` — Taiwan male
- `zh-CN-XiaoxiaoNeural` — Mainland female
- Tune pace with `--rate=+10%` / `--rate=-10%`.

List all voices: `edge-tts --list-voices | grep zh-`

### 4. Concatenate into one mp3

```bash
: > audio/list.txt
for n in $(seq -w 1 $(ls scripts/page-*.txt | wc -l)); do
  echo "file '$PWD/audio/page-$n.mp3'" >> audio/list.txt
done
ffmpeg -y -f concat -safe 0 -i audio/list.txt -c:a libmp3lame -b:a 128k OUTPUT.mp3
```

Re-encoding (`libmp3lame`) yields clean joins; `-c copy` is faster but can click
at boundaries if codec params differ between segments.

### 5. Verify

```bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 OUTPUT.mp3
```

Confirm the file count (`ls audio/*.mp3 | wc -l`) equals the page count and the
duration is sane before delivering `OUTPUT.mp3`.

## Notes

- Intermediate artifacts (`pages/`, `scripts/`, `audio/`) are kept — re-run step 3
  after editing any `scripts/page-NN.txt`, or step 4 only to re-stitch, without
  redoing the whole pipeline.
- The helper script `scripts/build.sh` runs steps 1, 3, 4 in one shot once the
  per-page `scripts/page-NN.txt` files exist (step 2 still needs a model to read images).
