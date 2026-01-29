"""
run_system.py
Owner: Member A (System Architect, Inference & UI Engineer)

Purpose:
    System runner that manages the CLIPS environment via CLIPSPY.
    Handles loading rules, asserting facts, executing inference,
    and extracting structured results.

Usage:
    from run_system import TomatoExpertSystem
    
    system = TomatoExpertSystem()
    results = system.run_diagnosis(symptoms=[
        {"name": "yellow-leaves", "severity": "moderate", "cf": 1.0},
        {"name": "brown-spots", "severity": "severe", "cf": 0.9},
    ])
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    import clips
except ImportError:
    raise ImportError(
        "CLIPSPY is required. Install with: pip install clipspy"
    )


# =============================================================================
# Path Configuration
# =============================================================================

# Get the directory containing this script
BASE_DIR = Path(__file__).parent.absolute()
CLIPS_RULES_DIR = BASE_DIR / "clips_rules"


# =============================================================================
# Expert System Class
# =============================================================================

class TomatoExpertSystem:
    """
    Main expert system class that manages CLIPS inference.
    
    Attributes:
        env: CLIPS environment instance
        loaded: Whether rules have been loaded
    """
    
    def __init__(self):
        """Initialize the expert system."""
        self.env: Optional[clips.Environment] = None
        self.loaded: bool = False
        self._initialize_environment()
    
    def _initialize_environment(self) -> None:
        """Create and initialize the CLIPS environment."""
        self.env = clips.Environment()
        self.loaded = False
    
    def load_rules(self) -> None:
        """
        Load all CLIPS rule files in the correct order.
        
        Order:
            1. main_system.clp (templates and control)
            2. disease_rules.clp (Member B)
            3. nutrient_rules.clp (Member C)
            4. integration.clp (Member A)
        """
        if self.loaded:
            return
        
        rule_files = [
            "main_system.clp",     # Templates and phase control
            "disease_rules.clp",   # Disease rules (Member B)
            "nutrient_rules.clp",  # Nutrient rules (Member C)
            "integration.clp",     # Integration logic (Member A)
        ]
        
        for filename in rule_files:
            filepath = CLIPS_RULES_DIR / filename
            if filepath.exists():
                self.env.load(str(filepath))
            else:
                print(f"Warning: Rule file not found: {filepath}")
        
        self.loaded = True
    
    def reset(self) -> None:
        """Reset the CLIPS environment for a new inference cycle."""
        if self.env:
            self.env.reset()
    
    def assert_symptoms(self, symptoms: List[Dict[str, Any]]) -> None:
        """
        Assert symptom facts into working memory.
        
        Args:
            symptoms: List of symptom dictionaries with keys:
                - name: Symptom name (symbol) — only required key
                - severity: (ignored) kept for backward compatibility
                - cf: (ignored) kept for backward compatibility
        
        Example:
            system.assert_symptoms([
                {"name": "brown-leaf-spots"},
                {"name": "yellow-halos"},
            ])
        """
        for symptom in symptoms:
            symptom_name = clips.Symbol(symptom.get("name", "unknown"))
            self.env.assert_string(f"(symptom (name {symptom_name}))")
    
    def run_inference(self) -> int:
        """
        Execute the inference engine.
        
        Returns:
            Number of rules fired
        """
        return self.env.run()
    
    def extract_results(self) -> Dict[str, Any]:
        """
        Extract inference results from working memory.
        
        Returns:
            Dictionary containing:
                - disease: Final disease diagnosis (or None)
                - nutrient: Final nutrient recommendation (or None)
                - all_diseases: All disease conclusions
                - all_nutrients: All nutrient conclusions
                - adjustments: CF adjustment records
                - phase: Final phase reached
        """
        results = {
            "disease": None,
            "nutrient": None,
            "all_diseases": [],
            "all_nutrients": [],
            "adjustments": [],
            "phase": None,
        }
        
        # Extract final disease
        for fact in self.env.facts():
            template_name = fact.template.name if fact.template else None
            
            if template_name == "final-disease":
                results["disease"] = {
                    "name": str(fact["name"]),
                    "cf": float(fact["cf"]),
                    "explanation": str(fact["explanation"]),
                }
            
            elif template_name == "final-nutrient":
                results["nutrient"] = {
                    "name": str(fact["name"]),
                    "cf": float(fact["cf"]),
                    "explanation": str(fact["explanation"]),
                }
            
            elif template_name == "disease":
                results["all_diseases"].append({
                    "name": str(fact["name"]),
                    "cf": float(fact["cf"]),
                    "explanation": str(fact["explanation"]),
                })
            
            elif template_name == "nutrient-deficiency":
                results["all_nutrients"].append({
                    "name": str(fact["name"]),
                    "cf": float(fact["cf"]),
                    "explanation": str(fact["explanation"]),
                })
            
            elif template_name == "adjusted-nutrient-cf":
                results["adjustments"].append({
                    "nutrient": str(fact["nutrient-name"]),
                    "original_cf": float(fact["original-cf"]),
                    "adjusted_cf": float(fact["adjusted-cf"]),
                    "disease": str(fact["applied-disease"]),
                    "impact_factor": float(fact["impact-factor"]),
                })
            
            elif template_name == "phase":
                results["phase"] = str(fact["name"])
        
        # Sort by CF (highest first)
        results["all_diseases"].sort(key=lambda x: x["cf"], reverse=True)
        results["all_nutrients"].sort(key=lambda x: x["cf"], reverse=True)
        
        return results
    
    def run_diagnosis(self, symptoms: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run complete diagnosis cycle.
        
        This is the main entry point for running the expert system.
        
        Args:
            symptoms: List of symptom dictionaries
        
        Returns:
            Complete results dictionary
        
        Example:
            results = system.run_diagnosis([
                {"name": "yellow-leaves", "severity": "moderate", "cf": 1.0},
            ])
            print(results["disease"])
        """
        # Reset for new inference
        self.reset()
        
        # Load rules if not already loaded
        self.load_rules()
        
        # Reset again after loading
        self.reset()
        
        # Assert symptoms
        self.assert_symptoms(symptoms)
        
        # Run inference
        rules_fired = self.run_inference()
        
        # Extract results
        results = self.extract_results()
        results["rules_fired"] = rules_fired
        
        return results
    
    def get_facts(self) -> List[str]:
        """
        Get all current facts as strings (for debugging).
        
        Returns:
            List of fact string representations
        """
        return [str(fact) for fact in self.env.facts()]
    
    def print_facts(self) -> None:
        """Print all current facts (for debugging)."""
        print("\n=== Current Facts ===")
        for fact in self.env.facts():
            print(f"  {fact}")
        print("=====================\n")


