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

;;;============================================================
;;; Disease helper functions
;;;============================================================

(deffacts MAIN::disease-symptom-table

;; ================= EARLY BLIGHT =================
(disease-symptom (disease early-blight) (symptom brown-leaf-spots)   (role core) (cf 0.85))
(disease-symptom (disease early-blight) (symptom yellow-halos)       (role core) (cf 0.85))
(disease-symptom (disease early-blight) (symptom bulls-eye-pattern)  (role core) (cf 0.85))
(disease-symptom (disease early-blight) (symptom lower-leaves-first) (role core) (cf 0.85))
(disease-symptom (disease early-blight) (symptom dark-fruit-lesions) (role core) (cf 0.85))

;; ================= SEPTORIA =================
(disease-symptom (disease septoria) (symptom small-gray-tan-spots) (role core) (cf 0.85))
(disease-symptom (disease septoria) (symptom dark-spot-margins)    (role core) (cf 0.85))

;; ================= LATE BLIGHT =================
(disease-symptom (disease late-blight) (symptom water-soaked-blotches) (role core)    (cf 0.55))
(disease-symptom (disease late-blight) (symptom oily-fruit-lesions)    (role core)    (cf 0.55))
(disease-symptom (disease late-blight) (symptom rapid-leaf-browning)   (role support) (cf 0.55))

;; ================= FUSARIUM =================
(disease-symptom (disease fusarium) (symptom lower-leaf-yellowing) (role core)    (cf 0.65))
(disease-symptom (disease fusarium) (symptom stem-discoloration)   (role core)    (cf 0.65))
(disease-symptom (disease fusarium) (symptom plant-wilting)        (role support) (cf 0.65))
(disease-symptom (disease fusarium) (symptom bottom-up-collapse)   (role support) (cf 0.45))

;; ================= MOSAIC =================
(disease-symptom (disease mosaic) (symptom leaf-mottling)   (role core)    (cf 0.45))
(disease-symptom (disease mosaic) (symptom leaf-distortion) (role core)    (cf 0.45))
(disease-symptom (disease mosaic) (symptom stunted-growth)  (role support) (cf 0.45))

;; ================= BACTERIAL =================
(disease-symptom (disease bacterial) (symptom small-dark-spots) (role core)    (cf 0.45))
(disease-symptom (disease bacterial) (symptom spots-merging)    (role core)    (cf 0.45))
(disease-symptom (disease bacterial) (symptom leaf-yellowing)   (role support) (cf 0.45))
(disease-symptom (disease bacterial) (symptom leaf-drop)        (role support) (cf 0.45))
)

;;;============================================================
;;; Probabilistic OR
;;;============================================================

(deffunction DISEASE::prob-or ($?cfs)
   (bind ?p 1.0)

   (foreach ?cf $?cfs
      (bind ?p (* ?p (- 1.0 ?cf)))
   )

   (- 1.0 ?p)
)

;;;============================================================
;;; Constants
;;;============================================================

(defglobal
   ?*RULE-CF-STRONG* = 0.9
   ?*RULE-CF-MEDIUM* = 0.7
   ?*RULE-CF-WEAK*   = 0.45
)

;;;============================================================
;;; EARLY BLIGHT (No Support)
;;; Core: brown-leaf-spots, yellow-halos, bulls-eye-pattern, ;;; lower-leaves-first, dark-fruit-lesions
;;;============================================================

(defrule DISEASE::early-blight-strong
   (declare (salience 30))
   (not (disease (name early-blight)))

   (symptom (name ?s1))
   (symptom (name ?s2))

   (disease-symptom (disease early-blight) (symptom ?s1) (role core) (cf ?c1))
   (disease-symptom (disease early-blight) (symptom ?s2) (role core) (cf ?c2))

   (test (neq ?s1 ?s2))
=>
   (assert (disease
      (name early-blight)
      (cf (* (min ?c1 ?c2) ?*RULE-CF-STRONG*))
      (explanation "Early blight: multiple core symptoms.")
      (evidence (create$ ?s1 ?s2))))
)

(defrule DISEASE::early-blight-weak
   (declare (salience 10))
   (not (disease (name early-blight)))

   (symptom (name ?s))

   (disease-symptom (disease early-blight) (symptom ?s) (role core) (cf ?cf))
=>
   (assert (disease
      (name early-blight)
      (cf (* ?cf ?*RULE-CF-WEAK*))
      (explanation "Early blight: single core symptom.")
      (evidence (create$ ?s))))
)

