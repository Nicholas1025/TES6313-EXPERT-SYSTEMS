;;;============================================================
;;; nutrient_rules.clp
;;; Owner: Member C (Nutrient Knowledge Engineer)
;;; Purpose: Nutrient deficiency diagnosis with CF integration
;;;          using rule-based forward chaining
;;;
;;; RULE EXECUTION ORDER:
;;; 1. Growth-stage base nutrient rules (Salience 30)
;;; 2. Disease-context modifier rules (Salience 25)
;;; 3. Symptom-based evidence rules (Salience 15)
;;; 4. Weak symptom reinforcement (Salience 14)
;;; 5. Symptom CF aggregation (Salience 13)
;;; 6. Final CF integration using min() (Salience -50)
;;;
;;; CONSTRAINT VERIFICATION:
;;; - No duplicate CF counting
;;; - Disease rules only MODIFY existing nutrients (never assert new ones)
;;; - Symptom rules ASSERT symptom-cf facts (never modify nutrient facts)
;;; - Weak symptom reinforcement uses formula: 1 - Π(1 - CFi)
;;; - Final CF = min(Base CF, Disease-Adjusted CF, Symptom CF)
;;;
;;; REFERENCE STANDARDS:
;;; - Mengel & Kirkby (2001) - Mineral nutrition of plants
;;; - Marschner (2012) - Plant mineral nutrition
;;;
;;; LOADING NOTES:
;;; - This file should be loaded after main_system.clp
;;; - All required templates are defined in main_system.clp
;;; - Do not redefine templates here to avoid conflicts
;;;============================================================

;;;------------------------------------------------------------
;;; GROWTH-STAGE BASE NUTRIENT RULES (Salience 30)
;;; 
;;; PURPOSE:
;;; Assert initial nutrient CF values based on tomato growth stage
;;; according to physiological demand curves.
;;;
;;; CONSTRAINT:
;;; These rules establish the foundation for all subsequent CF
;;; adjustments. Salience 30 ensures they execute first.
;;; Do NOT modify these rules.
;;;------------------------------------------------------------

(defrule NUTRIENT::growth-stage-rooting-phosphorus
   (declare (salience 30))
   (growth-stage (name rooting))
   (not (nutrient (name P)))
   =>
   (assert (nutrient (name P) (cf 0.85) (base-cf 0.85) (modified no)))
   (printout t "RULE FIRED [Salience 30]: Growth stage rooting → Nutrients asserted (P=0.85)" crlf))

(defrule NUTRIENT::growth-stage-vegetative-nitrogen
   (declare (salience 30))
   (growth-stage (name vegetative))
   (not (nutrient (name N)))
   =>
   (assert (nutrient (name N) (cf 0.85) (base-cf 0.85) (modified no)))
   (printout t "RULE FIRED [Salience 30]: Growth stage vegetative → Nutrients asserted (N=0.85)" crlf))

(defrule NUTRIENT::growth-stage-flowering-potassium
   (declare (salience 30))
   (growth-stage (name flowering))
   (not (nutrient (name K)))
   =>
   (assert (nutrient (name K) (cf 0.85) (base-cf 0.85) (modified no)))
   (printout t "RULE FIRED [Salience 30]: Growth stage flowering → Nutrients asserted (K=0.85)" crlf))

(defrule NUTRIENT::growth-stage-flowering-calcium
   (declare (salience 30))
   (growth-stage (name flowering))
   (nutrient (name K) (cf 0.85))
   (not (nutrient (name Ca) (cf 0.85)))
   =>
   (assert (nutrient (name Ca) (cf 0.85) (base-cf 0.85) (modified no)))
   (printout t "RULE FIRED [Salience 30]: Growth stage flowering → Nutrients asserted (Ca=0.85)" crlf))

(defrule NUTRIENT::growth-stage-fruiting-potassium
   (declare (salience 30))
   (growth-stage (name fruiting))
   (not (nutrient (name K)))
   =>
   (assert (nutrient (name K) (cf 0.90) (base-cf 0.90) (modified no)))
   (printout t "RULE FIRED [Salience 30]: Growth stage fruiting → Nutrients asserted (K=0.90)" crlf))

