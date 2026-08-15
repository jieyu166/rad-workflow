## ADDED Requirements

### Requirement: Deterministic core cephalometric measurements

The measurement core SHALL calculate SNA as angle S-N-A, SNB as angle S-N-B, and ANB as SNA minus SNB. Results SHALL use source-image coordinates and SHALL be rounded only for display.

#### Scenario: Calculate complete core measurements

- **WHEN** S, N, A, and B are present with finite source-image coordinates
- **THEN** the measurement result contains finite SNA, SNB, and signed ANB values in degrees

##### Example: Two-degree ANB fixture

- **GIVEN** rays from N toward S, A, and B have directions 0°, 82°, and 80°
- **WHEN** the core calculates the three measurements
- **THEN** SNA equals 82°, SNB equals 80°, and ANB equals 2° within 0.01°

#### Scenario: Omit incomplete core measurements

- **WHEN** at least one of S, N, A, or B is absent or non-finite
- **THEN** the result omits SNA, SNB, and ANB and identifies the missing or invalid dependencies

### Requirement: Conservative sagittal classification

The report generator SHALL label the core reference as Steiner adult reference with SNA 82° ± 2°, SNB 80° ± 2°, and ANB 2° ± 2°. It SHALL describe ANB below 0° as a Class III tendency, ANB from 0° through 4° as a Class I tendency, and ANB above 4° as a Class II tendency.

#### Scenario: Classify ANB boundary values

- **WHEN** the report generator receives a finite ANB value
- **THEN** it applies the inclusive and exclusive boundaries exactly as specified

##### Example: ANB classification table

| ANB | Expected wording |
| ---: | ---------------- |
| -0.1° | Class III tendency |
| 0.0° | Class I tendency |
| 4.0° | Class I tendency |
| 4.1° | Class II tendency |

#### Scenario: Avoid a default class

- **WHEN** ANB is absent, invalid, or depends on a missing core landmark
- **THEN** the report omits skeletal class wording and SHALL NOT default to Class I

### Requirement: Dependency-gated advanced angular measurements

The core SHALL calculate advanced angular measurements only when every named landmark dependency is present and finite.

#### Scenario: Calculate skeletal plane measurements

- **WHEN** S, N, Go, and Me are present
- **THEN** the result contains the smaller undirected angle between SN and Go-Me as SN-MP

#### Scenario: Calculate palatal-mandibular plane measurement

- **WHEN** ANS, PNS, Go, and Me are present
- **THEN** the result contains the smaller undirected angle between ANS-PNS and Go-Me as PP-MP

#### Scenario: Calculate dental angular measurements

- **WHEN** U1 tip, U1 apex, L1 tip, L1 apex, ANS, PNS, Go, and Me are present
- **THEN** the result contains U1-PP, L1-MP, and interincisal angles using the cephalometric obtuse-angle convention defined as 180° minus the smaller undirected angle between the relevant lines, yielding 90° through 180° independently of endpoint order

#### Scenario: Omit a partial optional group

- **WHEN** an advanced measurement lacks at least one named dependency
- **THEN** the result omits that measurement and the report marks its analysis group as not performed

### Requirement: Uncertainty propagation

Every measurement SHALL carry uncertain as true when at least one dependency landmark has uncertain set to true.

#### Scenario: Report an uncertain measurement

- **WHEN** ANB depends on an uncertain S, N, A, or B landmark
- **THEN** the displayed value and associated interpretation include an approximate and review-required notice

#### Scenario: Keep unrelated measurements certain

- **WHEN** an uncertain landmark is not a dependency of a measurement
- **THEN** that measurement retains uncertain as false

### Requirement: Calibrated manual distance measurements

The page SHALL allow a user to create a labeled two-point distance after valid scale calibration. The result SHALL equal source-pixel Euclidean distance multiplied by mmPerPixel and SHALL remain a raw measurement without automatic normal or abnormal interpretation.

#### Scenario: Calculate a calibrated distance

- **WHEN** a valid calibration exists and the user confirms two distinct measurement points with a non-empty label
- **THEN** the page displays the labeled distance in millimeters and makes it available to the report generator

