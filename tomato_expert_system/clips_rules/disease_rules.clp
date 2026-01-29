;;; This disease_rules.clp contains all the disease diagonosis rules
;;; tomato expert system. 
;;;
;;;============================================================
;;; Disease Rule Design and Validation Workflow
;;;============================================================
;;;
;;; The disease rules in this expert system are validated using
;;; a reliable academic reference from the University of Maryland Extension: 
;;;     Key to Common Problems of Tomatoes | University of Maryland Extension. (n.d.).
;;;     Extension.umd.edu. https://extension.umd.edu/resource/key-common-problems-tomatoes/
;;;
;;; Each symptom is defined as either a core symptom or a
;;; supporting symptom based on its importance score which is calculated by adding 
;;; frequency (from the reference) and specificity (how many times the symptoms appear in all diseases) 
;;; to the disease.
;;;
;;; Symptom selection is based on importance score thresholds:
;;; - If the score is greater than or equal to 4, core symptoms
;;;   are selected.
;;; - If the score is less than 2, the two highest scores are
;;;   selected.
;;;
;;; Certainty Factor (CF) values are assigned according to
;;; disease occurrence frequency:
;;; - Very Common   : 0.85
;;; - Common        : 0.65
;;; - Not Common    : 0.55
;;; - Occasional    : 0.45
;;;
;;; Three types of rules are defined for each disease:
;;; - Strong rules  : Two or more core symptoms
;;; - Medium rules  : One core and two or more support symptoms
;;; - Weak rules    : One core symptom
;;;
;;; Rule CF values are assigned as follows:
;;; - Strong : 0.9
;;; - Medium : 0.7
;;; - Weak   : 0.45
;;;
;;; Reinforcement rules are applied when symptom CF values
;;; are low (not common or occasional):
;;; - If CF < 0.55, reinforcement is calculated as:
;;;   CF = 1 - (1 - CF_i)
;;; - Otherwise, the minimum CF is selected.
;;;
;;; Salience values are assigned to control rule priority:
;;; - Strong rules  : 30
;;; - Medium rules  : 20
;;; - Weak rules    : 10
;;;
;;; Each rule also includes the condition:
;;; (not (disease (name xxx)))
;;; to ensure that once a disease is asserted, no other
;;; rules for the same disease will fire again.
;;;
;;; The combination of salience and the (not) condition
;;; prevents double counting and duplicate diagnoses.
;;;
;;;============================================================
;;; Disease Domain knowledge Base
;;;============================================================
;;; Total 6 diseases and 21 symptoms
;;; The following disease-symptom template maps disease symptoms to their corresponding CF scores

(deffacts MAIN::disease-symptom-table

;;; ================= EARLY BLIGHT =================
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
;;; Probabilistic OR gate: used to reinforce for all weak evidence
;;;============================================================

(deffunction DISEASE::prob-or ($?cfs)
   (bind ?p 1.0)

   (foreach ?cf $?cfs
      (bind ?p (* ?p (- 1.0 ?cf)))
   )

   (- 1.0 ?p)
)

;;;============================================================
;;; Rule CF
;;;============================================================

(defglobal
   ?*RULE-CF-STRONG* = 0.9
   ?*RULE-CF-MEDIUM* = 0.7
   ?*RULE-CF-WEAK*   = 0.45
)

;;;============================================================
;;; EARLY BLIGHT (No Medium rule)
;;; Core: brown-leaf-spots, yellow-halos, bulls-eye-pattern, lower-leaves-first, dark-fruit-lesions
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
;;; SEPTORIA (No Medium rule)
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
;;; LATE BLIGHT (No Medium rule)
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
;;; MOSAIC (No Medium rule)
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
