# 2026 下半年舊戶信用卡回饋資料庫

## 研究範圍

本資料庫只研究既有持卡人或既有帳戶客戶，期間固定為 **2026-08-01 至 2026-12-31**。新戶、新卡首刷、新申辦、首次綁定與新開戶優惠均排除；不把抽獎、贈品或不保證取得的回饋換算為固定回饋率。

## 方法與狀態

來源優先順序為官方活動辦法／權益 PDF、官方產品頁／公告、官方新聞稿。每個列入比較的方案至少需要一個可重現的官方來源。`complete` 表示研究視窗已有完整官方覆蓋；`partial` 表示只覆蓋部分期間，其餘標示待公告；`unavailable` 表示目前找不到可用官方來源或消費回饋功能。

回饋同時記錄總回饋率與「基本回饋＋活動加碼」組成，點數與現金分開。可計算時，加碼可刷金額為 `加碼回饋上限 ÷ 加碼回饋率`，並標註為推導值；名額、登錄與額滿狀態不與金額上限混用。海外回饋另列國外交易服務費。

## 文件清單

研究文件建立後以 `[ ]` 表示尚未完成查證，以 `[x]` 表示已完成；本清單不預先宣稱任何回饋已獲證實。

### 信用卡與金融卡

- [ ] 第一銀行 iLEO 卡 — `cards/first-ileo.md`
- [ ] 第一銀行 一卡通綠活卡 — `cards/first-green.md`
- [ ] 台新 Richart 卡（原 @GoGo 舊戶）— `cards/taishin-richart-gogo.md`
- [ ] 永豐 DAWHO 現金回饋信用卡 — `cards/sinopac-dawho.md`
- [ ] 永豐幣倍卡 — `cards/sinopac-coin.md`
- [ ] 永豐 DAWAY 卡 — `cards/sinopac-daway.md`
- [ ] 國泰世華 CUBE 卡 — `cards/cathay-cube.md`
- [ ] 中國信託 LINE Pay 信用卡 — `cards/ctbc-line-pay.md`
- [ ] 樂天國際銀行金融卡 — `cards/rakuten-bank-card.md`
- [ ] 王道銀行一般簽帳金融卡（排除 O! Range）— `cards/obank-debit.md`
- [ ] Visa LINE Bank 快點卡 — `cards/line-bank-debit.md`
- [ ] 玉山 Pi 拍錢包信用卡 — `cards/esun-pi.md`
- [ ] 玉山 Unicard — `cards/esun-unicard.md`
- [ ] 玉山 U Bear 信用卡 — `cards/esun-ubear.md`
- [ ] 台北富邦 Costco 聯名卡 — `cards/fubon-costco.md`

### 常用行動支付

- [ ] LINE Pay — `payments/line-pay.md`
- [ ] iPASS MONEY — `payments/ipass-money.md`
- [ ] 全支付 — `payments/px-pay.md`

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

`comparison.md` 將在 15 項產品與 3 項支付文件完成後建立，並回溯至各文件的官方證據。

## 限制

研究不登入網銀、銀行 App 或個人帳戶，不讀取消費資料，也不保證涵蓋使用者清單以外的市場產品。動態頁、圖片或 PDF 需保存頁面標題、活動期間與定位資訊；來源失效時保留無法重開狀態。
