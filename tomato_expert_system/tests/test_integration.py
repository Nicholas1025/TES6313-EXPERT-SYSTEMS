"""
test_integration.py

Purpose:
    System-level verification tests for the expert system.
    Tests CF adjustment correctness, conflict resolution, and reasoning order.

Test Categories:
    1. CF Adjustment Tests
    2. Conflict Resolution Tests
    3. Reasoning Order Tests
    4. Integration Flow Tests

Usage:
    pytest tests/test_integration.py -v
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.cf_utils import (
    cf_combine,
    cf_combine_multiple,
    cf_adjust,
    cf_compare,
    cf_select_highest,
    cf_rank_conclusions,
    cf_meets_threshold,
    cf_to_confidence_level,
    validate_cf,
)


# =============================================================================
# CF Utility Tests
# =============================================================================

class TestCFCombine:
    """Tests for CF combination logic."""
    
    def test_combine_both_positive(self):
        """Test combining two positive CFs."""
        result = cf_combine(0.8, 0.6)
        # Formula: 0.8 + 0.6 * (1 - 0.8) = 0.8 + 0.12 = 0.92
        assert abs(result - 0.92) < 0.001
    
    def test_combine_both_negative(self):
        """Test combining two negative CFs."""
        result = cf_combine(-0.5, -0.3)
        # Formula: -0.5 + (-0.3) * (1 + (-0.5)) = -0.5 + (-0.15) = -0.65
        assert abs(result - (-0.65)) < 0.001
    
    def test_combine_mixed_signs(self):
        """Test combining CFs with mixed signs."""
        result = cf_combine(0.7, -0.4)
        # Formula: (0.7 + (-0.4)) / (1 - min(0.7, 0.4)) = 0.3 / 0.6 = 0.5
        assert abs(result - 0.5) < 0.001
    
    def test_combine_with_zero(self):
        """Test combining with zero CF."""
        result = cf_combine(0.8, 0.0)
        assert abs(result - 0.8) < 0.001
    
    def test_combine_clamping(self):
        """Test that result is clamped to [-1, 1]."""
        result = cf_combine(0.99, 0.99)
        assert result <= 1.0


class TestCFAdjust:
    """Tests for CF adjustment logic."""
    
    def test_adjust_increase(self):
        """Test CF adjustment with factor > 1."""
        result = cf_adjust(0.8, 1.2)
        # 0.8 * 1.2 = 0.96
        assert abs(result - 0.96) < 0.001
    
    def test_adjust_decrease(self):
        """Test CF adjustment with factor < 1."""
        result = cf_adjust(0.8, 0.7)
        # 0.8 * 0.7 = 0.56
        assert abs(result - 0.56) < 0.001
    
    def test_adjust_neutral(self):
        """Test CF adjustment with factor = 1."""
        result = cf_adjust(0.8, 1.0)
        assert abs(result - 0.8) < 0.001
    
    def test_adjust_clamping_high(self):
        """Test that adjusted CF is clamped to 1.0."""
        result = cf_adjust(0.9, 1.5)
        assert result <= 1.0
    
    def test_adjust_clamping_low(self):
        """Test that adjusted CF is clamped to -1.0."""
        result = cf_adjust(-0.9, 1.5)
        assert result >= -1.0


class TestConflictResolution:
    """Tests for conflict resolution logic."""
    
    def test_select_highest_single(self):
        """Test selecting highest from single conclusion."""
        conclusions = [("disease-a", 0.8)]
        result = cf_select_highest(conclusions)
        assert result == ("disease-a", 0.8)
    
    def test_select_highest_multiple(self):
        """Test selecting highest from multiple conclusions."""
        conclusions = [
            ("disease-a", 0.6),
            ("disease-b", 0.9),
            ("disease-c", 0.7),
        ]
        result = cf_select_highest(conclusions)
        assert result == ("disease-b", 0.9)
    
    def test_select_highest_empty(self):
        """Test selecting from empty list."""
        result = cf_select_highest([])
        assert result is None
    
    def test_rank_conclusions(self):
        """Test ranking conclusions by CF."""
        conclusions = [
            ("a", 0.5),
            ("b", 0.9),
            ("c", 0.7),
        ]
        result = cf_rank_conclusions(conclusions)
        assert result[0] == ("b", 0.9)
        assert result[1] == ("c", 0.7)
        assert result[2] == ("a", 0.5)


class TestCFThresholds:
    """Tests for CF threshold helpers."""
    
    def test_meets_threshold_above(self):
        """Test CF above threshold."""
        assert cf_meets_threshold(0.5, 0.4) is True
    
    def test_meets_threshold_below(self):
        """Test CF below threshold."""
        assert cf_meets_threshold(0.3, 0.4) is False
    
    def test_meets_threshold_equal(self):
        """Test CF equal to threshold."""
        assert cf_meets_threshold(0.4, 0.4) is True
    
    def test_confidence_level_very_high(self):
        """Test confidence level for very high CF."""
        assert cf_to_confidence_level(0.9) == "Very High"
    
    def test_confidence_level_moderate(self):
        """Test confidence level for moderate CF."""
        assert cf_to_confidence_level(0.5) == "Moderate"
    
    def test_confidence_level_negative(self):
        """Test confidence level for negative CF."""
        assert "Negative" in cf_to_confidence_level(-0.3)


class TestCFValidation:
    """Tests for CF validation."""
    
    def test_validate_valid_cf(self):
        """Test validation of valid CF values."""
        assert validate_cf(0.5) is True
        assert validate_cf(-0.5) is True
        assert validate_cf(1.0) is True
        assert validate_cf(-1.0) is True
        assert validate_cf(0.0) is True
    
    def test_validate_invalid_cf(self):
        """Test validation of invalid CF values."""
        assert validate_cf(1.5) is False
        assert validate_cf(-1.5) is False


# =============================================================================
# Integration Flow Tests
# =============================================================================

class TestReasoningOrder:
    """
    Tests for correct reasoning order.
    
    Note: These tests require the full CLIPS system to be loaded.
    They will be skipped if CLIPSPY is not available.
    """
    
    @pytest.fixture
    def expert_system(self):
        """Create expert system instance."""
        try:
            from run_system import TomatoExpertSystem
            system = TomatoExpertSystem()
            system.load_rules()
            return system
        except ImportError:
            pytest.skip("CLIPSPY not available")
    
    def test_phase_progression(self, expert_system):
        """
        Test that phases progress in correct order.
        
        Expected order:
        symptoms → disease → integration → nutrient → resolution → output → complete
        """
        # Run with minimal symptoms
        test_symptoms = [
            {"name": "yellow-leaves", "severity": "moderate", "cf": 1.0},
        ]
        
        results = expert_system.run_diagnosis(test_symptoms)
        
        # Should reach 'complete' phase
        assert results.get("phase") == "complete"
    
    def test_symptoms_asserted(self, expert_system):
        """Test that symptoms are correctly asserted."""
        test_symptoms = [
            {"name": "yellow-leaves", "severity": "moderate", "cf": 1.0},
            {"name": "brown-spots", "severity": "severe", "cf": 0.9},
        ]
        
        expert_system.reset()
        expert_system.assert_symptoms(test_symptoms)
        
        # Check facts contain symptoms
        facts = expert_system.get_facts()
        fact_str = " ".join(facts)
        
        assert "yellow-leaves" in fact_str
        assert "brown-spots" in fact_str


class TestCFAdjustmentIntegration:
    """
    Tests for CF adjustment in the integration layer.
    
    These tests verify that disease-nutrient impact factors
    correctly adjust nutrient CFs.
    """
    
    def test_adjustment_formula(self):
        """Test the adjustment formula mathematically."""
        base_cf = 0.8
        impact_factor = 1.2
        expected = 0.96  # 0.8 * 1.2
        
        result = cf_adjust(base_cf, impact_factor)
        assert abs(result - expected) < 0.001
    
    def test_multiple_adjustments(self):
        """
        Test that multiple adjustments can be tracked.
        
        Note: In the actual system, each disease-nutrient pair
        should only have one adjustment. This test verifies
        the concept.
        """
        # Simulate two adjustments
        base_cf = 0.7
        
        # First adjustment
        adjusted_1 = cf_adjust(base_cf, 1.1)  # 0.77
        
        # If we were to apply another factor (hypothetically)
        adjusted_2 = cf_adjust(adjusted_1, 0.9)  # 0.693
        
        # Verify chain
        assert adjusted_1 > base_cf  # Factor > 1 increases CF
        assert adjusted_2 < adjusted_1  # Factor < 1 decreases CF


class TestConflictResolutionIntegration:
    """
    Tests for conflict resolution in the resolution layer.
    
    These tests verify that the highest CF wins for both
    disease and nutrient conclusions.
    """
    
    def test_disease_conflict_resolution(self):
        """Test that highest CF disease wins."""
        diseases = [
            {"name": "early-blight", "cf": 0.7},
            {"name": "late-blight", "cf": 0.9},
            {"name": "bacterial-spot", "cf": 0.6},
        ]
        
        # Convert to tuple format for helper function
        conclusions = [(d["name"], d["cf"]) for d in diseases]
        winner = cf_select_highest(conclusions)
        
        assert winner[0] == "late-blight"
        assert winner[1] == 0.9
    
    def test_nutrient_conflict_resolution(self):
        """Test that highest CF nutrient wins."""
        nutrients = [
            {"name": "nitrogen", "cf": 0.65},
            {"name": "calcium", "cf": 0.85},
            {"name": "potassium", "cf": 0.55},
        ]
        
        conclusions = [(n["name"], n["cf"]) for n in nutrients]
        winner = cf_select_highest(conclusions)
        
        assert winner[0] == "calcium"
        assert winner[1] == 0.85
    
    def test_independent_resolution(self):
        """
        Test that disease and nutrient resolution are independent.
        
        Disease resolution should not affect nutrient resolution.
        """
        # Disease conclusions
        diseases = [("disease-a", 0.9), ("disease-b", 0.7)]
        disease_winner = cf_select_highest(diseases)
        
        # Nutrient conclusions (independent)
        nutrients = [("nutrient-x", 0.6), ("nutrient-y", 0.8)]
        nutrient_winner = cf_select_highest(nutrients)
        
        # Both should be resolved independently
        assert disease_winner[0] == "disease-a"
        assert nutrient_winner[0] == "nutrient-y"


# =============================================================================
# Edge Case Tests
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_no_symptoms(self):
        """Test handling of empty symptom list."""
        try:
            from run_system import TomatoExpertSystem
            system = TomatoExpertSystem()
            system.load_rules()
            results = system.run_diagnosis([])
            
            # Should still complete
            assert results.get("phase") == "complete"
        except ImportError:
            pytest.skip("CLIPSPY not available")
    
    def test_cf_boundary_values(self):
        """Test CF at boundary values."""
        # Test 1.0
        result = cf_adjust(1.0, 1.0)
        assert result == 1.0
        
        # Test -1.0
        result = cf_adjust(-1.0, 1.0)
        assert result == -1.0
        
        # Test 0.0
        result = cf_adjust(0.0, 1.5)
        assert result == 0.0
    
    def test_very_small_cf(self):
        """Test handling of very small CF values."""
        result = cf_adjust(0.01, 0.5)
        assert result == 0.005
        assert cf_meets_threshold(result, 0.1) is False


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# =============================================================================
# END OF test_integration.py
# =============================================================================
