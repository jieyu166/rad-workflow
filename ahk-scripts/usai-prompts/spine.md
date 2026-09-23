# Spine X-ray Reporting Prompt — Landmark JSON and Report

Draft a Spine X-ray report from the supplied images. Apply only sections supported by the provided views; examples illustrate wording, not findings to copy.

Output SPINE_JSON followed by REPORT as specified below. Use TELEGRAPHIC DIAGNOSTIC style inside REPORT.

FINAL REPORT RULES:
- NO Markdown formatting or code fences in either output section; JSON punctuation is required in SPINE_JSON.
- Outside REPORT, output only the requested SPINE_JSON data, measurements and concise limitations; no hidden reasoning or teaching commentary.
- Each finding on its own line.
- Spine findings and non-spine incidental findings separated by ONE blank line.
- Use concise conventional radiology wording.
- Do NOT fabricate uncertain findings.
- Apply each finding-specific reporting threshold below. When visibility prevents assessment, state the limitation; do not substitute a negative finding.
- When a subtle abnormality is suspicious but not definite, use cautious wording rather than falsely reporting a normal study.

=== LANDMARK JSON WORKFLOW — ADULT LUMBAR LATERAL VIEWS ===

Perform: image/view identification -> vertebral numbering -> observed six-point landmarks -> JSON measurements -> cross-view comparison when eligible -> clinical report.
These are observable data outputs, not a request for hidden chain-of-thought. Do not create coordinates to justify a preselected diagnosis. This workflow takes precedence over conflicting geometric shortcuts or example numbers below.

OUTPUT CONTRACT:
Return exactly these two labeled sections, without Markdown fences:
SPINE_JSON:
One valid JSON object (double quotes, no comments, no NaN/Infinity).
REPORT:
The plain-text radiology report in the format below.
Report-only examples below illustrate ONLY the REPORT section. Never omit SPINE_JSON.
The JSON is a review artifact, not an automatically saved file or a verified spinal-annotation-web v2.3 export. Do not claim software execution, file saving, physician review, or original-image hashes that were not supplied.

JSON CONTRACT (all numeric outputs are numbers or null):
Top level: schemaVersion="usai-spine-landmarks-1.1", physicianReviewed=false, imageMode, images=[], dynamicComparisons=[], limitations=[].
For each supplied image include:
  imageId (image_1, image_2 in input order), view (AP/lateral/flexion/extension/unknown), viewEvidence,
  temporalRole (current/previous/unknown according to image mode),
  coordinateSystem (original_pixels/display_pixels/unavailable), width, height,
  pixelSpacingMm (null or {x,y,source}), anteriorDirection (left/right/unknown),
  numberingStatus (confirmed/assumed/uncertain), numberingBasis, vertebrae=[], segments=[], limitations=[].
For each visible vertebra include:
  id (stable visible ordinal), level (null if uncertain), status (measurable/partial/unassessable),
  points={anteriorSuperior,middleSuperior,posteriorSuperior,anteriorInferior,middleInferior,posteriorInferior},
  each point is {x,y} or null; uncertainPoints=[], limitations=[],
  metrics={measurementMethodId:"VERTEBRAL_HEIGHT_AVERAGE_AXIS_V1",anteriorHeight,middleHeight,posteriorHeight,heightUnit,HaHp,HmHp,HmMeanEnds},
  morphology={anteriorWedging,biconcave,crush,fractureAssessment,visualEvidence}.
Morphology flags are true/false/null; fractureAssessment is suspected/supported/not_identified/indeterminate, never inferred from a ratio alone.
For each assessable adjacent segment include:
  upperId, lowerId, level, status, calculationMethod="LUMBAR_LOCAL_GEOMETRY_V2", discHeightMethod="DISC_HEIGHT_AVERAGE_AXIS_V1",
  signedSlipPercent, signedSlipMm, segmentAngleDeg,
  discAnteriorHeight, discMiddleHeight, discPosteriorHeight, heightUnit,
  listhesisDirection (anterior/posterior/none/indeterminate),
  discNarrowing (present/absent/indeterminate), visualEvidence, limitations=[].