;;;============================================================
;;; SEPTORIA (No Support)
;;; Core: small-gray-tan-spots, dark-spot-margins
;;;============================================================

(defrule DISEASE::septoria-strong
   (declare (salience 30))
   (not (disease (name septoria-leaf-spot)))

   (symptom (name ?s1))
   (symptom (name ?s2))

   (disease-symptom (disease septoria) (symptom ?s1) (role core) (cf ?c1))
   (disease-symptom (disease septoria) (symptom ?s2) (role core) (cf ?c2))

   (test (neq ?s1 ?s2))
=>
   (assert (disease
      (name septoria-leaf-spot)
      (cf (* (min ?c1 ?c2) ?*RULE-CF-STRONG*))
      (explanation "Septoria: multiple core symptoms.")
      (evidence (create$ ?s1 ?s2))))
)

(defrule DISEASE::septoria-weak
   (declare (salience 10))
   (not (disease (name septoria-leaf-spot)))

   (symptom (name ?s))

   (disease-symptom (disease septoria) (symptom ?s) (role core) (cf ?cf))
=>
   (assert (disease
      (name septoria-leaf-spot)
      (cf (* ?cf ?*RULE-CF-WEAK*))
      (explanation "Septoria: single core symptom.")
      (evidence (create$ ?s))))
)

;;;============================================================
;;; LATE BLIGHT
;;; Core: water-soaked-blotches, oily-fruit-lesions 
;;; Support: rapid-leaf-browning
;;;============================================================

(defrule DISEASE::late-blight-strong
   (declare (salience 30))
   (not (disease (name late-blight)))

   (symptom (name ?s1))
   (symptom (name ?s2))

   (disease-symptom (disease late-blight) (symptom ?s1) (role core) (cf ?c1))
   (disease-symptom (disease late-blight) (symptom ?s2) (role core) (cf ?c2))

   (test (neq ?s1 ?s2))
=>
   (assert (disease
      (name late-blight)
      (cf (* (min ?c1 ?c2) ?*RULE-CF-STRONG*))
      (explanation "Late blight: multiple core symptoms.")
      (evidence (create$ ?s1 ?s2))))
)

(defrule DISEASE::late-blight-weak
   (declare (salience 10))
   (not (disease (name late-blight)))

   (symptom (name ?s))

   (disease-symptom (disease late-blight) (symptom ?s) (role core) (cf ?cf))
=>
   (assert (disease
      (name late-blight)
      (cf (* ?cf ?*RULE-CF-WEAK*))
      (explanation "Late blight: single core symptom.")
      (evidence (create$ ?s))))
)

;;;============================================================
;;; FUSARIUM
;;; Core: lower-leaf-yellowing, stem-discoloration 
;;; Support: plant-wilting, bottom-up-collapse
;;;============================================================

(defrule DISEASE::fusarium-strong
   (declare (salience 30))
   (not (disease (name fusarium-wilt)))

   (symptom (name ?s1))
   (symptom (name ?s2))

   (disease-symptom (disease fusarium) (symptom ?s1) (role core) (cf ?c1))
   (disease-symptom (disease fusarium) (symptom ?s2) (role core) (cf ?c2))

   (test (neq ?s1 ?s2))
=>
   (assert (disease
      (name fusarium-wilt)
      (cf (* (min ?c1 ?c2) ?*RULE-CF-STRONG*))
      (explanation "Fusarium: multiple core symptoms.")
      (evidence (create$ ?s1 ?s2))))
)

(defrule DISEASE::fusarium-medium
   (declare (salience 20))

   (not (disease (name fusarium-wilt)))

   ;; One core
   (symptom (name ?c))

   ;; Two supports
   (symptom (name ?s1))
   (symptom (name ?s2))

   ;; Core lookup
   (disease-symptom
      (disease fusarium)
      (symptom ?c)
      (role core)
      (cf ?cfc))

   ;; Support lookup
   (disease-symptom
      (disease fusarium)
      (symptom ?s1)
      (role support)
      (cf ?cf1))

   (disease-symptom
      (disease fusarium)
      (symptom ?s2)
      (role support)
      (cf ?cf2))

   ;; Make sure supports differ
   (test (neq ?s1 ?s2))
=>
   (bind ?agg (min ?cfc ?cf1 ?cf2))
   (bind ?final (* ?agg ?*RULE-CF-MEDIUM*))

   (assert
      (disease
         (name fusarium-wilt)
         (cf ?final)
         (explanation "Fusarium: core + two supporting symptoms.")
         (evidence (create$ ?c ?s1 ?s2))))
)


