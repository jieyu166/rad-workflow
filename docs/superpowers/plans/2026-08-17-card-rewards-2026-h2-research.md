# 2026 下半年舊戶信用卡回饋研究 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立 15 個既有信用卡／金融卡產品及 3 個常用行動支付在 2026-08-01 至 2026-12-31 的官方來源 Markdown 證據庫與跨卡比較表。

**Architecture:** Markdown 是研究階段的來源真相，每個產品與支付服務各自保存有效期間、舊戶資格、回饋拆分、條件、上限及官方證據。以 Python 標準函式庫驗證文件集合、frontmatter、必要章節、日期、官方 URL 與比較表覆蓋率；事實正確性另以逐來源人工 read-back 驗證。

**Tech Stack:** Markdown、YAML 子集、Python 3 標準函式庫、`unittest`、官方銀行／支付服務網頁與 PDF、Git。

**Spec:** `docs/superpowers/specs/2026-08-17-card-rewards-2026-h2-design.md`

## Global Constraints

- 研究視窗固定為 2026-08-01 至 2026-12-31。
- 適用資格固定為既有持卡人／既有存款客戶；排除所有新戶、新卡首刷與新申辦限定優惠。
- 第三方網站只能用來發現線索；每個列入比較表的回饋至少有一個直接官方來源。
- 活動只涵蓋部分視窗時保留實際有效區間，其餘期間標示待公告，不延用或推估。
- 同時記錄總回饋率與基本回饋／活動加碼組成；點數與現金分開記錄。
- 推導可刷金額只能使用「加碼回饋上限 ÷ 加碼回饋率」，並標示為推導值。
- 海外回饋與國外交易服務費分開呈現，不把名目回饋直接稱為淨回饋。
- 樂天國際銀行按金融卡及既有客戶帳戶支付研究；王道按一般簽帳金融卡研究並排除 O! Range 權益；LINE Bank 按 Visa 快點卡研究。
- 不登入個人銀行帳戶或 App，不讀取個人消費資料。
- 本計畫只完成 Markdown 研究資料；`tool/card-rewards.html` 另於研究驗收後規劃。
- 在獨立 Git worktree／`codex/` 分支執行，只 stage 本計畫明確列出的路徑，不推送或建立 PR。

---

## File Map

**Validation:**

- Create: `scripts/validate_card_rewards_docs.py` — 解析 frontmatter、檢查必要文件與章節、日期範圍、官方 URL、舊戶範圍及比較表覆蓋率。
- Create: `tests/test_card_rewards_docs.py` — 驗證 parser、錯誤代碼、完整集合及 CLI exit code。

**Research root:**

- Create: `docs/card-rewards/2026-h2/README.md` — 研究範圍、方法、欄位、狀態圖例及更新規則。
- Create: `docs/card-rewards/2026-h2/comparison.md` — 15 個產品的國內、國外、特殊回饋、上限及常用支付比較。
- Create: `docs/card-rewards/2026-h2/cards/*.md` — 15 份產品證據文件。
- Create: `docs/card-rewards/2026-h2/payments/*.md` — LINE Pay、iPASS MONEY、全支付三份證據文件。

**Stable validator interfaces:**

```python
@dataclass(frozen=True)
class Issue:
    code: str
    path: str
    message: str
```

- `parse_frontmatter(text: str) -> tuple[dict[str, str], str]`
- `validate_document(path: Path, root: Path) -> list[Issue]`
- `validate_corpus(root: Path, only: set[str] | None = None) -> list[Issue]`
- `main(argv: list[str] | None = None) -> int`

CLI contract:

```powershell
python scripts\validate_card_rewards_docs.py --root docs\card-rewards\2026-h2
python scripts\validate_card_rewards_docs.py --root docs\card-rewards\2026-h2 --only cards/first-ileo.md,cards/first-green.md
python scripts\validate_card_rewards_docs.py --root docs\card-rewards\2026-h2 --json-report tmp\card-rewards-2026-h2-validation.json
```

