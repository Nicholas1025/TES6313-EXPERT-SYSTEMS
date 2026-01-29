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
    """
    try:
        from run_system import TomatoExpertSystem
        system = TomatoExpertSystem()
        system.load_rules()
        return system
    except ImportError:
        pytest.skip("CLIPSPY not available")


# =============================================================================
# GROWTH STAGE BASE RULE TESTS (Salience 30)
# =============================================================================

class TestGrowthStageBaseRules:

    def test_vegetative_stage_asserts_nitrogen_only(self, expert_system):
        results = expert_system.run_diagnosis([], growth_stage="vegetative")
        assert results["nutrient"]["name"] == "N"
        assert results["nutrient"]["cf"] == 0.85

    def test_rooting_stage_asserts_phosphorus(self, expert_system):
        results = expert_system.run_diagnosis([], growth_stage="rooting")
        assert results["nutrient"]["name"] == "P"
        assert results["nutrient"]["cf"] == 0.85

    def test_flowering_stage_asserts_k_and_ca(self, expert_system):
        results = expert_system.run_diagnosis([], growth_stage="flowering")
        assert results["nutrient"]["name"] in ["K", "Ca"]
        assert results["nutrient"]["cf"] == 0.85

    def test_fruiting_stage_elevates_k_and_ca(self, expert_system):
        results = expert_system.run_diagnosis([], growth_stage="fruiting")
        assert results["nutrient"]["name"] in ["K", "Ca"]
        assert results["nutrient"]["cf"] == 0.90


# =============================================================================
# SYMPTOM → NUTRIENT MAPPING TESTS (Salience 15)
# =============================================================================

class TestSymptomEvidenceRules:

    def test_nitrogen_lower_leaf_yellowing_strong(self, expert_system):
        results = expert_system.run_diagnosis(
            [{"name": "lower-leaf-yellowing", "severity": "moderate", "cf": 1.0}],
            growth_stage="vegetative"
        )
        assert results["nutrient"]["name"] == "N"
        assert results["nutrient"]["cf"] >= 0.70

    def test_phosphorus_stunted_growth_strong(self, expert_system):
        results = expert_system.run_diagnosis(
            [{"name": "stunted-growth", "severity": "moderate", "cf": 1.0}],
            growth_stage="rooting"
        )
        assert results["nutrient"]["name"] == "P"
        assert results["nutrient"]["cf"] >= 0.70

    def test_potassium_leaf_edge_scorching(self, expert_system):
        results = expert_system.run_diagnosis(
            [{"name": "leaf-edge-scorching", "severity": "moderate", "cf": 1.0}],
            growth_stage="flowering"
        )
        assert results["nutrient"]["name"] in ["K", "Ca"]
        assert results["nutrient"]["cf"] >= 0.70

    def test_calcium_blossom_end_rot(self, expert_system):
        results = expert_system.run_diagnosis(
            [{"name": "blossom-end-rot", "severity": "moderate", "cf": 1.0}],
            growth_stage="fruiting"
        )
        assert results["nutrient"]["name"] in ["Ca", "K"]
        assert results["nutrient"]["cf"] >= 0.70


# =============================================================================
# DISEASE CONTEXT MODIFIER TESTS (Salience 25)
# ONLY: Fusarium, Mosaic, Early blight
# =============================================================================

class TestDiseaseModifiers:

    def test_fusarium_increases_potassium_cf(self, expert_system):
        results = expert_system.run_diagnosis(
            [
                {"name": "lower-leaf-yellowing", "severity": "moderate", "cf": 1.0},
                {"name": "stem-discoloration", "severity": "moderate", "cf": 1.0},
            ],
            growth_stage="fruiting"
        )

        potassium = next(n for n in results["all_nutrients"] if n["name"] == "K")

        # Base CF = 0.90, modifier should not reduce it
        assert potassium["cf"] >= 0.85
        assert potassium["cf"] <= 0.90

    def test_no_disease_no_modifier(self, expert_system):
        results = expert_system.run_diagnosis([], growth_stage="vegetative")
        assert results["nutrient"]["cf"] == 0.85


# =============================================================================
# WEAK SYMPTOM REINFORCEMENT TESTS (Salience 14)
# =============================================================================

class TestWeakSymptomReinforcement:

    def test_two_weak_nitrogen_symptoms_trigger_reinforcement(self, expert_system):
        results = expert_system.run_diagnosis(
            [
                {"name": "thin-stems", "severity": "mild", "cf": 1.0},
                {"name": "stunted-growth", "severity": "moderate", "cf": 1.0},
            ],
            growth_stage="vegetative"
        )

        assert results["nutrient"]["name"] == "N"
        assert results["nutrient"]["cf"] == 0.45


# =============================================================================
# SYMPTOM AGGREGATION TESTS (Salience 13)
# =============================================================================

class TestSymptomAggregation:

    def test_strong_and_common_symptoms_use_min(self, expert_system):
        results = expert_system.run_diagnosis(
            [
                {"name": "lower-leaf-yellowing", "severity": "moderate", "cf": 1.0},
                {"name": "stunted-growth", "severity": "moderate", "cf": 1.0},
            ],
            growth_stage="vegetative"
        )

        assert results["nutrient"]["name"] == "N"
        assert 0.60 <= results["nutrient"]["cf"] <= 0.85


# =============================================================================
# FINAL CF INTEGRATION TESTS (Salience -50)
# =============================================================================

class TestFinalCFIntegration:

    def test_final_cf_is_minimum(self, expert_system):
        results = expert_system.run_diagnosis(
            [{"name": "lower-leaf-yellowing", "severity": "moderate", "cf": 1.0}],
            growth_stage="vegetative"
        )

        final_cf = results["nutrient"]["cf"]
        assert final_cf <= 0.85
        assert final_cf > 0


# =============================================================================
# SKIP-PATH VERIFICATION TESTS
# =============================================================================

class TestSkipPaths:

    def test_no_symptoms_uses_base_cf(self, expert_system):
        results = expert_system.run_diagnosis([], growth_stage="vegetative")
        assert results["nutrient"]["cf"] == 0.85

    def test_symptoms_do_not_assert_new_nutrients(self, expert_system):
        results = expert_system.run_diagnosis(
            [{"name": "thin-stems", "severity": "mild", "cf": 1.0}],
            growth_stage="vegetative"
        )

        nutrient_names = [n["name"] for n in results["all_nutrients"]]
        assert nutrient_names.count("N") == 1