(defrule DISEASE::fusarium-weak
   (declare (salience 10))
   (not (disease (name fusarium-wilt)))

   (symptom (name ?s))

   (disease-symptom (disease fusarium) (symptom ?s) (role core) (cf ?cf))
=>
   (assert (disease
      (name fusarium-wilt)
      (cf (* ?cf ?*RULE-CF-WEAK*))
      (explanation "Fusarium: single core symptom.")
      (evidence (create$ ?s))))
)

;;;============================================================
;;; MOSAIC
;;; Core: leaf-mottling, leaf-distortion 
;;; Support: stunted-growth
;;;============================================================

(defrule DISEASE::mosaic-strong
   (declare (salience 30))
   (not (disease (name mosaic-virus)))

   (symptom (name ?s1))
   (symptom (name ?s2))

   (disease-symptom (disease mosaic) (symptom ?s1) (role core) (cf ?c1))
   (disease-symptom (disease mosaic) (symptom ?s2) (role core) (cf ?c2))

   (test (neq ?s1 ?s2))
=>
   (bind ?agg (prob-or ?c1 ?c2))

   (assert (disease
      (name mosaic-virus)
      (cf (* ?agg ?*RULE-CF-STRONG*))
      (explanation "Mosaic: multiple core symptoms.")
      (evidence (create$ ?s1 ?s2))))
)

(defrule DISEASE::mosaic-weak
   (declare (salience 10))
   (not (disease (name mosaic-virus)))

   (symptom (name ?s))

   (disease-symptom (disease mosaic) (symptom ?s) (role core) (cf ?cf))
=>
   (assert (disease
      (name mosaic-virus)
      (cf (* ?cf ?*RULE-CF-WEAK*))
      (explanation "Mosaic: single core symptom.")
      (evidence (create$ ?s))))
)

;;;============================================================
;;; BACTERIAL
;;; Core: small-dark-spots, spots-merging 
;;; Support: leaf-yellowing, leaf-drop
;;;============================================================

(defrule DISEASE::bacterial-strong
   (declare (salience 30))
   (not (disease (name bacterial-spot)))

   (symptom (name ?s1))
   (symptom (name ?s2))

   (disease-symptom (disease bacterial) (symptom ?s1) (role core) (cf ?c1))
   (disease-symptom (disease bacterial) (symptom ?s2) (role core) (cf ?c2))

   (test (neq ?s1 ?s2))
=>
   (bind ?agg (prob-or ?c1 ?c2))

   (assert (disease
      (name bacterial-spot)
      (cf (* ?agg ?*RULE-CF-STRONG*))
      (explanation "Bacterial: multiple core symptoms.")
      (evidence (create$ ?s1 ?s2))))
)

(defrule DISEASE::bacterial-medium
   (declare (salience 20))

   (not (disease (name bacterial-spot)))

   ;; One core
   (symptom (name ?c))

   ;; Two supports
   (symptom (name ?s1))
   (symptom (name ?s2))

   ;; Core lookup
   (disease-symptom
      (disease bacterial)
      (symptom ?c)
      (role core)
      (cf ?cfc))

   ;; Support lookup
   (disease-symptom
      (disease bacterial)
      (symptom ?s1)
      (role support)
      (cf ?cf1))

   (disease-symptom
      (disease bacterial)
      (symptom ?s2)
      (role support)
      (cf ?cf2))

   (test (neq ?s1 ?s2))
=>
   (bind ?agg (prob-or ?cfc ?cf1 ?cf2))
   (bind ?final (* ?agg ?*RULE-CF-MEDIUM*))

   (assert
      (disease
         (name bacterial-spot)
         (cf ?final)
         (explanation "Bacterial: core + two supporting symptoms.")
         (evidence (create$ ?c ?s1 ?s2))))
)


(defrule DISEASE::bacterial-weak
   (declare (salience 10))
   (not (disease (name bacterial-spot)))

   (symptom (name ?s))

   (disease-symptom (disease bacterial) (symptom ?s) (role core) (cf ?cf))
=>
   (assert (disease
      (name bacterial-spot)
      (cf (* ?cf ?*RULE-CF-WEAK*))
      (explanation "Bacterial: single core symptom.")
      (evidence (create$ ?s))))
)



;;; ============================================================
;;; MEMBER B: ADD YOUR DISEASE RULES ABOVE THIS LINE
;;; ============================================================

;;;============================================================
;;; END OF disease_rules.clp
;;;============================================================