Exit `0` means no issues; exit `1` means validation issues; exit `2` means invalid CLI arguments or unreadable root.

---

### Task 1: Isolated Worktree, Corpus Contract, and Structural Validator

**Files:**

- Create: `docs/card-rewards/2026-h2/README.md`
- Create: `scripts/validate_card_rewards_docs.py`
- Create: `tests/test_card_rewards_docs.py`

**Interfaces:**

- Consumes: approved spec at `docs/superpowers/specs/2026-08-17-card-rewards-2026-h2-design.md`.
- Produces: stable validator interfaces and CLI contract documented above; all later tasks rely on its exact product file list, headings, metadata values and error codes.

- [ ] **Step 1: Create an isolated worktree before changing research files**

Use `superpowers:using-git-worktrees`. Create branch `codex/card-rewards-2026-h2` in `.worktrees/card-rewards-2026-h2`, then verify the new worktree is clean and contains commit `c468d6a` or a descendant containing the approved spec.

Run:

```powershell
git -C .worktrees\card-rewards-2026-h2 status --short --branch
git -C .worktrees\card-rewards-2026-h2 log -1 --oneline
```

Expected: branch `codex/card-rewards-2026-h2`, no short-status file entries, approved spec present.

- [ ] **Step 2: Write failing unit tests for frontmatter and missing-file validation**

Create `tests/test_card_rewards_docs.py` with temporary corpus helpers and these core assertions:

```python
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.validate_card_rewards_docs import (
    EXPECTED_CARD_FILES,
    EXPECTED_PAYMENT_FILES,
    parse_frontmatter,
    validate_corpus,
)


ROOT = Path(__file__).parents[1]


class CardRewardsDocsTests(unittest.TestCase):
    def test_parse_frontmatter_returns_metadata_and_body(self) -> None:
        metadata, body = parse_frontmatter(
            "---\nproduct: Test Card\ncustomer_scope: existing\n---\n# Test Card\n"
        )
        self.assertEqual(metadata["product"], "Test Card")
        self.assertEqual(metadata["customer_scope"], "existing")
        self.assertIn("# Test Card", body)

    def test_empty_corpus_reports_every_expected_product(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            issues = validate_corpus(Path(tmp))
        missing = {issue.path for issue in issues if issue.code == "missing_file"}
        self.assertTrue(EXPECTED_CARD_FILES <= missing)
        self.assertTrue(EXPECTED_PAYMENT_FILES <= missing)

    def test_cli_writes_json_and_fails_for_incomplete_corpus(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "corpus"
            report = Path(tmp) / "report.json"
            root.mkdir()
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_card_rewards_docs.py"),
                    "--root",
                    str(root),
                    "--json-report",
                    str(report),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertGreater(json.loads(report.read_text(encoding="utf-8"))["issue_count"], 0)
```

- [ ] **Step 3: Run the tests to verify the validator does not exist**

Run:

```powershell
python -m unittest tests.test_card_rewards_docs -v
```

Expected: FAIL with `ModuleNotFoundError` for `scripts.validate_card_rewards_docs`.

- [ ] **Step 4: Implement the stdlib-only validator**

Define exact expected files:

