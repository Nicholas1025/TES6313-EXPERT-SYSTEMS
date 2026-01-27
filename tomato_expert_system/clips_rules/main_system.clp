;;;============================================================
;;; main_system.clp
;;; Owner: Member A (System Architect, Inference & UI Engineer)
;;;
;;; Purpose:
;;;   Inference control ONLY — no domain rules here.
;;;   Controls the reasoning order using CLIPS focus mechanism.
;;;
;;; Reasoning Order:
;;;   1. SYMPTOMS (input phase)
;;;   2. DISEASE (disease diagnosis)
;;;   3. INTEGRATION (CF adjustment via impact factors)
;;;   4. NUTRIENT (nutrient deficiency diagnosis)
;;;   5. RESOLUTION (conflict resolution within categories)
;;;   6. OUTPUT (final results)
;;;
;;; Note:
;;;   This file does NOT contain any disease or nutrient rules.
;;;   Domain knowledge is strictly separated in disease_rules.clp
;;;   and nutrient_rules.clp.
;;;============================================================

;;;------------------------------------------------------------
;;; Module Definitions (Focus Control)
;;;------------------------------------------------------------

(defmodule MAIN
   (export ?ALL))

(defmodule SYMPTOMS
   "Phase 1: Symptom input and assertion"
   (import MAIN ?ALL)
   (export ?ALL))

(defmodule DISEASE
   "Phase 2: Disease diagnosis rules (Member B)"
   (import MAIN ?ALL)
   (import SYMPTOMS ?ALL)
   (export ?ALL))

(defmodule INTEGRATION
   "Phase 3: CF adjustment and integration logic (Member A)"
   (import MAIN ?ALL)
   (import DISEASE ?ALL)
   (export ?ALL))

(defmodule NUTRIENT
   "Phase 4: Nutrient deficiency diagnosis rules (Member C)"
   (import MAIN ?ALL)
   (import SYMPTOMS ?ALL)
   (import INTEGRATION ?ALL)
   (export ?ALL))

(defmodule RESOLUTION
   "Phase 5: Conflict resolution within categories"
   (import MAIN ?ALL)
   (import DISEASE ?ALL)
   (import NUTRIENT ?ALL)
   (export ?ALL))

(defmodule OUTPUT
   "Phase 6: Final output preparation"
   (import MAIN ?ALL)
   (import RESOLUTION ?ALL)
   (export ?ALL))

;;;------------------------------------------------------------
;;; Fact Templates (Shared Schema)
;;;------------------------------------------------------------

;;; Symptom fact template
;;; Asserted by: Python (run_system.py) based on user input
(deftemplate MAIN::symptom
   "Represents an observed symptom with optional certainty"
   (slot name (type SYMBOL))           ; e.g., yellow-leaves, brown-spots
   (slot severity (type SYMBOL)        ; mild, moderate, severe
         (default moderate))
   (slot cf (type FLOAT)               ; certainty factor [0.0, 1.0]
         (default 1.0)))

;;; Disease diagnosis result template
;;; Asserted by: disease_rules.clp (Member B)
(deftemplate MAIN::disease
   "Represents a diagnosed disease with certainty factor"
   (slot name (type SYMBOL))           ; e.g., early-blight, bacterial-spot
   (slot cf (type FLOAT))              ; certainty factor [-1.0, 1.0]
   (slot explanation (type STRING)     ; reasoning explanation
         (default "")))

;;; Nutrient deficiency result template
;;; Asserted by: nutrient_rules.clp (Member C)
(deftemplate MAIN::nutrient-deficiency
   "Represents a nutrient deficiency diagnosis with certainty"
   (slot name (type SYMBOL))           ; e.g., nitrogen, potassium, calcium
   (slot cf (type FLOAT))              ; certainty factor [-1.0, 1.0]
   (slot explanation (type STRING)     ; reasoning explanation
         (default "")))

;;; Disease-Nutrient Impact Factor template
;;; Asserted by: Member C (defines the impact relationships)
(deftemplate MAIN::disease-nutrient-impact
   "Impact factor: how a disease affects nutrient CF adjustment"
   (slot disease-name (type SYMBOL))   ; the diagnosed disease
   (slot nutrient-name (type SYMBOL))  ; the affected nutrient
   (slot impact-factor (type FLOAT)))  ; multiplier for CF adjustment

;;; Adjusted nutrient CF (after integration)
;;; Asserted by: integration.clp (Member A)
(deftemplate MAIN::adjusted-nutrient-cf
   "Stores the adjusted CF for a nutrient after disease impact"
   (slot nutrient-name (type SYMBOL))
   (slot original-cf (type FLOAT))
   (slot adjusted-cf (type FLOAT))
   (slot applied-disease (type SYMBOL))
   (slot impact-factor (type FLOAT)))

;;; Final resolved conclusion templates
(deftemplate MAIN::final-disease
   "The final disease conclusion after conflict resolution"
   (slot name (type SYMBOL))
   (slot cf (type FLOAT))
   (slot explanation (type STRING)))

(deftemplate MAIN::final-nutrient
   "The final nutrient recommendation after conflict resolution"
   (slot name (type SYMBOL))
   (slot cf (type FLOAT))
   (slot explanation (type STRING)))

;;; Phase control fact
(deftemplate MAIN::phase
   "Tracks current inference phase"
   (slot name (type SYMBOL)))

;;;------------------------------------------------------------
;;; Phase Transition Rules
;;;------------------------------------------------------------

;;; Start inference: Move from MAIN to SYMPTOMS
(defrule MAIN::start-inference
   "Initialize inference and move to symptom processing"
   (declare (salience 100))
   (not (phase (name ?)))
   =>
   (assert (phase (name symptoms)))
   (focus SYMPTOMS))

;;; SYMPTOMS → DISEASE
(defrule SYMPTOMS::proceed-to-disease
   "After symptoms are loaded, proceed to disease diagnosis"
   (declare (salience -100))
   ?p <- (phase (name symptoms))
   =>
   (retract ?p)
   (assert (phase (name disease)))
   (focus DISEASE))

;;; DISEASE → INTEGRATION
(defrule DISEASE::proceed-to-integration
   "After disease diagnosis, proceed to integration"
   (declare (salience -100))
   ?p <- (phase (name disease))
   =>
   (retract ?p)
   (assert (phase (name integration)))
   (focus INTEGRATION))

;;; INTEGRATION → NUTRIENT
(defrule INTEGRATION::proceed-to-nutrient
   "After integration, proceed to nutrient diagnosis"
   (declare (salience -100))
   ?p <- (phase (name integration))
   =>
   (retract ?p)
   (assert (phase (name nutrient)))
   (focus NUTRIENT))

;;; NUTRIENT → RESOLUTION
(defrule NUTRIENT::proceed-to-resolution
   "After nutrient diagnosis, proceed to conflict resolution"
   (declare (salience -100))
   ?p <- (phase (name nutrient))
   =>
   (retract ?p)
   (assert (phase (name resolution)))
   (focus RESOLUTION))

;;; RESOLUTION → OUTPUT
(defrule RESOLUTION::proceed-to-output
   "After conflict resolution, proceed to output"
   (declare (salience -100))
   ?p <- (phase (name resolution))
   =>
   (retract ?p)
   (assert (phase (name output)))
   (focus OUTPUT))

;;; OUTPUT complete
(defrule OUTPUT::inference-complete
   "Mark inference as complete"
   (declare (salience -100))
   ?p <- (phase (name output))
   =>
   (retract ?p)
   (assert (phase (name complete))))

;;;============================================================
;;; END OF main_system.clp
;;;============================================================
