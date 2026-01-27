;;;============================================================
;;; nutrient_rules.clp
;;; Owner: Member C (Nutrient Knowledge & Evaluation Lead)
;;;
;;; PURPOSE:
;;;   This file contains:
;;;   1. Nutrient deficiency diagnosis rules
;;;   2. Disease-nutrient impact factor definitions
;;;
;;; IMPORTANT FOR MEMBER C:
;;;   - Write nutrient rules in the NUTRIENT module
;;;   - Define impact factors using (disease-nutrient-impact ...) template
;;;   - Each rule should have a meaningful explanation string
;;;   - Impact factors should be justified from literature
;;;
;;;============================================================

;;;------------------------------------------------------------
;;; FACT TEMPLATES (DO NOT MODIFY - Defined in main_system.clp)
;;;------------------------------------------------------------
;;;
;;; INPUT: Symptoms from user
;;; (symptom
;;;    (name <SYMBOL>)         ; e.g., yellow-leaves, interveinal-chlorosis
;;;    (severity <SYMBOL>)     ; mild, moderate, severe
;;;    (cf <FLOAT>))           ; certainty [0.0, 1.0]
;;;
;;; OUTPUT: Nutrient deficiency diagnosis
;;; (nutrient-deficiency
;;;    (name <SYMBOL>)         ; e.g., nitrogen, potassium, calcium
;;;    (cf <FLOAT>)            ; certainty [-1.0, 1.0]
;;;    (explanation <STRING>)) ; reasoning for this conclusion
;;;
;;; DISEASE-NUTRIENT IMPACT (Member C defines these):
;;; (disease-nutrient-impact
;;;    (disease-name <SYMBOL>) ; the diagnosed disease
;;;    (nutrient-name <SYMBOL>); the affected nutrient
;;;    (impact-factor <FLOAT>)); multiplier for CF adjustment
;;;
;;;------------------------------------------------------------

;;;------------------------------------------------------------
;;; EXPECTED NUTRIENT NAMES
;;;------------------------------------------------------------
;;;
;;; Member C should define the complete list of diagnosable
;;; nutrient deficiencies. Examples for tomato:
;;;
;;;   - nitrogen (N)
;;;   - phosphorus (P)
;;;   - potassium (K)
;;;   - calcium (Ca)
;;;   - magnesium (Mg)
;;;   - sulfur (S)
;;;   - iron (Fe)
;;;   - manganese (Mn)
;;;   - zinc (Zn)
;;;   - boron (B)
;;;   - copper (Cu)
;;;   - molybdenum (Mo)
;;;
;;;------------------------------------------------------------

;;;------------------------------------------------------------
;;; NUTRIENT RULE WRITING GUIDELINES
;;;------------------------------------------------------------
;;;
;;; 1. Each rule must be in the NUTRIENT module
;;;
;;; 2. Rule naming convention:
;;;    nutrient-<nutrient-name>-<variant>
;;;    Example: nutrient-nitrogen-deficiency-primary
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
;;;    (defrule NUTRIENT::nutrient-nitrogen-deficiency-primary
;;;       "Diagnose nitrogen deficiency based on characteristic symptoms"
;;;       (symptom (name pale-green-leaves) (severity ?s1))
;;;       (symptom (name stunted-growth) (cf ?cf))
;;;       =>
;;;       (assert (nutrient-deficiency 
;;;          (name nitrogen)
;;;          (cf (* 0.75 ?cf))
;;;          (explanation "Nitrogen deficiency indicated by pale green 
;;;                        leaves and stunted growth. Ref: [Citation]"))))
;;;
;;;------------------------------------------------------------

;;;------------------------------------------------------------
;;; DISEASE-NUTRIENT IMPACT FACTOR GUIDELINES
;;;------------------------------------------------------------
;;;
;;; PURPOSE:
;;;   Impact factors define how a disease diagnosis affects the
;;;   certainty of nutrient deficiency recommendations.
;;;
;;; FORMULA (applied in integration.clp):
;;;   Adjusted_Nutrient_CF = Base_Nutrient_CF × Disease_Impact_Factor
;;;
;;; IMPACT FACTOR INTERPRETATION:
;;;   - 1.0: No impact (neutral)
;;;   - > 1.0: Disease increases likelihood of deficiency (max ~1.5)
;;;   - < 1.0: Disease decreases likelihood of deficiency (min ~0.5)
;;;   - 0.0: Disease completely negates the deficiency signal
;;;
;;; EXAMPLE IMPACT FACTORS:
;;;
;;;   (deffacts NUTRIENT::disease-nutrient-impacts
;;;      "Disease-nutrient impact factor definitions"
;;;      
;;;      ; Early blight may increase calcium deficiency signal
;;;      (disease-nutrient-impact
;;;         (disease-name early-blight)
;;;         (nutrient-name calcium)
;;;         (impact-factor 1.2))
;;;      
;;;      ; Fusarium wilt may affect nitrogen uptake
;;;      (disease-nutrient-impact
;;;         (disease-name fusarium-wilt)
;;;         (nutrient-name nitrogen)
;;;         (impact-factor 0.8))
;;;      
;;;      ; Blossom end rot strongly linked to calcium
;;;      (disease-nutrient-impact
;;;         (disease-name blossom-end-rot)
;;;         (nutrient-name calcium)
;;;         (impact-factor 1.5)))
;;;
;;; IMPORTANT:
;;;   - All impact factors must be justified with literature
;;;   - Document the reasoning for each factor value
;;;   - Share the final list with Member A for integration testing
;;;
;;;------------------------------------------------------------

;;;------------------------------------------------------------
;;; PLACEHOLDER: Disease-Nutrient Impact Factors
;;; TODO: Member C implements actual impact factors below
;;;------------------------------------------------------------

;;; ============================================================
;;; MEMBER C: ADD YOUR IMPACT FACTORS BELOW THIS LINE
;;; ============================================================

(deffacts NUTRIENT::disease-nutrient-impacts
   "Disease-nutrient impact factor definitions"
   ;; TODO: Member C adds actual impact factors here
   ;; Example format:
   ;; (disease-nutrient-impact
   ;;    (disease-name <disease>)
   ;;    (nutrient-name <nutrient>)
   ;;    (impact-factor <float>))
)

;;; ============================================================
;;; MEMBER C: ADD YOUR IMPACT FACTORS ABOVE THIS LINE
;;; ============================================================

;;;------------------------------------------------------------
;;; PLACEHOLDER: Nutrient Deficiency Rules
;;; TODO: Member C implements actual rules below
;;;------------------------------------------------------------

;;; ============================================================
;;; MEMBER C: ADD YOUR NUTRIENT RULES BELOW THIS LINE
;;; ============================================================




;;; ============================================================
;;; MEMBER C: ADD YOUR NUTRIENT RULES ABOVE THIS LINE
;;; ============================================================

;;;============================================================
;;; END OF nutrient_rules.clp
;;;============================================================