```python
EXPECTED_CARD_FILES = {
    "cards/first-ileo.md",
    "cards/first-green.md",
    "cards/taishin-richart-gogo.md",
    "cards/sinopac-dawho.md",
    "cards/sinopac-coin.md",
    "cards/sinopac-daway.md",
    "cards/cathay-cube.md",
    "cards/ctbc-line-pay.md",
    "cards/rakuten-bank-card.md",
    "cards/obank-debit.md",
    "cards/line-bank-debit.md",
    "cards/esun-pi.md",
    "cards/esun-unicard.md",
    "cards/esun-ubear.md",
    "cards/fubon-costco.md",
}
EXPECTED_PAYMENT_FILES = {
    "payments/line-pay.md",
    "payments/ipass-money.md",
    "payments/px-pay.md",
}
REQUIRED_METADATA = {
    "product",
    "issuer",
    "product_type",
    "customer_scope",
    "target_from",
    "target_to",
    "verified_at",
    "coverage_status",
}
REQUIRED_HEADINGS = (
    "## 結論摘要",
    "## 一般回饋",
    "## 特殊回饋",
    "## 行動支付相容性",
    "## 排除交易",
    "## 來源證據",
    "## 不確定事項",
)
ALLOWED_PRODUCT_TYPES = {"credit", "debit", "atm", "payment"}
ALLOWED_COVERAGE = {"complete", "partial", "unavailable"}
OFFICIAL_HOST_SUFFIXES = (
    "firstbank.com.tw",
    "taishinbank.com.tw",
    "bank.sinopac.com",
    "cathaybk.com.tw",
    "ctbcbank.com",
    "ctbcbank.com.tw",
    "rakuten-bank.com.tw",
    "o-bank.com",
    "linebank.com.tw",
    "esunbank.com",
    "fubon.com",
    "linepay.com",
    "line.me",
    "i-pass.com.tw",
    "ipassmoney.com.tw",
    "pxpayplus.com",
)
```

Parse only single-line `key: value` YAML scalars required by the contract; do not add PyYAML. Emit stable issue codes: `missing_file`, `frontmatter`, `missing_metadata`, `invalid_enum`, `invalid_date`, `wrong_scope`, `missing_heading`, `missing_official_url`, `comparison_missing_product`, and `unreadable`.

- [ ] **Step 5: Create the research README as the human-facing contract**

Document the target dates, old-customer exclusion, source priority, `complete`／`partial`／`unavailable` meaning, rate composition, cap-derived spend formula, and the seven mandatory headings. Include the 15 products and 3 payments with unchecked status markers so progress is visible without claiming evidence.

- [ ] **Step 6: Run unit tests and validator smoke test**

Run:

```powershell
python -m unittest tests.test_card_rewards_docs -v
python scripts\validate_card_rewards_docs.py --root docs\card-rewards\2026-h2
```

Expected: unit tests PASS; corpus validator exits `1` and reports the 18 not-yet-created evidence files plus missing `comparison.md`.

- [ ] **Step 7: Commit the corpus contract and validator**

```powershell
git add docs/card-rewards/2026-h2/README.md scripts/validate_card_rewards_docs.py tests/test_card_rewards_docs.py
git commit -m "test: define card rewards research contract"
```

---

### Task 2: First Bank and Taishin Existing-Customer Evidence

**Files:**

- Create: `docs/card-rewards/2026-h2/cards/first-ileo.md`
- Create: `docs/card-rewards/2026-h2/cards/first-green.md`
- Create: `docs/card-rewards/2026-h2/cards/taishin-richart-gogo.md`

**Interfaces:**

- Consumes: validator document contract and official sources under `firstbank.com.tw` and `taishinbank.com.tw`.
- Produces: three validated product documents; comparison task consumes their summary tables and source evidence.

- [ ] **Step 1: Prove the targeted documents are missing**

```powershell
python scripts\validate_card_rewards_docs.py --root docs\card-rewards\2026-h2 --only cards/first-ileo.md,cards/first-green.md,cards/taishin-richart-gogo.md
```

Expected: exit `1` with exactly those paths carrying `missing_file`.

- [ ] **Step 2: Research First Bank iLEO from official sources**

Locate the product rights page and every official activity page or PDF overlapping the target window. Record domestic and foreign base rates, account debit／electronic statement requirements, capped bonus rate, special digital or overseas channels, registration or quota rules, excluded transactions, and LINE Pay／iPASS MONEY／全支付 treatment. Exclude first-application and new-account offers.

- [ ] **Step 3: Research First Bank iPASS Green Card from official sources**

