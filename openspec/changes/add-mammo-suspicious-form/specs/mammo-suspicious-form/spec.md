## ADDED Requirements

### Requirement: Import patient data from clipboard JSON

tool/mammo-suspicious-form.html SHALL import data when the user pastes a payload (Ctrl+V anywhere, including while a text field such as the report box has focus) or presses the "從剪貼簿匯入" button. A non-payload paste inside a text field SHALL be left to the browser as a normal paste. If the report box contains a whole payload JSON when the user presses "AI 解析", the page SHALL import it first and send only the payload's reportText to the LLM. The page SHALL accept only a JSON object whose source equals "rad-workflow/mammo-form"; any other clipboard content SHALL show an error message and leave existing form data unchanged. The page SHALL NOT read patient data from the URL and SHALL NOT persist patient data to localStorage, sessionStorage or IndexedDB.

#### Scenario: Valid payload

- **WHEN** the user pastes a payload with source "rad-workflow/mammo-form"
- **THEN** 病歷號, 姓名, 出生日期, 攝影日期 and the report text area are filled from the payload

#### Scenario: Payload pasted into the report box

- **WHEN** the report box has focus and the user pastes a payload with source "rad-workflow/mammo-form"
- **THEN** the header fields are filled from the payload, the report box contains only reportText, and no chart number or name is later sent to the LLM

#### Scenario: Foreign clipboard content

- **WHEN** the user pastes plain text "hello"
- **THEN** an error message in Traditional Chinese is shown and no field changes

#### Scenario: Chinese name missing

- **WHEN** the payload has nameZh "" and nameEn "CHEN^MEI"
- **THEN** 姓名 shows "CHEN MEI" and the field is highlighted as needing manual correction

### Requirement: ROC date conversion

The page SHALL render 出生日期 and 攝影日期 as ROC year, month and day in the form's 民國 ___ 年 ___ 月 ___ 日 slots. The page SHALL accept input dates as YYYYMMDD, YYYY.MM.DD, YYYY/MM/DD or YYYY-MM-DD. An unparseable or empty date SHALL leave the slots blank.

#### Scenario: Convert Gregorian to ROC

- **WHEN** a date is imported
- **THEN** ROC year equals Gregorian year minus 1911 and month and day keep leading zeros removed

##### Example: date inputs

| Input | 年 | 月 | 日 |
| ----- | -- | -- | -- |
| 20261006 | 115 | 10 | 6 |
| 1965.03.09 | 54 | 3 | 9 |
| 1950/12/31 | 39 | 12 | 31 |
| abc | (blank) | (blank) | (blank) |

### Requirement: Fixed header fields

醫院名稱 SHALL be pre-filled with "佳里奇美醫院". 放射科醫師 and 身分證統一編號 SHALL be blank on import so that the physician can stamp and the ID can be handwritten; both SHALL remain editable on screen.

#### Scenario: Header after import

- **WHEN** any valid payload is imported
- **THEN** 醫院名稱 is "佳里奇美醫院", 放射科醫師 is blank and the ten ID boxes are blank

### Requirement: Deterministic BI-RADS category

The page SHALL derive the 疑似異常結果 category from the report text with the case-insensitive pattern `(?:BI-?RADS\s*)?category\s*:?\s*(\d)([abc])?(?![a-z])` (first match), without using the LLM. When the category is 4 and the letter group matched, the page SHALL tick the matching sub-box a, b or c from that letter; the LLM cat4Sub value SHALL be used only when no letter is present. Category 0, 3, 4 and 5 SHALL tick the matching box. Category 1, 2, 6 or no match SHALL show a warning that the report does not need this form, and SHALL leave every category box unticked while still allowing manual ticking.

#### Scenario: Category from report

- **WHEN** the report contains "(BI-RADS category 0, need additional imaging evaluation)"
- **THEN** Category 0 is ticked and Categories 3, 4 and 5 are not

##### Example: category mapping

| Report fragment | Ticked | Warning |
| --------------- | ------ | ------- |
| BI-RADS category 0 | Category 0 | no |
| BI-RADS Category 4 | Category 4 | no |
| BI-RADS assessment: Category 4C (Suspicious...) | Category 4, sub c | no |
| BI-RADS category 2 | none | yes |
| (no BI-RADS line) | none | yes |

### Requirement: LLM lesion parsing

