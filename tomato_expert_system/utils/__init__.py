"""
utils package

This package contains utility modules for the tomato expert system:
- cf_utils: Certainty factor computation
- explanation_utils: Explanation generation
- data_loader: Data and configuration loading
"""

from .cf_utils import (
    cf_combine,
    cf_combine_multiple,
    cf_adjust,
    cf_compare,
    cf_select_highest,
    cf_rank_conclusions,
    cf_meets_threshold,
    cf_to_confidence_level,
    cf_to_percentage,
    validate_cf,
    CF_THRESHOLD_VERY_HIGH,
    CF_THRESHOLD_HIGH,
    CF_THRESHOLD_MODERATE,
    CF_THRESHOLD_LOW,
    CF_THRESHOLD_MINIMUM,
)

from .explanation_utils import (
    generate_disease_explanation,
    generate_nutrient_explanation,
    generate_cf_adjustment_explanation,
    generate_conflict_resolution_explanation,
    format_reasoning_chain,
    generate_summary,
)

from .data_loader import (
    load_symptom_list,
    get_symptom_categories,
    load_severity_options,
    get_symptom_display_name,
    get_symptom_description,
    load_system_config,
    validate_symptom,
    validate_severity,
)
