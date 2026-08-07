## ADDED Requirements

### Requirement: Reference-based crosslink model
The viewer SHALL use Sequence 1 as the reference sequence and SHALL maintain one independent ordered anchor list for Sequence 1 to Sequence 2 and, in three-sequence mode, one independent ordered anchor list for Sequence 1 to Sequence 3.

#### Scenario: Create anchors in three-sequence mode
- **WHEN** the user adds a Sequence 1 to Sequence 2 anchor and a Sequence 1 to Sequence 3 anchor
- **THEN** the viewer stores the pairs in separate target-specific anchor lists

### Requirement: Anchor creation and editing
The viewer SHALL create an anchor from the currently displayed source and target slices and SHALL allow an existing anchor to be selected, edited, or deleted from the timeline.

#### Scenario: Add an anatomical correspondence
- **WHEN** Sequence 1 displays slice 16, Sequence 2 displays slice 50, and the user adds a crosslink anchor for Sequence 2
- **THEN** the viewer stores and displays the anchor pair 16 to 50 on both timelines

#### Scenario: Delete an anchor
- **WHEN** the user selects an existing timeline anchor and confirms deletion
- **THEN** the anchor is removed and subsequent synchronization uses the remaining anchors

### Requirement: Strictly monotonic anchor validation
Each anchor list SHALL contain unique reference indices and unique target indices, and both index series SHALL be strictly increasing after canonical sequence orientation is applied. The viewer SHALL reject a candidate that violates either condition without changing existing anchors.

#### Scenario: Reject crossing anchors
- **WHEN** anchors 7 to 39 and 27 to 63 exist and the user attempts to add 20 to 65
- **THEN** the viewer rejects the candidate, preserves the existing anchors, and identifies the conflict

#### Scenario: Reject duplicate index
- **WHEN** an anchor with reference index 16 already exists and the user attempts to add another anchor with reference index 16
- **THEN** the viewer rejects the candidate and identifies the duplicate reference index

### Requirement: Piecewise mapping behavior
The viewer SHALL map slice positions with no anchor as independent state, with one anchor as a fixed offset, and with two or more anchors as piecewise linear interpolation. Positions outside the outer anchors SHALL use the slope of the nearest segment and SHALL be clamped to the valid target range.

#### Scenario: One-anchor offset
- **WHEN** the only anchor is 16 to 50 and Sequence 1 moves to position 18
- **THEN** the mapped Sequence 2 position is 52 before range clamping

#### Scenario: Interpolate between anchors
- **WHEN** anchors are 7 to 39 and 27 to 63 and Sequence 1 moves to position 17
- **THEN** the mapped Sequence 2 position is 51

#### Scenario: Extrapolate and clamp
- **WHEN** the nearest outer segment projects a target position beyond the target sequence depth
- **THEN** the viewer clamps the mapped position to the nearest valid target endpoint

### Requirement: Reversible synchronization
The viewer SHALL derive target-to-reference mapping by inverting the same monotonic anchor segments, and a scroll action in Sequence 2 or Sequence 3 SHALL map through Sequence 1 before updating every other synchronized sequence.

#### Scenario: Scroll a secondary sequence
- **WHEN** the user scrolls Sequence 2 to a new slice in three-sequence mode
- **THEN** the viewer maps Sequence 2 to Sequence 1 and then maps the resulting Sequence 1 position to Sequence 3

#### Scenario: Round only axial display
- **WHEN** a mapping produces target position 50.4
- **THEN** the axial viewport displays original frame 50 while MPR retains position 50.4 for interpolation

### Requirement: Independent mode without anchors
The viewer SHALL keep sequences independently scrollable when the corresponding target anchor list is empty and SHALL NOT infer a normalized-index mapping.

#### Scenario: Scroll before crosslink creation
- **WHEN** Sequence 1 to Sequence 2 has no anchors and the user scrolls Sequence 1
- **THEN** Sequence 2 remains at its current position

### Requirement: Timeline crosslink visualization
The viewer SHALL display each anchor as a selectable marker on the related sequence timelines and SHALL draw a connector that identifies the paired slices without obscuring thumbnail selection.

#### Scenario: Display multiple anchors
- **WHEN** three valid anchors exist for Sequence 1 to Sequence 2
- **THEN** both timelines display three selectable markers and three corresponding connectors