(defrule NUTRIENT::growth-stage-fruiting-calcium
   (declare (salience 30))
   (growth-stage (name fruiting))
   (nutrient (name K) (cf 0.90))
   (not (nutrient (name Ca) (cf 0.90)))
   =>
   (assert (nutrient (name Ca) (cf 0.90) (base-cf 0.90) (modified no)))
   (printout t "RULE FIRED [Salience 30]: Growth stage fruiting → Nutrients asserted (Ca=0.90)" crlf))

;;;------------------------------------------------------------
;;; DISEASE-CONTEXT MODIFIER RULES (Salience 25)
;;;
;;; PURPOSE:
;;; Modify nutrient CF values based on disease presence.
;;; Uses multiplication with capping to ensure CF stays within bounds.
;;;
;;; CONSTRAINT:
;;; These rules MODIFY existing nutrient facts only.
;;; They do NOT assert new nutrient facts.
;;; Salience 25 ensures they execute after growth-stage rules.
;;; Do NOT modify these rules.
;;;------------------------------------------------------------

(defrule NUTRIENT::disease-fusarium-nitrogen-reduction
   (declare (salience 25))
   (disease (name fusarium-wilt) (cf ?dcf&:(>= ?dcf 0.7)))
   ?nFact <- (nutrient (name N) (cf ?ncf&:(> ?ncf 0.1)) (base-cf ?nbcf) (modified no))
   =>
   (bind ?adjusted (* ?ncf 0.7))
   (modify ?nFact (cf ?adjusted) (modified yes))
   (printout t "RULE FIRED [Salience 25]: Fusarium → N CF reduced (×0.7)" crlf))

(defrule NUTRIENT::disease-fusarium-potassium-increase
   (declare (salience 25))
   (disease (name fusarium-wilt) (cf ?dcf&:(>= ?dcf 0.7)))
   ?kFact <- (nutrient (name K) (cf ?kcf) (base-cf ?kbcf) (modified no))
   =>
   (bind ?adjusted (min ?kbcf (* ?kcf 1.2)))
   (modify ?kFact (cf ?adjusted) (modified yes))
   (printout t "RULE FIRED [Salience 25]: Fusarium → K CF increased (×1.2, capped at base)" crlf))

(defrule NUTRIENT::disease-fusarium-calcium-increase
   (declare (salience 25))
   (disease (name fusarium-wilt) (cf ?dcf&:(>= ?dcf 0.7)))
   ?caFact <- (nutrient (name Ca) (cf ?cacf) (base-cf ?cabcf) (modified no))
   =>
   (bind ?adjusted (min ?cabcf (* ?cacf 1.1)))
   (modify ?caFact (cf ?adjusted) (modified yes))
   (printout t "RULE FIRED [Salience 25]: Fusarium → Ca CF increased (×1.1, capped at base)" crlf))

(defrule NUTRIENT::disease-mosaic-nitrogen-support
   (declare (salience 25))
   (disease (name mosaic-virus) (cf ?dcf&:(>= ?dcf 0.7)))
   ?nFact <- (nutrient (name N) (cf ?ncf) (base-cf ?nbcf) (modified no))
   =>
   (bind ?adjusted (min ?nbcf (* ?ncf 1.1)))
   (modify ?nFact (cf ?adjusted) (modified yes))
   (printout t "RULE FIRED [Salience 25]: Mosaic → N CF supported (×1.1, capped at base)" crlf))

(defrule NUTRIENT::disease-early-blight-nitrogen-reduction
   (declare (salience 25))
   (disease (name early-blight) (cf ?dcf&:(>= ?dcf 0.7)))
   ?nFact <- (nutrient (name N) (cf ?ncf) (base-cf ?nbcf) (modified no))
   =>
   (bind ?adjusted (* ?ncf 0.8))
   (modify ?nFact (cf ?adjusted) (modified yes))
   (printout t "RULE FIRED [Salience 25]: Early blight → N CF reduced (×0.8)" crlf))

(defrule NUTRIENT::disease-early-blight-potassium-support
   (declare (salience 25))
   (disease (name early-blight) (cf ?dcf&:(>= ?dcf 0.7)))
   ?kFact <- (nutrient (name K) (cf ?kcf) (base-cf ?kbcf) (modified no))
   =>
   (bind ?adjusted (min ?kbcf (* ?kcf 1.1)))
   (modify ?kFact (cf ?adjusted) (modified yes))
   (printout t "RULE FIRED [Salience 25]: Early blight → K CF supported (×1.1, capped at base)" crlf))