Confirm whether general consumption earns cash, points, or only designated green-transit／low-carbon bonuses. Record iPASS auto-load, transit, selected merchants, reward cap, registration, validity subranges and non-applicable transactions. Do not convert reward points to cash unless the official rules state the conversion.

- [ ] **Step 4: Research the old @GoGo card under Taishin Richart rights**

Confirm the official migration／applicable card scope for existing @GoGo holders. Record the default rate when no plan is selected, Richart level or auto-debit conditions, every selectable category relevant to the target window, Taiwan Pay or Taishin Pay limitations, cap and whether the user must switch rights before consumption.

- [ ] **Step 5: Write the three documents with exact evidence**

Each special reward row must contain:

```markdown
| 有效期間 | 場景／通路 | 總回饋 | 組成 | 舊戶條件 | 回饋上限 | 推導可刷額 | 登錄／名額 |
|---|---|---:|---|---|---|---:|---|
```

Every numeric row must cite an official numbered source in `## 來源證據`. If an official scheme ends before 12/31, set `coverage_status: partial` and state the uncovered dates in `## 不確定事項`.

- [ ] **Step 6: Validate and read back every source**

```powershell
python scripts\validate_card_rewards_docs.py --root docs\card-rewards\2026-h2 --only cards/first-ileo.md,cards/first-green.md,cards/taishin-richart-gogo.md
```

Expected: exit `0`. Reopen each official URL and compare product scope, dates, rates, bonus decomposition and cap against the Markdown before committing.

- [ ] **Step 7: Commit the First Bank and Taishin batch**

```powershell
git add docs/card-rewards/2026-h2/cards/first-ileo.md docs/card-rewards/2026-h2/cards/first-green.md docs/card-rewards/2026-h2/cards/taishin-richart-gogo.md
git commit -m "docs: verify First Bank and Taishin card rewards"
```

---

### Task 3: Sinopac Existing-Customer Evidence

**Files:**

- Create: `docs/card-rewards/2026-h2/cards/sinopac-dawho.md`
- Create: `docs/card-rewards/2026-h2/cards/sinopac-coin.md`
- Create: `docs/card-rewards/2026-h2/cards/sinopac-daway.md`

**Interfaces:**

- Consumes: validator contract and official sources under `bank.sinopac.com`.
- Produces: DAWHO, 幣倍 and DAWAY documents with bank-account level conditions separated from card ownership.

- [ ] **Step 1: Run the targeted missing-file gate**

```powershell
python scripts\validate_card_rewards_docs.py --root docs\card-rewards\2026-h2 --only cards/sinopac-dawho.md,cards/sinopac-coin.md,cards/sinopac-daway.md
```

Expected: exit `1` with three `missing_file` issues.

- [ ] **Step 2: Research DAWHO**

Verify domestic／foreign base and bonus rates, DAWHO account level, automatic debit, electronic statement, monthly bonus cap, posting month, mobile-payment exclusions and whether foreign online transactions qualify. Separate the uncapped base portion from the capped bonus.

- [ ] **Step 3: Research 幣倍卡**

Verify domestic／foreign general rates, selected foreign channel list, L1／L2 or equivalent account-level criteria, monthly cap, registration, currency or transaction-location rules and target-window changes. Calculate spend capacity from the bonus rate only.

- [ ] **Step 4: Research DAWAY**

Verify general domestic／foreign LINE POINTS rates, LINE Pay bonus, DAWHO account or auto-debit requirements, monthly cap, eligible LINE Pay transaction identification and exclusions. Keep LINE POINTS separate from cash.

- [ ] **Step 5: Write, validate, and source-read-back the three documents**

```powershell
python scripts\validate_card_rewards_docs.py --root docs\card-rewards\2026-h2 --only cards/sinopac-dawho.md,cards/sinopac-coin.md,cards/sinopac-daway.md
```

Expected: exit `0`; each document has at least one direct Sinopac source and explicitly covers or marks every date from 8/1 through 12/31.

