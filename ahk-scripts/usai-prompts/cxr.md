Draft a Chest X-ray report from the supplied images. Output a clean, plain-text report in TELEGRAPHIC DIAGNOSTIC style. NO Markdown formatting in the final text (no bold, no italics, no headers). Use hyphens '- ' for each line.

=== PHASE 1: TECHNICAL & PATIENT ASSESSMENT (Internal - do not output) ===
- View: PA / AP / Lateral / Decubitus.
- Rotation: Check spinous processes centered between clavicular heads.
- Inspiration: Good (>=9 posterior ribs above diaphragm) / Poor.
- Use patient age only if supplied; do not estimate it or use an assumed age to add findings.

=== PHASE 2: SYSTEMATIC ANALYSIS (Follow this order strictly) ===

[1. LUNGS - The Anchor, most critical]
- Compare both lung fields systematically: apex -> mid -> base.
- NORMAL: output exactly 'No active lung lesion is noted.'
- IF ABNORMAL, use the most specific applicable:
  a. Infiltration: 'Patchy opacity/infiltration in [RUL/RML/RLL/LUL/LLL], could be pneumonia or others.'
  b. Consolidation: 'Consolidation with air bronchograms in [location], could be pneumonia or others.'
  c. Mass/Nodule: 'A nodular opacity/mass lesion in [location]. Recommend CT for further evaluation.'
  d. Emphysema/COPD: 'Hyperinflated lungs with flattened diaphragms, compatible with COPD/emphysematous change.'
  e. Congestion: 'Bilateral perihilar haziness and upper lobe venous distention, compatible with pulmonary congestion.'
  f. Old TB/Fibrosis: 'Fibrocalcified change in [bilateral upper lobes / location], suspect old infection/inflammatory changes, eg. old TB or others.'
  g. Atelectasis: 'Band-like opacity/volume loss in [location], compatible with atelectasis.'
  h. Interstitial: 'Reticular/reticulonodular pattern in [location], suggest interstitial lung disease. Recommend CT correlation.'

[2. PLEURA]
- Costophrenic angles: Sharp (normal) / Blunted (effusion).
  If blunted: 'Blunting of [R/L/bilateral] costophrenic angle(s), suggesting pleural effusion.'
  Grade: Small / Moderate / Large.
- Pneumothorax: 'Pneumothorax at [R/L] [apex/hemithorax].'
- Pleural thickening: 'Apical pleural thickening [bilateral/unilateral].'
- If all normal: omit this section entirely.

[3. HEART]
- Cardiothoracic ratio (CTR) on PA view:
  CTR <0.5 -> 'Normal heart size.'
  CTR 0.5-0.55 -> 'Borderline cardiomegaly.'
  CTR >0.55 -> 'Cardiomegaly.'
- On AP view, account for projection when describing visible heart size. Do not automatically report enlargement; if size cannot be assessed, state that limitation.

[4. AORTA & MEDIASTINUM]
- ONLY report what is visually evident. Do NOT assume calcification based on age alone.
  Calcification seen -> 'Intimal calcification of aorta.'
  Tortuous -> 'Tortuous aorta.' Add calcification separately only when visible.
  Dilated -> 'Dilated ascending aorta.'
  Widened mediastinum -> 'Mild mediastinal widening.'
- Hilar prominence/lymphadenopathy: note if present.
- Tracheal deviation: note direction if present.
- If all normal: omit this section entirely.

[5. DIAPHRAGM]
- Elevated hemidiaphragm: note side.
- Free air under diaphragm -> 'Free air under [R/L] hemidiaphragm. Pneumoperitoneum? Clinical correlation required.'
- Flattened diaphragm -> supports COPD (report with lungs).
- If normal: omit this section entirely.

[6. BONES & SOFT TISSUE]
- IF visually normal (young, no degeneration) -> 'Unremarkable bony structure.'
- IF degenerative changes visible -> 'Degenerative change and spur formation of spine.'
- IF reduced bone density visible -> add 'Generalized diminished bone density.' or 'Osteoporotic change of visible bony structures.' if severe.
- Rib fractures: note level and side if seen.
- Soft tissue: subcutaneous emphysema, mastectomy, chest wall mass.

[7. DEVICES & FOREIGN BODIES - Only if present]
- ETT: 'Status post endotracheal tube insertion with tip approximately [X] cm above carina.'
- CVC: 'Status post central venous catheter via [R/L] [subclavian/IJ] with tip in SVC.'
- NGT: 'Status post nasogastric tube insertion with tip in stomach.'
- Chest tube: 'Chest tube in [R/L] hemithorax.'
- Pacemaker/ICD: 'Pacemaker/ICD with leads in [RA/RV/CS].'
- Port-A-Cath: 'Implantable port via [side] with tip in SVC.'
- Sternal wires, IABP, ECMO, or other devices: describe accordingly.
- If no devices: omit this section entirely.

[8. OTHERS - Only if present]
- Distended stomach.
- Calcified granuloma.
- Any other incidental findings.
- If none: omit this section entirely.

=== OUTPUT STRUCTURE (Strict) ===
(Output strictly as a list of lines starting with '- '. Only include lines for findings present or required.)
- [Lungs - Include a supported finding or assessment limitation. When adequately assessed and normal: 'No active lung lesion is noted.']
- [Pleura - Include if effusion, pneumothorax, or thickening. Omit if normal.]
- [Heart - Include supported heart-size assessment or its limitation; do not force a normal or enlarged finding.]
- [Aorta/Mediastinum - Include ONLY if calcification, tortuosity, dilation, or deviation is VISIBLE. Do NOT assume.]
- [Diaphragm - Include only if abnormal. Omit if normal.]
- [Bones - Include supported findings, 'Unremarkable bony structure' when adequately assessed and normal, or an assessment limitation.]
- [Devices - Include each device on its own line. Omit if no devices.]
- [Others - Omit if none.]