;;;------------------------------------------------------------
;;; SYMPTOM-BASED EVIDENCE RULES (Salience 15)
;;; Asserts symptom-cf facts WITHOUT modifying nutrient
;;;
;;; CRITICAL CONSTRAINTS:
;;; - Symptom rules ASSERT symptom-cf facts only
;;; - Do NOT modify nutrient CF directly
;;; - Symptom CF values (strong=0.85, common=0.65, weak=0.45)
;;; - These facts are aggregated and integrated in final phase
;;;  
;;; NOTE: These rules fire AFTER disease rules (salience 25)
;;;------------------------------------------------------------

;;;========== NITROGEN SYMPTOM RULES ==========

(defrule NUTRIENT::symptom-nitrogen-lower-leaf-yellowing
   (declare (salience 15))
   (symptom (name lower-leaf-yellowing))
   (nutrient (name N))
   (not (symptom-cf (nutrient N) (cf 0.85)))
   =>
   (assert (symptom-cf (nutrient N) (cf 0.85)))
   (printout t "RULE FIRED [Salience 15]: Symptom lower-leaf-yellowing → N symptom-cf=0.85 (strong indicator)" crlf))

(defrule NUTRIENT::symptom-nitrogen-leaf-yellowing
   (declare (salience 15))
   (symptom (name leaf-yellowing))
   (not (symptom (name lower-leaf-yellowing)))
   (nutrient (name N))
   (not (symptom-cf (nutrient N) (cf 0.85)))
   =>
   (assert (symptom-cf (nutrient N) (cf 0.65)))
   (printout t "RULE FIRED [Salience 15]: Symptom leaf-yellowing → N symptom-cf=0.65 (common indicator)" crlf))

(defrule NUTRIENT::symptom-nitrogen-stunted-growth
   (declare (salience 15))
   (symptom (name stunted-growth))
   (nutrient (name N))
   =>
   (assert (symptom-cf (nutrient N) (cf 0.65)))
   (printout t "RULE FIRED [Salience 15]: Symptom stunted-growth → N symptom-cf=0.65 (common indicator)" crlf))

(defrule NUTRIENT::symptom-nitrogen-thin-stems
   (declare (salience 15))
   (symptom (name thin-stems))
   (nutrient (name N))
   =>
   (assert (symptom-cf (nutrient N) (cf 0.45)))
   (printout t "RULE FIRED [Salience 15]: Symptom thin-stems → N symptom-cf=0.45 (weak indicator)" crlf))

;;;========== PHOSPHORUS SYMPTOM RULES ==========

(defrule NUTRIENT::symptom-phosphorus-stunted-growth
   (declare (salience 15))
   (symptom (name stunted-growth))
   (nutrient (name P))
   =>
   (assert (symptom-cf (nutrient P) (cf 0.85)))
   (printout t "RULE FIRED [Salience 15]: Symptom stunted-growth → P symptom-cf=0.85 (strong indicator)" crlf))

(defrule NUTRIENT::symptom-phosphorus-dark-green-purplish-leaves
   (declare (salience 15))
   (symptom (name dark-green-or-purplish-leaves))
   (nutrient (name P))
   =>
   (assert (symptom-cf (nutrient P) (cf 0.85)))
   (printout t "RULE FIRED [Salience 15]: Symptom dark-green-or-purplish-leaves → P symptom-cf=0.85 (strong indicator)" crlf))

(defrule NUTRIENT::symptom-phosphorus-delayed-flowering
   (declare (salience 15))
   (symptom (name delayed-flowering))
   (nutrient (name P))
   =>
   (assert (symptom-cf (nutrient P) (cf 0.65)))
   (printout t "RULE FIRED [Salience 15]: Symptom delayed-flowering → P symptom-cf=0.65 (common indicator)" crlf))

;;;========== POTASSIUM SYMPTOM RULES ==========

(defrule NUTRIENT::symptom-potassium-leaf-edge-scorching
   (declare (salience 15))
   (symptom (name leaf-edge-scorching))
   (nutrient (name K))
   =>
   (assert (symptom-cf (nutrient K) (cf 0.85)))
   (printout t "RULE FIRED [Salience 15]: Symptom leaf-edge-scorching → K symptom-cf=0.85 (strong indicator)" crlf))

