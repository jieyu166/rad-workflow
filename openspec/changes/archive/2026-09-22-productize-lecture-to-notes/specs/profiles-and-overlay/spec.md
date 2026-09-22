## ADDED Requirements

### Requirement: Layered configuration resolution

The effective configuration SHALL be resolved from these layers, highest precedence first: CLI arguments; the project overlay directory `.lecture2notes/` in the current working directory; the user overlay directory `~/.lecture2notes/`; the named profile directory `profiles/<name>/` inside the package (selected by `--profile`, then by the key `profile` in a higher layer, defaulting to generic); the package built-in defaults. A layer that lacks a given file contributes nothing for that file.

Overlay-able files are exactly: `note.frontmatter.yaml`, `note.template.md`, `corrections.json`, `outputs.toml`, `privacy.toml`. Template files replace lower layers entirely; `corrections.json` and `outputs.toml` and `privacy.toml` merge key by key with the higher layer winning.

#### Scenario: Project overlay wins over user overlay

- **WHEN** `~/.lecture2notes/outputs.toml` sets note.style = "faithful" and `./.lecture2notes/outputs.toml` sets note.style = "concise"
- **THEN** `l2n profile show` reports note.style = concise with source layer project

#### Scenario: Corrections merge

- **WHEN** the radiology profile maps "空中馬來西亞" to "chondromalacia" and the user overlay maps "口拍的" to "Copilot"
- **THEN** both replacements are active, and a user overlay entry for "空中馬來西亞" would override the profile's value

### Requirement: Built-in profiles

The package SHALL ship `profiles/generic` (default) and `profiles/radiology`. The generic profile SHALL set note.style = concise, pbf = false, hub = true, a frontmatter template limited to title, date, source, tags, and a corrections table containing only general technology terms authored for this project. The radiology profile SHALL add a reading-case callout template, a radiology corrections table, and privacy patterns for patient identifiers, and SHALL NOT be active unless selected.

#### Scenario: Default profile

- **WHEN** no `--profile` and no overlay specify a profile
- **THEN** `l2n profile show` reports profile = generic with source layer builtin

#### Scenario: No ZeroType-derived entries

- **WHEN** the shipped corrections tables are inspected
- **THEN** no entry carries a source value referencing ZeroType or USER.md

### Requirement: Effective configuration is inspectable

`l2n profile show` SHALL print every effective key with its value and the layer it came from (cli, project, user, profile, builtin), and `l2n profile show --json` SHALL emit the same as a JSON object keyed by setting name with fields value and source.

#### Scenario: JSON inspection

- **WHEN** `l2n profile show --json` runs
- **THEN** the output parses as JSON and contains an entry for note.style with fields value and source

### Requirement: Invalid overlay files fail loudly

A malformed overlay file SHALL cause the command to print the file path and line number of the parse error and exit 2 without applying any part of that file or any lower-precedence value for the keys it would have set.

#### Scenario: Broken TOML

- **WHEN** `./.lecture2notes/outputs.toml` contains a syntax error on line 7
- **THEN** any subcommand that resolves configuration prints the path and `line 7` and exits 2

### Requirement: Minimal overlay example ships with the repository

The repository SHALL contain `examples/overlay-minimal/` with one valid instance of each overlay-able file using placeholder content, and the README SHALL describe how to copy it to `~/.lecture2notes/`.

#### Scenario: Example overlay is valid

- **WHEN** `examples/overlay-minimal/` is copied to `~/.lecture2notes/` and `l2n profile show` runs
- **THEN** every key defined in the example is reported with source layer user and no parse error occurs
