;;;============================================================
;;; integration.clp
;;; CROSS-DOMAIN INTEGRATION & CONFLICT RESOLUTION LAYER
;;;============================================================
;;;
;;; This module implements the "Integration Strategy" defined in
;;; Chapter 3.4.3. It bridges the gap between the Disease Knowledge Base
;;; and the Nutrient Knowledge Base.
;;;
;;; [Integration Model: Disease-Nutrient Interaction]
;;; Scientific literature suggests that disease stress alters plant
;;; nutrient uptake. This system models usage via a declarative
;;; impact factor approach.
;;;
;;; Mathematical Model for CF Adjustment:
;;; --------------------------------------
;;; CF_adjusted = CF_base * Impact_Factor
;;;
;;; Where:
;;; - CF_base: Initial confidence from nutrient symptoms/growth stage.
;;; - Impact_Factor: Multiplier defined by domain experts (e.g., 1.2, 0.7).
;;;
;;; [Rationale]
;;; By decoupling the interaction logic from the core diagnosis rules,
;;; we maintain modularity. The nutrient rules do not need to "know"
;;; about diseases directly; this layer handles the modification.
;;;
;;; [Conflict Resolution Strategy]
;;; If multiple competing diagnoses exist within a domain (e.g., two
;;; diseases identified), the system applies a "Maximum Confidence"
;;; heuristic (Highest CF wins) to select the final output.
;;;
;;;============================================================

;;;------------------------------------------------------------
;;; CF Adjustment Rules (INTEGRATION Module)
;;; [Knowledge Part]: Cross-domain integration logic defining how
;;; diseases influence nutrient deficiency confidence.
;;;------------------------------------------------------------

;;; Apply disease impact to nutrient CF
;;; This rule reads impact factors defined by Member C
(defrule INTEGRATION::apply-disease-impact
   "Adjust nutrient CF based on disease impact factor"
   (declare (salience 50))
   
   ; A disease has been diagnosed
   (disease (name ?disease-name) (cf ?disease-cf))
   
   ; An impact factor exists for this disease-nutrient pair
   ; (Defined by Member C in nutrient_rules.clp or separate impact file)
   (disease-nutrient-impact 
      (disease-name ?disease-name)
      (nutrient-name ?nutrient-name)
      (impact-factor ?impact))
   
   ; A nutrient deficiency has been identified (base CF)
   (nutrient-deficiency (name ?nutrient-name) (cf ?base-cf))
   
   ; Haven't already adjusted this nutrient for this disease
   (not (adjusted-nutrient-cf 
           (nutrient-name ?nutrient-name) 
           (applied-disease ?disease-name)))
   =>
   ; Calculate adjusted CF
   (bind ?adjusted-cf (* ?base-cf ?impact))
   
   ; Clamp CF to valid range [-1.0, 1.0]
   (if (> ?adjusted-cf 1.0) then (bind ?adjusted-cf 1.0))
   (if (< ?adjusted-cf -1.0) then (bind ?adjusted-cf -1.0))
   
   ; Assert the adjusted CF
   (assert (adjusted-nutrient-cf
              (nutrient-name ?nutrient-name)
              (original-cf ?base-cf)
              (adjusted-cf ?adjusted-cf)
              (applied-disease ?disease-name)
              (impact-factor ?impact))))

;;; Handle nutrients without disease impact
;;; If no impact factor exists, keep original CF
(defrule INTEGRATION::no-disease-impact
   "Preserve nutrient CF when no disease impact applies"
   (declare (salience 40))
   
   ; A nutrient deficiency exists
   (nutrient-deficiency (name ?nutrient-name) (cf ?base-cf))
   
   ; No impact factor defined for this nutrient
   (not (disease-nutrient-impact (nutrient-name ?nutrient-name)))
   
   ; Not already processed
   (not (adjusted-nutrient-cf (nutrient-name ?nutrient-name)))
   =>
   ; Keep original CF (impact factor = 1.0)
   (assert (adjusted-nutrient-cf
              (nutrient-name ?nutrient-name)
              (original-cf ?base-cf)
              (adjusted-cf ?base-cf)
              (applied-disease none)
              (impact-factor 1.0))))

;;;------------------------------------------------------------
;;; Conflict Resolution Rules (RESOLUTION Module)
;;;------------------------------------------------------------

;;; Resolve disease conflicts: highest CF wins
(defrule RESOLUTION::resolve-disease-conflict
   "Select the disease with highest CF as final diagnosis"
   (declare (salience 50))
   
   ; A disease conclusion exists
   (disease (name ?name1) (cf ?cf1) (explanation ?exp1))
   
   ; No other disease has higher CF
   (not (disease (name ?name2&~?name1) (cf ?cf2&:(> ?cf2 ?cf1))))
   
   ; Not already resolved
   (not (final-disease))
   =>
   (printout t "RESOLUTION: Selecting disease " ?name1 " with CF " ?cf1 crlf)
   (assert (final-disease 
              (name ?name1) 
              (cf ?cf1) 
              (explanation ?exp1))))

;;; Resolve nutrient conflicts: highest CF wins (Updated for Member C's schema)
(defrule RESOLUTION::resolve-nutrient-conflict
   "Select the nutrient with highest final CF as recommendation"
   (declare (salience 50))
   
   ; A final nutrient calculation exists (from Member C)
   (nutrient-final (name ?name1) (cf ?cf1))
   
   ; No other nutrient has higher CF
   (not (nutrient-final (name ?name2&~?name1) (cf ?cf2&:(> ?cf2 ?cf1))))
   
   ; Not already resolved
   (not (final-nutrient))
   =>
   (assert (final-nutrient 
              (name ?name1) 
              (cf ?cf1) 
              (explanation "Diagnosis based on integration of growth stage, disease context, and symptoms."))))

;;; Handle case: no disease diagnosed
(defrule RESOLUTION::no-disease-found
   "Handle case when no disease is diagnosed"
   (declare (salience 30))
   
   (not (disease (name ?)))
   (not (final-disease))
   =>
   (assert (final-disease 
              (name none) 
              (cf 0.0) 
              (explanation "No disease detected based on provided symptoms."))))

;;; Handle case: no nutrient deficiency found (Updated for Member C's schema)
(defrule RESOLUTION::no-nutrient-found
   "Handle case when no nutrient deficiency is identified"
   (declare (salience 30))
   
   (not (nutrient-final (name ?)))
   (not (final-nutrient))
   =>
   (assert (final-nutrient 
              (name none) 
              (cf 0.0) 
              (explanation "No nutrient deficiency detected based on provided symptoms."))))

;;;------------------------------------------------------------
;;; CF Combination Helper (for use in rules)
;;;------------------------------------------------------------

;;; Note: Complex CF combination logic is implemented in Python
;;; (cf_utils.py) and can be called via CLIPSPY if needed.
;;; 
;;; Standard CF Combination Formula:
;;;   If CF1 > 0 and CF2 > 0:
;;;     CF_combined = CF1 + CF2 * (1 - CF1)
;;;   If CF1 < 0 and CF2 < 0:
;;;     CF_combined = CF1 + CF2 * (1 + CF1)
;;;   Otherwise:
;;;     CF_combined = (CF1 + CF2) / (1 - min(|CF1|, |CF2|))

;;;============================================================
;;; END OF integration.clp
;;;============================================================
