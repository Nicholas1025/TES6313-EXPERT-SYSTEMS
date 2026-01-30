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

    def test_vegetative_stage_base_nutrients(self, expert_system):
        results = expert_system.run_diagnosis([], growth_stage="vegetative")

        nutrients = {n["name"]: n["cf"] for n in results["all_nutrients"]}

        assert nutrients["N"] == 0.85
        assert nutrients["P"] == 0.60
        assert nutrients["K"] == 0.60
        assert nutrients["Ca"] == 0.60

    def test_rooting_stage_base_nutrients(self, expert_system):
        results = expert_system.run_diagnosis([], growth_stage="rooting")

        nutrients = {n["name"]: n["cf"] for n in results["all_nutrients"]}

        assert nutrients["P"] == 0.85
        assert nutrients["N"] == 0.60
        assert nutrients["K"] == 0.60
        assert nutrients["Ca"] == 0.60

    def test_flowering_stage_base_nutrients(self, expert_system):
        results = expert_system.run_diagnosis([], growth_stage="flowering")

        nutrients = {n["name"]: n["cf"] for n in results["all_nutrients"]}

        assert nutrients["K"] == 0.85
        assert nutrients["Ca"] == 0.85
        assert nutrients["N"] == 0.60
        assert nutrients["P"] == 0.60

    def test_fruiting_stage_base_nutrients(self, expert_system):
        results = expert_system.run_diagnosis([], growth_stage="fruiting")

        nutrients = {n["name"]: n["cf"] for n in results["all_nutrients"]}

        assert nutrients["K"] == 0.90
        assert nutrients["Ca"] == 0.90
        assert nutrients["N"] == 0.60
        assert nutrients["P"] == 0.60


# =============================================================================
# SYMPTOM → NUTRIENT EVIDENCE TESTS (Salience 15)
# =============================================================================

class TestSymptomEvidenceRules:

    def test_strong_nitrogen_symptom_dominates(self, expert_system):
        results = expert_system.run_diagnosis(
            [{"name": "lower-leaf-yellowing", "cf": 1.0}],
            growth_stage="vegetative"
        )

        assert results["nutrient"]["name"] == "N"
        assert results["nutrient"]["cf"] <= 0.85
        assert results["nutrient"]["cf"] > 0.60

    def test_strong_phosphorus_symptom_dominates(self, expert_system):
        results = expert_system.run_diagnosis(
            [{"name": "stunted-growth", "cf": 1.0}],
            growth_stage="rooting"
        )

        assert results["nutrient"]["name"] == "P"
        assert results["nutrient"]["cf"] <= 0.85
        assert results["nutrient"]["cf"] > 0.60

    def test_potassium_leaf_edge_scorching(self, expert_system):
        results = expert_system.run_diagnosis(
            [{"name": "leaf-edge-scorching", "cf": 1.0}],
            growth_stage="flowering"
        )

        assert results["nutrient"]["name"] == "K"
        assert results["nutrient"]["cf"] <= 0.85
        assert results["nutrient"]["cf"] > 0.60

    def test_calcium_blossom_end_rot(self, expert_system):
        results = expert_system.run_diagnosis(
            [{"name": "blossom-end-rot", "cf": 1.0}],
            growth_stage="fruiting"
        )

        assert results["nutrient"]["name"] == "Ca"
        assert results["nutrient"]["cf"] <= 0.90
        assert results["nutrient"]["cf"] > 0.60


# =============================================================================
# DISEASE MODIFIER TESTS (Salience 25)
# =============================================================================

class TestDiseaseModifiers:

    def test_fusarium_reduces_nitrogen(self, expert_system):
        results = expert_system.run_diagnosis(
            [
                {"name": "lower-leaf-yellowing", "cf": 1.0},
                {"name": "stem-discoloration", "cf": 1.0},
            ],
            growth_stage="vegetative"
        )

        nitrogen = next(n for n in results["all_nutrients"] if n["name"] == "N")

        assert nitrogen["cf"] < 0.85
        assert nitrogen["cf"] >= 0.40

    def test_fusarium_supports_potassium(self, expert_system):
        results = expert_system.run_diagnosis(
            [{"name": "stem-discoloration", "cf": 1.0}],
            growth_stage="fruiting"
        )

        potassium = next(n for n in results["all_nutrients"] if n["name"] == "K")

        assert potassium["cf"] <= 0.90
        assert potassium["cf"] >= 0.60


# =============================================================================
# WEAK SYMPTOM REINFORCEMENT TESTS (Salience 14)
# =============================================================================

class TestWeakSymptomReinforcement:

    def test_two_weak_nitrogen_symptoms_reinforced(self, expert_system):
        results = expert_system.run_diagnosis(
            [
                {"name": "thin-stems", "cf": 1.0},
                {"name": "weak-stems", "cf": 1.0},
            ],
            growth_stage="vegetative"
        )

        # Reinforcement: 1 - (1-0.45)^2 = 0.7425
        assert results["nutrient"]["name"] == "N"
        assert 0.70 <= results["nutrient"]["cf"] <= 0.75


# =============================================================================
# FINAL CF INTEGRATION TESTS (Salience -50)
# =============================================================================

class TestFinalCFIntegration:

    def test_final_cf_is_minimum_of_all_sources(self, expert_system):
        results = expert_system.run_diagnosis(
            [{"name": "lower-leaf-yellowing", "cf": 1.0}],
            growth_stage="vegetative"
        )

        final_cf = results["nutrient"]["cf"]

        assert final_cf <= 0.85
        assert final_cf <= 1.0
        assert final_cf > 0.0


# =============================================================================
# CONSTRAINT VERIFICATION TESTS
# =============================================================================

class TestConstraintVerification:

    def test_no_symptoms_uses_growth_stage_only(self, expert_system):
        results = expert_system.run_diagnosis([], growth_stage="vegetative")

        assert results["nutrient"]["name"] == "N"
        assert results["nutrient"]["cf"] == 0.85

    def test_symptoms_do_not_create_new_nutrients(self, expert_system):
        results = expert_system.run_diagnosis(
            [{"name": "thin-stems", "cf": 1.0}],
            growth_stage="vegetative"
        )

        nutrient_names = [n["name"] for n in results["all_nutrients"]]

        assert set(nutrient_names) == {"N", "P", "K", "Ca"}
