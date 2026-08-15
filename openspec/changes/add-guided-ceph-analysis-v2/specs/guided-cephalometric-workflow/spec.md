## ADDED Requirements

### Requirement: Offline image intake and privacy

The page SHALL accept exactly one lateral cephalometric PNG or JPEG through a paste event, drag and drop, or a file picker. The page SHALL decode the image locally and SHALL NOT upload, persist, or transmit the image or associated patient data.

#### Scenario: Load a supported image

- **WHEN** the user supplies a decodable PNG or JPEG not exceeding 50 MiB and 16384 pixels on either side
- **THEN** the page displays the image and enables the survey and calibration stages without making a network request

#### Scenario: Reject an unsupported image without data loss

- **WHEN** the user supplies a non-image file, unsupported image type, undecodable image, oversized file, or oversized dimensions while a study is already loaded
- **THEN** the page displays a specific error and retains the existing image, survey, calibration, landmarks, and report

#### Scenario: Keep study data ephemeral

- **WHEN** the page holds an image, patient metadata, landmarks, or report text
- **THEN** the page SHALL keep that data in current-page memory and SHALL NOT write it to localStorage, IndexedDB, cookies, or a remote endpoint

### Requirement: Progressive wizard stages

The page SHALL present a single guided path in this order: image, six-area survey, scale calibration, core landmarks, optional advanced groups, and report. The active stage SHALL show only the instructions and controls needed for the current action.

#### Scenario: Unlock the basic report

- **WHEN** S, N, A, and B are all confirmed
- **THEN** the page enables basic cephalometric measurement and report generation

#### Scenario: Keep the basic report locked

- **WHEN** any of S, N, A, or B is absent
- **THEN** the page keeps basic cephalometric report generation disabled and names every missing core landmark

#### Scenario: Skip an optional group

- **WHEN** the user skips the ANS/PNS/Go/Me group or the U1/L1 tip-and-apex group
- **THEN** the wizard proceeds without fabricating measurements that depend on the skipped group

### Requirement: Landmark placement and editing

The page SHALL guide the user through S, N, A, B, ANS, PNS, Go, Me, U1 tip, U1 apex, L1 tip, and L1 apex in configured group order. Each point SHALL store normalized source-image coordinates and an uncertainty flag.

For incisor-axis placement, the page SHALL identify U1 as a maxillary permanent central incisor (FDI 11 or 21) and L1 as a mandibular permanent central incisor (FDI 31 or 41). It SHALL explain that the lateral projection superimposes right and left teeth, that the user should select a relatively labial central-incisor trace whose incisal tip and root apex can both be followed clearly, and that the two endpoints MUST belong to the same tooth. The page SHALL define the line joining those two endpoints as the incisor long axis. It SHALL instruct the user to mark the points uncertain or skip the optional group when same-tooth pairing is unreliable.

#### Scenario: Teach same-tooth incisor-axis placement

- **WHEN** the user views or starts the optional incisor group
- **THEN** the page shows a two-point long-axis schematic, the FDI 11/21 and 31/41 mappings, and the same-tooth pairing rule
- **AND** it does not imply that U1 or L1 is fixed to one side on a superimposed lateral projection

##### Example: Overlapping central-incisor traces

- **GIVEN** the right and left central-incisor images are superimposed
- **WHEN** one trace has an identifiable incisal tip but its root apex cannot be followed reliably
- **THEN** the user is told not to pair that tip with the contralateral apex and to mark the pair uncertain or skip the optional group

#### Scenario: Place a landmark through a transformed viewport

- **WHEN** the user clicks a visible image location after zooming or panning
- **THEN** the page converts the pointer location into normalized source-image coordinates independent of the display transform

#### Scenario: Refine a landmark

- **WHEN** the user selects a confirmed landmark and uses pointer repositioning or arrow-key nudge
- **THEN** the page updates that landmark, recomputes dependent measurements, and preserves unrelated landmarks

