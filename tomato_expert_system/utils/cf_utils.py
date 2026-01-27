"""
cf_utils.py
Owner: Member A (System Architect, Inference & UI Engineer)

Purpose:
    Certainty Factor (CF) computation utilities for the expert system.
    
Functions:
    - cf_combine: Combine two CFs using MYCIN formula
    - cf_adjust: Adjust CF by impact factor
    - cf_compare: Compare two CFs and return the higher one
    - cf_threshold: Check if CF meets confidence threshold
    - cf_to_confidence_level: Convert CF to human-readable level
"""

from typing import Tuple, Optional


# =============================================================================
# CF Combination (MYCIN Formula)
# =============================================================================

def cf_combine(cf1: float, cf2: float) -> float:
    """
    Combine two certainty factors using the MYCIN combination formula.
    
    The formula handles three cases:
    1. Both CFs positive: CF = CF1 + CF2 * (1 - CF1)
    2. Both CFs negative: CF = CF1 + CF2 * (1 + CF1)
    3. Mixed signs: CF = (CF1 + CF2) / (1 - min(|CF1|, |CF2|))
    
    Args:
        cf1: First certainty factor [-1.0, 1.0]
        cf2: Second certainty factor [-1.0, 1.0]
    
    Returns:
        Combined certainty factor [-1.0, 1.0]
    
    Examples:
        >>> cf_combine(0.8, 0.6)  # Both positive
        0.92
        >>> cf_combine(-0.5, -0.3)  # Both negative
        -0.65
        >>> cf_combine(0.7, -0.4)  # Mixed signs
        0.5
    """
    # Validate inputs
    cf1 = _clamp_cf(cf1)
    cf2 = _clamp_cf(cf2)
    
    if cf1 >= 0 and cf2 >= 0:
        # Both positive: accumulate evidence
        result = cf1 + cf2 * (1 - cf1)
    elif cf1 < 0 and cf2 < 0:
        # Both negative: accumulate disbelief
        result = cf1 + cf2 * (1 + cf1)
    else:
        # Mixed signs: conflict resolution
        denominator = 1 - min(abs(cf1), abs(cf2))
        if denominator == 0:
            result = 0.0  # Complete uncertainty
        else:
            result = (cf1 + cf2) / denominator
    
    return _clamp_cf(result)


def cf_combine_multiple(cfs: list) -> float:
    """
    Combine multiple certainty factors sequentially.
    
    Args:
        cfs: List of certainty factors
    
    Returns:
        Combined certainty factor [-1.0, 1.0]
    
    Example:
        >>> cf_combine_multiple([0.8, 0.6, 0.4])
        0.952
    """
    if not cfs:
        return 0.0
    
    result = cfs[0]
    for cf in cfs[1:]:
        result = cf_combine(result, cf)
    
    return result


# =============================================================================
# CF Adjustment (Integration Layer)
# =============================================================================

def cf_adjust(base_cf: float, impact_factor: float) -> float:
    """
    Adjust a certainty factor by an impact factor.
    
    Formula: Adjusted_CF = Base_CF × Impact_Factor
    
    This is used in the integration layer to adjust nutrient CFs
    based on disease diagnosis impact factors.
    
    Args:
        base_cf: Original certainty factor [-1.0, 1.0]
        impact_factor: Multiplier for adjustment (typically 0.5 to 1.5)
    
    Returns:
        Adjusted certainty factor, clamped to [-1.0, 1.0]
    
    Examples:
        >>> cf_adjust(0.8, 1.2)  # Increase confidence
        0.96
        >>> cf_adjust(0.8, 0.7)  # Decrease confidence
        0.56
    """
    adjusted = base_cf * impact_factor
    return _clamp_cf(adjusted)


# =============================================================================
# CF Comparison (Conflict Resolution)
# =============================================================================

def cf_compare(cf1: float, cf2: float) -> int:
    """
    Compare two certainty factors.
    
    Args:
        cf1: First certainty factor
        cf2: Second certainty factor
    
    Returns:
        1 if cf1 > cf2
        -1 if cf1 < cf2
        0 if cf1 == cf2
    
    Example:
        >>> cf_compare(0.8, 0.6)
        1
    """
    if cf1 > cf2:
        return 1
    elif cf1 < cf2:
        return -1
    else:
        return 0


