Draft a Knee X-ray report from the supplied images. Output a clean, plain-text report in TELEGRAPHIC DIAGNOSTIC style. NO Markdown. NO Bullet points.

PHASE 1: ANATOMY & VIEW RECOGNITION:
- Identify if the image shows Right, Left, or Bilateral Knees.
- Identify if post-surgical implants (TKA) are present.
- CRITICAL: Ignore any non-knee anatomy (e.g., faint spine or pelvis parts) unless clinically significant to the knee.

PHASE 2: SPECIFIC ANALYSIS LOGIC:

(1. FRACTURE & DISLOCATION CHECK):
- Scan femur, tibia, fibula, and patella for fracture lines.
- If Normal: Output 'No obvious evidence of displaced bony fracture. No obvious joint dislocation.'
- If Fracture: Describe location, type (e.g., 'Non-displaced', 'Comminuted'), and union status (e.g., 'Without bone union', 'Healing fracture').

(2. OSTEOARTHRITIS (OA) ASSESSMENT - MANDATORY):
- Detection: Look for osteophytes, joint space narrowing, and subchondral sclerosis.
- GRADING (Must use 'Kellgren & Lawrence system'):
  - Grade I: Doubtful narrowing, possible osteophytic lipping.
  - Grade II: Definite osteophytes, possible narrowing.
  - Grade III: Moderate multiple osteophytes, definite narrowing, some sclerosis.
  - Grade IV: Large osteophytes, marked narrowing, severe sclerosis.
- Standard Phrase: 'OA in [side] knee. Kellgren & Lawrence system, grade [I-IV].'

(3. PATELLA & ALIGNMENT):
- Check for Patellar Tilt (especially on Merchant/Skyline view).
- If Normal: 'No obvious patellar tilt or patellar subluxation.'
- If Abnormal: 'Lateral tilting of patella.'

(4. SOFT TISSUE & BONE MATRIX):
- Effusion: Assess the suprapatellar pouch when visible. Report effusion and its degree only when supported; preserve uncertainty when equivocal and state limitations when not assessable. Do not add effusion because it appears in an example.
- Bone Density: Check for 'Disuse osteoporosis' or 'Probably osteoporosis'.

PHASE 3: OUTPUT STRUCTURE & STYLE RULES:
1. Telegraphic Style: Use short phrases. (e.g., 'Facet arthrosis' instead of 'There is facet arthrosis').
2. Comparisons: Describe temporal change only in previous/current comparison mode. In current-study modes, do not invent a previous study.
3. Sequence: Fracture/Implant -> OA/Degeneration -> Patella -> Soft Tissue.

WORDING EXAMPLES (include only findings supported in the current case):
(Example 1 - Adequately assessed normal study):
'No obvious evidence of displaced bony fracture. No obvious joint dislocation. No obvious patellar tilt.'
(Example 2 - OA):
'OA in right knee. Kellgren & Lawrence system, grade III. Joint space narrowing, osteophyte formation of patellofemoral joint. Mild joint effusion. Disuse osteoporosis.'
(Example 3 - Fracture):
'Non-displaced fracture of patella. Without bone union. Mild joint effusion. Soft tissue swelling.'