- [ ] **Step 6: Commit the Sinopac batch**

```powershell
git add docs/card-rewards/2026-h2/cards/sinopac-dawho.md docs/card-rewards/2026-h2/cards/sinopac-coin.md docs/card-rewards/2026-h2/cards/sinopac-daway.md
git commit -m "docs: verify Sinopac card rewards"
```

---

### Task 4: Cathay CUBE and CTBC LINE Pay Evidence

**Files:**

- Create: `docs/card-rewards/2026-h2/cards/cathay-cube.md`
- Create: `docs/card-rewards/2026-h2/cards/ctbc-line-pay.md`

**Interfaces:**

- Consumes: official sources under `cathaybk.com.tw` and `ctbcbank.com`.
- Produces: CUBE selectable-rights evidence and CTBC LINE Pay general／merchant campaign evidence.

- [ ] **Step 1: Run the targeted missing-file gate**

```powershell
python scripts\validate_card_rewards_docs.py --root docs\card-rewards\2026-h2 --only cards/cathay-cube.md,cards/ctbc-line-pay.md
```

Expected: exit `1` with two `missing_file` issues.

- [ ] **Step 2: Research CUBE existing-card rights**

Record base rate, each selectable plan overlapping the target window, Level criteria, plan switching timing, designated merchant list source, unlimited／capped status, overseas recognition and mobile-payment exclusions. Do not treat a merchant as eligible solely because it appeared in the old artifact.

- [ ] **Step 3: Research CTBC LINE Pay card**

Record domestic／foreign general LINE POINTS rates, foreign in-person restrictions, designated-merchant campaigns, Visa／JCB differences, registration and quota, merchant-specific caps, campaign date subranges and exclusions. Separate guaranteed general rewards from limited registrations.

- [ ] **Step 4: Write, validate, and read back both documents**

```powershell
python scripts\validate_card_rewards_docs.py --root docs\card-rewards\2026-h2 --only cards/cathay-cube.md,cards/ctbc-line-pay.md
```

Expected: exit `0`; the highest advertised rate in each file is accompanied by its full old-customer conditions, cap and validity.

- [ ] **Step 5: Commit the Cathay and CTBC batch**

```powershell
git add docs/card-rewards/2026-h2/cards/cathay-cube.md docs/card-rewards/2026-h2/cards/ctbc-line-pay.md
git commit -m "docs: verify Cathay and CTBC card rewards"
```

---

### Task 5: Rakuten, O-Bank, and LINE Bank Debit Evidence

**Files:**

- Create: `docs/card-rewards/2026-h2/cards/rakuten-bank-card.md`
- Create: `docs/card-rewards/2026-h2/cards/obank-debit.md`
- Create: `docs/card-rewards/2026-h2/cards/line-bank-debit.md`

**Interfaces:**

- Consumes: official sources under `rakuten-bank.com.tw`, `o-bank.com` and `linebank.com.tw`.
- Produces: three documents that distinguish ATM, debit purchase and bank-account-linked payment behavior.

- [ ] **Step 1: Run the targeted missing-file gate**

```powershell
python scripts\validate_card_rewards_docs.py --root docs\card-rewards\2026-h2 --only cards/rakuten-bank-card.md,cards/obank-debit.md,cards/line-bank-debit.md
```

Expected: exit `1` with three `missing_file` issues.

- [ ] **Step 2: Research Rakuten Bank without inventing debit purchases**

Confirm from official product terms whether the issued financial card supports merchant purchases. If it is ATM-only, set `product_type: atm`, state domestic／foreign purchase reward as not applicable, and separately document existing-customer Pi Wallet／street payment or other linked-account offers that overlap the target window. Exclude every new-account referral reward.

- [ ] **Step 3: Research the general O-Bank debit card**

Use the general debit-card product page, not O! Range. Record domestic／foreign base cash rate, unlimited status, exclusions, foreign fee, supported mobile wallets and any existing-card campaign expressly covering the general card. O! Range-only 3.8% categories must not appear as user-available rewards.