# =============================================================================
# Convenience Functions
# =============================================================================

def run_quick_diagnosis(symptoms: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Quick diagnosis function for simple use cases.
    
    Args:
        symptoms: List of symptom dictionaries
    
    Returns:
        Results dictionary
    
    Example:
        results = run_quick_diagnosis([
            {"name": "yellow-leaves", "cf": 1.0},
        ])
    """
    system = TomatoExpertSystem()
    return system.run_diagnosis(symptoms)


# =============================================================================
# Main (for testing)
# =============================================================================

if __name__ == "__main__":
    # Test the system
    print("Tomato Expert System - Test Run")
    print("================================\n")
    
    # Create system instance
    system = TomatoExpertSystem()
    
    # Test symptoms
    test_symptoms = [
        {"name": "yellow-leaves", "severity": "moderate", "cf": 1.0},
        {"name": "brown-spots", "severity": "severe", "cf": 0.9},
        {"name": "wilting", "severity": "mild", "cf": 0.7},
    ]
    
    print("Input Symptoms:")
    for s in test_symptoms:
        print(f"  - {s['name']} ({s['severity']}, CF={s['cf']})")
    print()
    
    # Run diagnosis
    try:
        results = system.run_diagnosis(test_symptoms)
        
        print(f"Rules Fired: {results['rules_fired']}")
        print(f"Final Phase: {results['phase']}")
        print()
        
        print("Disease Diagnosis:")
        if results["disease"]:
            d = results["disease"]
            print(f"  Name: {d['name']}")
            print(f"  CF: {d['cf']}")
            print(f"  Explanation: {d['explanation']}")
        else:
            print("  No disease diagnosed")
        print()
        
        print("Nutrient Recommendation:")
        if results["nutrient"]:
            n = results["nutrient"]
            print(f"  Name: {n['name']}")
            print(f"  CF: {n['cf']}")
            print(f"  Explanation: {n['explanation']}")
        else:
            print("  No nutrient deficiency identified")
        print()
        
        if results["adjustments"]:
            print("CF Adjustments:")
            for adj in results["adjustments"]:
                print(f"  - {adj['nutrient']}: {adj['original_cf']} -> {adj['adjusted_cf']}")
                print(f"    (due to {adj['disease']}, factor={adj['impact_factor']})")
        
    except Exception as e:
        print(f"Error during diagnosis: {e}")
        import traceback
        traceback.print_exc()


# =============================================================================
# END OF run_system.py
# =============================================================================
