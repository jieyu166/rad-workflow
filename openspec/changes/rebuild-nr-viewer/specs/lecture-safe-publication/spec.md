## ADDED Requirements

### Requirement: Live replacement probe is explicit and disposable
Preflight SHALL remain read-only unless the operator supplies the live-replace probe flag and exact course confirmation. The probe SHALL create uniquely named disposable files under live and staging roots, verify create/read/SHA-256/cross-root `os.replace`/cleanup with all handles closed, and SHALL NOT use formal course names. Publication SHALL require a passing probe-backed receipt.

#### Scenario: Probe is not authorized
- **WHEN** preflight runs without the opt-in flag or exact course ID confirmation
- **THEN** no live probe file is created and publication remains blocked

### Requirement: Publication receipt is bound to roots, sources, and run
Before any lecture manifest is built, publication SHALL verify a passing `preflight.json` whose course, staging, and backup roots, expected count, source full-content hashes, `replace_probe_passed`, run ID, and `course-run.json` SHA-256 match the current staged run. A missing, unbound, stale, or changed receipt SHALL fail before live modification.

#### Scenario: Source changes after preflight
- **WHEN** an SRT byte changes after receipt binding
- **THEN** publication rejects the source inventory before manifest creation

### Requirement: Backup and run identities use sortable local timestamps
Every publication run ID SHALL begin with the local wall-clock timestamp captured at run creation in exact `YYYYMMDD-HHMMSS` format. The backup directory or backup name for that run SHALL include the identical run ID. If that timestamp already exists under the selected backup root, the system SHALL append the lowest available decimal collision suffix beginning with `-01` and increasing deterministically (`-02`, `-03`, and so on); arbitrary non-temporal identifiers SHALL NOT satisfy the run ID or backup naming contract. The preflight receipt, `course-run.json`, every lecture and homepage manifest, and external recovery evidence SHALL record the resolved run ID and backup path so the backup remains traceable across publication and recovery.

#### Scenario: Timestamped backup path is created
- **WHEN** a run is created at local time 2026-08-09 14:05:07 and no matching backup name exists
- **THEN** its run ID is exactly `20260809-140507`, its backup directory or name contains `20260809-140507`, and the receipt, run record, manifests, and recovery evidence fields use that same identity and path

#### Scenario: Same-second backup name collides
- **WHEN** backup names `20260809-140507` and `20260809-140507-01` already exist for a run created in that same local second
- **THEN** the system deterministically resolves both the run ID and backup directory or name to `20260809-140507-02` before writing publication state

#### Scenario: Non-temporal run ID is supplied
- **WHEN** an operator or resumed state supplies run ID `nr-final` even if its roots and hashes otherwise match
- **THEN** preflight or publication rejects it before backup creation or live modification

### Requirement: Each lecture publishes as one manifested transaction
A lecture transaction SHALL include its JSON, viewer, PBF, `.v4.md`, selected frame assets, and audit report. The manifest SHALL record named live, immutable staged, backup paths, old existence/hash, new hash, state, verified hash, errors, rollback errors, and persistence errors. Existing files SHALL be backed up and hash-verified before replacement. Each replacement SHALL copy immutable staging to a sibling live temporary file and use `os.replace`; `shutil.move` SHALL NOT be the commit primitive.

#### Scenario: All replacements succeed
- **WHEN** every staged file exists, every backup verifies, every live replacement hash matches, and manifest writes succeed
- **THEN** the lecture manifest reaches `committed` and immutable staging remains available

### Requirement: Any lecture replacement failure triggers whole-lecture rollback
If any backup, manifest persistence, temporary copy, replace, or verification step fails, the publisher SHALL stop that lecture, restore every previously existing file to its recorded old hash in reverse order, delete every live file created solely by the transaction, and verify the restored state. A failed publication SHALL stop the same publication invocation even when rollback completes, and later lectures plus the homepage SHALL remain untouched.

#### Scenario: Middle file replacement fails
- **WHEN** the second file replacement fails after the first file changed
- **THEN** both files end in their complete old state, transaction-created assets are absent, the failure and rollback outcome are recorded, and no later lecture manifest is built

### Requirement: Recovery evidence survives manifest persistence failure
If the transaction directory cannot persist state, the system SHALL perform best-effort rollback and SHALL write recovery evidence outside that transaction directory under the backup recovery root. Unverified rollback SHALL mark `recovery_required`, preserve backup and staging evidence, surface both original and rollback errors verbatim, and block homepage publication.

#### Scenario: Transaction directory becomes read-only
- **WHEN** manifest persistence fails during publication
- **THEN** old live hashes are restored when possible and an external recovery JSON records entries, original error, persistence errors, and rollback status

### Requirement: Homepage publishes last as an independent transaction
The course homepage SHALL remain unchanged until exactly 11 unique lecture manifests from the same run are committed, every current live hash matches its manifest, post-publish smoke/E2E passes, and course audit is `ok=true`. The homepage SHALL then be generated from canonical staged outputs, backed up, and replaced as one independent single-file transaction. Homepage rollback SHALL NOT alter lecture files.

#### Scenario: One lecture is failed or rolled back
- **WHEN** fewer than 11 manifests are committed or any lecture audit is not passing
- **THEN** homepage generation or publication is rejected and the old homepage hash remains unchanged

### Requirement: NAS operations and cleanup require separate authorization
Application work SHALL NOT access or modify the NAS course, execute long real-course processing, publish, roll back, or delete retained backups unless the user provides explicit authorization for that operational phase. Staging, backups, manifests, audit instances, rewrites, transcripts, frames, sensitive data, and NAS outputs SHALL remain outside Git.

#### Scenario: Apply completes without rollout authorization
- **WHEN** implementation and automated verification are complete but no NAS authorization exists
- **THEN** the system stops at the documented execution handoff and performs no NAS operation