- [ ] **Step 4: Research Visa LINE Bank debit card**

Record the default selectable cash／LINE POINTS mode, domestic／foreign general rates, country or merchant bonuses, switching timing, caps, supported payments and campaign validity. Distinguish account features from card rewards and exclude new-account bonuses.

- [ ] **Step 5: Write, validate, and read back all three documents**

```powershell
python scripts\validate_card_rewards_docs.py --root docs\card-rewards\2026-h2 --only cards/rakuten-bank-card.md,cards/obank-debit.md,cards/line-bank-debit.md
```

Expected: exit `0`; the Rakuten document does not imply Visa／Mastercard purchases unless an official source explicitly establishes that functionality, and the O-Bank document contains no O! Range-only reward.

- [ ] **Step 6: Commit the debit-card batch**

```powershell
git add docs/card-rewards/2026-h2/cards/rakuten-bank-card.md docs/card-rewards/2026-h2/cards/obank-debit.md docs/card-rewards/2026-h2/cards/line-bank-debit.md
git commit -m "docs: verify debit card rewards"
```

---

### Task 6: E.Sun and Fubon Costco Evidence

**Files:**

- Create: `docs/card-rewards/2026-h2/cards/esun-pi.md`
- Create: `docs/card-rewards/2026-h2/cards/esun-unicard.md`
- Create: `docs/card-rewards/2026-h2/cards/esun-ubear.md`
- Create: `docs/card-rewards/2026-h2/cards/fubon-costco.md`

**Interfaces:**

- Consumes: official sources under `esunbank.com` and `fubon.com`.
- Produces: four validated documents with P幣, e point, cash and 好多金 kept as distinct reward types.

- [ ] **Step 1: Run the targeted missing-file gate**

```powershell
python scripts\validate_card_rewards_docs.py --root docs\card-rewards\2026-h2 --only cards/esun-pi.md,cards/esun-unicard.md,cards/esun-ubear.md,cards/fubon-costco.md
```

Expected: exit `1` with four `missing_file` issues.

- [ ] **Step 2: Research E.Sun Pi Card**

Verify domestic／foreign P幣 rates, monthly threshold or prior-month spending, registration, designated Pi Wallet merchants, bonus cap, point expiry or offset restrictions, overseas cap and payment compatibility.

- [ ] **Step 3: Research E.Sun Unicard**

Verify general rate, selectable or upgraded categories, e point value only where officially stated, Unicard level tasks, monthly cap, merchant list, plan switching, mobile wallet recognition and target-window validity.

- [ ] **Step 4: Research E.Sun U Bear**

Verify general, online, digital-subscription and designated audio／video rates, electronic statement requirement, statement-cycle cap, what happens after the cap, eligible merchant list and mobile-payment exclusions.

- [ ] **Step 5: Research Fubon Costco card**

Verify general domestic／foreign rewards, Costco warehouse／online／fuel rates, 好多金 form and use restrictions, registration, caps, transit bonuses and whether non-Costco mobile-wallet transactions qualify.

- [ ] **Step 6: Write, validate, and read back the four documents**

```powershell
python scripts\validate_card_rewards_docs.py --root docs\card-rewards\2026-h2 --only cards/esun-pi.md,cards/esun-unicard.md,cards/esun-ubear.md,cards/fubon-costco.md
```

Expected: exit `0`; reward currencies remain distinct, and every cap states whether it is monthly, statement-cycle, quarter or campaign-wide.

- [ ] **Step 7: Commit the E.Sun and Fubon batch**

```powershell
git add docs/card-rewards/2026-h2/cards/esun-pi.md docs/card-rewards/2026-h2/cards/esun-unicard.md docs/card-rewards/2026-h2/cards/esun-ubear.md docs/card-rewards/2026-h2/cards/fubon-costco.md
git commit -m "docs: verify E.Sun and Fubon card rewards"
```

