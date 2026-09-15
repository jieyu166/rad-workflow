# 路徑約定

`<skill>`／`<lecture-skill>` 是目前載入的 lecture-to-notes 根目錄；`<whisper-skill>` 從技能目錄取得，先確認 `scripts/transcribe.py` 存在。命令中的相對腳本路徑均以相應 skill 根目錄為基準。

## Step 2 — 分段導航 JSON

把逐字稿切成 8–15 段（長片可多），每段給時間碼、標題、摘要、重點。這步是 LLM 做的，
沒有腳本。

**先找校正依據**，優先序如 HARD RULE 3：
1. 官方講義 `.html` → `defuddle parse "<檔>" --md`；`.md` 直接讀；`.pdf` → `pdftotext`
2. 投影片截圖 → 用 Read 工具逐張看
3. 都沒有 → 靠領域知識，不確定的標「（可能為 XXX）」

<details>
<summary>分段 prompt（可直接用，或交給 API）</summary>

```
你是一位「字幕整理 +（可選）投影片校正」助手。
我會提供：(1) 字幕（VTT 或 SRT，可能有錯字但含時間碼）(2) 投影片/講義內容（可選）

【任務】
1) 自動分段（8–15 段為主，除非影片很長）
   - 以主題轉換/投影片標題為主要分段依據
   - 每段給 start_time/end_time (mm:ss 或 hh:mm:ss)，同時給 start_sec/end_sec
2) 每段輸出：title（像投影片標題，用投影片上的正確術語）、summary_zh（繁中 2–4 句）、
   bullets_zh（繁中 2–6 點，保留英文專有名詞）
3) 全片輸出：overall_summary_zh（100–500 字，長講座寫滿沒關係）、takeaways_zh（6–12 點）

【校正規則】
- 專有名詞若字幕明顯錯字，必須用投影片/講義校正（血管名稱、器材、術式、分類系統）
- 投影片上清楚可見的正確拼寫優先於字幕文字
- 不得腦補字幕沒提到的內容；投影片有但字幕沒講到的，不要硬塞
- 不確定拼字就保留原字幕並加註「（可能為XXX）」
- 中文錯字也要校正（如「方測科」→「放射科」、「送神」→「送審」）

【只輸出 JSON，不要輸出其他文字】
```
</details>

### JSON schema

```json
{
  "overall_summary_zh": "100-500字繁中整體摘要",
  "takeaways_zh": ["結論/可應用原則 1", "...最多12點"],
  "segments": [{
    "index": 1, "start_time": "mm:ss", "end_time": "mm:ss",
    "start_sec": 0, "end_sec": 62,
    "title": "段落標題", "summary_zh": "繁中2-4句", "bullets_zh": ["重點1", "重點2"],
    "frame": "frames/<stem>-MMSS.png",
    "frames": ["frames/<stem>-MMSS.png"],
    "frame_ocr": [{"frame": "frames/<stem>-MMSS.png", "text": "投影片上的文字…"}]
  }],
  "ocr_meta": {"engine": "rapidocr-onnxruntime", "frames_total": 0}
}
```

`frame`/`frames` 由 Step 3 的 `slide_frames.py` 填、`frame_ocr`/`ocr_meta` 由
`ocr_frames.py` 填。存成 `<stem>.json`，UTF-8 **不得有 BOM**（web player 會解析失敗）。

