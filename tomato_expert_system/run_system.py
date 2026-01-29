"""
run_system.py
Owner: Member A (System Architect, Inference & UI Engineer)

FIXED VERSION
- Symptoms are TEMPLATE-based (MAIN::symptom)
- Growth stage is explicitly asserted
- Compatible with updated main_system.clp and nutrient_rules.clp
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
            # "integration.clp",  # TODO: Fix syntax errors before loading
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
        """
        self.env.assert_string(
            f"(growth-stage (name {stage}))"
        )

    def assert_symptoms(self, symptoms: List[Dict[str, Any]]) -> None:
        """
        Assert symptoms as TEMPLATE-BASED facts.
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

    def run_inference(self) -> int:
        return self.env.run()

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
        rules_fired = self.run_inference()

        # OUTPUT
        results = self.extract_results()
        results["rules_fired"] = rules_fired
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

    test_symptoms = [
        {"name": "pale-green-leaves", "severity": "moderate", "cf": 1.0},
        {"name": "stunted-growth", "severity": "moderate", "cf": 0.9},
    ]

    results = system.run_diagnosis(test_symptoms, growth_stage="vegetative")

    print("Rules Fired:", results["rules_fired"])
    print("Final Phase:", results["phase"])
    print("Nutrient Result:", results["nutrient"])