When the user presses "AI 解析", the page SHALL send the report text with a fixed system prompt to the Gemini generateContent endpoint, using the same model id constant as tool/ldct-report.html and responseMimeType application/json. The API key SHALL come from a password input on the page and SHALL NOT be stored. The response SHALL be validated against this schema before use:

`{"cat4Sub":"a"|"b"|"c"|null,"lesions":[{"type":"mass"|"calcification"|"asymmetry"|"distortion"|"skin_nipple"|"axillary_ln"|"ducts"|"diffuse_skin"|"other","side":"R"|"L"|"multiple_unilateral"|"multiple_bilateral","location":["UOQ"|"UIQ"|"LOQ"|"LIQ"|"Subareolar"|"Axillary tail"],"oneView":["upper"|"lower"|"outer"|"inner"],"size":"<1"|"1-2"|"2-3"|"3-4"|">4"|null,"shape":"round"|"oval"|"lobular"|"irregular"|null,"margin":"circumscribed"|"microlobulated"|"obscured"|"indistinct"|"spiculated"|null,"density":"high"|"equal"|"low"|"fat"|null,"distribution":"grouped"|"linear"|"segmental"|"regional"|"diffuse"|null,"morphology":"amorphous"|"coarse_heterogeneous"|"fine_pleomorphic"|"fine_linear_branching"|null,"asymmetryType":"asymmetry"|"focal"|"developing"|null,"otherText":string|null}]}`

Unknown enum values SHALL be dropped (left unticked) rather than guessed. The prompt SHALL instruct the model to list only findings that drive the suspicious category and to exclude findings described as benign (for example "benign calcification"), and to put a finding with no matching form item under type "other" with otherText.

#### Scenario: Benign finding excluded

- **WHEN** the report lists "Benign calcification of both breasts." and "Focal asymmetry in left UOQ breast"
- **THEN** exactly one lesion page is produced, with 3. Asymmetry, Lt., Focal asymmetry and UOQ ticked

#### Scenario: Invalid LLM response

- **WHEN** the response is not valid JSON or lesions is not an array
- **THEN** an error message is shown, no checkbox changes, and the raw response is shown for copying

#### Scenario: Missing API key

- **WHEN** the user presses "AI 解析" with an empty key field
- **THEN** the page shows a message asking for the Gemini key and sends no request

### Requirement: One form page per lesion

The page SHALL render one complete form page (header, category and lesion sections) per lesion in the parsed result, in report order, each page carrying the same header data and category. With zero lesions the page SHALL render one page with no lesion item ticked. The user SHALL be able to delete a page and add a blank page before printing.

#### Scenario: Bilateral lesions

- **WHEN** the parsed result has a right mass and a left calcification
- **THEN** two pages are rendered: page 1 ticks 1. Mass Rt., page 2 ticks 2. Calcifications Lt.

### Requirement: Manual-tick prompt after parsing

After LLM results are applied, the page SHALL check every form page and, for each page that still needs manual input, show a screen-only alert above that page listing the missing parts: no lesion item 1–9 ticked; a ticked item 1–8 with no side (Rt., Lt., or a Multiple option); a ticked item 1–4 with no location or one-view box; item 9 ticked with an empty description. When any page has an alert, the status line SHALL be a warning naming those pages and asking for manual ticking instead of the success message. Each alert SHALL update as the user ticks boxes and disappear when nothing is missing. Alerts SHALL NOT print.

#### Scenario: No lesion found

- **WHEN** the LLM returns lesions []
- **THEN** the status line is a warning containing 人工勾選 and page 1 shows 未勾選任何病灶項目

#### Scenario: Missing side and location cleared by the user

- **WHEN** the LLM returns a mass with side null and location [] on page 1 and a complete lesion on page 2
- **THEN** only page 1 shows an alert mentioning 左右側 and 位置, and after the user ticks Rt. and UOQ on page 1 the alert disappears

### Requirement: Manual edit and A4 print

Every checkbox and text field on every form page SHALL be editable by the user after parsing. Printing SHALL output only the form pages, each on its own A4 portrait sheet with the layout of 附表四之五 (114 年 1 月修訂), hiding all controls, key input and report text area.

#### Scenario: Print preview

- **WHEN** the user prints a two-page result
- **THEN** the preview shows exactly two A4 pages, each containing the form title "健康署婦女乳房X光攝影檢查服務之篩檢疑似異常個案報告表" and no buttons