(defrule NUTRIENT::symptom-potassium-poor-fruit-quality
   (declare (salience 15))
   (symptom (name poor-fruit-quality))
   (nutrient (name K))
   =>
   (assert (symptom-cf (nutrient K) (cf 0.65)))
   (printout t "RULE FIRED [Salience 15]: Symptom poor-fruit-quality → K symptom-cf=0.65 (common indicator)" crlf))

(defrule NUTRIENT::symptom-potassium-increased-fruit-acidity
   (declare (salience 15))
   (symptom (name increased-fruit-acidity))
   (nutrient (name K))
   =>
   (assert (symptom-cf (nutrient K) (cf 0.65)))
   (printout t "RULE FIRED [Salience 15]: Symptom increased-fruit-acidity → K symptom-cf=0.65 (common indicator)" crlf))

(defrule NUTRIENT::symptom-potassium-weak-stems
   (declare (salience 15))
   (symptom (name weak-stems))
   (nutrient (name K))
   =>
   (assert (symptom-cf (nutrient K) (cf 0.45)))
   (printout t "RULE FIRED [Salience 15]: Symptom weak-stems → K symptom-cf=0.45 (weak indicator)" crlf))

;;;========== CALCIUM SYMPTOM RULES ==========

(defrule NUTRIENT::symptom-calcium-blossom-end-rot
   (declare (salience 15))
   (symptom (name blossom-end-rot))
   (nutrient (name Ca))
   =>
   (assert (symptom-cf (nutrient Ca) (cf 0.85)))
   (printout t "RULE FIRED [Salience 15]: Symptom blossom-end-rot → Ca symptom-cf=0.85 (strong indicator)" crlf))

(defrule NUTRIENT::symptom-calcium-young-leaf-tip-necrosis
   (declare (salience 15))
   (symptom (name young-leaf-tip-necrosis))
   (nutrient (name Ca))
   =>
   (assert (symptom-cf (nutrient Ca) (cf 0.65)))
   (printout t "RULE FIRED [Salience 15]: Symptom young-leaf-tip-necrosis → Ca symptom-cf=0.65 (common indicator)" crlf))

(defrule NUTRIENT::symptom-calcium-poor-fruit-firmness
   (declare (salience 15))
   (symptom (name poor-fruit-firmness))
   (nutrient (name Ca))
   =>
   (assert (symptom-cf (nutrient Ca) (cf 0.45)))
   (printout t "RULE FIRED [Salience 15]: Symptom poor-fruit-firmness → Ca symptom-cf=0.45 (weak indicator)" crlf))

;;;------------------------------------------------------------
;;; SYMPTOM REINFORCEMENT RULE (Salience 14)
;;; Applies reinforcement formula for weak symptoms ONLY
;;;  
;;; CONDITIONS:
;;; - ≥ 2 symptom-cf facts for same nutrient
;;; - Each symptom CF ≤ 0.55 (weak symptoms only)
;;; 
;;; ACTION:
;;; - Computes: Reinforced_CF = 1 - Π(1 - CFi)
;;; - Asserts single reinforced symptom-cf fact
;;; - Does NOT modify nutrient
;;;------------------------------------------------------------

(defrule NUTRIENT::weak-symptom-reinforcement
   (declare (salience 14))
   (symptom-cf (nutrient ?n) (cf ?cf1&:(<= ?cf1 0.55)))
   (symptom-cf (nutrient ?n) (cf ?cf2&:(<= ?cf2 0.55)))
   (test (neq ?cf1 ?cf2))
   (not (symptom-cf-final (nutrient ?n)))
   =>
   (bind ?prob-or (- 1.0 (* (- 1.0 ?cf1) (- 1.0 ?cf2))))
   (assert (symptom-cf-final (nutrient ?n) (cf ?prob-or)))
   (printout t "RULE FIRED [Salience 14]: Weak symptom reinforcement → " ?n " reinforced-cf=" ?prob-or crlf))