For each eligible matched pair of motion segments include:
  level, imageIds, status (assessable/indeterminate/not_applicable),
  angle1Deg, angle2Deg, signedAngularChangeDeg, angularChangeDeg,
  signedSlip1Percent, signedSlip2Percent, signedTranslationChangePercentagePoints, translationChangePercentagePoints, translationChangeMm,
  criteria={criterionId,criterionVersion,name,source,measurementMethodId,viewProtocol,population,levels,approvalStatus,angularThresholdDeg,translationThresholdMm,translationThresholdPercentagePoints,operator,combinationRule},
  angularHypermobility, translationalHypermobility, overallHypermobility (true/false/null), limitations=[].
Do not use zero for missing data. Retain unassessable visible levels and reasons rather than dropping difficult cases. AP images have no lateral six-point metrics. For ineligible pairs dynamicComparisons may be empty with the reason in top-level limitations.

COORDINATES AND LANDMARKS:
- Origin is the top-left of the identified image canvas; x increases rightward, y downward. Use actual supplied image dimensions. Do not guess original dimensions from a resized preview.
- Use original_pixels only if original dimensions and any crop/resize mapping are known. Otherwise use known display_pixels with its actual canvas dimensions. If neither canvas is established, use unavailable, null points/metrics, and describe visible findings qualitatively.
- Do not calculate angles on independently normalized x/y coordinates without restoring aspect ratio. If pixel aspect ratio is unknown or distorted, angular and geometric measurements are indeterminate.
- Use the visible endplate/body junction at the anterior and posterior margins, excluding projecting osteophyte tips. This is the project's annotation convention. If the underlying junction is obscured, mark the point null/uncertain rather than inventing it.
- Mark MS/MI at the 50% AP station of its own endplate corner chord: follow the perpendicular through the chord midpoint to the actual cortical contour. Do not simply use the chord midpoint, interpolate the contour from corners, or move to the deepest focal depression. If the contour cannot be resolved, use null. Record eccentric depression/double contours separately; six points cannot represent the whole contour.
- Infer anatomical anterior/posterior from anatomy/labels, not image-left/right alone. Do not fabricate hidden points behind implants. Keep partial boundary vertebrae with only visible endplate points.
- Number visible lower thoracic vertebrae too. The lowest visible rib-bearing vertebra is not automatically T12; restricted field of view and transitional anatomy may require assumed numbering.

GEOMETRY (engineering measurement convention, not a universal clinical definition):
- Coordinates remain in the documented pixel canvas. For geometry, use an undistorted metric with known pixel aspect ratio. Output mm only when supplied calibration is reliable for the object plane AND current crop/resize; detector spacing alone does not establish object-plane scale. Otherwise report pixel lengths, ratios and angles as supported; never infer mm from average body size or screen DPI.
- For each vertebra, e=unit(unit(AS-PS)+unit(AI-PI)). Choose perpendicular n so dot(n,(AS+PS)/2-(AI+PI)/2)>0 (cranial). Ha=dot(AS-AI,n), Hm=dot(MS-MI,n), Hp=dot(PS-PI,n). Require positive heights; HaHp=Ha/Hp, HmHp=Hm/Hp, HmMeanEnds=Hm/((Ha+Hp)/2). Null only dependent results for missing points. S1 may have only its superior endplate; do not fabricate S1 inferior points or apply lumbar-body fracture ratios to S1.
- At each disc, let U be the upper vertebra and L the lower. eL=unit(L.AS-L.PS), pointing anatomically anterior. Signed slip s=dot(U.PI-L.PS,eL). W=norm(L.AS-L.PS); signedSlipPercent=100*s/W. Positive=anterolisthesis; negative=retrolisthesis. signedSlipMm is s only in calibrated mm; otherwise null. Do not substitute global horizontal x shift.
- eU=unit(U.AI-U.PI). Set gap=(U.AI+U.PI)/2-(L.AS+L.PS)/2. Choose nL perpendicular to eL with dot(nL,gap)>0 (cranial/disc side). segmentAngleDeg=degrees(atan2(dot(eU,nL),dot(eU,eL))); lordotic opening is positive. This anatomical construction handles screen y-down and mirrored canvases when landmark semantics remain correct. If normal sign is ambiguous, angle=null.
- Disc AP axis eD=unit(eU+eL); choose perpendicular nD with dot(nD,gap)>0. Disc heights: HA=dot(U.AI-L.AS,nD), HM=dot(U.MI-L.MS,nD), HP=dot(U.PI-L.PS,nD). These are normal-projected paired-point heights using the average endplate axis. Nonpositive heights trigger geometry_invalid_or_projection_ambiguous; never clamp to zero or diagnose narrowing from this alone. Preserve an invalid signed value for audit with status=indeterminate; do not use it in a diagnostic rule.
- Measurements must be consistent with the output points and method. Use a calculation tool if actually available; do not claim tool-verified arithmetic otherwise. Do not attach invented decimal precision to poorly localized landmarks. Never replace an unavailable calculation with an eyeballed numerical angle.

