"""
This test_disease.py aims to verify the disease diagnosis rules in the tomato expert system.

In this system, verification is carried out using automated tests with Python and PyTest. 
The test class TestDiseaseRules is used to check the main disease rules. 
Each test case gives a set of symptoms and 
checks whether the system returns the correct disease and certainty factor (CF).

The tests cover strong, medium, and weak symptom cases. 
They also check OR-gate calculations and rule priority when more than one disease is matched.

By running these tests, errors in rules, logic, or calculations can be found early. 
This helps ensure that the expert system works correctly and gives reliable results.

Expected Outcome
1. Individual Disease Rule Tests
    Each disease rule is tested using specific symptoms.
    The system correctly matches symptoms to the correct disease.
    The system produces certainty factor (CF) values within the expected range.

2. CF Value Tests
    The system calculates CF values correctly based on the given rules.
    CF calculations using OR-gate rules are handled correctly.

"""

import pytest
import sys
from pathlib import Path

#add parent directory to path for import
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def expert_system():
    # to create expert system instance for testing

    try:
        from run_system import TomatoExpertSystem
        system = TomatoExpertSystem()
        system.load_rules()
        return system
    except ImportError:
        pytest.skip("CLIPSPY not available")


class TestDiseaseRules: # class name start with Test
    # Cover core disease rules with representative tests:
    # strong rules, weak rules, medium rules
    # probability theory (OR gate) calculation, priority, etc.

    def test_early_blight_strong(self, expert_system):
        # test disease early blight with strong symptoms
        symptoms = [
            {"name": "brown-leaf-spots"},
            {"name": "yellow-halos"},
        ]

        results = expert_system.run_diagnosis(symptoms)

        assert results["disease"]["name"] == "early-blight"
        assert results["disease"]["cf"] >= 0.76
    
    def test_septoria_weak(self, expert_system):
        # test disease septoria leaf spot with weak symptoms
        symptoms = [
            {"name": "small-gray-tan-spots"},
        ]

        results = expert_system.run_diagnosis(symptoms)

        assert results["disease"]["name"] == "septoria-leaf-spot"
        assert 0.38 <= results["disease"]["cf"] <= 0.39

    def test_fusarium_medium(self, expert_system):
        # test disease fusarium wilt with medium symptoms
        symptoms = [
            {"name": "lower-leaf-yellowing"},
            {"name": "plant-wilting"},
            {"name": "bottom-up-collapse"},
        ]

        results = expert_system.run_diagnosis(symptoms)

        assert results["disease"]["name"] == "fusarium-wilt"
        assert 0.31 <= results["disease"]["cf"] <= 0.32


    def test_mosaic_prob_or(self, expert_system):
        # test disease mosaic with trigger OR gate
        symptoms = [
            {"name": "leaf-mottling"},
            {"name": "leaf-distortion"},
        ]

        results = expert_system.run_diagnosis(symptoms)

        assert results["disease"]["name"] == "mosaic-virus"
        assert results["disease"]["cf"] >= 0.62


    def test_bacterial_medium(self, expert_system):
        # test disease bacterial with medium symptoms and OR gate
        symptoms = [
            {"name": "small-dark-spots"},
            {"name": "leaf-yellowing"},
            {"name": "leaf-drop"},
        ]

        results = expert_system.run_diagnosis(symptoms)

        assert results["disease"]["name"] == "bacterial-spot"
        assert 0.58 <= results["disease"]["cf"] <= 0.59


    def test_priority(self, expert_system):
        # test priority when multiple diseases match
        symptoms = [
            {"name": "brown-leaf-spots"},
            {"name": "yellow-halos"},
        ]

        results = expert_system.run_diagnosis(symptoms)

        highest = max(d["cf"] for d in results["all_diseases"])
        assert abs(results["disease"]["cf"] - highest) < 0.001


# Run Tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

