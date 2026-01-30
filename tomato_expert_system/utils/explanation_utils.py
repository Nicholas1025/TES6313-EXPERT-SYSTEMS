"""
explanation_utils.py

Purpose:
    Explanation generation utilities for the expert system.
    Provides functions to create human-readable explanations
    for diagnosis results, CF adjustments, and reasoning paths.
    
Functions:
    - generate_disease_explanation: Explain disease diagnosis
    - generate_nutrient_explanation: Explain nutrient recommendation
    - generate_cf_adjustment_explanation: Explain CF adjustment
    - generate_conflict_resolution_explanation: Explain conflict resolution
    - format_reasoning_chain: Format the full reasoning path
"""

from typing import Dict, List, Optional, Any
from .cf_utils import cf_to_confidence_level, cf_to_percentage


# =============================================================================
# Disease Explanation
# =============================================================================

def generate_disease_explanation(
    disease_name: str,
    cf: float,
    matched_symptoms: List[str],
    rule_explanation: str = ""
) -> str:
    """
    Generate a human-readable explanation for a disease diagnosis.
    
    Args:
        disease_name: Name of the diagnosed disease
        cf: Certainty factor of the diagnosis
        matched_symptoms: List of symptoms that matched the rule
        rule_explanation: Original explanation from the rule (if any)
    
    Returns:
        Formatted explanation string
    
    Example:
        >>> generate_disease_explanation(
        ...     "early-blight",
        ...     0.85,
        ...     ["brown-spots", "yellow-leaves"],
        ...     "Based on concentric ring pattern"
        ... )
        "Disease: Early Blight (85% confidence)..."
    """
    # Format disease name for display
    display_name = _format_name(disease_name)
    confidence = cf_to_percentage(cf)
    level = cf_to_confidence_level(cf)
    
    explanation_parts = [
        f"**Diagnosis: {display_name}**",
        f"Confidence: {confidence} ({level})",
        "",
        "**Evidence (Matched Symptoms):**"
    ]
    
    for symptom in matched_symptoms:
        explanation_parts.append(f"  • {_format_name(symptom)}")
    
    if rule_explanation:
        explanation_parts.extend([
            "",
            "**Reasoning:**",
            rule_explanation
        ])
    
    return "\n".join(explanation_parts)


# =============================================================================
# Nutrient Explanation
# =============================================================================

def generate_nutrient_explanation(
    nutrient_name: str,
    cf: float,
    original_cf: Optional[float] = None,
    matched_symptoms: List[str] = None,
    rule_explanation: str = ""
) -> str:
    """
    Generate a human-readable explanation for a nutrient recommendation.
    
    Args:
        nutrient_name: Name of the nutrient deficiency
        cf: Final certainty factor (after adjustment)
        original_cf: Original CF before adjustment (optional)
        matched_symptoms: List of symptoms that matched the rule
        rule_explanation: Original explanation from the rule (if any)
    
    Returns:
        Formatted explanation string
    """
    display_name = _format_name(nutrient_name)
    confidence = cf_to_percentage(cf)
    level = cf_to_confidence_level(cf)
    
    explanation_parts = [
        f"**Nutrient Deficiency: {display_name}**",
        f"Confidence: {confidence} ({level})"
    ]
    
    # Show adjustment if CF was modified
    if original_cf is not None and original_cf != cf:
        original_pct = cf_to_percentage(original_cf)
        explanation_parts.append(f"(Adjusted from {original_pct} due to disease interaction)")
    
    if matched_symptoms:
        explanation_parts.extend([
            "",
            "**Evidence (Matched Symptoms):**"
        ])
        for symptom in matched_symptoms:
            explanation_parts.append(f"  • {_format_name(symptom)}")
    
    if rule_explanation:
        explanation_parts.extend([
            "",
            "**Reasoning:**",
            rule_explanation
        ])
    
    return "\n".join(explanation_parts)


# =============================================================================
# CF Adjustment Explanation
# =============================================================================

def generate_cf_adjustment_explanation(
    nutrient_name: str,
    disease_name: str,
    original_cf: float,
    impact_factor: float,
    adjusted_cf: float
) -> str:
    """
    Generate an explanation for how disease affected nutrient CF.
    
    Args:
        nutrient_name: Name of the nutrient
        disease_name: Name of the affecting disease
        original_cf: Original nutrient CF
        impact_factor: Disease impact factor applied
        adjusted_cf: Resulting adjusted CF
    
    Returns:
        Formatted explanation string
    """
    nutrient_display = _format_name(nutrient_name)
    disease_display = _format_name(disease_name)
    
    original_pct = cf_to_percentage(original_cf)
    adjusted_pct = cf_to_percentage(adjusted_cf)
    
    # Determine impact direction
    if impact_factor > 1.0:
        direction = "increased"
    elif impact_factor < 1.0:
        direction = "decreased"
    else:
        direction = "unchanged"
    
    explanation = (
        f"The presence of **{disease_display}** has {direction} the confidence "
        f"in **{nutrient_display}** deficiency.\n\n"
        f"• Original confidence: {original_pct}\n"
        f"• Impact factor: {impact_factor:.2f}\n"
        f"• Adjusted confidence: {adjusted_pct}\n\n"
        f"Formula: {original_pct} × {impact_factor:.2f} = {adjusted_pct}"
    )
    
    return explanation


# =============================================================================
# Conflict Resolution Explanation
# =============================================================================