- Guard every normalization and division against zero/degenerate length and nearly opposed endplate vectors. Undefined axes make dependent metrics null. These local methods are engineering conventions, not validated Dupuis, Frobin/DCRA or Genant implementations. Record method IDs; do not mix their results with thresholds derived using incompatible methods.

MORPHOLOGY AND REPORTING:
- Preserve the existing >5% static slip reporting threshold below as a LOCAL reporting preference, not a universal diagnostic cutoff or a dynamic-motion threshold. Near-threshold or uncertain measurements remain indeterminate.
- Ha/Hp <0.8 and Hm/Hp <0.8 are geometric flags for anterior wedging and central height loss, respectively, not sufficient diagnoses of compression fracture or complete Genant grading. Inspect endplate/cortical morphology and non-fracture mimics. Record visually suspicious deformity even when a ratio cannot be calculated.
- Generalized height loss requires a suitable reference; posterior/anterior ratio alone cannot establish crush, and height loss alone cannot establish burst fracture. Do not assign fracture age from these points.
- Assess narrowing using measured heights together with level, projection, adjacent diseased levels, and degenerative signs. Do not introduce an unsupported universal percentage cutoff or diagnose narrowing from intersecting lines alone.
- No-mm calibration does not prevent a reliable angle or proportion, but prevents an absolute-mm criterion.

TWO-IMAGE COMPARISON AND HYPERMOBILITY:
- Two images alone are insufficient: verify same patient/exam, matched vertebral numbering and a true flexion-extension pair. Honor image-mode instructions: previous/current is temporal comparison, AP+lateral is multi-view assessment, neither establishes flexion-extension motion.
- Labels or supplied acquisition information should establish flexion/extension; differing lordosis alone is suggestive, not conclusive. Record unknown view when unverified.
- Compare per-image JSON segment metrics for the SAME anatomical segment, not raw point coordinates from two different canvases. Do not subtract global lordosis angles to obtain segmental motion.
- Directed-angle difference: wrapSigned180(a)=((a+180) modulo 360)-180, using a NONNEGATIVE modulo. signedAngularChangeDeg=wrapSigned180(angle2-angle1); angularChangeDeg=abs(signedAngularChangeDeg). Here 180 names the output range, not a modulo-180 operation. -6 to +6 gives +12 degrees; the reverse gives -12. Posterior-to-anterior endpoints fix direction: a near-180-degree reversal is a landmark/orientation QA failure, not motion to silently fold away.
- signedTranslationChangePercentagePoints=signedSlipPercent_2-signedSlipPercent_1; translationChangePercentagePoints=abs(signedTranslationChangePercentagePoints). +5% to -3% gives -8 signed and 8 absolute percentage points, not 8% relative change. Never subtract unsigned magnitudes or import the static 5% threshold into dynamic assessment.
- translationChangeMm=abs(signedSlipMm_2-signedSlipMm_1) only with reliable comparable calibration for both views; otherwise null. Never subtract raw pixels across different images.
- Hypermobility criteria MUST be explicitly approved and method-compatible: criterion ID/version, source, measurement method, view protocol, population, levels, thresholds/operators and AND/OR logic form an inseparable package. If any required compatibility information is missing or incompatible, flags=null with a reason. Do not apply healthy/degenerative/unoperated adult criteria to cervical, pediatric, traumatic or postoperative fusion assessment. Do not convert between mm and percentage thresholds without the criterion explicitly permitting it.
- DEFAULT: no approved hypermobility threshold is supplied by this prompt. Output available motion measurements, criteria fields=null, hypermobility flags=null, and state that threshold-based classification is indeterminate. The examples below do not authorize a threshold.
- If an approved criterion is provided, evaluate angular and translational components separately; overall assessment is true only when the specified rule is met with adequate data, false only when sufficient reliable evidence excludes all components required by that rule, otherwise null.
- Inadequate flexion/extension effort, mismatched positioning, rotation, obscured landmarks or uncertain levels prevent a reassuring negative statement. Reduced observed motion cannot by itself exclude instability. Static slip alone does not prove dynamic instability.
- Record measured residual motion at instrumented levels in JSON even if the report omits clinically unimportant static slip. Motion or implant abnormalities require review, not automatic attribution to fusion failure.

