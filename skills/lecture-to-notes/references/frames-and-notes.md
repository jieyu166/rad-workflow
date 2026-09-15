# 路徑約定

`<skill>`／`<lecture-skill>` 是目前載入的 lecture-to-notes 根目錄；`<whisper-skill>` 從技能目錄取得，先確認 `scripts/transcribe.py` 存在。命令中的相對腳本路徑均以相應 skill 根目錄為基準。

## Step 3 — 換頁截圖 + OCR

```bash
python <skill>/scripts/slide_frames.py "<影片>" --json "<stem>.json" --width 1280
python <skill>/scripts/ocr_frames.py "<stem>.json"
```

- `slide_frames.py`：PySceneDetect adaptive（無則退 ffmpeg scene filter）抓「真正換頁」
  那張存到 `frames/<stem>-MMSS.png`，把 `frame`/`frames` 併回 JSON，另產
  `<stem>.frames.json` manifest。完成後再繼續相依步驟，見入口完成條件。
- `ocr_frames.py`：每張 OCR 一次（RapidOCR，CPU，約 0.5 s/張），文字併進 `frame_ocr`，
  快取在 `<stem>.frames_ocr.json`（size+mtime 指紋，重跑只補新圖）。需要
  `pip install rapidocr-onnxruntime`，缺套件直接 exit 3 不默默略過。

**OCR 是這條管線最划算的一步**：實測乳攝講座中 `Architectural Distortion`、`vacuum`
只出現在投影片上、逐字稿完全沒有——沒有這層就永遠搜不到。但它也把「處置」讀成「鬣置」，
所以只當定位線索（HARD RULE 3）。

## Step 4 — 寫 V4 筆記

1. 讀齊素材：**官方講義（最高）→ `frame_ocr` → 需要細看的截圖 → 逐字稿**
2. ==讀圖策略==：有 `frame_ocr` 時**先讀 OCR 決定哪幾張值得開**，不要整批 Read 圖——
   長片 100+ 張時這是最大的一筆浪費。需要開圖的情況：表格、分類標準、影像（CT/MRI/US）、
   OCR 明顯亂掉、以及任何要寫進筆記的數值與術語。
3. 產出 `<stem>.v4.md`：

```markdown
---
(V4 YAML — source 放講者/課程名)
---
Topics :: [[相關主題]] <br>
Parent Link :: [[=索引頁]] <br>

---
# Evergreen Note
「**一句話核心觀念**」

# Summary
- **重點1**
- 易混淆觀念：...

# Note (layer 1-3)
## 小標題
（內容；比較用表格。多講者時標 **(講師A觀點)**）
![[frames/<stem>-MMSS.png]]

### 參考來源
[^1]: 出處

## 題目
Q: / A:

## 閱片
（如適用）
```

規則：繁體中文、專有名詞保留英文；**不可自行編造**，所有內容須來自素材；講者的經驗與洞見
也要記；有投影片來源時每個主要段落至少嵌一張相關截圖；純音檔不要求或捏造截圖；至少做一項學習驗證（費曼輸出／應用情境／行動清單／
知識連結／自我測驗）。

> **草稿豁免**：這是機器轉錄＋合成的產物，直接寫進 inbox，不必先給草稿——使用者在
> Obsidian 裡審閱。

