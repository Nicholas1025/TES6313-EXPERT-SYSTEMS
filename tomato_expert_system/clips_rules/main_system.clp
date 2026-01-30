;;;============================================================
;;; main_system.clp
;;; EXPERT SYSTEM INFERENCE ARCHITECTURE AND CONTROL
;;;============================================================
;;;
;;; This module serves as the central nervous system of the expert
;;; system. It does not contain domain-specific medical knowledge
;;; (diseases or nutrients) but rather establishes the:
;;; 1.  System Ontology (Fact Templates)
;;; 2.  Inference Control Strategy (Module Focus Stack)
;;; 3.  Execution Workflow (Phases)
;;;
;;; [Inference Strategy]
;;; The system employs a phased forward-chaining approach controlled
;;; by CLIPS 'focus' mechanism. This ensures a deterministic execution
;;; order crucial for the integration logic:
;;;
;;; Phase Sequence:
;;; 1. SYMPTOMS    : Ingestion of user observations.
;;; 2. DISEASE     : Primary diagnosis (Disease Domain).
;;; 3. INTEGRATION : Cross-domain reasoning (Disease -> Nutrient).
;;;                  *Crucial for adjusting nutrient confidence based on
;;;                   pathological context.*
;;; 4. NUTRIENT    : Secondary diagnosis (Nutrient Domain).
;;; 5. RESOLUTION  : Conflict resolution and final selection.
;;; 6. OUTPUT      : Formatting results for the host application.
;;;
;;; [Knowledge Representation]
;;; Data is modeled using 'deftemplate' constructs to enforce strict
;;; schema validation. This ensures that symptoms, diseases, and
;;; nutrients share a consistent structure across all modules.
;;;
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
;;; [Knowledge Part]: Definition of data structures (Ontology)
;;; representing symptoms, diagnoses, and system states.
;;;------------------------------------------------------------

;;; Symptom fact template
;;; Asserted by: Python (run_system.py) based on user input
;;; Format: (symptom <name> <severity> <cf>)
;;; Example: (symptom (name brown-leaf-spots) (severity moderate) (cf 0.9))
(deftemplate MAIN::symptom
   "Represents an observed symptom"
   (slot name (type SYMBOL))           ; e.g., brown-leaf-spots, yellow-halos
   (slot severity (type SYMBOL)        ; mild, moderate, severe
         (default moderate))
   (slot cf (type FLOAT)               ; certainty of symptom presence
         (default 1.0)))

;;; Growth stage fact template
;;; Asserted by: Python (run_system.py) - REQUIRED for nutrient rules
;;; Format: (growth-stage (name <stage>))
;;; Example: (growth-stage (name vegetative))
(deftemplate MAIN::growth-stage
   "Represents the current growth stage of the plant"
   (slot name (type SYMBOL)))          ; rooting, vegetative, flowering, fruiting

;;; Disease diagnosis result template
;;; Asserted by: disease_rules.clp (Member B)
(deftemplate MAIN::disease
   "Represents a diagnosed disease with certainty factor and evidence"
   (slot name (type SYMBOL))           ; e.g., early-blight, septoria-leaf-spot
   (slot cf (type FLOAT))              ; certainty factor [-1.0, 1.0]
   (slot explanation (type STRING)     ; reasoning explanation
         (default ""))
   (multislot evidence))               ; symptom evidence used

;;; Nutrient deficiency result template
;;; Asserted by: nutrient_rules.clp (Member C)
(deftemplate MAIN::nutrient-deficiency
   "Represents a nutrient deficiency diagnosis with certainty"
   (slot name (type SYMBOL))           ; e.g., nitrogen, potassium, calcium
   (slot cf (type FLOAT))              ; certainty factor [-1.0, 1.0]
   (slot explanation (type STRING)     ; reasoning explanation
         (default "")))

;;; Nutrient working template (internal use during inference)
;;; Asserted by: nutrient_rules.clp (Member C) during diagnosis
;;; Tracks CF adjustments and evidence
(deftemplate MAIN::nutrient
   "Working nutrient fact for diagnosis (internal to nutrient reasoning)"
   (slot name (type SYMBOL))           ; e.g., nitrogen, potassium, calcium
   (slot cf (type FLOAT))              ; current certainty factor
   (slot base-cf (type FLOAT))         ; base CF from growth stage rules
   (slot modified (type SYMBOL)        ; whether CF has been modified
         (default no)))

;;; Symptom evidence template (CF from symptoms)
;;; Asserted by: nutrient_rules.clp (Member C) during symptom evaluation
(deftemplate MAIN::symptom-cf
   "Stores CF value for a nutrient from a symptom"
   (slot nutrient (type SYMBOL))       ; which nutrient this supports
   (slot cf (type FLOAT)))             ; CF from symptom evidence

;;; Final aggregated symptom CF (after aggregation/reinforcement)
;;; Asserted by: nutrient_rules.clp (Member C)
(deftemplate MAIN::symptom-cf-final
   "Final aggregated CF from all symptoms for a nutrient"
   (slot nutrient (type SYMBOL))       ; which nutrient
   (slot cf (type FLOAT)))             ; aggregated CF value

;;; Final nutrient diagnosis (after CF integration)
;;; Asserted by: nutrient_rules.clp (Member C) at salience -50
(deftemplate MAIN::nutrient-final
   "Final nutrient diagnosis after CF integration"
   (slot name (type SYMBOL))           ; nutrient name
   (slot cf (type FLOAT)))             ; final integrated CF

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

;;; Disease-Symptom Knowledge Table
;;; Asserted by: disease_rules.clp (Member B)
;;; Stores the relationships between diseases and their symptoms
(deftemplate MAIN::disease-symptom
   "Maps diseases to symptoms with role (core/support) and CF value"
   (slot disease (type SYMBOL))        ; e.g., early-blight, septoria
   (slot symptom (type SYMBOL))        ; e.g., brown-leaf-spots, yellow-halos
   (slot role (type SYMBOL))           ; core or support
   (slot cf (type FLOAT)))             ; certainty factor for this symptom

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
