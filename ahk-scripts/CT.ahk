
;============================================================================================
; CT
;============================================================================================


:O:ildct;::
(
- Fibrosis semi-quantification (visual): A-arch _%, Carina-1cm _%, PVC _%, Mid _%, RHD+1cm _%, RHD-2cm _%, Average _%. (Srs/Img:_/_)`r
*Semi-quantitative fibrosis estimation is subjective and may be different in different observers. `r
)

:O:ctadd::
HotstringMenuV("A","MenuShortcut2","NoC|*This is a Non contrast medium injection image.`rLimited evalution for lymphadenopathy, vascular structure, soft tissue density organs and soft tissue lesions survey","CTA|*Some venous phase enhanced lesions/mass could be obscured due to the protocol is specially designed for aorta arterial phase, either benign or early malignancy was reported","Low dose|*LDCT is only limited in detection and follow-up of pulmonary nodules. It is not suitable to replace HRCT to evaluate interstitial lung disease, nor to be used for soft tissue lesions in chest wall, mediastinum and upper abdomen","BRK","*Motion artifact may interfere with interpretation","*Metallic artifact may interfere with interpretation", "The dental fillings and the opaque material within the teeth obscure the area due to beam hardening artifact","BRK","This screening abdominal MRI is focusing on upper abdomen, thus, subtle lesion arising from GI tract, urotract and reproductive system could be underestimated", "Other supplementary survey such as tumor markers, urine analysis, urotract sonography, Panendoscopy and Colonoscopy should be considered","Semi-quantitative fibrosis estimation is subjective and may be different in different observers","Beam-hardening artifacts, skull base lesions may be obscured.")
return

:O:ctpren::
SendInput Other details are mentioned as followings:`r----------------------------------------------------------------------`r
HotstringMenuV("A","MenuShortcut2","Abd-C|CT study of abdomen (_) without contrast medium:`r  Pre-contrast scans: 5 mm slice thickness from diaphragm to pubic symphysis","NCCT of the brain with axial, coronal, sagittal sections showed:","Chest CT-c|CT study of the thorax was performed with a multi-slice CT scanner.`rMETHOD: (1) HRCT (2) Noncontrast survey were performed`rSCAN RANGE: lower neck to adrenal gland`rINDICATION: _")
SendInput `r`r`r*This is a Non contrast medium injection image.`rLimited evalution for lymphadenopathy, vascular structure, soft tissue density organs and soft tissue lesions survey;
return