##### Example: Twenty-millimeter distance

- **GIVEN** mmPerPixel equals 0.1 and measurement points are 200 source pixels apart
- **WHEN** the distance is calculated
- **THEN** the displayed result equals 20.0 mm

#### Scenario: Block an uncalibrated distance

- **WHEN** mmPerPixel is null
- **THEN** the page disables calibrated distance creation and the report SHALL NOT contain a millimeter result derived from image pixels

### Requirement: Structured radiology report

The report generator SHALL produce editable English UTF-8 plain text with Examination/Technique, Findings, Cephalometric Analysis, Impression, and Limitations sections. All system-generated report wording SHALL be English. It SHALL use only explicit survey state, completed measurements, physician-entered text, and named reference data. Physician-entered notes SHALL be preserved verbatim and SHALL NOT be translated automatically.

#### Scenario: Generate an English report while preserving physician text

- **WHEN** the report is generated with no physician-entered note
- **THEN** the report contains no CJK Unified Ideographs and all system-generated wording is English
- **AND WHEN** a physician-entered note contains non-English text
- **THEN** that note remains verbatim inside the otherwise English report

#### Scenario: Generate a complete basic report

- **WHEN** the six survey items have explicit statuses and S, N, A, and B are complete
- **THEN** the report contains technique and calibration status, survey findings, SNA/SNB/ANB with the named reference, sagittal impression, and fixed limitations

#### Scenario: Represent an unperformed analysis group

- **WHEN** an optional landmark group is skipped or incomplete
- **THEN** the report labels that group as not performed and omits its values and interpretation

#### Scenario: Preserve abnormal notes

- **WHEN** a survey item is abnormal and has a physician-entered note
- **THEN** the Findings section includes that note without replacing it with generated normal wording

#### Scenario: Represent unassessed or limited anatomy

- **WHEN** any anatomy survey item is unassessed or limited
- **THEN** the report names the affected region in Findings or Limitations and omits any whole-image no-additional-abnormality statement

#### Scenario: State whole-image negative findings only after explicit review

- **WHEN** sellaSkullBase, sinusesNasopharynx, tmj, jawsDentition, and cervicalAirway are all explicitly normal
- **THEN** the report can state that no significant additional abnormality is seen within the imaged field

### Requirement: Fixed clinical limitations

Every generated report SHALL state that lateral cephalometry is a two-dimensional projection affected by positioning, magnification, and landmark identification. The report SHALL state that airway appearance is screening-only and SHALL NOT diagnose obstructive sleep apnea. When calibration is absent, it SHALL state that linear measurements were not reported.

#### Scenario: Generate airway-safe wording

- **WHEN** the cervicalAirway survey is normal, abnormal, limited, or unassessed
- **THEN** the report contains no diagnosis or exclusion of obstructive sleep apnea based solely on the lateral cephalogram

#### Scenario: Generate uncalibrated limitation

- **WHEN** mmPerPixel is null
- **THEN** the Limitations section states that no calibrated linear value was generated

### Requirement: Editable report snapshot

A generated report SHALL remain an editable snapshot. Changes to survey, calibration, landmarks, measurements, or patient metadata after generation SHALL mark the snapshot stale and SHALL NOT overwrite physician edits.

#### Scenario: Preserve physician edits after an upstream change

- **WHEN** the physician edits report text and then moves a landmark or changes a survey status
- **THEN** the current report text remains unchanged and the page displays a stale warning

#### Scenario: Explicitly regenerate a stale report

- **WHEN** the physician activates regenerate on a stale report and confirms replacement
- **THEN** the page replaces the editable text with a newly generated snapshot from current state and clears the stale indicator

### Requirement: Report copy fallback

The page SHALL provide a copy action and SHALL leave the report in a selectable editable control when clipboard writing fails.

#### Scenario: Copy succeeds

- **WHEN** the browser clipboard write operation succeeds
- **THEN** the page announces that the current report snapshot was copied

#### Scenario: Copy is unavailable

- **WHEN** clipboard writing is blocked or unsupported
- **THEN** the page displays manual-copy instructions without deleting or changing report text
