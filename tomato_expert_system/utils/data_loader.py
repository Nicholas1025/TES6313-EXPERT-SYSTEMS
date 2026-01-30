"""
data_loader.py
Owner: Member A (System Architect, Inference & UI Engineer)

Purpose:
    Data loading utilities for the expert system.
    Handles loading symptom lists, predefined data, and
    configuration for the UI and inference engine.

Functions:
    - load_symptom_list: Load available symptoms for UI
    - load_severity_options: Load severity level options
    - get_symptom_categories: Get symptom categories for organization
"""

from typing import Dict, List, Tuple


# =============================================================================
# Symptom Definitions
# =============================================================================

# Symptom categories and their associated symptoms
# Updated based on Member B and Member C rule requirements
SYMPTOM_CATEGORIES: Dict[str, List[str]] = {
    "Leaves & Stems": [
        "brown-leaf-spots",
        "yellow-halos",
        "bulls-eye-pattern",
        "lower-leaves-first",
        "small-gray-tan-spots",
        "dark-spot-margins",
        "water-soaked-blotches",
        "rapid-leaf-browning",
        "lower-leaf-yellowing",
        "stem-discoloration",
        "leaf-mottling",
        "leaf-distortion",
        "small-dark-spots",
        "leaf-yellowing",
        "spots-merging",
        "leaf-drop",
        "young-leaf-tip-necrosis",
        "dark-green-or-purplish-leaves",
        "leaf-edge-scorching",
        "weak-stems",
        "thin-stems"
    ],
    "Blossoms & Fruits": [
        "dark-fruit-lesions",
        "oily-fruit-lesions",
        "blossom-end-rot",
        "poor-fruit-quality",
        "increased-fruit-acidity",
        "poor-fruit-firmness",
        "delayed-flowering"
    ],
    "Whole Plant": [
        "plant-wilting",
        "bottom-up-collapse",
        "stunted-growth"
    ]
}

# Severity options
SEVERITY_OPTIONS: List[Tuple[str, str]] = [
    ("mild", "Mild - Minor symptoms, plant mostly healthy"),
    ("moderate", "Moderate - Noticeable symptoms, some damage"),
    ("severe", "Severe - Significant symptoms, major damage"),
]


# =============================================================================
# Symptom Loading Functions
# =============================================================================

def load_symptom_list() -> List[str]:
    """
    Load the complete list of available symptoms.
    
    Returns:
        List of all symptom names (symbols)
    
    Example:
        >>> symptoms = load_symptom_list()
        >>> print(symptoms[:3])
        ['yellow-leaves', 'brown-spots', 'leaf-curl']
    """
    all_symptoms = []
    for symptoms in SYMPTOM_CATEGORIES.values():
        all_symptoms.extend(symptoms)
    return all_symptoms


def get_symptom_categories() -> Dict[str, List[str]]:
    """
    Get symptoms organized by category.
    
    Returns:
        Dictionary mapping category names to symptom lists
    
    Example:
        >>> categories = get_symptom_categories()
        >>> print(categories["Leaf Symptoms"][:2])
        ['yellow-leaves', 'brown-spots']
    """
    return SYMPTOM_CATEGORIES.copy()


def load_severity_options() -> List[Tuple[str, str]]:
    """
    Load available severity level options.
    
    Returns:
        List of tuples (value, display_label)
    
    Example:
        >>> options = load_severity_options()
        >>> print(options[0])
        ('mild', 'Mild - Minor symptoms, plant mostly healthy')
    """
    return SEVERITY_OPTIONS.copy()


def get_symptom_display_name(symptom: str) -> str:
    """
    Convert symptom symbol to display-friendly name.
    
    Args:
        symptom: Symptom symbol (e.g., 'yellow-leaves')
    
    Returns:
        Display name (e.g., 'Yellow Leaves')
    """
    return symptom.replace("-", " ").replace("_", " ").title()


def get_symptom_description(symptom: str) -> str:
    """
    Get a description for a symptom (for tooltips/help).
    
    Args:
        symptom: Symptom symbol
    
    Returns:
        Description string
    
    Note:
        TODO: Add detailed descriptions for each symptom
    """
    # Placeholder descriptions - can be expanded
    descriptions = {
        "yellow-leaves": "Leaves turning yellow, may indicate nutrient deficiency or disease",
        "brown-spots": "Brown or dark spots appearing on leaves",
        "leaf-curl": "Leaves curling upward or downward",
        "wilting": "Plant or leaves drooping despite adequate water",
        "blossom-end-rot": "Dark, sunken areas at the blossom end of fruit",
        "fruit-rot": "Soft, decaying areas on fruit",
        "mosaic-pattern": "Mottled light and dark green patterns on leaves",
        "stunted-growth": "Plant significantly smaller than expected",
        "interveinal-chlorosis": "Yellowing between leaf veins while veins stay green",
    }
    return descriptions.get(symptom, f"Observed symptom: {get_symptom_display_name(symptom)}")


# =============================================================================
# Configuration Loading
# =============================================================================

def load_system_config() -> Dict:
    """
    Load system configuration settings.
    
    Returns:
        Configuration dictionary
    """
    return {
        "cf_threshold_minimum": 0.1,
        "cf_threshold_display": 0.2,  # Minimum CF to show in results
        "max_results_disease": 3,
        "max_results_nutrient": 3,
        "show_explanations": True,
        "show_alternatives": True,
    }


# =============================================================================
# Validation Functions
# =============================================================================

def validate_symptom(symptom: str) -> bool:
    """
    Check if a symptom is in the valid symptom list.
    
    Args:
        symptom: Symptom to validate
    
    Returns:
        True if valid, False otherwise
    """
    return symptom in load_symptom_list()


def validate_severity(severity: str) -> bool:
    """
    Check if a severity level is valid.
    
    Args:
        severity: Severity to validate
    
    Returns:
        True if valid, False otherwise
    """
    valid_severities = [s[0] for s in SEVERITY_OPTIONS]
    return severity in valid_severities


# =============================================================================
# END OF data_loader.py
# =============================================================================