:O:ctprec::
SendInput Other details are mentioned as followings:`r----------------------------------------------------------------------`r
HotstringMenuV("A","MenuShortcut2","Abd+C|CT study of abdomen (_) without and with contrast medium:`r  Pre-contrast and post-contrast venous and delayed scans: 5 mm slice thickness from diaphragm to pubis symphysis","NCCT and CECT of the brain with axial, coronal, sagittal sections showed:","Chest CT+c|CT study of the thorax was performed with a multi-slice CT scanner.`rMETHOD: (1) HRCT (2) Noncontrast survey (3) contrast enhancement were performed`rSCAN RANGE: lower neck to adrenal gland`rINDICATION: _","CTA|Spiral CTA of aorta was performed with a multi-slice CT scanner.`rMETHOD: (1) Noncontrast survey (2) CE-CTA with MPR were performed.  `rSCAN RANGE: lower neck to hip.`rINDICATION: _","BRK","CTPAOD|CT and CT arteriography of lower extremity without and with contrast medium:`r  Pre- and post- contrast scans: 7 mm slice thickness from diaphragm to plantar.")
SendInput `rBefore and after the administration of intravenous contrast there was no adverse effect.`r`r
return

:O:ca;::
HotstringMenuV("A","MenuShortcut","Calcified granulomas in both lungs", "Calcified tendinitis in _","calcified granuloma","BRK","Dystrophic calcification in _.")
return


::ctbx::
(
CT guide biopsy is performed under clinical request. The operation procedure and potential risk are well explained. Patient agreement and consensus are obtained.

Under CT guide, tissue specimens are smoothly taken for pathology examination.

1. Position: _Supine _Prone
2. Target lesions: _
3. Devices: 19G coaxial needle with 20G biopsy needle
4. Specimens: _ cores
5. Complications: _Minimal pneumothorax_/hemothorax
 
The patient is sent back to the ward under stable condition. Recommend close f/u patient''s vital signs.

Impression: _ s/p CT-guided biopsy, with _.
)

::ctabd::
(
Imaging findings :
1. Liver                : No definite space occupying lesion can be identified.
2. Biliary system       : No evidence of bile duct dilatation.
3. Pancreas             : 
4. Spleen               : 
5. Adrenal glands       : 
6. Urinary system       : 
7. GI system            : 
8. Lymph node           : 
9. Musculoskeletal      : 
10. Reproductive system : 
11. Lower chest         : 
12. Others              : 

_Not unusual for age. 
Unremarkable 

)
::ctch::
(
Imaging findings :
1. Lung, airway, pleura : 
2. Lymph node           : 
3. Mediastinum          : 
4. Cardiovascular system: 
5. Visible lower neck   : 
6. Breast, axilla       : 
7. Visible upper abdomen: 
8. Musculoskeletal      : 
9. Others               : 

_Not unusual for age. Unremarkable 
)
::ctneck::
(
The aim of this CT scan was requested to evaluate a case of ___.

NCCT _and CECT of the neck with axial, coronal, sagittal sections showed:

Imaging findings :
1. Nasopharynx:
- Unremarkble nasopharynx.
2. Oropharynx, Oral cavity:
- Unremarkble tongue and floor of mouth, oropharynx.
3. Hypopharynx, Larynx:
- Unremarkble supraglottic, glottic and subglottic larynx, hypopharynx.
4. Lymph nodes: 
- Visible LNs short-axis <1cm.
5. Salivary glands:
- Unremarkble parotid, submandibular and sublingual glands.
6. Thyroid: Unremarkable.
7. Vessels and carotid space: Unremarkable.
8. Bony structures: Unremarkable.
9. Face, other head     : Unremarkable
10. Other neck structure: Unremarkable
11. Visible brain       : Unremarkable
12. Visible lung        : Unremarkable
13. Others              : Unremarkable 

nrhnct
)
::ctch2::
(
======================================================================
Low Dose Computed Tomography (LDCT) of lung is performed from the apex through the lung base without intravenous contrast medium. 
Thin sliced axial and maximum intensity projection (MIP) images are reviewed.
----------------------------------------------------------------------
CT dose information:
According to AAPM TG23 report, the estimated Effective Dose of current chest CT study in adult is _ mGy-cm (DLP) x 0.014 = __ mSv.  CTDIvol _ mGy.
----------------------------------------------------------------------
Clinical Indication: Lung cancer screening _/ Nodule follow-up
Comparison with previous chest CT or LDCT (date): _not available

Findings:
_Small nodules in  (<6mm,srs/img:)
Suggest annual image f/u.
Calcified granuloma in (srs/img:)

Other incidental findings:
_N/A

** LDCT is only limited in detection and follow-up of pulmonary nodules. It is not suitable to replace HRCT to evaluate interstitial lung disease, nor to be used for soft tissue lesions in chest wall, mediastinum and upper abdomen.
)

::zabdct3n::
(
CT study of abdomen (_) without and with contrast medium:
  Pre-contrast scans: 5 mm slice thickness from diaphragm to pubic symphysis;
  Arterial phase: 5 mm slice thickness from diaphragm to kidney;
  Early portal venous phase: 5 mm slice thickness from diaphragm to kidney;
  Late portal venous phase: 5 mm slice thickness from diaphragm to pubic
  symphysis.

Comparison with previous CT on _.
)

::zabdctu::
(
CT study of abdomen (_) without and with contrast medium:
  Pre-contrast scans: 5 mm slice thickness from diaphragm to pubic symphysis;
  Corticomedullary phase : 5 mm slice thickness from diaphragm to kidney;
  Nephrographic phase : 5 mm slice thickness from diaphragm to pubic symphysis;
  Excretory phase: 5 mm slice thickness from diaphragm to pubic symphysis.

Comparison with previous CT on _.

)

::ctadrenal::
(
CT study of abdomen with emphasis on adrenal gland(_) without and with contrast medium:
  Pre-contrast scans: 5 mm slice thickness from diaphragm to pubic symphysis;
  Arterial phase : 5 mm slice thickness from diaphragm to kidney;
  Early venous phase : 5 mm slice thickness from diaphragm to pubic symphysis;
  Delayed venous phase: 5 mm slice thickness from diaphragm to pubic symphysis.

Comparison with previous CT on _.

Imaging findings :
5. Adrenal glands     : 
   - Hypodense nodule with enhancement is seen in _ adrenal gland(Srs/Img:_/_), about _cm in size.
       Precontrast density about _ HU
       Early enhancement density about _ HU
       10-min delayed CECT density about _ HU
          Contrast wash-out technique: Absolute percentage wash-out: _%
     These features are favored as adrenal _adenoma.
)

::ctpaod::
(
Imaging findings :

1. Artery of lower extremities:

   Right side:
     Iliac arteries: patent
     Common femoral artery: patent
     Deep femoral artery: patent
     Superficial femoral artery: patent
     Popliteal artery: patent
     Tibioperoneal trunk: patent
     Anterior tibial artery: patent
     Posterior tibial artery: patent
     Peroneal artery: patent
     Dorsalis pedis artery: patent
     Plantar arteries: patent

   Left side:
     Iliac arteries: patent
     Common femoral artery: patent
     Deep femoral artery: patent
     Superficial femoral artery: patent
     Popliteal artery: patent
     Tibioperoneal trunk: patent
     Anterior tibial artery: patent
     Posterior tibial artery: patent
     Peroneal artery: patent
     Dorsalis pedis artery: patent
     Plantar arteries: patent

2. Venous structures: Unremarkable
3. Musculoskeletal: Unremarkable
4. Others: 
)

:O:ctaorta::
(
Imaging findings :

1. Aorta: 
-- Type _A dissection intramural hematoma(IMH) from _ to  _
-- Maximal outer diameter is 
-- Maximal thickness of false lumen is 
-- Entry site:
-- Re-entry site:  
Associate lesion
A. IMH--Ulcer like projection: No
B. IMH--Intramural arteriolar tear: No
C. Pericardium: Not unusual
D. Pleural effusion: No
Branch type/malperfusion syndrome [Gaxotte''s classifcation]:
A. Arch: not involved
B. Celiac: not involved
C  SMA: not involved
D. IMA: not involved
E. RT renal artery: not involved
F. LT renal artery: not involved
G. RT common iliac artery: not involved
H. LT common iliac artery: not involved

2.Lung, pleura and airway: The lung parenchyma was normal.
3.Mediastinum: unremarkable.
4.Pericardium and heart: not unusual for age.
5.Chest wall and bony structure: not unusual for age.
6.Neck:
7.Upper abdomen and adrenals: not unusual for age.
)

;============================================================================================
; MRI
;============================================================================================


::pabdmrm::
(

Other details are mentioned as followings:
----------------------------------------------------------------------
MRI of whole abdomen for tumor screening is performed without and with intravenous Gd-DOTA enhancement and the parameters as follows:
 without enhancement:
  Turbo spin echo: axial section of upper abdomen, lower abdomen and prostate;
                   sagittal section of pelvis; 
  HASTE: axial section of lower abdomen;
  HASTE: coronal section of whole abdomen;
  Chemical shift imaging: axial section of in phase and opposed phase of upper 
                          abdomen;
  MRCP
  DWI and ADC: axial section of liver.
 with Gd-DOTA enhancement: 
  dynamic study, four sequences of axial section and one coronal section.

Imaging findings:
1. Liver: 
   No definite space occupying lesion can be identified.
2. Biliary system: 
   No evidence of bile duct dilatation can be identified. 
   Normal size and appearance of GB are noted without evidence of gallstone or 
     focal lesion.
3. Pancreas: 
   Normal size and appearance are noted without definite space occupying lesion.
4. Spleen: 
   Normal size and appearance are noted.
5. Kidney: 
   Normal size and appearance. 
   No dilatation of bilateral pyelocalyceal systems or ureters.
6. Adrenal glands: 
   Normal size and appearance are noted.
7. Urinary bladder: 
   No definite polypoid lesion or focal wall thickening.
8. Prostate gland: 
   - Enlargement of prostate gland is noted with the size measured about __x__x__ cm (estimated about __c.c.). 
   Homogenous hyperintensity of the peripheral zone in T2WI is noted without 
     definite space occupying lesion.
9. Seminal vesicles: 
   Normal size and appearance are noted.
10.Retroperitoneum: 
   No obvious lesion can be depicted.
11.No definite para-aortic or pelvic lymphadenopathy can be identified.
12.No obvious lesion can be identified in the visible bony structures.

)


::mrliv::
(


Other details are mentioned as followings:
----------------------------------------------------------------------
MR Imaging of the liver (_), with intravenous contrast medium(_) injection. 

Parameters:
1) T2WI FS axial images and TruFISP coronal images.
2) T1WI axial images.
3) In-phase and opposed-phase axial images.
4) Dynamic constrast enhanced axial images.
5) Delay phase contrast enhanced T1WI axial images.
6) DWI and ADC.

Imaging findings:
1. Liver: 
   No definite space occupying lesion can be identified.
2. Biliary system: 
   No evidence of bile duct dilatation can be identified. 
   Normal size and appearance of GB are noted without evidence of gallstone or
   focal lesion.
3. Pancreas: 
   Normal size and appearance are noted without definite space occupying lesion.
4. Spleen: 
   Normal size and appearance are noted.
5. Kidney: 
   Normal size and appearance. 
   No dilatation of bilateral pelvicalyceal systems.
6. Adrenal glands: 
   Normal size and appearance are noted.
7. No definite para-aortic lymphadenopathy can be identified.
8. No obvious lesion can be identified in the visible bony structures.

)
::pabdmrf::
(


Other details are mentioned as followings:
----------------------------------------------------------------------
MRI of whole abdomen for tumor screening is performed without and with
intravenous Gd-DOTA enhancement and the parameters as follows:
 without enhancement:
  Turbo spin echo: axial section of upper abdomen and lower abdomen;
                   sagittal section of pelvis; 
  HASTE: axial section of lower abdomen;
  HASTE: coronal section of whole abdomen;
  Chemical shift imaging: axial section of in phase and opposed phase of upper 
                          abdomen and lower abdomen;
  MRCP
  DWI and ADC: axial section of liver.
 with Gd-DOTA enhancement: 
  Dynamic study, four sequences of axial section and one coronal section.

Imaging findings:
1. Liver: 
   No definite space occupying lesion can be identified.
2. Biliary system: 
   No evidence of bile duct dilatation can be identified. 
   Normal size and appearance of GB are noted without evidence of gallstone or 
     focal lesion.
3. Pancreas: 
   Normal size and appearance are noted without definite space occupying lesion.
4. Spleen: 
   Normal size and appearance are noted.
5. Kidney: 
   Normal size and appearance are noted without definite space occupying lesion 
     or dilatation of bilateral pyelocalyceal systems or ureters.
6. Adrenal glands: 
   Normal size and appearance are noted.
7. Urinary bladder: 
   No definite polypoid lesion or focal wall thickening.
8. GYN: 
   Unremarkable
9. Retroperitoneum: 
   No obvious lesion can be depicted.
10. No definite para-aortic or pelvic lymphadenopathy can be identified.
11. No obvious lesion can be identified in the visible bony structures.

)


::@mrcp::
(

Other details are mentioned as followings:
----------------------------------------------------------------------

MR cholangiopancreatography, with intravenous contrast medium injection. 

Compared with previous image: _

Parameters:
1) T2WI FS axial images and TruFISP coronal images.
2) T1WI axial images.
3) In-phase and opposed-phase axial images.
4) Dynamic constrast enhanced axial images.
5) Delay phase contrast enhanced T1WI axial images.
6) DWI and ADC.
7) Coronal heavy T2WI with MIP reconstruction.

Imaging findings:
1. Liver: 
   No definite space occupying lesion can be identified.
2. Biliary system: 
   No evidence of bile duct dilatation can be identified. 
3. Pancreas: 
   Normal size and appearance are noted without definite space occupying lesion.
4. Spleen: 
   Normal size and appearance are noted.
5. Kidney: 
   Normal size and appearance. 
   No dilatation of bilateral pelvicalyceal systems.
6. Adrenal glands: 
   Normal size and appearance are noted.
7. No definite para-aortic lymphadenopathy can be identified.
8. No obvious lesion can be identified in the visible bony structures.

p.s. According to the limitation of MR resolution and motion artifact. Small 
   lesion could be obscured on MRI. Suggest ERCP and close F/U if 
   clinically indicated.
)



;============================================================================================
; Neuro
;============================================================================================
::nrcta::
(
Clinical information: _left side weakness, suspect CVA.
----------------------------------------------------------------------
Pre- and post-contrast CT angiographic images of the brain:
Pre-contrast : 4.8 mm slice thickness from skull base to vertex with MPRs
Arterial phase: 2.0 mm slice thickness from skull base to vertex with axial, coronal, and sagittal plane MIP images
Delayed phase : 5 mm slice thickness from skull base to vertex with MPRs 3D volume rendering view of the circle of Willis
No previous CTA is available for comparison.
----------------------------------------------------------------------
[Imaging findings]
1. Vasular structures:
- No definite CTA evidence of large vessel occlusion (LVO).
- CT perufsion: ( calculated for _left hemisphere ) .
  The infact core = _ ml. The hypoerfusion  = _ ml.
  The mismatch ratio = _
- Intracranial atherosclerosis change.
2. Brain parenchyma:
- No acute intracranial hemorrhage.
3. Ventricle and extra-axial spaces:
- Bilateral ventricular systems are symmetric.
4. Extracranial structures:
- Visualized paranasal sinuses and mastoids are clear.
5. Others:
)
::nrtaibrct::
(
The aim of this CT scan was requested to evaluate a case of ___.

NCCT _and CECT of the brain with axial, coronal, sagittal sections showed:

_- No definite acute intracranial lesion identified. Advise check MR study for further evaluation if clinically indicated.  
_- No definite acute intracranial hemorrhage noted. 

- No definite acute intraparenchymal hemorrhage or acute subdural hemorrhage or acute epidural hemorrhage or acute subarachnoid hemorrhage noted.

_- Intracranial atherosclerosis change.
_- Mild brain atrophy.

_ No strong evidence of hydrocephalus.
 No obvious midline shifting noted.
 Intact white matter and gray matter differentiation of bilateral cerebral hemisphere noted.
 No obvious displaced fracture seen.

_- Post contrast study showed no abnormal enhancing mass lesion in the brain and no abnormal leptomeningeal enhancement noted.
_- Severe motion artifact noted. The intracranial condition could not be well evaluated in this study, some tiny/occult lesion could be underestimated.
)

::nrtaibrctadd::
(
_______Old insults_____________
- Old insult with encephalomalacia change within the left high frontoparietal and right parietal white matter.



_______Acute trauma_____________
_- Bilateral frontal _subdural efffusion with thickness up to 6mm.
_- Suspicious left temporal traumatic SAH. 


- Left orbital floor fracture.
- Left orbital retroocular fat stranding, suggesting traumatic optic neuropathy.
- Left cheek/periorbital/frontal subcutaneous hemorrhage.
- Status post scleral buckling surgery for right retinal detachment.
)

::nrtaibrmr::
(
The aim of this MR study was requested to evaluate a case of ___. 

The MR of the brain performed with sagittal T1WI (localizer)
Axial T1WI, T2WI, FLAIR (Fluid Attenuated Inversion Recovery) 
Coronal T2WI
DWI, ADC map
GE T2*
MRA
_
And post Gd enhancement with axial and coronal T1WI showed:

_
. Subcortical arteriosclerotic encephalopathy.				
. Mild frontotemporal cortical atrophy.				
. _Paranasal sinusitis.				
. _Left_Right otomastoiditis.				

. _Mild intracranial atherosclerosis change.				
. Atherosclerosis change with _presumed_severe thrombotic stenosis of _bilateral_left_right _MCA M1_cavernous ICA_basilar artery.
. Significant thrombotic stenosis of bilateral cavernous ICA, could be consequence of atherosclerosis change or infective vasculitis. Advise clinical correlation and further evaluation.



. No strong evidence of intracranial mass lesion noted in these MR images.				
. No definite abnormal mass lesion over bilateral cerebellopontine angle and internal auditory canal region.


. Bilateral _frontal_frontoparietal subcortical ischemic/infarct or aging related gliotic foci.				
. Old lacune involving _bilateral basal ganglia region,_left_right pons.
_. Old insult with encephalomalacia in bilateral _high frontal and temporal lobes.


_. No strong evidence of hydrocephalus.
. No obvious midline shifting noted.
. Intact white matter and gray matter differentiation of bilateral cerebral hemisphere noted.


_. Post contrast study showed no abnormal enhancing mass lesion in the brain and no abnormal leptomeningeal enhancement noted.
_. The MRA study showed no obvious stenosis or aneurysm lesion in the circle of Willis region.
_. Severe motion artifact noted. The intracranial condition could not be well evaluated in this study, some tiny/occult lesion could be underestimated.



最近打的診斷
1. Acute hemorrhage (1.6*1.8*2.2cm) within the left thalamus/putamen, associated with perifocal edema and mass effect, could be HTN angiopathy or cavernous malformation or amyloid angiopathy or tumor bleeding. Suggest neuroimaging follow-up.
2. Some scattered hemosiderin deposit within the pons and right cerebellum and bilateral thalamus and right parietooccipital subcortical, could be HTN angiopathy or cavernous malformation or amyloid angiopathy.

1. Acute infarct involving left thalamus. 
2. High T2 change within the central pons, probably consequence of prior PRES brainstem variant (posterior reversible encephalopathy syndrome) or demyelination process or central pontine myelinolysis. Advise clinical correlation and further evaluation.

7. Nasopharyngeal Tornwaldt's cyst (5mm).

1. Status post right VP shunting and left craniotomy procedure.

4. Diffuse cerebral pachymeningeal enhancement noted, probably related to postsurgical change.

1. High T2 change within the right optic nerve, suggesting optic neuritis. Suggest clinical check up. 

3. Suspicious left cavernous ICA saccular aneurysm (1.17mm). Suggest MRA follow-up. 

4. Some hemosiderin deposit within the pons, could be HTN angiopathy or cavernous malformation. 


)


::nrhnct::
(
Clinical information:
___

CT of neck ___without and with contrast enhancement showed:

___
- Presence of dilatation of all ventricles and proportional widening of bilateral cerebral sulci. Favored Mild brain atrophy.
- Mild cervical spondylosis.


No mass lesion along the nasopharynx, tonsil, tongue base, or soft palate. 
No mass lesion in the parapharyngeal space and pterygoid plate and muscles. 
The maxillary sinus is unremarkable. 
The parotid gland and submandibular glands are intact.  
No evidence of lymph node enlargement along the neck. 
The thyroid and larynx are unremarkable.

Suggest clinical correlation and follow up.

*** Due to non-contrast enhancing study, some lesions may be obscured.
- Beam hardening artifact at the level of oral cavity. Some lesions may be obscured.

_________ Infection Abscess____________
- Rt peritonsillar abscess with surrounding fat stranding/ edema.
- Hypodense lesion (24*13mm) within enlarged Lt palatine tonsil with peripheral rim enhancement and surrounding fat stranding/ edema.

- Enlargement of Rt parotid gland with heterogeneous enhancement as compared witht Lt parotid gland.
- Mild enlargement of Rt submandibular gland with mild surrounding fat stranding.
- Probably Rt submandibular sialadenitis.


- Some borderline enlarged lymph nodes at bil. neck level _. Probably reactive lymph nodes.
- One enlarged lymph node at Rt neck level II (19mm) with surroundin fat stranding. Probably pyogenic lymphadenitis. DDx: reactive LN.
- Clustered small LNs (<1cm) at Rt neck level II, III, and IV.
Stable the residual lymph nodes (up to 2cm) in bilateral neck level II-V. 

_________ Cancer ____________

- Post-OP/_CCRT _1st neck image study.(about _)
- This study is compared with the previous films. (_2020.11.5.)


Left buccal cancer, pT4N1M0, s/p wide excision with partial maxillectomy, 
 marginal resection of left zygoam and left mandible, selective neck 
 dissection with flap repair, and CCRT.
1.Left buccal cancer s/p wide excision, left partial maxillectomy and marginal
  resection of left zygoam and left mandible, and left selective neck dissection 
  (level I,II,III,IV), and flap repair. No evidence of local tumor recurrence or 
  neck nodal metastasis.


20大癌影像簡碼2014JUN更新版
.NPC:                _NPCCT     _NPCMR
.Oral cavity cancer:  OCACT      OCAMR
.Oropharynx cancer:   OPCT       OPMR
.Hypopharynx cancer:  HPCT       HPMR
.Larynx cancer:       LCACT      LCAMR

)

