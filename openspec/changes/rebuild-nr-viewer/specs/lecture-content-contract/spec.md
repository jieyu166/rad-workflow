## ADDED Requirements

### Requirement: Canonical lecture schema and normalization
The system SHALL normalize legacy lecture JSON into one canonical segment shape containing `start_sec`, `end_sec`, `title`, `summary_zh`, `takeaways_zh`, `editorial_notes_zh`, and `frames`. Each formal frame SHALL contain `time`, `ocr`, and a safe course-relative `path`; JSON writes SHALL use UTF-8 and atomic replacement.

#### Scenario: Legacy content is normalized without losing timing
- **WHEN** a lecture contains start/end aliases, legacy bullets, string frame paths, or legacy OCR maps
- **THEN** the normalized result uses only canonical fields and retains the exact original segment time signature

#### Scenario: Unsafe frame data is reported structurally
- **WHEN** a frame has an absolute or parent-traversing path, a non-finite or out-of-range time, a non-string OCR value, or a missing file
- **THEN** validation returns structured findings for every detected error without crashing on the first malformed frame

### Requirement: Chapter timing is immutable
Every rewrite, render, audit, and publication input SHALL preserve the source segment count and every exact start/end pair. A changed count or time SHALL be a hard failure before formal output or publication.

#### Scenario: A rewritten end time differs
- **WHEN** segment 3 changes from end time `120.0` to `120.1`
- **THEN** the system rejects the lecture and identifies segment 3 as the changed range

### Requirement: Focused Traditional Chinese content
Each segment SHALL have a title that identifies one diagnosis, finding, anatomy, or reading task; a `summary_zh` containing 250–600 Han characters in one or two paragraphs; exactly four non-empty distinct `takeaways_zh`; and a list-valued `editorial_notes_zh`. Content SHALL use Traditional Chinese Taiwan terminology and SHALL NOT contain Simplified Chinese-only characters, unfinished markers, template prompts, empty titles, generic chapter labels, or excessive verbatim transcript copying.

#### Scenario: Valid focused chapter content passes
- **WHEN** a segment has a focused medical title, a 250–600 character structured summary, four distinct takeaways, and valid editorial notes
- **THEN** content validation returns no error findings

#### Scenario: Invalid count and unfinished content fail
- **WHEN** a segment has three takeaways or contains an unfinished marker or template prompt
- **THEN** validation returns blocking findings for every violated rule

### Requirement: Speaker content and editorial knowledge remain separated
`summary_zh` and `takeaways_zh` SHALL contain only source-confirmed speaker content reorganized or paraphrased for clarity. For evidence coverage, each segment's complete `summary_zh` SHALL be one speaker claim clause and each of its exactly four indexed `takeaways_zh` SHALL be one speaker claim clause. General background, modern classification, extra differential diagnosis, or teaching guidance not explicitly stated by the speaker SHALL appear only in separately labeled `editorial_notes_zh`. Editorial notes SHALL NOT be speaker claim clauses, citations, or support for case claims. The system SHALL NOT invent patient history, imaging findings, diagnoses, or other case-specific facts.

#### Scenario: Editorial note remains separate
- **WHEN** a segment contains a source-supported summary and four source-supported takeaways plus an editorial note with modern teaching guidance
- **THEN** the system keeps the note labeled under `editorial_notes_zh`, excludes it from the five speaker claim clauses, and rejects any attempt to cite the note as support for a case claim

#### Scenario: Review confirms source boundaries without text equality
- **WHEN** a rewrite paraphrases source-supported speaker content and keeps additional knowledge only in `editorial_notes_zh`
- **THEN** source-boundary validation evaluates the five claim attestations and does not require exact or fuzzy equality between the claim and source text

### Requirement: Claim-level trusted evidence and human support attestation
Every segment SHALL provide complete evidence coverage for its five speaker claim clauses: the whole `summary_zh` and each of the exactly four indexed `takeaways_zh`, including clauses copied unchanged from legacy `existing_content`. Every clause SHALL cite one or more trusted transcript paragraphs or externally trusted canonical frame sources. A transcript citation SHALL resolve by stable paragraph identity and SHA-256 to a trusted transcript source represented by the approved evidence packet. A frame citation SHALL resolve by stable frame identity, asset/source hashes, and allowed citation type to an independently trusted external canonical frame manifest. A hash stored only inside the evidence packet SHALL prove packet integrity only and SHALL NOT establish source authenticity.

