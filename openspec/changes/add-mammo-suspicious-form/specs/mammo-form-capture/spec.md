## ADDED Requirements

### Requirement: Suspicious-form button in the mammo GUI

The mammo; GUI in ahk-scripts/Mammo.ahk SHALL contain a button labelled "疑陽表單" that starts the capture flow. Pressing the button SHALL NOT change the report text in chk060 and SHALL NOT trigger the existing 輸出 action.

#### Scenario: Button starts capture

- **WHEN** the user opens the mammo; GUI and presses "疑陽表單"
- **THEN** the capture flow runs and the existing report-output routine is not invoked

### Requirement: Collect report and patient data

The capture flow SHALL collect the following fields:

- reportText: full text of chk060 control ThunderRT6TextBox14
- chartNo: the first 8 digits of chk060 control ThunderRT6TextBox9
- dicomChartNo: the first 8-digit run of the DICOM "Patient ID" line
- birthDate: DICOM "Patient's Birth Date"
- studyDate: DICOM "Study Date"
- nameEn: DICOM "Patient's Name"
- nameZh: result of GetPACSPatientChineseName() read from the INFINITT PACS window
- accession: result of GetAccessionNumber() on the same DICOM text

The flow SHALL NOT read or transmit the DICOM "Other Patient IDs" (0010,1000) value, which holds the national ID number.

The flow SHALL read the DICOM header only once per press and SHALL restore the clipboard content that existed before the press when the flow aborts.

#### Scenario: All sources available

- **WHEN** chk060 shows a report and INFINITT PACS shows the same patient
- **THEN** every listed field is filled and nameZh contains 2 to 6 CJK characters

#### Scenario: Chinese name not found

- **WHEN** GetPACSPatientChineseName() returns an empty string
- **THEN** nameZh is an empty string, nameEn keeps the DICOM English name, and the flow continues

### Requirement: Abort on missing source or patient mismatch

The capture flow SHALL abort with a Traditional Chinese MsgBox and SHALL NOT open the web page when any of these holds: reportText is empty after trimming whitespace; no INFINITT PACS window exists; chartNo is not 8 digits; dicomChartNo differs from chartNo.

#### Scenario: Chart numbers differ

- **WHEN** chk060 chartNo is 12345678 and DICOM Patient ID yields 87654321
- **THEN** a MsgBox reports that the HIS and PACS patients differ, the clipboard is restored, and Edge is not launched

#### Scenario: Empty report

- **WHEN** ThunderRT6TextBox14 contains only whitespace
- **THEN** a MsgBox asks the user to open the report first and the flow stops

### Requirement: Clipboard JSON hand-off

On success the flow SHALL place exactly one JSON object on the clipboard and then open tool/mammo-suspicious-form.html (resolved from the script directory) in Edge with no query string or fragment. The JSON SHALL have this shape, with every value a string:

`{"source":"rad-workflow/mammo-form","version":"1","chartNo":"","nameZh":"","nameEn":"","birthDate":"","studyDate":"","accession":"","reportText":""}`

String values SHALL be escaped per RFC 8259 (backslash, double quote, control characters including CR, LF and TAB). Dates SHALL be passed as the DICOM value with non-digits removed (YYYYMMDD).

#### Scenario: Report with quotes and line breaks

- **WHEN** reportText contains a double quote, a backslash, CRLF line breaks and a TAB
- **THEN** the clipboard text parses as valid JSON and the parsed reportText equals the original text exactly

##### Example: escaping

| Input fragment | JSON fragment |
| -------------- | ------------- |
| `size 1"` | `size 1\"` |
| `C:\a` | `C:\a` |
| CR LF | `\r\n` |
| TAB | `\t` |

#### Scenario: No patient data in the URL

- **WHEN** Edge is launched
- **THEN** the URL contains no query string and no fragment