def cf_select_highest(conclusions: list) -> Optional[Tuple[str, float]]:
    """
    Select the conclusion with the highest CF for conflict resolution.
    
    Args:
        conclusions: List of tuples [(name, cf), ...]
    
    Returns:
        Tuple (name, cf) of the highest CF conclusion, or None if empty
    
    Example:
        >>> cf_select_highest([("disease-a", 0.8), ("disease-b", 0.6)])
        ("disease-a", 0.8)
    """
    if not conclusions:
        return None
    
    return max(conclusions, key=lambda x: x[1])


def cf_rank_conclusions(conclusions: list) -> list:
    """
    Rank conclusions by their certainty factors (highest first).
    
    Args:
        conclusions: List of tuples [(name, cf), ...]
    
    Returns:
        Sorted list of tuples, highest CF first
    
    Example:
        >>> cf_rank_conclusions([("a", 0.5), ("b", 0.9), ("c", 0.7)])
        [("b", 0.9), ("c", 0.7), ("a", 0.5)]
    """
    return sorted(conclusions, key=lambda x: x[1], reverse=True)


# =============================================================================
# CF Threshold Helpers
# =============================================================================

# Default confidence thresholds
CF_THRESHOLD_VERY_HIGH = 0.8
CF_THRESHOLD_HIGH = 0.6
CF_THRESHOLD_MODERATE = 0.4
CF_THRESHOLD_LOW = 0.2
CF_THRESHOLD_MINIMUM = 0.1  # Below this, conclusion is too uncertain


def cf_meets_threshold(cf: float, threshold: float = CF_THRESHOLD_MINIMUM) -> bool:
    """
    Check if a certainty factor meets the minimum confidence threshold.
    
    Args:
        cf: Certainty factor to check
        threshold: Minimum acceptable CF (default: 0.1)
    
    Returns:
        True if CF >= threshold, False otherwise
    
    Example:
        >>> cf_meets_threshold(0.5, 0.4)
        True
    """
    return cf >= threshold


def cf_to_confidence_level(cf: float) -> str:
    """
    Convert a certainty factor to a human-readable confidence level.
    
    Args:
        cf: Certainty factor [-1.0, 1.0]
    
    Returns:
        String describing the confidence level
    
    Examples:
        >>> cf_to_confidence_level(0.9)
        "Very High"
        >>> cf_to_confidence_level(0.5)
        "Moderate"
        >>> cf_to_confidence_level(-0.3)
        "Negative (against)"
    """
    if cf < 0:
        return "Negative (against)"
    elif cf >= CF_THRESHOLD_VERY_HIGH:
        return "Very High"
    elif cf >= CF_THRESHOLD_HIGH:
        return "High"
    elif cf >= CF_THRESHOLD_MODERATE:
        return "Moderate"
    elif cf >= CF_THRESHOLD_LOW:
        return "Low"
    else:
        return "Very Low"


def cf_to_percentage(cf: float) -> str:
    """
    Convert a certainty factor to a percentage string.
    
    Args:
        cf: Certainty factor [-1.0, 1.0]
    
    Returns:
        Percentage string (e.g., "85%")
    
    Example:
        >>> cf_to_percentage(0.85)
        "85%"
    """
    return f"{int(cf * 100)}%"


# =============================================================================
# Internal Helpers
# =============================================================================

def _clamp_cf(cf: float) -> float:
    """
    Clamp a certainty factor to the valid range [-1.0, 1.0].
    
    Args:
        cf: Certainty factor to clamp
    
    Returns:
        Clamped certainty factor
    """
    return max(-1.0, min(1.0, cf))


def validate_cf(cf: float) -> bool:
    """
    Validate that a value is a valid certainty factor.
    
    Args:
        cf: Value to validate
    
    Returns:
        True if valid CF, False otherwise
    """
    return isinstance(cf, (int, float)) and -1.0 <= cf <= 1.0


# =============================================================================
# END OF cf_utils.py
# =============================================================================