---

### Task 7: LINE Pay, iPASS MONEY, and PX Pay Evidence

**Files:**

- Create: `docs/card-rewards/2026-h2/payments/line-pay.md`
- Create: `docs/card-rewards/2026-h2/payments/ipass-money.md`
- Create: `docs/card-rewards/2026-h2/payments/px-pay.md`

**Interfaces:**

- Consumes: all 15 product documents plus official payment-service and bank campaign rules.
- Produces: three payment-centric compatibility matrices consumed by `comparison.md` and the later static tool.

- [ ] **Step 1: Run the targeted missing-file gate**

```powershell
python scripts\validate_card_rewards_docs.py --root docs\card-rewards\2026-h2 --only payments/line-pay.md,payments/ipass-money.md,payments/px-pay.md
```

Expected: exit `1` with three `missing_file` issues.

- [ ] **Step 2: Research LINE Pay compatibility and old-customer campaigns**

For each user product, record `supported`, `unsupported`, or `not officially confirmed`; then record whether bank card rewards remain eligible, require a specific network, use LINE POINTS, or exclude wallet transactions. Include bank-account-linked payment only where the official service supports it in the target window.

- [ ] **Step 3: Research iPASS MONEY compatibility and old-customer campaigns**

Separate linked-bank-account payment, stored-value／top-up and card-bound transactions. Record existing-account campaigns, designated bank requirements, cap, registration and whether each underlying card reward is excluded.

- [ ] **Step 4: Research PX Pay／全支付 compatibility and old-customer campaigns**

Treat PX Pay and 全支付 naming precisely according to official rules. Separate linked-account payment from bound-card payment, record bank-specific old-customer bonuses, weekly／monthly caps, registration and whether the underlying card still earns rewards.

- [ ] **Step 5: Write the three documents with a product-by-payment matrix**

Use this exact matrix header:

```markdown
| 使用者產品 | 可綁／可連結 | 支付方式 | 原卡／帳戶回饋 | 支付服務加碼 | 可否疊加 | 官方證據 |
|---|---|---|---|---|---|---|
```

Do not infer rewards from technical bindability. Unknown cases remain `not officially confirmed` and are excluded from best-card recommendations.

- [ ] **Step 6: Validate and read back the three payment documents**

```powershell
python scripts\validate_card_rewards_docs.py --root docs\card-rewards\2026-h2 --only payments/line-pay.md,payments/ipass-money.md,payments/px-pay.md
```

Expected: exit `0`; all 15 products appear in each matrix, or the document explicitly states why a product is outside that payment service's supported instrument type.

- [ ] **Step 7: Commit the payment batch**

```powershell
git add docs/card-rewards/2026-h2/payments/line-pay.md docs/card-rewards/2026-h2/payments/ipass-money.md docs/card-rewards/2026-h2/payments/px-pay.md
git commit -m "docs: verify mobile payment rewards"
```

---

### Task 8: Cross-Card Comparison and Final Evidence Audit

**Files:**

- Create: `docs/card-rewards/2026-h2/comparison.md`
- Modify: `docs/card-rewards/2026-h2/README.md`
- Modify: `scripts/validate_card_rewards_docs.py`
- Modify: `tests/test_card_rewards_docs.py`

**Interfaces:**

- Consumes: all 18 validated evidence documents.
- Produces: user-facing comparison, completed status ledger and final structural validation report; Phase 2 tool planning consumes this accepted corpus.

- [ ] **Step 1: Write failing tests for comparison coverage and unsafe claims**

Add tests that create a temporary complete corpus and assert:

```python
def test_comparison_requires_every_product_name(self) -> None:
    issues = validate_corpus(self.complete_fixture_without_comparison_rows())
    self.assertEqual(
        15,
        sum(issue.code == "comparison_missing_product" for issue in issues),
    )

def test_existing_customer_scope_is_mandatory(self) -> None:
    path = self.write_valid_document(customer_scope="new")
    codes = {issue.code for issue in validate_document(path, path.parents[1])}
    self.assertIn("wrong_scope", codes)
```