;;;------------------------------------------------------------
;;; SYMPTOM CF AGGREGATION RULE (Salience 13)
;;; Combines multiple symptom-cf facts using min() when
;;; reinforcement is NOT applied
;;;
;;; CONDITIONS:
;;; - symptom-cf facts exist for nutrient
;;; - Reinforcement was NOT triggered
;;; - No symptom-cf-final yet
;;; 
;;; ACTION:
;;; - Uses min(CF1, CF2, ...) aggregation
;;; - Asserts symptom-cf-final with aggregated value
;;; - Does NOT modify nutrient
;;;------------------------------------------------------------

(defrule NUTRIENT::symptom-aggregation-single
   (declare (salience 13))
   (symptom-cf (nutrient ?n) (cf ?cf))
   (not (symptom-cf (nutrient ?n) (cf ~?cf)))
   (not (symptom-cf-final (nutrient ?n)))
   =>
   (assert (symptom-cf-final (nutrient ?n) (cf ?cf)))
   (printout t "RULE FIRED [Salience 13]: Symptom aggregation (single) → " ?n " symptom-cf-final=" ?cf crlf))

(defrule NUTRIENT::symptom-aggregation-multiple
   (declare (salience 13))
   (symptom-cf (nutrient ?n) (cf ?cf1))
   (symptom-cf (nutrient ?n) (cf ?cf2&:(> ?cf2 0.55)))
   (test (neq ?cf1 ?cf2))
   (not (symptom-cf-final (nutrient ?n)))
   =>
   (bind ?min-cf (min ?cf1 ?cf2))
   (assert (symptom-cf-final (nutrient ?n) (cf ?min-cf)))
   (printout t "RULE FIRED [Salience 13]: Symptom aggregation (multiple) → " ?n " symptom-cf-final=" ?min-cf crlf))

;;;------------------------------------------------------------
;;; FINAL NUTRIENT CF INTEGRATION (Salience -50)
;;;
;;; FINAL FORMULA (MANDATORY - USE min() ONLY):
;;; Final_CF = min(
;;;    nutrient.base-cf,
;;;    nutrient.cf (after disease adjustments),
;;;    symptom-cf-final.cf (if present)
;;; )
;;;
;;; CONSTRAINT VERIFICATION:
;;; - Use min() only
;;; - No averaging, weighting, or summation
;;; - Output nutrient name + final CF only
;;; - No duplicate CF counting
;;;
;;; EXECUTION SEQUENCE VERIFICATION:
;;; 1. Growth-stage base rules (salience 30) establish base-cf and initial cf
;;; 2. Disease modifier rules (salience 25) adjust cf via multiplication with capping
;;; 3. Symptom rules (salience 15) assert symptom evidence only
;;; 4. Reinforcement rule (salience 14) applies formula: 1 - Π(1 - CFi)
;;; 5. Aggregation rules (salience 13) use min() for multiple symptoms
;;; 6. Final integration (salience -50) computes strict min(base-cf, disease-cf, symptom-cf-final)
;;;------------------------------------------------------------

(defrule NUTRIENT::final-integrate-nutrient-cf-with-symptom
   (declare (salience -50))
   ?nFact <- (nutrient (name ?name) (cf ?disease-cf) (base-cf ?base-cf))
   (symptom-cf-final (nutrient ?name) (cf ?symptom-cf))
   (not (nutrient-final (name ?name)))
   =>
   (bind ?final-cf (min ?base-cf ?disease-cf ?symptom-cf))
   (assert (nutrient-final
      (name ?name)
      (cf ?final-cf)))
   (printout t "FINAL RESOLUTION [Salience -50]: Nutrient " ?name " → Final CF = " ?final-cf crlf))

(defrule NUTRIENT::final-integrate-nutrient-cf-without-symptom
   (declare (salience -50))
   ?nFact <- (nutrient (name ?name) (cf ?disease-cf) (base-cf ?base-cf))
   (not (symptom-cf-final (nutrient ?name)))
   (not (nutrient-final (name ?name)))
   =>
   (bind ?final-cf (min ?base-cf ?disease-cf))
   (assert (nutrient-final
      (name ?name)
      (cf ?final-cf)))
   (printout t "FINAL RESOLUTION [Salience -50]: Nutrient " ?name " → Final CF = " ?final-cf crlf))

;;;============================================================
;;; END OF nutrient_rules.clp
;;;============================================================