MEASUREMENT / RULE / DIAGNOSIS SEPARATION:
- Continuous signed displacement describes geometry, not disease. listhesisDirection indicates geometric direction; reporting still uses the explicit local policy and visibility assessment.
- Clinical instability, symptoms and fusion indications cannot be concluded from a motion threshold alone. Fracture statements remain image-based draft interpretations for physician review, never outputs of height ratios alone.
- No universal disc-narrowing cutoff or validated retrolisthesis severity scale is introduced. Preserve existing local descriptive preferences as local policy only.
- Any example coordinates and measurements are illustrative unless independently recalculated. Never copy sample numbers into a case.

FINAL CONSISTENCY CHECK:
Include every supplied image, preserve identifiers and view order, verify coordinate bounds and anatomical point order, null invalid calculations, and ensure REPORT does not contradict JSON. A qualitative finding may be reported with its measurement limitation. JSON coordinates/metrics are AI estimates pending physician review, not independently validated measurements.

=== OUTPUT FORMAT (REPORT SECTION ONLY) ===

First line:
L-S Spine ({views}):

View labels:
- Single lateral = (Lat.)
- AP + lateral = (AP+Lat.)
- AP + flexion + extension = (AP+Flex.+Ext.)
- Flexion + extension only = (Flex.+Ext.)

Recommended finding order:

For neutral / lateral studies:
  1. Compression fracture / acute osseous finding
  2. Postoperative change / hardware
  3. Spondylolisthesis / retrolisthesis / pars defect
  4. Degenerative disc disease / disc space narrowing
  5. Spondylosis
  6. Facet joint arthrosis
  7. Baastrup disease
  8. Loss of lordosis / hyperlordosis
  9. Bone density
  10. [blank line]
  11. Incidental findings

For flexion-extension studies:
  1. Compression fracture / acute osseous finding
  2. Postoperative change / hardware
  3. Dynamic instability / hypermobility
  4. View-dependent or static spondylolisthesis / retrolisthesis
  5. Degenerative disc disease / disc space narrowing
  6. Spondylosis
  7. Facet joint arthrosis
  8. Baastrup disease
  9. Bone density
  10. [blank line]
  11. Incidental findings

Incidental examples:
- Intimal calcification of aorta.
- Mild increased bowel gas.
- Renal stone.
- Pelvic phleboliths.

=== GENERAL REPORTING PRINCIPLES ===

- Use only findings supported by the supplied image(s).
- Do NOT force a diagnosis when visibility is inadequate.
- Do NOT over-report minimal alignment variation caused by projection or positioning.
- Do NOT use implant brand names unless explicitly requested or clinically important.
- Generic descriptions such as "posterior instrumental fixation", "interbody fusion", "interbody cage", and "cement augmentation" are sufficient.
- In postoperative spines, prioritize clinically meaningful instability, adjacent-segment disease, and hardware complications rather than emphasizing harmless residual deformity.
- If a fused/instrumented level has residual static spondylolisthesis but fixation is intact and there is no dynamic instability, interval worsening, or hardware complication, the residual slip does NOT need to be routinely reported.
- Adjacent-level listhesis should still be assessed and reported normally.

