;;;============================================================
;;; disease_rules.clp
;;; Owner: Member B (Disease Knowledge Engineer)
;;;
;;; PURPOSE:
;;;   This file contains all disease diagnosis rules for the
;;;   tomato expert system. Rules should be validated against
;;;   literature sources for academic credibility.
;;;
;;; IMPORTANT FOR MEMBER B:
;;;   - Write rules in the DISEASE module
;;;   - Use the predefined fact templates (see below)
;;;   - Each rule should have a meaningful explanation string
;;;   - CF values should be justified from literature
;;;
;;;============================================================

;;;------------------------------------------------------------
;;; FACT TEMPLATES (DO NOT MODIFY - Defined in main_system.clp)
;;;------------------------------------------------------------
;;;
;;; INPUT: Symptoms from user
;;; (symptom
;;;    (name <SYMBOL>)         ; e.g., yellow-leaves, brown-spots
;;;    (severity <SYMBOL>)     ; mild, moderate, severe
;;;    (cf <FLOAT>))           ; certainty [0.0, 1.0]
;;;
;;; OUTPUT: Disease diagnosis
;;; (disease
;;;    (name <SYMBOL>)         ; e.g., early-blight, bacterial-spot
;;;    (cf <FLOAT>)            ; certainty [-1.0, 1.0]
;;;    (explanation <STRING>)) ; reasoning for this conclusion
;;;
;;;------------------------------------------------------------

;;;------------------------------------------------------------
;;; EXPECTED SYMPTOM NAMES (Coordinate with UI - Member A)
;;;------------------------------------------------------------
;;;
;;; Member B should coordinate with Member A to define the
;;; complete list of symptom names. Examples:
;;;
;;;   - yellow-leaves
;;;   - brown-spots
;;;   - wilting
;;;   - leaf-curl
;;;   - fruit-rot
;;;   - stem-lesions
;;;   - mosaic-pattern
;;;   - stunted-growth
;;;   - blossom-end-rot
;;;   - white-powder
;;;
;;; TODO: Finalize symptom list with Member A before writing rules
;;;
;;;------------------------------------------------------------

;;;------------------------------------------------------------
;;; EXPECTED DISEASE NAMES (For Integration - Member A)
;;;------------------------------------------------------------
;;;
;;; Member B should define the complete list of diagnosable
;;; diseases. Examples for tomato:
;;;
;;;   - early-blight (Alternaria solani)
;;;   - late-blight (Phytophthora infestans)
;;;   - bacterial-spot (Xanthomonas spp.)
;;;   - fusarium-wilt (Fusarium oxysporum)
;;;   - tomato-mosaic-virus
;;;   - septoria-leaf-spot
;;;   - powdery-mildew
;;;   - gray-mold (Botrytis cinerea)
;;;
;;; TODO: Finalize disease list and share with Member C for
;;;       disease-nutrient impact mapping
;;;
;;;------------------------------------------------------------

;;;------------------------------------------------------------
;;; RULE WRITING GUIDELINES
;;;------------------------------------------------------------
;;;
;;; 1. Each rule must be in the DISEASE module
;;;
;;; 2. Rule naming convention:
;;;    disease-<disease-name>-<variant>
;;;    Example: disease-early-blight-primary
;;;
;;; 3. Each rule should include:
;;;    - Meaningful symptom combinations
;;;    - Appropriate CF values (with literature justification)
;;;    - Clear explanation string
;;;
;;; 4. CF Value Guidelines:
;;;    - 0.8 - 1.0: Very strong evidence
;;;    - 0.6 - 0.8: Strong evidence
;;;    - 0.4 - 0.6: Moderate evidence
;;;    - 0.2 - 0.4: Weak evidence
;;;    - < 0.2: Very weak evidence
;;;
;;; 5. Example rule structure:
;;;
;;;    (defrule DISEASE::disease-early-blight-primary
;;;       "Diagnose early blight based on characteristic symptoms"
;;;       (symptom (name brown-spots) (severity ?s1))
;;;       (symptom (name yellow-leaves) (severity ?s2))
;;;       (symptom (name concentric-rings) (cf ?cf3))
;;;       =>
;;;       (bind ?combined-cf (* 0.85 ?cf3))  ; Adjust based on evidence
;;;       (assert (disease 
;;;          (name early-blight)
;;;          (cf ?combined-cf)
;;;          (explanation "Early blight diagnosed based on brown spots 
;;;                        with concentric rings and yellowing leaves. 
;;;                        Ref: [Citation]"))))
;;;
;;;------------------------------------------------------------

;;;------------------------------------------------------------
;;; PLACEHOLDER: Disease Diagnosis Rules
;;; TODO: Member B implements actual rules below
;;;------------------------------------------------------------

;;; ============================================================
;;; MEMBER B: ADD YOUR DISEASE RULES BELOW THIS LINE
;;; ============================================================




;;; ============================================================
;;; MEMBER B: ADD YOUR DISEASE RULES ABOVE THIS LINE
;;; ============================================================

;;;============================================================
;;; END OF disease_rules.clp
;;;============================================================
