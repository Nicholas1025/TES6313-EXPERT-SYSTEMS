"""
test_disease.py
Owner: Member B (Disease Knowledge Engineer)

============================================================
THIS FILE IS OWNED BY MEMBER B
Member A provides structure and guidance only.
Actual test cases will be implemented after rule finalization.
============================================================

Purpose:
    Rule-level verification tests for disease diagnosis rules.
    Tests should verify that disease rules fire correctly
    given specific symptom combinations.

Test Categories Expected:
    1. Individual Disease Rule Tests
       - Test each disease rule in isolation
       - Verify correct symptom → disease mapping
       - Verify CF values are correctly calculated

    2. Symptom Combination Tests
       - Test different symptom combinations
       - Verify correct disease is diagnosed
       - Verify priority when multiple diseases match

    3. CF Value Tests
       - Verify CF values match literature justification
       - Test CF propagation through rules

============================================================
GUIDANCE FOR MEMBER B
============================================================

Expected Test Structure:
------------------------

Each test should follow this pattern:

    def test_disease_<disease_name>_<scenario>(self):
        '''Test <disease> diagnosis with <scenario>.'''
        # 1. Define test symptoms
        symptoms = [
            {"name": "<symptom>", "severity": "<level>", "cf": <value>},
            ...
        ]
        
        # 2. Run inference
        results = self.system.run_diagnosis(symptoms)
        
        # 3. Assert expected disease
        assert results["disease"]["name"] == "<expected-disease>"
        
        # 4. Assert CF within expected range
        assert results["disease"]["cf"] >= <min_cf>
        assert results["disease"]["cf"] <= <max_cf>


Expected Input Format (Symptoms):
---------------------------------

    {
        "name": str,      # Symptom symbol (e.g., "brown-spots")
        "severity": str,  # "mild", "moderate", or "severe"
        "cf": float       # Certainty factor [0.0, 1.0]
    }


Expected Output Format (Disease):
---------------------------------

    results["disease"] = {
        "name": str,        # Disease symbol (e.g., "early-blight")
        "cf": float,        # Certainty factor [-1.0, 1.0]
        "explanation": str  # Reasoning explanation
    }


Example Test Case Template:
---------------------------

class TestEarlyBlight:
    '''Tests for Early Blight diagnosis rules.'''
    
    def test_early_blight_classic_symptoms(self, expert_system):
        '''
        Test: Classic early blight symptom combination
        
        Symptoms:
            - brown-spots (severe)
            - concentric-rings (moderate)
            - yellow-leaves (moderate)
        
        Expected: early-blight with CF >= 0.8
        
        Literature Reference: [Citation needed]
        '''
        symptoms = [
            {"name": "brown-spots", "severity": "severe", "cf": 1.0},
            {"name": "concentric-rings", "severity": "moderate", "cf": 0.9},
            {"name": "yellow-leaves", "severity": "moderate", "cf": 0.8},
        ]
        
        results = expert_system.run_diagnosis(symptoms)
        
        assert results["disease"]["name"] == "early-blight"
        assert results["disease"]["cf"] >= 0.8


Coordinate With:
----------------

- Member A: Symptom list and fact schema
- Member C: Disease names for impact factor mapping

============================================================
PLACEHOLDER: Actual Tests
============================================================
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def expert_system():
    """
    Create expert system instance for testing.
    
    Note: Member B should ensure disease_rules.clp is complete
    before running these tests.
    """
    try:
        from run_system import TomatoExpertSystem
        system = TomatoExpertSystem()
        system.load_rules()
        return system
    except ImportError:
        pytest.skip("CLIPSPY not available")


# =============================================================================
# MEMBER B: ADD YOUR DISEASE TESTS BELOW THIS LINE
# =============================================================================

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



# =============================================================================
# MEMBER B: ADD YOUR DISEASE TESTS ABOVE THIS LINE
# =============================================================================


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# =============================================================================
# END OF test_disease.py
# =============================================================================