=== PHASE 0: VERTEBRAL COUNTING — DO THIS FIRST, EVERY TIME ===

- Determine vertebral numbering BEFORE assigning any abnormality to a level.
- Prefer two anchors whenever possible:
  1. Thoracolumbar junction / lowest rib-bearing vertebra.
  2. Sacrum / lumbosacral junction.

Counting from above:
- Identify T12 only when numbering anchors support it; the lowest visible rib-bearing vertebra alone is insufficient in a cropped image.
- Vertebra directly below T12 = L1.
- Count downward:
  L1 -> L2 -> L3 -> L4 -> L5.
- Confirm L5 by identifying the sacrum below it.

Counting from below:
- If ribs are cropped or difficult to identify, locate the sacrum first.
- Count upward:
  L5 -> L4 -> L3 -> L2 -> L1.

Transitional anatomy:
- Check for lumbosacral transitional vertebra before assigning levels.
- Do NOT use surgical hardware position alone to determine numbering.
- If thoracolumbar and lumbosacral landmarks cannot both be confidently assessed, avoid overconfident numbering.
- If transitional anatomy is suspected, use cautious numbering rather than forcing a level.

VISIBLE LOWER THORACIC SPINE:
- Do NOT restrict evaluation to L1-L5.
- Inspect EVERY visible vertebral body, including visible lower thoracic levels such as T8-T12.
- Compression deformities in visible lower thoracic vertebrae must not be ignored.

Common error:
- Assigning a lumbar level without first confirming the rib-bearing vertebra or sacrum.

=== PHASE 1: SYSTEMATIC CHECKLIST — LATERAL VIEW ===

[A: LORDOSIS]

Reference:
- Cobb angle from T12 inferior endplate to L5 inferior endplate.

Approximate interpretation:
- <20 degrees = loss of lordosis.
- 20-45 degrees = normal; do NOT report.
- >45 degrees = hyperlordosis.

Important:
- Precise angle measurement is unreliable by visual inspection.
- Only report loss of lordosis when the spine is clearly straightened or kyphotic.
- Only report hyperlordosis when clearly excessive.
- When uncertain, do NOT report.

[B: COMPRESSION FRACTURE — HIGHEST PRIORITY]

- Deliberately inspect EVERY visible thoracic and lumbar vertebral body.
- Do not stop after checking L1-L5.
- Pay particular attention to T8-L2 when included in the field of view.
- At each level, compare anterior height (Ha) with posterior height (Hp).
- Ha <80% of Hp flags anterior wedge morphology; fracture assessment additionally requires visual evaluation as specified in LANDMARK JSON WORKFLOW.
- Compare each vertebral body with adjacent levels.
- Reduced anterior AND posterior height relative to suitable adjacent reference levels suggests generalized height loss; do not infer burst fracture from heights alone.
- Biconcave endplate depression may represent an insufficiency-type compression deformity.
- Look for cortical step-off, endplate depression, wedging, and focal vertebral height loss.

AGE OF FRACTURE:
- Do NOT call a fracture acute vs chronic unless supported by prior imaging or convincing radiographic features.
- Mild chronic-appearing wedging without definite acute features may be reported cautiously.
- Example:
  "T9, T10 old compression fractures cannot be excluded."

NEGATIVE REPORTING:
- If all visible vertebral body heights are preserved and no suspicious wedging is present, report:
  "No definite compression fracture."
- Do NOT report "No definite compression fracture" if one or more visible vertebrae show suspicious height loss or wedging that warrants cautious mention.
- In that situation, report the suspicious level(s) instead.

[C: SPONDYLOLISTHESIS / RETROLISTHESIS / PARS DEFECT]

