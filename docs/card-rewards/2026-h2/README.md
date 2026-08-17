# 2026 下半年舊戶信用卡回饋資料庫

## 研究範圍

本資料庫只研究既有持卡人或既有帳戶客戶，期間固定為 **2026-08-01 至 2026-12-31**。新戶、新卡首刷、新申辦、首次綁定與新開戶優惠均排除；不把抽獎、贈品或不保證取得的回饋換算為固定回饋率。

## 方法與狀態

來源優先順序為官方活動辦法／權益 PDF、官方產品頁／公告、官方新聞稿。每個列入比較的方案至少需要一個可重現的官方來源。`complete` 表示研究視窗已有完整官方覆蓋；`partial` 表示只覆蓋部分期間，其餘標示待公告；`unavailable` 表示目前找不到可用官方來源或消費回饋功能。

回饋同時記錄總回饋率與「基本回饋＋活動加碼」組成，點數與現金分開。可計算時，加碼可刷金額為 `加碼回饋上限 ÷ 加碼回饋率`，並標註為推導值；名額、登錄與額滿狀態不與金額上限混用。海外回饋另列國外交易服務費。

## 文件清單

最後一次逐 URL 官方來源稽核：**2026-08-18**。`[x]` 只用於目標期間完整覆蓋、文件通過驗證且定量主張已由可重開官方頁 read-back 的 `complete` 文件；`[ ]` 後附 `partial` 表示文件已建立，但仍有明列的期間／來源／逐通路缺口，不得把已知權益外推到未重建情境。

狀態合計（15 項產品＋3 項支付）：

- `complete`：9
- `partial`：9
- `unavailable`：0

### 信用卡與金融卡

- [x] 第一銀行 iLEO 卡 — `complete` — `cards/first-ileo.md`
- [x] 第一銀行 一卡通綠活卡 — `complete` — `cards/first-green.md`
- [x] 台新 Richart 卡（原 @GoGo 舊戶）— `complete` — `cards/taishin-richart-gogo.md`
- [x] 永豐 DAWHO 現金回饋信用卡 — `complete` — `cards/sinopac-dawho.md`
- [x] 永豐幣倍卡 — `complete` — `cards/sinopac-coin.md`
- [x] 永豐 DAWAY 卡 — `complete` — `cards/sinopac-daway.md`
- [ ] 國泰世華 CUBE 卡 — `partial`：固定回饋已完整重建；玩數位、樂饗購、趣旅行、集精選、全支付、慶生月於全目標期的全部商戶與逐通路細則尚未重建 — `cards/cathay-cube.md`
- [ ] 中國信託 LINE Pay 信用卡 — `partial`：歐盟海外實體加碼條款衝突 — `cards/ctbc-line-pay.md`
- [ ] 樂天國際銀行金融卡 — `partial`：商店簽帳功能未獲完整條款證實 — `cards/rakuten-bank-card.md`
- [x] 王道銀行一般簽帳金融卡（排除 O! Range）— `complete` — `cards/obank-debit.md`
- [ ] Visa LINE Bank 快點卡 — `partial`：基本與日本／泰國回饋已覆蓋至 12-31，但 YOLO／TGIF 等特殊加碼只公告至 09-27 — `cards/line-bank-debit.md`
- [ ] 玉山 Pi 拍錢包信用卡 — `partial`：核心權益只公告至 2026-08-31 — `cards/esun-pi.md`
- [x] 玉山 Unicard — `complete` — `cards/esun-unicard.md`
- [ ] 玉山 U Bear 信用卡 — `partial`：核心權益只公告至 2026-08-31 — `cards/esun-ubear.md`
- [x] 台北富邦 Costco 聯名卡 — `complete` — `cards/fubon-costco.md`

### 常用行動支付

- [ ] LINE Pay — `partial`：多項產品缺特定綁卡／平台疊加正面證據 — `payments/line-pay.md`
- [ ] iPASS MONEY — `partial`：多項產品缺特定綁卡／平台疊加正面證據 — `payments/ipass-money.md`
- [ ] 全支付 — `partial`：多項產品缺特定綁卡／平台疊加正面證據 — `payments/px-pay.md`

## 固定章節

每份產品或支付文件必須包含：

1. `## 結論摘要`
2. `## 一般回饋`
3. `## 特殊回饋`
4. `## 行動支付相容性`
5. `## 排除交易`
6. `## 來源證據`
7. `## 不確定事項`

每份文件使用相同 frontmatter：`product`、`issuer`、`product_type`、`customer_scope`、`target_from`、`target_to`、`verified_at`、`coverage_status`。官方來源找不到時，必須明確寫出查詢範圍與 `unavailable`，不得猜填數字。

官方 URL 必須放在 `## 來源證據` 章節；`unavailable` 文件若沒有 URL，必須在該章節以 `查詢範圍：...` 記錄查證範圍，並在 `## 不確定事項` 提供具體說明，單獨寫「查無」不符合契約。

`partial` 文件必須在正文使用 `未覆蓋期間：YYYY-MM-DD 至 YYYY-MM-DD` 明列至少一段缺口；`unavailable` 文件的 `## 結論摘要` 不得提出百分比推薦。

跨產品結果見 [`comparison.md`](comparison.md)。每個產品以 stable `product-id` 恰好出現一次，並以腳註連回證據文件；比較表不會把 `partial`／`unavailable` 的未覆蓋期間當作確定推薦。

## 限制

研究不登入網銀、銀行 App 或個人帳戶，不讀取消費資料，也不保證涵蓋使用者清單以外的市場產品。動態頁、圖片或 PDF 需保存頁面標題、活動期間與定位資訊；來源失效時保留無法重開狀態。
