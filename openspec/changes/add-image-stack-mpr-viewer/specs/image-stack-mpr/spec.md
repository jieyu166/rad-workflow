## ADDED Requirements

### Requirement: Trilinear intensity sampling
The reslicer SHALL sample an in-bounds `Uint8Array` volume with trilinear interpolation, SHALL return a floating-point intensity from 0 through 255, and SHALL return 0 for an out-of-bounds coordinate.

#### Scenario: Sample the center of eight voxels
- **WHEN** a 2 by 2 by 2 volume contains corner intensities 0, 10, 20, 30, 40, 50, 60, and 70 and the reslicer samples coordinate 0.5, 0.5, 0.5
- **THEN** the returned intensity is 35

#### Scenario: Sample outside the volume
- **WHEN** any sample coordinate is outside the inclusive volume bounds
- **THEN** the returned intensity is 0

### Requirement: Standard orthogonal reslices
The viewer SHALL render axial planes at constant canonical z, coronal planes at constant canonical y, and sagittal planes at constant canonical x, using sequence spacing and orientation transforms to preserve the configured physical aspect ratio.

#### Scenario: Reconstruct a coronal plane
- **WHEN** the user opens the COR viewport for a valid sequence volume
- **THEN** horizontal output movement follows canonical x and vertical output movement follows canonical z scaled by in-plane and slice spacing

#### Scenario: Reconstruct a sagittal plane
- **WHEN** the user opens the SAG viewport for a valid sequence volume
- **THEN** horizontal output movement follows canonical y and vertical output movement follows canonical z scaled by in-plane and slice spacing

### Requirement: Arbitrary oblique reslice
The viewer SHALL define an oblique plane from a volume center point plus azimuth, tilt, and roll angles, SHALL allow the center and angles to be changed by direct manipulation or numeric controls, and SHALL provide a reset to a standard plane.

#### Scenario: Change oblique orientation
- **WHEN** the user changes azimuth, tilt, or roll
- **THEN** the viewer computes new orthonormal plane basis vectors and rebuilds the oblique image through the unchanged center point

#### Scenario: Reset oblique plane
- **WHEN** the user activates Oblique Reset
- **THEN** the viewer restores the documented zero-angle standard plane and retains the current crosshair center

### Requirement: Crosslinked MPR location
The viewer SHALL use fractional crosslink positions to place corresponding crosshairs and reslice centers in secondary sequences and SHALL update all synchronized MPR views when any sequence becomes the interaction source.

#### Scenario: Use fractional target position
- **WHEN** Sequence 1 maps to Sequence 2 position 50.4
- **THEN** Sequence 2 MPR samples around z position 50.4 without rounding it to an original frame index

### Requirement: Basic image interaction
The viewer SHALL support wheel slice navigation, Ctrl or Meta plus wheel zoom, pan, crosshair movement, right-button drag intensity adjustment, Fit, Reset, Invert, and independent controls for synchronizing zoom and pan or intensity across sequences.

#### Scenario: Zoom without changing slice
- **WHEN** the pointer is over a viewport and the user rotates the wheel while holding Ctrl or Meta
- **THEN** that viewport zoom changes and its slice position remains unchanged

#### Scenario: Adjust intensity
- **WHEN** the user right-drags horizontally and vertically in a viewport
- **THEN** the viewer changes 8-bit intensity width and center and does not label the control as HU or DICOM Window Level

#### Scenario: Reset a viewport
- **WHEN** the user activates Reset
- **THEN** the viewport restores fit-to-frame pan and zoom, non-inverted display, and default full-range intensity

### Requirement: Responsive comparison workspace
Crosslink mode SHALL display two or three large axial viewports above corresponding thumbnail timelines. MPR mode SHALL display a large Sequence 1 2 by 2 AX, COR, SAG, and Oblique grid with synchronized Sequence 2 and Sequence 3 comparison views on wide screens and SHALL reflow comparison regions vertically on narrow screens.

#### Scenario: Wide three-sequence MPR
- **WHEN** three-sequence MPR mode is displayed at a viewport width of at least 1400 CSS pixels
- **THEN** the Sequence 1 2 by 2 grid and both secondary comparison regions are visible without horizontal page scrolling

#### Scenario: Narrow layout
- **WHEN** MPR mode is displayed below 900 CSS pixels
- **THEN** the primary grid and secondary comparison regions stack vertically without clipping controls or images

### Requirement: Progressive reslice quality
The viewer SHALL render MPR interaction previews with a maximum dimension of 256 pixels and SHALL schedule a full render 120 milliseconds after input stops, using the viewport device-pixel size with a maximum dimension of 1024 pixels. A newer generation SHALL prevent an older render result from replacing current state.

#### Scenario: Drag an oblique plane
- **WHEN** the user continuously drags an oblique orientation handle
- **THEN** preview renders remain at or below 256 pixels and the latest state receives a full render after 120 milliseconds without input

#### Scenario: Ignore stale render
- **WHEN** a slow render for generation 4 completes after generation 5 has started
- **THEN** the viewer discards generation 4 and retains generation 5 output

### Requirement: Unknown geometry warning
The viewer SHALL display a persistent scale warning in reconstructed views when in-plane pixel spacing is the default unknown value and SHALL describe the MPR as positioning-only rather than measurement-capable.

#### Scenario: Reconstruct with default spacing
- **WHEN** a sequence uses default 1 mm in-plane spacing because source metadata is absent
- **THEN** every MPR workspace containing that sequence displays an unknown-scale positioning-only warning