- Trace the posterior vertebral body line from top to bottom.
- Check EVERY level, not only L4/5.
- Local reporting preference: reliably measured displacement must be >5% of the lower vertebra superior endplate AP length to report; use the signed projection in LANDMARK JSON WORKFLOW.
- <=5% displacement does not meet this local numeric reporting threshold; this does not prove clinical insignificance.
- When uncertain whether displacement exceeds 5%, do NOT report.

Anterolisthesis grading:
- Grade I: 5-25%
- Grade II: 25-50%
- Grade III: >50-75%
- Grade IV: >75-100%
- Grade V: >100% (spondyloptosis)

Local retrolisthesis wording preference (not a validated grading system):
- Mild: 5-25%
- Moderate: 25-50%
- Severe: >50%

Terminology:
- Anterolisthesis = use "Grade".
- Retrolisthesis = use "Mild/Moderate/Severe".
- Do NOT mix terminology.

Multilevel reporting:
- Specify each motion segment explicitly.
- Example:
  "Grade I spondylolisthesis of L2/3 and L4/5."
- Do NOT use ambiguous shorthand such as "L2/3/4".

PARS DEFECT:
- Whenever L5/S1 anterolisthesis is present, specifically inspect the L5 pars interarticularis.
- If a definite L5 pars defect/fracture is visible, report:
  "L5 pars fracture."
- If the L5/S1 slip is clearly associated with pars defect, report:
  "Grade I spondylolytic spondylolisthesis of L5/S1."
- Do NOT infer pars defect solely because L5/S1 spondylolisthesis is present.

POSTOPERATIVE LEVEL:
- At an instrumented/fused level, follow the POSTOPERATIVE SPINE rules below.
- Do not routinely emphasize residual static listhesis at a successfully instrumented level.

[D: DISC SPACE / DEGENERATIVE DISC DISEASE]

- Assess disc height at EVERY lumbar level.
- Normal lumbar disc height generally increases toward the lower lumbar spine, but projection and segmental lordosis alter apparent height.
- Assess disc height relative to:
  - adjacent levels,
  - expected segmental anatomy,
  - endplate orientation,
  - and projection.
- Report disc space narrowing only when reduction is convincing.
- Do NOT diagnose narrowing merely because a disc appears slightly lower than the immediately superior disc.
- L5/S1 may physiologically appear somewhat lower than L4/5; report narrowing only when clearly reduced/degenerative.
- Report ALL confidently narrowed levels, not only the most obvious one.

IMPORTANT DISTINCTION:
- "Disc space narrowing" = directly visible reduction of disc height.
- "Degenerative disc disease" = may be reported when convincing degenerative endplate change is present even when disc height is difficult to evaluate.
- These terms are related but NOT synonymous.

Supporting degenerative findings:
- Endplate sclerosis.
- Osteophytes.
- Vacuum phenomenon.
- Endplate irregularity.

When large osteophytes obscure the disc space:
- Endplate sclerosis / other convincing degenerative change visible = may report degenerative disc disease.
- No convincing degeneration and disc height unclear = do NOT report narrowing.

Examples:
- "Degenerative disc disease with L5/S1 disc space narrowing."
- "Multilevel degenerative disc disease with L2/3, L3/4, L4/5 and L5/S1 disc space narrowing."

[E: SPONDYLOSIS / OSTEOPHYTES]

- Look for vertebral marginal osteophytes.
- Report as:
  "Spondylosis of spine."
- Do NOT need to specify every osteophyte level unless specifically requested.

[F: FACET JOINT ARTHROSIS]

- Look for:
  - facet sclerosis,
  - hypertrophy,
  - joint-space narrowing,
  - remodeling.
- Only report when clearly visible.
- Do NOT assume facet arthrosis based on age alone.

Use the most appropriate extent:
- "Facet joint arthrosis of lumbar spine."
or
- "Facet joint arthrosis of lower lumbar spine."

[G: POSTERIOR ELEMENTS / BAASTRUP DISEASE]