def generate_conflict_resolution_explanation(
    category: str,
    winner: Dict[str, Any],
    alternatives: List[Dict[str, Any]]
) -> str:
    """
    Generate an explanation for conflict resolution decision.
    
    Args:
        category: "disease" or "nutrient"
        winner: Dict with 'name' and 'cf' of winning conclusion
        alternatives: List of alternative conclusions that were rejected
    
    Returns:
        Formatted explanation string
    """
    winner_name = _format_name(winner.get('name', 'Unknown'))
    winner_cf = cf_to_percentage(winner.get('cf', 0))
    
    explanation_parts = [
        f"**{category.title()} Conflict Resolution**",
        "",
        f"Selected: **{winner_name}** ({winner_cf} confidence)",
        "",
        "This was chosen because it has the highest certainty factor."
    ]
    
    if alternatives:
        explanation_parts.extend([
            "",
            "**Alternative considerations (lower confidence):**"
        ])
        for alt in alternatives:
            alt_name = _format_name(alt.get('name', 'Unknown'))
            alt_cf = cf_to_percentage(alt.get('cf', 0))
            explanation_parts.append(f"  • {alt_name}: {alt_cf}")
    
    return "\n".join(explanation_parts)


# =============================================================================
# Full Reasoning Chain
# =============================================================================

def format_reasoning_chain(
    symptoms: List[str],
    disease_result: Optional[Dict[str, Any]],
    nutrient_result: Optional[Dict[str, Any]],
    adjustments: List[Dict[str, Any]] = None
) -> str:
    """
    Format the complete reasoning chain for display.
    
    Args:
        symptoms: List of input symptoms
        disease_result: Disease diagnosis result dict
        nutrient_result: Nutrient recommendation result dict
        adjustments: List of CF adjustment records
    
    Returns:
        Complete formatted reasoning chain
    """
    sections = []
    
    # Section 1: Input Symptoms
    sections.append("## 📋 Input Symptoms\n")
    for symptom in symptoms:
        sections.append(f"• {_format_name(symptom)}")
    sections.append("")
    
    # Section 2: Disease Diagnosis
    sections.append("## 🔬 Disease Diagnosis\n")
    if disease_result and disease_result.get('name') != 'none':
        disease_name = _format_name(disease_result.get('name', 'Unknown'))
        disease_cf = cf_to_percentage(disease_result.get('cf', 0))
        sections.append(f"**{disease_name}** ({disease_cf} confidence)")
        if disease_result.get('explanation'):
            sections.append(f"\n{disease_result['explanation']}")
    else:
        sections.append("No disease detected based on provided symptoms.")
    sections.append("")
    
    # Section 3: CF Adjustments (if any)
    if adjustments:
        sections.append("## 🔄 Integration Layer (CF Adjustments)\n")
        for adj in adjustments:
            sections.append(generate_cf_adjustment_explanation(
                adj.get('nutrient', 'Unknown'),
                adj.get('disease', 'Unknown'),
                adj.get('original_cf', 0),
                adj.get('impact_factor', 1.0),
                adj.get('adjusted_cf', 0)
            ))
        sections.append("")
    
    # Section 4: Nutrient Recommendation
    sections.append("## 🥗 Nutrient Recommendation\n")
    if nutrient_result and nutrient_result.get('name') != 'none':
        nutrient_name = _format_name(nutrient_result.get('name', 'Unknown'))
        nutrient_cf = cf_to_percentage(nutrient_result.get('cf', 0))
        sections.append(f"**{nutrient_name} Deficiency** ({nutrient_cf} confidence)")
        if nutrient_result.get('explanation'):
            sections.append(f"\n{nutrient_result['explanation']}")
    else:
        sections.append("No nutrient deficiency detected based on provided symptoms.")
    sections.append("")
    
    return "\n".join(sections)


# =============================================================================
# Summary Generation
# =============================================================================

def generate_summary(
    disease_result: Optional[Dict[str, Any]],
    nutrient_result: Optional[Dict[str, Any]]
) -> str:
    """
    Generate a brief summary of the diagnosis results.
    
    Args:
        disease_result: Disease diagnosis result dict
        nutrient_result: Nutrient recommendation result dict
    
    Returns:
        Brief summary string
    """
    parts = []
    
    if disease_result and disease_result.get('name') != 'none':
        disease_name = _format_name(disease_result.get('name', 'Unknown'))
        disease_cf = cf_to_percentage(disease_result.get('cf', 0))
        parts.append(f"🔬 **{disease_name}** ({disease_cf})")
    
    if nutrient_result and nutrient_result.get('name') != 'none':
        nutrient_name = _format_name(nutrient_result.get('name', 'Unknown'))
        nutrient_cf = cf_to_percentage(nutrient_result.get('cf', 0))
        parts.append(f"🥗 **{nutrient_name} Deficiency** ({nutrient_cf})")
    
    if not parts:
        return "No significant findings based on the provided symptoms."
    
    return " | ".join(parts)


# =============================================================================
# Helper Functions
# =============================================================================

def _format_name(name: str) -> str:
    """
    Format a symbol name for display (e.g., 'early-blight' -> 'Early Blight').
    
    Args:
        name: Raw name with hyphens
    
    Returns:
        Formatted display name
    """
    if not name:
        return "Unknown"
    return name.replace("-", " ").replace("_", " ").title()


# =============================================================================
# END OF explanation_utils.py
# =============================================================================
