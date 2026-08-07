## ADDED Requirements

### Requirement: Offline single-file image stack import
The viewer SHALL run from a single local HTML file, SHALL read PNG and JPEG files only through the browser file picker or drag-and-drop interface, and SHALL NOT require or initiate a network request.

#### Scenario: Import while offline
- **WHEN** the user opens the viewer through `file://` without network connectivity and selects local PNG or JPEG files
- **THEN** the viewer decodes the selected files locally and exposes sequence organization controls without contacting an external origin

#### Scenario: External runtime dependency is absent
- **WHEN** the HTML document is inspected
- **THEN** it contains no external script, stylesheet, font, analytics, API, or image resource URL

### Requirement: Natural ordering and sequence count
The viewer SHALL sort imported files with a stable, case-insensitive natural-number comparator and SHALL support exactly two or three active sequences.

#### Scenario: Natural filename ordering
- **WHEN** files named `IMG_10.png`, `img_2.png`, and `IMG_1.png` are imported in arbitrary picker order
- **THEN** the organizer displays them as `IMG_1.png`, `img_2.png`, and `IMG_10.png`

#### Scenario: Choose three sequences
- **WHEN** the user selects three-sequence mode before assigning files
- **THEN** the organizer displays three sequence lanes and two movable boundaries

### Requirement: Boundary and per-image assignment
The organizer SHALL assign sorted files in bulk from movable boundaries and SHALL allow each file to be reassigned to another active sequence or excluded before volume construction.

#### Scenario: Split sixty-six files into two sequences
- **WHEN** 66 sorted files are loaded in two-sequence mode and the user places the boundary after file 30
- **THEN** files 1 through 30 are assigned to Sequence 1 and files 31 through 66 are assigned to Sequence 2

#### Scenario: Reassign an individual image
- **WHEN** the user drags an included thumbnail from Sequence 2 to Sequence 1
- **THEN** that file's assignment changes to Sequence 1 without changing the stable order of the other files

#### Scenario: Exclude an image
- **WHEN** the user clears an image's inclusion control
- **THEN** the image remains visible in the organizer as excluded and is omitted from volume construction

### Requirement: Sequence geometry configuration
Each sequence SHALL default to axial orientation, 1 mm per pixel in both in-plane axes, and 5 mm slice spacing, and SHALL expose forward or reverse slice order, rotation of 0, 90, 180, or 270 degrees, horizontal flip, vertical flip, positive pixel spacing, and positive slice spacing.

#### Scenario: Use default geometry
- **WHEN** the user constructs a volume without entering spacing or orientation metadata
- **THEN** the sequence uses axial orientation, forward order, zero rotation, no flips, 1 mm in-plane spacing, and 5 mm slice spacing and displays an unknown-scale warning

#### Scenario: Correct exported orientation
- **WHEN** the user selects reverse order, 90-degree rotation, and horizontal flip for one sequence
- **THEN** axial and reconstructed views for that sequence use the corrected canonical coordinate mapping

#### Scenario: Reject invalid spacing
- **WHEN** the user enters zero, a negative value, or a non-numeric value for spacing
- **THEN** the viewer restores 1 mm in-plane spacing or 5 mm slice spacing as applicable and displays the unknown-scale warning

### Requirement: Decode and dimension validation
The viewer SHALL decode included images sequentially, SHALL build each valid sequence as a single-channel `Uint8Array` volume, and SHALL preserve organizer state when a file cannot be decoded, canonical dimensions differ, or fewer than two valid images remain.

#### Scenario: Dimension mismatch
- **WHEN** one included image has canonical dimensions different from the other included images in its sequence
- **THEN** the viewer identifies the filename, blocks volume construction for that sequence, and keeps all assignments available for correction

#### Scenario: Decode failure
- **WHEN** a selected file cannot be decoded as PNG or JPEG
- **THEN** the viewer identifies the filename, marks the thumbnail as failed, and does not silently remove the file

#### Scenario: Insufficient depth
- **WHEN** a sequence contains fewer than two valid included images
- **THEN** the viewer blocks MPR volume construction for that sequence and identifies the minimum requirement

### Requirement: Memory-aware volume construction
The viewer SHALL estimate grayscale volume bytes before allocation, SHALL require explicit confirmation when the total estimate is at least 512 MiB, SHALL release full-resolution decode resources after each slice is copied, and SHALL surface allocation failure without discarding organizer state.

#### Scenario: Large allocation warning
- **WHEN** the estimated total grayscale volume size is 512 MiB or greater
- **THEN** the viewer displays the estimate and waits for user confirmation before allocating the volumes

#### Scenario: Allocation fails
- **WHEN** the browser cannot allocate a requested volume buffer
- **THEN** the viewer reports the affected sequence and retains file assignments, geometry settings, and thumbnails
