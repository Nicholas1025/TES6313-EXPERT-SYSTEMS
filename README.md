# A Rule-Based Expert System with Uncertainty Reasoning for Smart Tomato Disease Diagnosis and Nutrient Recommendation

## Abstract
This project develops a rule-based expert system for diagnosing tomato diseases and recommending nutrient interventions under uncertainty. The system implements certainty factors (CF) for uncertainty handling and uses a CLIPS inference engine (via CLIPSPY) with a Streamlit interface for interactive use. Disease diagnosis and nutrient recommendations remain logically independent; disease outcomes only adjust nutrient confidence values through a separate integration layer.

## Objectives
- Provide explainable tomato disease diagnosis based on observable symptoms.
- Recommend nutrient deficiencies and interventions with CF-based uncertainty reasoning.
- Preserve modular knowledge separation for disease and nutrient domains.
- Ensure academic transparency and verifiability of rule bases.

## System Architecture
The system is organized into three major layers:
1) **User Interface** — Streamlit-based input and result visualization.
2) **Inference Orchestration** — CLIPSPY environment setup, fact assertion, and inference execution.
3) **Knowledge Modules** — Disease rules, nutrient rules, and an integration layer for CF adjustment.

## Reasoning Flow
1. Assert symptoms.
2. Run disease inference.
3. Apply CF-based integration:
   $\text{Adjusted\_Nutrient\_CF} = \text{Base\_Nutrient\_CF} \times \text{Disease\_Impact\_Factor}$
4. Run nutrient inference.
5. Resolve conflicts independently within disease and nutrient conclusions (highest CF wins).

## Uncertainty Handling
Certainty Factors (CF) quantify confidence in conclusions. The system supports CF combination and adjustment. Disease outcomes do not control nutrient logic; they only influence nutrient confidence through impact factors defined by the nutrient knowledge module.

## Conflict Resolution
Conflict resolution is applied independently within disease conclusions and within nutrient recommendations using CF comparison, ensuring consistent and explainable decision-making.

## Implementation Overview
- Inference control and templates are defined in [tomato_expert_system/clips_rules/main_system.clp](tomato_expert_system/clips_rules/main_system.clp).
- CF adjustment and conflict resolution are defined in [tomato_expert_system/clips_rules/integration.clp](tomato_expert_system/clips_rules/integration.clp).
- Disease rules are defined in [tomato_expert_system/clips_rules/disease_rules.clp](tomato_expert_system/clips_rules/disease_rules.clp).
- Nutrient rules and disease–nutrient impact factors are defined in [tomato_expert_system/clips_rules/nutrient_rules.clp](tomato_expert_system/clips_rules/nutrient_rules.clp).
- System orchestration is implemented in [tomato_expert_system/run_system.py](tomato_expert_system/run_system.py).
- The Streamlit UI is implemented in [tomato_expert_system/app.py](tomato_expert_system/app.py).

## Project Structure
```
tomato_expert_system/
├── app.py
├── run_system.py
│
├── clips_rules/
│   ├── main_system.clp
│   ├── integration.clp
│   ├── disease_rules.clp
│   └── nutrient_rules.clp
│
├── utils/
│   ├── cf_utils.py
│   ├── explanation_utils.py
│   └── data_loader.py
│
└── tests/
	├── test_integration.py
	├── test_disease.py
	└── test_nutrient.py
```

## Installation
1. Install dependencies from [requirements.txt](requirements.txt).
2. Ensure Python 3.8+ and CLIPSPY are available.

## Running the Application
Use Streamlit to launch the UI:

- Entry point: [tomato_expert_system/app.py](tomato_expert_system/app.py)

## Testing
- System-level tests: [tomato_expert_system/tests/test_integration.py](tomato_expert_system/tests/test_integration.py)
- Disease rule tests: [tomato_expert_system/tests/test_disease.py](tomato_expert_system/tests/test_disease.py)
- Nutrient rule tests: [tomato_expert_system/tests/test_nutrient.py](tomato_expert_system/tests/test_nutrient.py)

## Project Contributors
This research project and expert system implementation were conducted by:

*   **Nicholas Tay Jun Yang**
*   **Ong Hai Mei**
*   **Yap Pei Ying**

The team collectively contributed to the system architecture design, knowledge engineering for disease and nutrient domains, and the development of the uncertainty reasoning framework.

## Knowledge Sources and Validation
All disease and nutrient rules must be justified with literature sources. Impact factors should be documented with citations and aligned with agronomic evidence.

## Limitations
The system is a rule-based academic prototype and depends on the completeness and quality of the encoded knowledge base. Outputs are intended for educational and decision-support purposes, not as a replacement for expert agronomic consultation.

