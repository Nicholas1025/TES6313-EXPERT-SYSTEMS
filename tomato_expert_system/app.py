"""
app.py
Owner: Member A (System Architect, Inference & UI Engineer)

Purpose:
    Streamlit user interface for the Tomato Expert System.
    Provides symptom input, diagnosis execution, and result display.
    
    Style: Scientific, Minimalist, Academic, White-theme.

Usage:
    streamlit run app.py
"""

import streamlit as st
from typing import List, Dict, Any

# Import system components
from run_system import TomatoExpertSystem
from utils.data_loader import (
    get_symptom_categories,
    load_severity_options,
    get_symptom_display_name,
    load_system_config,
)
from utils.explanation_utils import (
    format_reasoning_chain,
    generate_summary,
)
from utils.cf_utils import (
    cf_to_percentage,
    cf_to_confidence_level,
)


# =============================================================================
# Page Configuration
# =============================================================================

st.set_page_config(
    page_title="Tomato Diagnostics Expert System",
    page_icon="🍅",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for scientific/academic look
st.markdown("""
<style>
    /* Global Text Styles */
    body {
        color: #333333;
        background-color: #FFFFFF;
        font-family: "Segoe UI", Arial, sans-serif;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #2c3e50;
        font-weight: 600;
        font-family: "Segoe UI", Arial, sans-serif;
    }
    
    h1 {
        font-size: 2.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #f0f0f0;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #e9ecef;
    }
    
    /* Result Cards */
    div.result-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: #2c3e50;
    }
    
    /* Buttons */
    button[data-testid="baseButton-primary"] {
        background-color: #2c3e50;
        border-color: #2c3e50;
    }
    button[data-testid="baseButton-primary"]:hover {
        background-color: #34495e;
        border-color: #34495e;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# Session State Initialization
# =============================================================================

def init_session_state():
    """Initialize session state variables."""
    if "selected_symptoms" not in st.session_state:
        st.session_state.selected_symptoms = []
    if "results" not in st.session_state:
        st.session_state.results = None
    if "expert_system" not in st.session_state:
        st.session_state.expert_system = TomatoExpertSystem()


# =============================================================================
# UI Components
# =============================================================================

def render_header():
    """Render the application header with academic styling."""
    
    # Header container
    col1, col2 = st.columns([1, 4])
    
    with col1:
        # Placeholder for reliable tomato image
        # Using a generic specific scientific-looking tomato illustration or icon
        st.image("https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&w=300&q=80", use_container_width=True)
    
    with col2:
        st.title("Tomato Expert System")
        st.markdown("### Intelligent Diagnostic Support System")
        st.markdown("""
        *Rule-Based Inference Engine with Certainty Factor Reasoning*
        
        This system assists in the identification of tomato diseases and nutrient deficiencies
        through symptom analysis. It employs a modular knowledge base and uncertainty
        management to provide explainable diagnostic results.
        """)


def render_symptom_input():
    """Render the symptom input section."""
    st.sidebar.markdown("## 📋 Clinical Observation")
    st.sidebar.caption("Select observed symptoms and severity levels.")
    
    # Get symptom categories and severity options
    categories = get_symptom_categories()
    severity_options = load_severity_options()
    
    selected_symptoms = []
    
    # Render symptoms by category
    for category, symptoms in categories.items():
        with st.sidebar.expander(category, expanded=False):
            for symptom in symptoms:
                st.markdown(f"**{get_symptom_display_name(symptom)}**")
                col_check, col_sev, col_cf = st.columns([1, 3, 2])
                
                # Checkbox
                with col_check:
                    is_selected = st.checkbox(
                        "Observed",
                        key=f"symptom_{symptom}",
                        label_visibility="collapsed"
                    )
                
                if is_selected:
                    # Severity
                    with col_sev:
                        severity = st.selectbox(
                            "Severity",
                            options=[s[0] for s in severity_options],
                            format_func=lambda x: x.title(),
                            key=f"severity_{symptom}",
                            label_visibility="collapsed",
                        )
                    
                    # CF
                    with col_cf:
                        cf = st.number_input(
                            "CF",
                            min_value=0.1, max_value=1.0, value=1.0, step=0.1,
                            key=f"cf_{symptom}",
                            label_visibility="collapsed",
                            help="Certainty of observation (0.1 - 1.0)"
                        )
                    
                    selected_symptoms.append({
                        "name": symptom,
                        "severity": severity,
                        "cf": cf,
                    })
                st.divider()
    
    st.session_state.selected_symptoms = selected_symptoms
    
    if selected_symptoms:
        st.sidebar.info(f"{len(selected_symptoms)} symptoms recorded")
    
    return selected_symptoms


def render_run_button():
    """Render the run button."""
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🔬 Execute Diagnosis", type="primary", use_container_width=True):
        return True
    
    if st.sidebar.button("Reset System", use_container_width=True):
        st.session_state.results = None
        st.session_state.selected_symptoms = []
        st.rerun()
        return False
    
    return False


def run_diagnosis(symptoms: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Run the expert system diagnosis."""
    try:
        system = st.session_state.expert_system
        results = system.run_diagnosis(symptoms)
        return results
    except Exception as e:
        st.error(f"Error during diagnosis: {str(e)}")
        return None


def render_results(results: Dict[str, Any], symptoms: List[Dict[str, Any]]):
    """Render the diagnosis results."""
    
    st.markdown("## 📊 Diagnostic Report")
    
    if not results:
        render_empty_state()
        return
    
    # Summary Section
    with st.container(border=True):
        st.markdown("### Executive Summary")
        summary_text = generate_summary(results.get("disease"), results.get("nutrient"))
        st.markdown(f"**Findings:** {summary_text}")
    
    st.markdown("### Detailed Analysis")
    col1, col2 = st.columns(2)
    
    # Disease Analysis Column
    with col1:
        with st.container(border=True):
            render_disease_card(results)

    # Nutrient Analysis Column
    with col2:
        with st.container(border=True):
            render_nutrient_card(results)
    
    # Integration Analysis
    if results.get("adjustments"):
        with st.container(border=True):
            st.markdown("### 🔄 Interaction Effects (Integration Layer)")
            for adj in results["adjustments"]:
                st.markdown(f"""
                **{adj['nutrient'].title()} Confidence Adjustment:**
                - Influence: *{adj['disease'].replace('-', ' ').title()}*
                - Impact Factor: `{adj['impact_factor']:.2f}`
                - Adjustment: `{cf_to_percentage(adj['original_cf'])}` → `{cf_to_percentage(adj['adjusted_cf'])}`
                """)

    # Reasoning Chain
    with st.expander("📄 View Full Reasoning Trace"):
        symptom_names = [s["name"] for s in symptoms]
        reasoning = format_reasoning_chain(
            symptom_names,
            results.get("disease"),
            results.get("nutrient"),
            results.get("adjustments"),
        )
        st.markdown(reasoning)


def render_disease_card(results: Dict[str, Any]):
    st.markdown("#### 🔬 Disease Pathology")
    disease = results.get("disease")
    
    if disease and disease.get("name") != "none":
        st.success(f"**{disease['name'].replace('-', ' ').title()}**")
        st.metric("Certainty Factor", f"{disease['cf']:.2f}")
        st.progress(max(0, disease['cf']))
        st.markdown(f"**Reasoning:** {disease.get('explanation', '')}")
    else:
        st.info("No pathogenic disease identified from current symptoms.")


def render_nutrient_card(results: Dict[str, Any]):
    st.markdown("#### 🥗 Nutritional Status")
    nutrient = results.get("nutrient")
    
    if nutrient and nutrient.get("name") != "none":
        st.warning(f"**{nutrient['name'].replace('-', ' ').title()} Deficiency**")
        st.metric("Certainty Factor", f"{nutrient['cf']:.2f}")
        st.progress(max(0, nutrient['cf']))
        st.markdown(f"**Reasoning:** {nutrient.get('explanation', '')}")
    else:
        st.info("No nutritional deficiencies identified.")


def render_empty_state():
    """Render the empty state."""
    st.markdown("""
    <div style='background-color: #f8f9fa; padding: 20px; border-radius: 5px; border-left: 5px solid #2c3e50;'>
        <h4>System Ready</h4>
        <p>Please enter observed symptoms in the sidebar to initiate the diagnostic process.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=300&q=80", caption="Healthy Leaf Structure")
    with col2:
        st.image("https://images.unsplash.com/photo-1592841200221-a6898f307baa?auto=format&fit=crop&w=300&q=80", caption="Fruit Development")
    with col3:
        st.image("https://images.unsplash.com/photo-1560493676-04071c5f467b?auto=format&fit=crop&w=300&q=80", caption="Root Systems")


# =============================================================================
# Main Application
# =============================================================================

def main():
    init_session_state()
    render_header()
    symptoms = render_symptom_input()
    
    if render_run_button():
        if symptoms:
            with st.spinner("Processing knowledge rules..."):
                st.session_state.results = run_diagnosis(symptoms)
        else:
            st.sidebar.warning("Input required: No symptoms selected.")
    
    render_results(st.session_state.results, symptoms)
    
    st.markdown("---")
    st.caption("TES6313 Project | Department of Computer Science & Agriculture | Academic Use Only")


if __name__ == "__main__":
    main()



# =============================================================================
# END OF app.py
# =============================================================================