Every clause SHALL have one human source-support attestation that binds the validator-recomputed normalized claim SHA-256, the complete ordered set of trusted citation identities and hashes, the evidence packet SHA-256, the approved content SHA-256, a non-empty reviewer identity, and explicit `support_confirmed=true`. The mechanical validator SHALL verify clause coverage, citation existence and allowed types, trusted external source resolution, hashes and digests, reviewer identity, confirmation, and all attestation bindings. It MUST NOT treat exact matching, fuzzy matching, or unchanged legacy text as proof of semantic equivalence or source support. A missing citation, missing attestation, untrusted source, unsupported citation type, incomplete clause set, or binding mismatch SHALL fail closed. Findings SHALL identify only segment identity, clause identity, field, and error code and SHALL NOT echo sensitive claim or source text.

#### Scenario: Supported paraphrase with bound transcript attestation passes
- **WHEN** a paraphrased `summary_zh` cites trusted transcript paragraph `p-0042`, the citation paragraph hash resolves in the approved packet, and a named reviewer confirms support with matching claim, citation-set, packet, and approved-content hashes
- **THEN** claim-level validation accepts the summary without requiring clause equality to paragraph `p-0042`

#### Scenario: Exact unchanged legacy clause without citation fails
- **WHEN** a takeaway is byte-for-byte identical to legacy `existing_content` but has no trusted citation or source-support attestation
- **THEN** claim-level validation rejects that takeaway as `missing_citation` and `missing_attestation`

#### Scenario: Unrelated citation and attestation mismatch fail
- **WHEN** a takeaway cites an existing trusted paragraph that the reviewer did not bind to that claim, or the attestation citation set differs from the clause citation set
- **THEN** claim-level validation rejects the clause with a binding error and does not infer semantic support from citation existence

#### Scenario: Missing clause coverage fails
- **WHEN** a segment supplies valid attestations for its summary and only three of its four indexed takeaways
- **THEN** claim-level validation rejects the segment and identifies the uncovered takeaway identity without reproducing its text

#### Scenario: Trusted frame citation with external manifest passes
- **WHEN** a claim cites canonical frame `frame-017`, its allowed type and asset/source hashes match an independently trusted external canonical frame manifest, and the reviewer attestation binds that citation to the approved claim and packet digests
- **THEN** claim-level validation accepts the frame citation as trusted support

#### Scenario: Packet-only forged frame source fails
- **WHEN** a packet contains a self-consistent frame identity and hashes but no matching entry in an independently trusted external canonical frame manifest
- **THEN** claim-level validation rejects the frame citation as an untrusted source even though the packet hash is internally valid

#### Scenario: Reviewer confirmation type or hash tamper fails closed
- **WHEN** any bound reviewer identity, `support_confirmed` value, citation type, citation hash, normalized claim hash, evidence packet digest, or approved content digest is missing or changed after approval
- **THEN** claim-level validation rejects the affected clause without emitting sensitive claim or source text

### Requirement: Evidence-bound and privacy-gated rewrite
The system SHALL build one SHA-256-bound evidence packet per segment from trusted transcript paragraphs, selected frame references, timing, and existing content. The approved rewrite digest and claim attestations SHALL bind the reviewed output to that packet without granting automatic trust to `existing_content` or packet-internal frame assertions. Manual reviewed import SHALL be the default rewrite provider. External LLM generation SHALL remain disabled unless the operator supplies the explicit allow flag, the exact confirmation string `TEXT-EVIDENCE-ONLY`, and a full outbound-payload sensitive-data scan returns clean; credentials SHALL come only from environment or official SDK resolution, images and original files SHALL NOT be uploaded, and generated candidates SHALL NOT be applied before human review.

#### Scenario: External generation lacks explicit permission
- **WHEN** an operator requests the external provider without the allow flag or exact confirmation string
- **THEN** the request fails before a network call

#### Scenario: Sensitive evidence blocks external generation
- **WHEN** the outbound packet contains a medical record number, birth date, phone number, national identifier, email, or another configured sensitive pattern
- **THEN** external generation is rejected and manual or local review remains available