#### Scenario: Undo and redo landmark changes

- **WHEN** the user invokes undo or redo after placing, moving, deleting, or changing the uncertainty of a landmark
- **THEN** the page restores the previous or next study state without changing the loaded image

#### Scenario: Mark a point uncertain

- **WHEN** the user confirms a landmark with the uncertainty control active
- **THEN** the page stores uncertain as true and visibly distinguishes the point from a certain landmark

### Requirement: Diagnostic image controls

The page SHALL provide zoom, pan, invert, fit-to-view, and reset controls without altering source coordinates or measurements.

#### Scenario: Preserve geometry during viewing changes

- **WHEN** the user zooms, pans, inverts, fits, or resets the viewport
- **THEN** every stored landmark and computed measurement remains numerically unchanged

### Requirement: Six-area survey without default normal findings

The page SHALL represent imageQuality, sellaSkullBase, sinusesNasopharynx, tmj, jawsDentition, and cervicalAirway as survey items with status unassessed, normal, abnormal, or limited and an editable note. Every item SHALL start as unassessed.

#### Scenario: Record an abnormal survey finding

- **WHEN** the user sets a survey item to abnormal and enters a note
- **THEN** the page retains both the abnormal status and note for report generation

#### Scenario: Explicitly batch-mark normal findings

- **WHEN** the user activates the labeled batch-normal action and confirms the action
- **THEN** the page changes eligible unassessed survey items to normal and leaves abnormal or limited items unchanged

#### Scenario: Do not infer normality

- **WHEN** the user has not explicitly assessed a survey item
- **THEN** the page retains unassessed and SHALL NOT convert it to normal during navigation or report generation

### Requirement: Visible-ruler scale calibration

The page SHALL calibrate linear measurements from two user-selected source-image points and a finite positive known distance in millimeters. The scale SHALL equal known millimeters divided by source-pixel Euclidean distance.

#### Scenario: Complete valid calibration

- **WHEN** the selected ruler points are at least 20 source pixels apart and the entered distance is finite and greater than zero
- **THEN** the page stores a positive mmPerPixel value and enables calibrated distance tools

##### Example: Forty-millimeter interval

- **GIVEN** ruler points at source pixels (100, 200) and (500, 200)
- **WHEN** the user enters 40 mm
- **THEN** mmPerPixel equals 0.1

#### Scenario: Reject invalid calibration

- **WHEN** the two points are less than 20 source pixels apart or the entered distance is zero, negative, empty, infinite, or non-numeric
- **THEN** the page displays a calibration error, sets mmPerPixel to null, and keeps angle measurements available

#### Scenario: Skip calibration

- **WHEN** the user skips the calibration stage
- **THEN** the page continues to core landmarks and marks linear measurement capability as unavailable

### Requirement: Safe in-memory lifecycle

The page SHALL protect current in-memory work from accidental replacement while making clear that the browser cannot recover the study after the page closes.

#### Scenario: Replace the loaded study

- **WHEN** the user attempts to load another image after changing survey, calibration, landmarks, or report text
- **THEN** the page requests confirmation before clearing the current study and loads the new image only after confirmation

#### Scenario: Warn before leaving

- **WHEN** the current study contains unsaved in-memory changes and the user reloads or closes the page
- **THEN** the page invokes the browser standard beforeunload warning

### Requirement: Accessible responsive workspace

The page SHALL remain operable through keyboard controls and readable at 1440 by 900 and 1024 by 768 viewport sizes.

#### Scenario: Keyboard-only landmark refinement

- **WHEN** focus is on a landmark control and the user presses an arrow key
- **THEN** the page moves the landmark by the documented source-coordinate increment and announces the update through an accessible status region

#### Scenario: Desktop layout at supported sizes

- **WHEN** the page renders at 1440 by 900 or 1024 by 768
- **THEN** the image workspace, active-step controls, progress indicator, and primary actions remain visible without horizontal page overflow