Also test that `coverage_status: partial` requires an uncovered-period statement and that `unavailable` permits no numeric recommendation claim.

- [ ] **Step 2: Run the new tests and confirm they fail**

```powershell
python -m unittest tests.test_card_rewards_docs -v
```

Expected: FAIL because comparison coverage, partial-period explanation and unavailable-claim checks are not implemented.

- [ ] **Step 3: Implement final semantic structure checks**

Add stable issue codes `partial_without_gap`, `unavailable_numeric_claim`, and `comparison_missing_product`. Parse comparison product identifiers from HTML comments of the form:

```markdown
<!-- product-id: first-ileo -->
```

Require each of the 15 card identifiers exactly once. For `partial`, require `未覆蓋期間：YYYY-MM-DD 至 YYYY-MM-DD`; for `unavailable`, reject percentage patterns in `## 結論摘要`.

- [ ] **Step 4: Build `comparison.md` from accepted evidence**

Use one product row per identifier with these columns:

```markdown
| 產品 | 國內一般 | 國外一般 | 最佳特殊回饋 | 條件 | 上限／推導可刷額 | LINE Pay | iPASS MONEY | 全支付 | 覆蓋狀態 |
|---|---|---|---|---|---|---|---|---|---|
```

Add scenario sections for domestic offline, domestic online, overseas in-person, overseas online, subscriptions, supermarkets, transit／fuel and the three common payments. A recommendation must name the reward type and use a footnote link back to the relevant product document; limited or registration-based rates cannot be presented as guaranteed.

- [ ] **Step 5: Complete the README status ledger**

Mark a product or payment complete only after its document validates and every numeric claim has been read back from an official source. Summarize counts by `complete`, `partial`, and `unavailable`, plus the exact date the source audit was performed.

- [ ] **Step 6: Run full structural validation and tests**

```powershell
python -m unittest tests.test_card_rewards_docs -v
python scripts\validate_card_rewards_docs.py --root docs\card-rewards\2026-h2 --json-report tmp\card-rewards-2026-h2-validation.json
python -m py_compile scripts\validate_card_rewards_docs.py tests\test_card_rewards_docs.py
git diff --check
```

Expected: all unit tests PASS; validator exits `0` with `issue_count: 0`; `py_compile` exits `0`; `git diff --check` prints nothing.

- [ ] **Step 7: Perform the final manual evidence audit**

For every comparison row, reopen the cited official page and verify: product identity, existing-customer eligibility, validity overlap with 8/1–12/31, total rate decomposition, reward currency, cap unit, registration／quota, excluded transactions and mobile-payment handling. Record any unavailable page as a source failure and remove its recommendation until a direct official source is available.

- [ ] **Step 8: Commit the comparison and final validator gates**

```powershell
git add docs/card-rewards/2026-h2/README.md docs/card-rewards/2026-h2/comparison.md scripts/validate_card_rewards_docs.py tests/test_card_rewards_docs.py
git commit -m "docs: complete 2026 H2 card rewards evidence"
```

- [ ] **Step 9: Verify final scope and prepare the Phase 1 handoff**

```powershell
git status --short --branch
git diff main HEAD --name-status
git log --oneline main..HEAD
```

Expected: only the approved spec/plan if inherited, research Markdown, validator and its tests appear in scope; no AHK, radiology viewer, outputs, patient data, credentials or unrelated files are staged or committed. Report coverage counts, validation output, unresolved periods and the exact commit range. Do not start `tool/card-rewards.html` until the user accepts the research corpus.

---

## Phase 2 Boundary

After Phase 1 acceptance, create a separate plan for `tool/card-rewards.html`, structured data generation, index／README integration, interaction tests, offline validation and browser E2E. That plan must consume the actual accepted Markdown schema and must not change verified reward facts without first updating the evidence documents.
