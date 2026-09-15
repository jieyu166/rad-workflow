# Spine X-ray Reporting Prompt — Revised

Draft a Spine X-ray report from the supplied images. Apply only sections supported by the provided views; examples illustrate wording, not findings to copy.

Output a clean, plain-text report in TELEGRAPHIC DIAGNOSTIC style.

FINAL REPORT RULES:
- NO Markdown formatting in the final report.
- NO explanations, reasoning, confidence discussion, or teaching comments outside the report.
- Each finding on its own line.
- Spine findings and non-spine incidental findings separated by ONE blank line.
- Use concise conventional radiology wording.
- Do NOT fabricate uncertain findings.
- Apply each finding-specific reporting threshold below. When visibility prevents assessment, state the limitation; do not substitute a negative finding.
- When a subtle abnormality is suspicious but not definite, use cautious wording rather than falsely reporting a normal study.

=== OUTPUT FORMAT ===

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
- Find T12: the lowest vertebra with a rib attached.
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
- Ha <80% of Hp supports anterior wedge compression fracture.
- Compare each vertebral body with adjacent levels.
- Reduced anterior AND posterior height relative to adjacent levels may indicate a burst-type compression deformity.
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
- Displacement must be >5% of the endplate AP length to report.
- <5% displacement = not significant; do NOT report.
- When uncertain whether displacement exceeds 5%, do NOT report.

Anterolisthesis grading:
- Grade I: 5-25%
- Grade II: 25-50%
- Grade III: >50%

Retrolisthesis grading:
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

APPLICABILITY:
- Apply this section ONLY when true flexion and extension views are supplied.
- Do NOT infer flexion/extension solely from close timestamps.
- Use image labels when available.
- Otherwise identify:
  - Flexion = reduced/reversed lordosis.
  - Extension = increased/accentuated lordosis.

ASSESS EACH VIEW SEPARATELY FIRST:
- Evaluate alignment on the flexion image independently.
- Evaluate alignment on the extension image independently.
- Identify whether a slip is:
  - present on both views,
  - more conspicuous on flexion,
  - more conspicuous on extension,
  - or only visible on one view.

THEN ASSESS DYNAMIC MOTION:
- Compare the SAME motion segment between flexion and extension.
- Assess BOTH:
  1. Translational change.
  2. Segmental angular change.
- Check EVERY lumbar level.

IMPORTANT DISTINCTION:
- Presence of spondylolisthesis on one view does NOT automatically mean dynamic instability.
- A Grade I slip may become visible or more conspicuous during flexion without meeting the threshold for definite hypermobility.
- Therefore the following findings may coexist:
  "No obvious hypermobility."
  "Grade I spondylolisthesis of L2/3 and L4/5 during flexion."

RETROLISTHESIS PITFALL:
- Do NOT diagnose retrolisthesis merely because a vertebra appears less anterior on extension than on flexion.
- True posterior displacement must independently exceed the >5% reporting threshold.
- Avoid converting subtle view-dependent alignment change into false retrolisthesis.

HYPERMOBILITY:
- If no convincing excessive translation or angular change is present, report:
  "No obvious hypermobility."
- If abnormal motion is confidently identified, report level and type.
- If segmental angular change can be confidently estimated, include the approximate value.
- Example:
  "Mild L4/5 hypermobility, with approximately 12-degree angular change."

IMPORTANT:
- Never report "No obvious hypermobility" from a single neutral/lateral image.
- Do not overcall instability from projection or positioning differences alone.

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
