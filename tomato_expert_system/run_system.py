"""
run_system.py
EXPERT SYSTEM INFERENCE ENGINE CONTROLLER (PYTHON-CLIPS BRIDGE)

[System Architecture]
This class acts as the interface layer between the User Interface (Streamlit)
and the Inference Engine (CLIPS). It is responsible for:
1.  **Environment Initialization**: Setting up the CLIPS sandbox.
2.  **Knowledge Acquisition**: Loading the formalized rules (.clp files).
3.  **Fact Assertion**: Translating Python objects (inputs) into CLIPS facts.
4.  **Inference Execution**: Managing the run cycle and capturing rule traces.
5.  **Result Extraction**: Parsing the working memory for final diagnoses.

[Key Feature: Stepwise Inference Tracing]
To support the "Right to Explanation" in expert systems, this controller
implements a custom `run_inference()` method that executes the engine
one rule at a time (`limit=1`). This allows capturing the exact execution
path (trace) for verification and validation purposes.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional

import clips


# =============================================================================
# Path Configuration
# =============================================================================

BASE_DIR = Path(__file__).parent.absolute()
CLIPS_RULES_DIR = BASE_DIR / "clips_rules"


# =============================================================================
# Expert System Class
# =============================================================================

class TomatoExpertSystem:
    """
    Main expert system class that manages CLIPS inference.
    """

    def __init__(self):
        self.env: Optional[clips.Environment] = None
        self.loaded: bool = False
        self._initialize_environment()

    def _initialize_environment(self) -> None:
        self.env = clips.Environment()
        self.loaded = False

    # -------------------------------------------------------------------------
    # Rule Loading
    # -------------------------------------------------------------------------

    def load_rules(self) -> None:
        """
        Load all CLIPS rule files in the correct order.
        """
        if self.loaded:
            return

        rule_files = [
            "main_system.clp",
            "disease_rules.clp",
            "nutrient_rules.clp",
            "integration.clp",
        ]

        for filename in rule_files:
            filepath = CLIPS_RULES_DIR / filename
            if filepath.exists():
                self.env.load(str(filepath))
            else:
                raise FileNotFoundError(f"Missing rule file: {filepath}")

        self.loaded = True

    def reset(self) -> None:
        if self.env:
            self.env.reset()

    # -------------------------------------------------------------------------
    # Fact Assertion
    # -------------------------------------------------------------------------

    def assert_growth_stage(self, stage: str) -> None:
        """
        Assert plant growth stage (REQUIRED for nutrient rules).
        [Verification]: Validates crucial input context before inference.
        """
        self.env.assert_string(
            f"(growth-stage (name {stage}))"
        )

    def assert_symptoms(self, symptoms: List[Dict[str, Any]]) -> None:
        """
        Assert symptoms as TEMPLATE-BASED facts.
        [Verification]: Ensures all input data conforms to the 'symptom' template schema.
        """
        for symptom in symptoms:
            name = symptom.get("name", "unknown")
            severity = symptom.get("severity", "moderate")
            cf = float(symptom.get("cf", 1.0))
            self.env.assert_string(
                f"(symptom (name {name}) (severity {severity}) (cf {cf}))"
            )

    def assert_disease(self, name: str, cf: float) -> None:
        """
        Optional: manually assert disease for testing nutrient modifiers.
        """
        self.env.assert_string(
            f"(disease (name {name}) (cf {cf}))"
        )

    # -------------------------------------------------------------------------
    # Inference
    # -------------------------------------------------------------------------

    def run_inference(self) -> List[str]:
        """
        Runs execution step-by-step to capture the sequence of fired rules.
        [Validation]: Stepwise execution allows verifying the reasoning path
        matches the expected logic flow (Validation of Logic).
        [Evaluation]: Returns rule trace to evaluate system performance and complexity.
        Returns a list of rule names in the order they were executed.
        """
        fired_rules = []
        
        while True:
            # Check the agenda to see what is about to fire
            activations = list(self.env.activations())
            if not activations:
                break
                
            # The first activation is the one that will fire next (highest salience)
            next_activation = activations[0]
            fired_rules.append(next_activation.name)
            
            # Run one step
            self.env.run(limit=1)
            
        return fired_rules

    # -------------------------------------------------------------------------
    # Result Extraction
    # -------------------------------------------------------------------------

    def extract_results(self) -> Dict[str, Any]:
        results = {
            "disease": None,
            "nutrient": None,
            "all_diseases": [],
            "all_nutrients": [],
            "adjustments": [],
            "phase": None,
        }

        for fact in self.env.facts():
            template = fact.template.name

            if template == "final-disease":
                results["disease"] = {
                    "name": str(fact["name"]),
                    "cf": float(fact["cf"]),
                    "explanation": str(fact["explanation"]),
                }

            elif template == "final-nutrient":
                results["nutrient"] = {
                    "name": str(fact["name"]),
                    "cf": float(fact["cf"]),
                    "explanation": str(fact["explanation"]),
                }

            elif template == "disease":
                results["all_diseases"].append({
                    "name": str(fact["name"]),
                    "cf": float(fact["cf"]),
                    "explanation": str(fact["explanation"]),
                })

            elif template == "nutrient":
                results["all_nutrients"].append({
                    "name": str(fact["name"]),
                    "cf": float(fact["cf"]),
                })
            
            elif template == "nutrient-deficiency":
                results["all_nutrients"].append({
                    "name": str(fact["name"]),
                    "cf": float(fact["cf"]),
                    "explanation": str(fact["explanation"]),
                })

            elif template == "nutrient-final":
                # Alternative template name for nutrient results
                results["nutrient"] = {
                    "name": str(fact["name"]),
                    "cf": float(fact["cf"]),
                }

            elif template == "adjusted-nutrient-cf":
                results["adjustments"].append({
                    "nutrient": str(fact["nutrient-name"]),
                    "original_cf": float(fact["original-cf"]),
                    "adjusted_cf": float(fact["adjusted-cf"]),
                    "disease": str(fact["applied-disease"]),
                    "impact_factor": float(fact["impact-factor"]),
                })

            elif template == "phase":
                results["phase"] = str(fact["name"])

        results["all_diseases"].sort(key=lambda x: x["cf"], reverse=True)
        results["all_nutrients"].sort(key=lambda x: x["cf"], reverse=True)

        return results

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def run_diagnosis(
        self,
        symptoms: List[Dict[str, Any]],
        growth_stage: str = "vegetative"
    ) -> Dict[str, Any]:
        """
        Run full diagnosis cycle.
        """
        self.reset()
        self.load_rules()
        self.reset()

        # REQUIRED CONTEXT
        self.assert_growth_stage(growth_stage)

        # INPUT
        self.assert_symptoms(symptoms)

        # RUN
        fired_trace = self.run_inference()

        # OUTPUT
        results = self.extract_results()
        results["rules_fired"] = len(fired_trace)
        results["rules_triggered"] = fired_trace
        return results

    # -------------------------------------------------------------------------
    # Debug Utilities
    # -------------------------------------------------------------------------

    def print_facts(self) -> None:
        print("\n=== FACTS ===")
        for fact in self.env.facts():
            print(fact)
        print("=============\n")


# =============================================================================
# Convenience Function
# =============================================================================

def run_quick_diagnosis(symptoms: List[Dict[str, Any]]) -> Dict[str, Any]:
    system = TomatoExpertSystem()
    return system.run_diagnosis(symptoms)


# =============================================================================
# Manual Test
# =============================================================================

if __name__ == "__main__":
    system = TomatoExpertSystem()

    # Test 1: Disease Detection (Early Blight)
    print("=" * 50)
    print("TEST 1: Disease Detection (Early Blight)")
    print("=" * 50)
    test_symptoms_disease = [
        {"name": "brown-leaf-spots"},
        {"name": "bulls-eye-pattern"},
    ]
    results = system.run_diagnosis(test_symptoms_disease, growth_stage="vegetative")
    print("Rules Fired:", results["rules_fired"])
    print("Rules Triggered:", results.get("rules_triggered", []))
    print("Disease Result:", results["disease"])
    print("All Diseases Found:", results["all_diseases"])
    print()

    # Test 2: Nutrient Detection (Nitrogen Deficiency)
    print("=" * 50)
    print("TEST 2: Nutrient Detection (N Deficiency)")
    print("=" * 50)
    test_symptoms_nutrient = [
        {"name": "lower-leaf-yellowing"},
        {"name": "stunted-growth"},
    ]
    results = system.run_diagnosis(test_symptoms_nutrient, growth_stage="vegetative")
    print("Rules Fired:", results["rules_fired"])
    print("Nutrient Result:", results["nutrient"])
    print()

    # Test 3: Combined (Disease + Nutrient)
    print("=" * 50)
    print("TEST 3: Combined (Early Blight + Nutrient)")
    print("=" * 50)
    test_combined = [
        {"name": "brown-leaf-spots"},
        {"name": "bulls-eye-pattern"},
        {"name": "lower-leaf-yellowing"},
    ]
    results = system.run_diagnosis(test_combined, growth_stage="flowering")
    print("Rules Fired:", results["rules_fired"])
    print("Disease Result:", results["disease"])
    print("All Diseases Found:", results["all_diseases"])
    print("Nutrient Result:", results["nutrient"])
