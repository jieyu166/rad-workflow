Draft a Foot & Ankle report from the supplied images. Output a clean, plain-text report in TELEGRAPHIC DIAGNOSTIC style. NO Markdown. NO Bullet points.

PHASE 1: ANATOMY & VIEW RECOGNITION:
- Identify if the image is Ankle or Foot.
- If the image is unrelated (e.g., Spine, Chest, Knee), output 'Non-target anatomy' and STOP.

PHASE 2: TRAUMA & POST-OP CHECK (HIGHEST PRIORITY):
- Hardware: Look for Plates, Screws, Pins, or Intramedullary Nails.
- Union Status: If hardware or an old fracture is present, assess healing only when visible evidence supports it. Use the applicable wording:
  1. 'With bone union' (Fully healed)
  2. 'With callus formation and near bone union' (Healing)
  3. 'Without bone union' (only when supported; do not automatically add non-union/delayed union)
  4. 'Union status cannot be adequately assessed on the provided image(s).' (insufficient visualization)
- Fractures: If acute, specify type (e.g., 'Trimalleolar', 'Avulsion', 'Spiral').

PHASE 3: SPECIFIC ANATOMY CHECKLIST:

(IF ANKLE):
1. Malleoli: Check Medial, Lateral, and Posterior malleoli.
2. Talar Dome: Check for Osteochondral lesions (OCD) or 'Valgus deformity'.
3. Accessory Bones: Distinguish 'Os trigonum' or 'Os subfibulare' from fractures.
4. Soft Tissue: Report location of swelling (e.g., 'Soft tissue swelling around lateral malleolus').

(IF FOOT):
1. Navicular: Check for compression/sclerosis indicative of 'Mueller-Weiss disease'.
2. Calcaneus: Check for 'Plantar spur' or 'Haglund deformity' (posterior superior prominence).
3. 5th Metatarsal: Check base for Jones/Avulsion fracture.
4. Alignment: Check for Hallux Valgus or Pes Planus.

PHASE 4: REPORTING STYLE RULES:
1. Phrasing: Use 'Status post [procedure] with/without [finding]'. Example: 'Fracture of lateral malleolus status post screw fixation with bone union.'
2. Tone: Concise report wording. Preserve uncertainty and assessment limitations; do not force a definite diagnosis.
3. Negative Findings: Only mention relevant negatives (e.g., 'No evident bone lesion').

REQUIRED OUTPUT STRUCTURE:
(Block 1: Primary Diagnosis / Trauma)
[Line 1: Major Finding (e.g., 'Trimalleolar fracture status post plate fixation') or 'No acute fracture']
[Line 2: Healing Status (e.g., 'With callus formation and near bone union') - Omit if normal]

(Block 2: Secondary Findings & Degeneration)
[Line 1: Bone Lesions/Deformity (e.g., 'Mueller-Weiss disease considered' or 'Plantar calcaneal spur')]
[Line 2: Joints (e.g., 'Tibiotalar osteoarthritis' or 'Joint space narrowing')]

(Block 3: Soft Tissues & Others)
[Line 1: Soft Tissue (e.g., 'Lateral ankle swelling')]
[Line 2: Accessory Bones (e.g., 'Prominent os trigonum')]

(Block 4: Summary)
[Single concise summary line]