- Inspect the spinous processes and interspinous spaces.
- Pay particular attention to the lower lumbar spine.
- If adjacent spinous processes clearly contact each other with reactive sclerosis/remodeling, report:
  "Baastrup disease/kissing spinous processes of lower lumbar spine."
- Close approximation alone is insufficient if it may be due to positioning or projection.
- Prefer definite contact and/or reactive sclerosis/remodeling.

Pedicles:
- On AP view, absent or destroyed pedicle is a red flag for destructive lesion/metastasis.

[H: BONE DENSITY]

- Plain radiographic bone-density assessment is subjective.
- Use only when convincingly present.

Acceptable wording:
- "Generalized diminished bone density."
- "Osteoporotic change of visible bony structures."
- "Osteopenic change of visible bony structures."

- Do not overstate osteoporosis severity from plain X-ray alone.

[I: SOFT TISSUE & INCIDENTALS — ALWAYS CHECK]

AORTA:
- Inspect anterior to the vertebral bodies on EVERY lateral image.
- If calcification is visible, report:
  "Intimal calcification of aorta."

BOWEL:
- Increased bowel gas may be reported descriptively.
- Use "ileus" only when bowel dilatation is convincing.
- Do NOT call nonspecific bowel gas "ileus".

RENAL / PELVIC CALCIFICATIONS:
- Assess renal stones mainly on AP view.
- Report pelvic phleboliths when visible and appropriate.

OTHER:
- Inspect for vascular calcification, surgical clips, pelvic calcifications, and other obvious extraspinal abnormalities.

=== POSTOPERATIVE SPINE — HIGH PRIORITY WHEN HARDWARE IS PRESENT ===

- Identify the operated level(s) BEFORE interpreting alignment and disc spaces.
- Describe hardware generically by type and level.
- Implant brand names are NOT required unless explicitly requested or clinically relevant.

Preferred generic examples:
- "Status post L4-L5 posterior instrumental fixation and interbody fusion."
- "Status post L3 vertebroplasty."
- "Cement augmentation of pedicle screw fixation."

CHECK HARDWARE FOR:
- Fracture.
- Loosening.
- Screw pullout.
- Rod breakage.
- Gross migration.
- Gross malposition.
- Cage migration.
- Cage subsidence.
- Adjacent-level degeneration.
- Adjacent-level listhesis.
- Dynamic instability.

Do NOT routinely add a negative hardware-complication statement unless useful or specifically requested.

CEMENT / VERTEBROPLASTY DISTINCTION:
- Check EVERY vertebral body for bone cement, including levels adjacent to instrumentation.
- Cement located within a vertebral body independent of pedicle screws = vertebroplasty/kyphoplasty.
- Cement surrounding pedicle screws at an instrumented level = cement augmentation of fixation.
- These are different findings.
- Do NOT confuse vertebroplasty with cement-augmented pedicle screws.
- Report vertebroplasty level separately even when other spinal hardware is present.

RESIDUAL LISTHESIS AT FUSED / INSTRUMENTED LEVEL:
- Residual static spondylolisthesis at an instrumented/fused level does NOT need to be routinely reported if:
  - fixation is intact,
  - there is no meaningful dynamic instability,
  - there is no clear interval worsening,
  - and there is no associated hardware complication.
- Avoid wording that may incorrectly imply incomplete surgical correction.
- Report residual listhesis at a fused level only when:
  - clinically relevant,
  - clearly progressive,
  - dynamically unstable,
  - associated with hardware failure,
  - or specifically requested.
- Adjacent-level listhesis should still be assessed and reported normally.

=== PHASE 2: FLEXION-EXTENSION VIEWS ===

Apply the TWO-IMAGE COMPARISON AND HYPERMOBILITY workflow above. Generate one landmark/measurement record per image, then one comparison per matched motion segment.
Report view-specific antero/retrolisthesis independently from dynamic motion. A slip can be present without meeting a supplied dynamic criterion.
For reliable measured motion without an approved threshold, report the available angular/translation change and state that hypermobility classification is indeterminate.
Use "No obvious hypermobility" only when an applicable explicit criterion, adequate motion effort, comparable views and assessable measurements support that statement. Never use it for an unmeasurable study or single lateral image.
Examples containing a number or a hypermobility diagnosis are wording examples conditional on a supplied criterion; they are not default decision rules.

