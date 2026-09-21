## ADDED Requirements

### Requirement: Pluggable local transcription engines

The system SHALL expose an engine interface `transcribe(wav_path, lang) -> list[Cue]` where a Cue has start_sec, end_sec, and text. The package SHALL ship four local engines: `breeze_ct2` (default; Breeze-ASR-25 converted to CTranslate2), `faster_whisper` (official Whisper models), `whisper_cpp` (external binary, CPU-capable), and `qwen3_asr` (Qwen3-ASR open weights via the qwen-asr package, transformers backend by default, vLLM backend optional). Each engine SHALL declare metadata: name, local (bool), needs_gpu (bool), native_timestamps (bool), default_model.

#### Scenario: Engine selection

- **WHEN** `l2n transcribe video.mp4 --lang zh --engine qwen3_asr` is run with the qwen extra installed and weights available locally
- **THEN** transcription runs without any network request other than an initial weight download, and the resulting SRT passes `l2n check transcribe`

#### Scenario: Engine list

- **WHEN** `l2n transcribe --list-engines` is run
- **THEN** the command prints one line per engine with name, local, needs_gpu, native_timestamps, and whether its dependencies are currently satisfied

### Requirement: Cloud engines are gated

Any engine whose metadata declares local=false SHALL be refused unless `--allow-cloud` is passed. The package itself MUST NOT ship any engine with local=false; the gate exists for third-party plugins.

#### Scenario: Cloud engine without explicit consent

- **WHEN** a plugin engine with local=false is selected without `--allow-cloud`
- **THEN** the command prints a message stating that non-local engines require `--allow-cloud` because of the local-processing privacy rule, and exits 2

### Requirement: Model conversion helper for Breeze-ASR-25

`l2n convert-model` SHALL convert the Breeze-ASR-25 Hugging Face checkpoint to CTranslate2 format (float16 by default) into a user-specified or default directory, print the expected disk usage before starting, and refuse to overwrite an existing target directory unless `--force` is given.

#### Scenario: Conversion produces a usable engine

- **WHEN** `l2n convert-model --output ~/.lecture2notes/models/breeze-asr-25-ct2` completes with exit 0
- **THEN** `l2n transcribe video.mp4 --lang zh` (default engine) locates that directory and transcribes without further configuration

### Requirement: Raw transcript and correction sidecar are preserved

When correction tables are applied, the system SHALL write the uncorrected transcript to `<stem>.raw.srt` and a sidecar `<stem>.corrections.json` listing every replacement as heard, correct, count, source. The corrected `<stem>.srt` MUST keep cue numbering, timing, and blank-line structure identical to the raw file.

#### Scenario: Corrections are auditable

- **WHEN** a correction table replaces "口拍的" with "Copilot" 12 times
- **THEN** `<stem>.corrections.json` contains an entry with heard "口拍的", correct "Copilot", count 12, and `<stem>.raw.srt` still contains the original text

### Requirement: Hallucination loop detection

After transcription the system SHALL scan cues; a run of 30 or more consecutive cues with identical text SHALL be reported as a hallucination loop warning naming the first and last cue numbers.

#### Scenario: Repeated cue tail

- **WHEN** the last 71 cues of a transcript all contain the text "OK"
- **THEN** `l2n check transcribe` reports `warning: hallucination loop cues N..M (71 identical)` and exits 1

### Requirement: Official subtitle offset calibration

`l2n calibrate-subs <video> <subtitle>` SHALL measure the time offset between an official VTT or SRT file and the video by transcribing probe windows and matching them against the subtitle text, then write a time-shifted copy without altering any subtitle text.

Measurement rules:
- At least 3 probe windows of 90 seconds each, positioned at 300 seconds, at the midpoint, and at 92 percent of the duration by default; `--probes` SHALL override count and positions.
- Each probe cue is matched to the subtitle corpus by longest common substring; matches shorter than max(8, half the cue length) are discarded.
- The matched position is interpolated inside the matched subtitle cue by character ratio.
- Each probe reports the median offset of its accepted matches; a probe with fewer than 3 accepted matches is discarded.
- If fewer than 3 probes survive, no output file is written and the command exits 2.
- A least-squares line offset(t) = a + b*t is fitted through the probe medians; every cue start and end is shifted by subtracting offset(t).
- Shifted times below zero are clamped to zero; a cue whose end is not later than its start after shifting SHALL be extended to start + 0.3 seconds.

Outputs: `<stem>.srt` (calibrated), `<stem>.official.srt` (original converted to SRT), `<stem>.offset.json` with probes[] (at_sec, n_points, median_offset, min, max), fit (a, b), drift (true when the range of probe medians is 1.5 seconds or more).

#### Scenario: Constant offset

- **WHEN** the three probe medians are +1.44, +0.80, +0.96 seconds
- **THEN** drift is false, and a cue originally at 00:00:01.000 --> 00:00:03.000 is written with both times reduced by offset(t) evaluated at the cue start and end respectively

#### Scenario: Drift is flagged

- **WHEN** the probe medians are +3.14, +2.23, +0.86 seconds
- **THEN** drift is true, the fitted b is negative, and the report prints the range 2.28 seconds

##### Example: linear fit on synthetic drift

- **GIVEN** probe medians (300, 3.0), (5700, 2.0), (10500, 1.0)
- **WHEN** the fit is computed
- **THEN** a is within 0.05 of 3.06 and b is within 0.000005 of -0.000196

#### Scenario: Text is never modified

- **WHEN** calibration completes
- **THEN** concatenating the text lines of `<stem>.srt` equals concatenating the text lines of `<stem>.official.srt`
