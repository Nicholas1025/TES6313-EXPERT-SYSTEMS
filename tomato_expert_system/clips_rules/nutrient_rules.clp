;;; GROWTH-STAGE BASE NUTRIENT RULES (Salience 30)

(defrule NUTRIENT::growth-stage-rooting-phosphorus
   (declare (salience 30))
   (growth-stage (name rooting))
   (not (nutrient (name P)))
   (not (nutrient (name N)))
   (not (nutrient (name K)))
   (not (nutrient (name Ca)))
   =>
   (assert (nutrient (name P) (cf 0.85) (base-cf 0.85) (modified no)))
   (assert (nutrient (name N)  (cf 0.60) (base-cf 0.60) (modified no)))
   (assert (nutrient (name K)  (cf 0.60) (base-cf 0.60) (modified no)))
   (assert (nutrient (name Ca) (cf 0.60) (base-cf 0.60) (modified no)))
   (printout t "RULE FIRED [Salience 30]: Growth stage rooting → Nutrients asserted (P=0.85, N=0.60, K=0.60, Ca=0.60)" crlf))

(defrule NUTRIENT::growth-stage-vegetative-nitrogen
   (declare (salience 30))
   (growth-stage (name vegetative))
   (not (nutrient (name P)))
   (not (nutrient (name N)))
   (not (nutrient (name K)))
   (not (nutrient (name Ca)))
   =>
   (assert (nutrient (name N) (cf 0.85) (base-cf 0.85) (modified no)))
   (assert (nutrient (name P)  (cf 0.60) (base-cf 0.60) (modified no)))
   (assert (nutrient (name K)  (cf 0.60) (base-cf 0.60) (modified no)))
   (assert (nutrient (name Ca) (cf 0.60) (base-cf 0.60) (modified no)))
   (printout t "RULE FIRED [Salience 30]: Growth stage vegetative → Nutrients asserted (N=0.85, P=0.60, K=0.60, Ca=0.60)" crlf))

(defrule NUTRIENT::growth-stage-flowering-potassium-calcium
   (declare (salience 30))
   (growth-stage (name flowering))
   (not (nutrient (name P)))
   (not (nutrient (name N)))
   (not (nutrient (name K)))
   (not (nutrient (name Ca)))
   =>
   (assert (nutrient (name K) (cf 0.85) (base-cf 0.85) (modified no)))
   (assert (nutrient (name Ca) (cf 0.85) (base-cf 0.85) (modified no)))
   (assert (nutrient (name N) (cf 0.60) (base-cf 0.60) (modified no)))
   (assert (nutrient (name P) (cf 0.60) (base-cf 0.60) (modified no)))

   (printout t "RULE FIRED [Salience 30]: Growth stage flowering → Nutrients asserted (K=0.85, Ca=0.85, N=0.60, P=0.60)" crlf))


(defrule NUTRIENT::growth-stage-fruiting-potassium-calcium
   (declare (salience 30))
   (growth-stage (name fruiting))
   (not (nutrient (name P)))
   (not (nutrient (name N)))
   (not (nutrient (name K)))
   (not (nutrient (name Ca)))
   =>
   (assert (nutrient (name K) (cf 0.90) (base-cf 0.90) (modified no)))
   (assert (nutrient (name Ca) (cf 0.90) (base-cf 0.90) (modified no)))
   (assert (nutrient (name N) (cf 0.60) (base-cf 0.60) (modified no)))
   (assert (nutrient (name P) (cf 0.60) (base-cf 0.60) (modified no)))
   (printout t "RULE FIRED [Salience 30]: Growth stage fruiting → Nutrients asserted (K=0.90, Ca=0.90, N=0.60, P=0.60)" crlf))


;;; DISEASE-CONTEXT MODIFIER RULES (Salience 25)

(defrule NUTRIENT::disease-fusarium-nitrogen-reduction
   (declare (salience 25))
   (disease (name fusarium-wilt) (cf ?dcf&:(>= ?dcf 0.70)))
   ?nFact <- (nutrient
                (name N)
                (cf ?ncf&:(> ?ncf 0.1))
                (modified no))
   =>
   (bind ?adjusted (* ?ncf 0.7))
   (modify ?nFact
           (cf ?adjusted)
           (modified yes))
   (printout t "RULE FIRED [Salience 25]: Fusarium → N CF reduced (×0.7)" crlf))

(defrule NUTRIENT::disease-fusarium-potassium-increase
   (declare (salience 25))
   (disease (name fusarium-wilt) (cf ?dcf&:(>= ?dcf 0.55)))
   ?kFact <- (nutrient (name K) (cf ?kcf) (base-cf ?kbcf) (modified no))
   =>
   (bind ?adjusted (min ?kbcf (* ?kcf 1.2)))
   (modify ?kFact (cf ?adjusted) (modified yes))
   (printout t "RULE FIRED [Salience 25]: Fusarium → K CF increased (×1.2, capped at base)" crlf))

(defrule NUTRIENT::disease-fusarium-calcium-increase
   (declare (salience 25))
   (disease (name fusarium-wilt) (cf ?dcf&:(>= ?dcf 0.55)))
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

;;; SYMPTOM-BASED EVIDENCE RULES (Salience 15)

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


;;; SYMPTOM REINFORCEMENT RULE (Salience 14)

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


;;; SYMPTOM CF AGGREGATION RULE (Salience 13)


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


;;; FINAL NUTRIENT CF INTEGRATION (Salience -50)

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