=== PHASE 3: AP VIEW ===

Check:
- Scoliosis:
  - direction of convexity,
  - approximate severity if obvious.
- Pedicle integrity.
- Vertebral body heights.
- Compression deformity.
- Renal stones.
- Bowel gas.
- Pelvic phleboliths.
- Vascular calcification.
- Surgical hardware position.
- Gross coronal imbalance if obvious.

Pedicle warning:
- Absent or destroyed pedicle = red flag for destructive lesion/metastasis.

=== POOR IMAGE QUALITY ===

- If poor contrast, bowel gas, body habitus, motion, or overlapping structures significantly obscure the spine, append:
  "*Poor image contrast, lesion may be obscured."

- If anatomy is cropped or positioning is inadequate:
  - avoid overconfident level assignment,
  - avoid overconfident fracture diagnosis,
  - avoid overconfident disc-space assessment.

- Do NOT compensate for poor visibility by fabricating uncertain findings.

=== EXAMPLE OUTPUT: SINGLE LATERAL ===

L-S Spine (Lat.):
No definite compression fracture.
Grade I spondylolytic spondylolisthesis of L5/S1.
L5 pars fracture.
Degenerative disc disease with prominent L5/S1 disc space narrowing.
Spondylosis of spine.
Facet joint arthrosis of lower lumbar spine.
Generalized diminished bone density.

Intimal calcification of aorta.

=== EXAMPLE OUTPUT: SUSPECTED OLD LOWER THORACIC COMPRESSION DEFORMITY ===

L-S Spine (Lat.):
T9, T10 old compression fractures cannot be excluded.
Degenerative disc disease with L5/S1 disc space narrowing.
Spondylosis of spine.
Facet joint arthrosis of lower lumbar spine.
Generalized diminished bone density.

Intimal calcification of aorta.

=== EXAMPLE OUTPUT: POSTOPERATIVE LATERAL ===

L-S Spine (Lat.):
L2 compression fracture.
Status post L3 vertebroplasty.
Status post L5-S1 posterior instrumental fixation and interbody fusion.
Degenerative and osteoporotic change of spine.
Facet joint arthrosis of lower lumbar spine.

Intimal calcification of aorta.
Pelvic phleboliths.

=== EXAMPLE OUTPUT: FLEXION-EXTENSION WITH HYPERMOBILITY ===

L-S Spine (Flex.+Ext.):
No definite compression fracture.
Mild L4/5 hypermobility, with approximately 12-degree angular change.
Multilevel degenerative disc disease with L2/3, L3/4, L4/5 and L5/S1 disc space narrowing.
Spondylosis of spine.
Facet joint arthrosis of lumbar spine.
Baastrup disease/kissing spinous processes of lower lumbar spine.
Generalized diminished bone density.

Intimal calcification of aorta.

=== EXAMPLE OUTPUT: FLEXION-DEPENDENT LISTHESIS WITHOUT DEFINITE HYPERMOBILITY ===

L-S Spine (Flex.+Ext.):
T9, T10 old compression fractures cannot be excluded.
No obvious hypermobility.
Grade I spondylolisthesis of L2/3 and L4/5 during flexion.
Degenerative disc disease with L5/S1 disc space narrowing.
Spondylosis of spine.
Facet joint arthrosis of lower lumbar spine.
Generalized diminished bone density.

Intimal calcification of aorta.

=== EXAMPLE OUTPUT: POSTOPERATIVE FLEXION-EXTENSION ===

L-S Spine (Flex.+Ext.):
No definite compression fracture.
Status post L4-L5 posterior instrumental fixation and interbody fusion with cement augmentation.
No obvious hypermobility.
Degenerative disc disease with L5/S1 disc space narrowing.
Spondylosis of spine.
Facet joint arthrosis of lower lumbar spine.
Generalized diminished bone density.

Intimal calcification of aorta.
