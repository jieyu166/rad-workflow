
;============================================================================================
; Intervention
;============================================================================================

::ptcd;::
(
Indication: _ with obstructive jaundice.

- PTCD was performed via right _anterolateral approach under sonoguidance and fluoroscopy. An 8 Fr. catheter with self-locking is inserted into the CBD. 
- 5mL bile was aspirated.

_- Cholangiography showed narrowing at CHD, compatible with tumor growth at this location.

The procedure is smooth and the patient stands it well.

Impression: Biliary tree dilatation s/p PTCD.
)


::pcn;::
	; 1. 呼叫通用選擇器 (程式會暫停在這裡等您按按鈕)
    gosub GetSideSelection

    ; 2. (選用) 檢查使用者是否按了取消(X)，如果變數是空的就終止
    if (tSideCap = ""){
        tSideCap := "_"
		tSideLow := "_"
	}
	
	SendInput,
(
Clinical information: %tSideCap% moderate hydronephrosis, requested for PCN insertion.

- Presence of _moderate hydronephrosis of %tSideLow% kidney.

- Under sono-guidance and fluoroscopy, a 8 Fr. pigtail drainage catheter _with self-locking is inserted into %tSideLow% renal pelvis via posteriolateral and calyx approach.
- _ mL urine was aspirated _and sent for further evaluation.
- The procedure was smooth and the patient stood it. No immediate complication
  was noticed.

Impression: 
%tSideCap% PCN insertion was performed smoothly, without immediate complication.
)
	return	
	
::pcnr;::
	; 1. 呼叫通用選擇器 (程式會暫停在這裡等您按按鈕)
    gosub GetSideSelection

    ; 2. (選用) 檢查使用者是否按了取消(X)，如果變數是空的就終止
    if (tSideCap = ""){
        tSideCap := "_"
		tSideLow := "_"
	}

    ; 3. 貼上內容 (使用設定好的變數)
    SendInput,
(
Clinical information/Indication: 
- %tSideCap% hydronephrosis, status post %tSideLow% PCN insertion on 20_. Requested for revision.
- Status post %tSideLow% PCN insertion for a period of time. Requested for regular exchange.
- Previous PCN revision date: 20_.

- Under fluoroscopic guidance, the old PCN catheter was exchanged to a new _ Fr. WITH_ self-locked drainage catheter. The distal tip of the catheter was located in renal pelvis.
- No pulsatile bleeding from the PCN tract during exchange.
- The procedure was smooth and the patient stood it. No immediate complication
  was noticed.

Impression:
%tSideCap% PCN revision was performed smoothly, without immediate complication.
)
return

::ascites;::
(
Clinical information: ascites, requested for drainage.

- Under sono-guidance, a 8 Fr. pigtail drainage catheter was inserted into _right upper abdominal cavity.

The procedure was performed smoothly and the patient stood it well.

Conclusion: Ascites in _RUQ of abdomen s/p sonoguided pigtail catheter drainage.
)
::abscess;::
(
Clinical information: _Liver abscess requested for drainage.

- Under sono-guidance and fluoroscope, a _8 Fr. pigtail drainage catheter was inserted into liver abscess.
- _10ml pus was aspirated.

The procedure was performed smoothly and the patient stood it well.

Conclusion: _Liver abscess in S_ s/p sonoguided pigtail catheter drainage.
)