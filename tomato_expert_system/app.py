"""
app.py
Owner: Member A (System Architect, Inference & UI Engineer)

Purpose:
    Streamlit user interface for the Tomato Expert System.
    Provides symptom input, diagnosis execution, and result display.

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
    page_title="Tomato Disease & Nutrient Expert System",
    page_icon="🍅",
    layout="wide",
    initial_sidebar_state="expanded",
)


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
    """Render the application header."""
    st.title("🍅 Tomato Expert System")
    st.markdown("""
    **Smart Disease Diagnosis & Nutrient Recommendation System**
    
    This expert system uses rule-based reasoning with certainty factors
    to diagnose tomato plant diseases and identify nutrient deficiencies.
    
    ---
    """)


def render_symptom_input():
    """Render the symptom input section."""
    st.sidebar.header("📋 Symptom Input")
    
    # Get symptom categories and severity options
    categories = get_symptom_categories()
    severity_options = load_severity_options()
    
    st.sidebar.markdown("Select observed symptoms and their severity:")
    
    selected_symptoms = []
    
    # Render symptoms by category
    for category, symptoms in categories.items():
        with st.sidebar.expander(category, expanded=False):
            for symptom in symptoms:
                col1, col2, col3 = st.columns([3, 2, 1])
                
                display_name = get_symptom_display_name(symptom)
                
                # Checkbox for symptom selection
                with col1:
                    is_selected = st.checkbox(
                        display_name,
                        key=f"symptom_{symptom}",
                    )
                
                if is_selected:
                    # Severity selection
                    with col2:
                        severity = st.selectbox(
                            "Severity",
                            options=[s[0] for s in severity_options],
                            format_func=lambda x: x.title(),
                            key=f"severity_{symptom}",
                            label_visibility="collapsed",
                        )
                    
                    # Confidence slider
                    with col3:
                        cf = st.slider(
                            "CF",
                            min_value=0.1,
                            max_value=1.0,
                            value=1.0,
                            step=0.1,
                            key=f"cf_{symptom}",
                            label_visibility="collapsed",
                        )
                    
                    selected_symptoms.append({
                        "name": symptom,
                        "severity": severity,
                        "cf": cf,
                    })
    
    # Store in session state
    st.session_state.selected_symptoms = selected_symptoms
    
    # Display selected symptoms count
    st.sidebar.markdown("---")
    st.sidebar.metric(
        "Selected Symptoms",
        len(selected_symptoms),
    )
    
    return selected_symptoms


def render_run_button():
    """Render the diagnosis run button."""
    st.sidebar.markdown("---")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        run_clicked = st.button(
            "🔬 Run Diagnosis",
            type="primary",
            use_container_width=True,
        )
    
    with col2:
        clear_clicked = st.button(
            "🗑️ Clear",
            use_container_width=True,
        )
    
    if clear_clicked:
        st.session_state.results = None
        st.session_state.selected_symptoms = []
        st.rerun()
    
    return run_clicked


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
    if not results:
        render_empty_state()
        return
    
    # Summary at the top
    st.markdown("## 📊 Diagnosis Summary")
    summary = generate_summary(results.get("disease"), results.get("nutrient"))
    st.info(summary)
    
    # Create two columns for disease and nutrient
    col1, col2 = st.columns(2)
    
    # Disease Results
    with col1:
        render_disease_results(results)
    
    # Nutrient Results
    with col2:
        render_nutrient_results(results)
    
    # Detailed Reasoning Chain
    st.markdown("---")
    with st.expander("📝 Detailed Reasoning Chain", expanded=False):
        symptom_names = [s["name"] for s in symptoms]
        reasoning = format_reasoning_chain(
            symptom_names,
            results.get("disease"),
            results.get("nutrient"),
            results.get("adjustments"),
        )
        st.markdown(reasoning)
    
    # Debug Information (collapsible)
    with st.expander("🔧 Debug Information", expanded=False):
        st.json({
            "rules_fired": results.get("rules_fired"),
            "phase": results.get("phase"),
            "all_diseases": results.get("all_diseases"),
            "all_nutrients": results.get("all_nutrients"),
            "adjustments": results.get("adjustments"),
        })


def render_disease_results(results: Dict[str, Any]):
    """Render disease diagnosis results."""
    st.markdown("### 🔬 Disease Diagnosis")
    
    disease = results.get("disease")
    
    if disease and disease.get("name") != "none":
        name = disease["name"].replace("-", " ").title()
        cf = disease["cf"]
        explanation = disease.get("explanation", "")
        
        # Main result card
        st.success(f"**{name}**")
        
        # Confidence meter
        st.metric(
            "Confidence",
            cf_to_percentage(cf),
            cf_to_confidence_level(cf),
        )
        
        # Progress bar for CF
        st.progress(max(0, cf))
        
        # Explanation
        if explanation:
            st.markdown("**Reasoning:**")
            st.markdown(explanation)
        
        # Alternative diagnoses
        all_diseases = results.get("all_diseases", [])
        if len(all_diseases) > 1:
            st.markdown("**Other Possibilities:**")
            for d in all_diseases[1:3]:  # Show top 2 alternatives
                alt_name = d["name"].replace("-", " ").title()
                alt_cf = cf_to_percentage(d["cf"])
                st.caption(f"• {alt_name}: {alt_cf}")
    else:
        st.info("No disease detected based on provided symptoms.")


def render_nutrient_results(results: Dict[str, Any]):
    """Render nutrient recommendation results."""
    st.markdown("### 🥗 Nutrient Recommendation")
    
    nutrient = results.get("nutrient")
    
    if nutrient and nutrient.get("name") != "none":
        name = nutrient["name"].replace("-", " ").title()
        cf = nutrient["cf"]
        explanation = nutrient.get("explanation", "")
        
        # Main result card
        st.warning(f"**{name} Deficiency**")
        
        # Confidence meter
        st.metric(
            "Confidence",
            cf_to_percentage(cf),
            cf_to_confidence_level(cf),
        )
        
        # Progress bar for CF
        st.progress(max(0, cf))
        
        # Explanation
        if explanation:
            st.markdown("**Reasoning:**")
            st.markdown(explanation)
        
        # Check for CF adjustments
        adjustments = results.get("adjustments", [])
        nutrient_adj = [a for a in adjustments if a["nutrient"] == nutrient["name"]]
        if nutrient_adj:
            adj = nutrient_adj[0]
            if adj["original_cf"] != adj["adjusted_cf"]:
                st.caption(
                    f"*CF adjusted from {cf_to_percentage(adj['original_cf'])} "
                    f"due to {adj['disease'].replace('-', ' ').title()} "
                    f"(factor: {adj['impact_factor']:.2f})*"
                )
        
        # Alternative recommendations
        all_nutrients = results.get("all_nutrients", [])
        if len(all_nutrients) > 1:
            st.markdown("**Other Possibilities:**")
            for n in all_nutrients[1:3]:  # Show top 2 alternatives
                alt_name = n["name"].replace("-", " ").title()
                alt_cf = cf_to_percentage(n["cf"])
                st.caption(f"• {alt_name}: {alt_cf}")
    else:
        st.info("No nutrient deficiency detected based on provided symptoms.")


def render_empty_state():
    """Render the empty state when no diagnosis has been run."""
    st.markdown("## 🌱 Welcome to the Tomato Expert System")
    
    st.markdown("""
    ### How to Use
    
    1. **Select Symptoms** from the sidebar
       - Choose the symptoms you observe on your tomato plant
       - Set the severity level for each symptom
       - Adjust confidence if you're uncertain about a symptom
    
    2. **Run Diagnosis**
       - Click the "Run Diagnosis" button
       - The system will analyze your symptoms
    
    3. **View Results**
       - See disease diagnosis with confidence levels
       - Get nutrient deficiency recommendations
       - Review the reasoning chain
    
    ---
    
    ### About This System
    
    This expert system uses:
    - **Rule-based reasoning** with CLIPS inference engine
    - **Certainty Factors (CF)** for uncertainty handling
    - **Disease-nutrient integration** for comprehensive recommendations
    
    The system was developed as part of the TES6313 Expert Systems course.
    """)
    
    # Show example
    with st.expander("📖 Example Symptoms"):
        st.markdown("""
        Try selecting these symptoms to test the system:
        
        - Yellow Leaves (moderate severity)
        - Brown Spots (severe severity)
        - Wilting (mild severity)
        
        These symptoms might indicate various diseases like Early Blight
        or nutrient deficiencies like Nitrogen deficiency.
        """)


# =============================================================================
# Main Application
# =============================================================================

def main():
    """Main application entry point."""
    # Initialize session state
    init_session_state()
    
    # Render header
    render_header()
    
    # Render symptom input (sidebar)
    symptoms = render_symptom_input()
    
    # Render run button
    run_clicked = render_run_button()
    
    # Run diagnosis if button clicked
    if run_clicked:
        if symptoms:
            with st.spinner("Running diagnosis..."):
                results = run_diagnosis(symptoms)
                st.session_state.results = results
        else:
            st.sidebar.warning("Please select at least one symptom.")
    
    # Render results or empty state
    if st.session_state.results:
        render_results(st.session_state.results, symptoms)
    else:
        render_empty_state()
    
    # Footer
    st.markdown("---")
    st.caption(
        "TES6313 Expert Systems Project | "
        "Rule-Based Expert System with Certainty Factors"
    )


if __name__ == "__main__":
    main()


# =============================================================================
# END OF app.py
# =============================================================================
