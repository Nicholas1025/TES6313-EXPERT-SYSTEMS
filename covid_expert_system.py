"""
COVID-19 Diagnosis Expert System
A rule-based expert system using CLIPS (clipspy) for COVID-19 symptom diagnosis
with a tkinter GUI interface.
"""

import os
import sys

# Fix tkinter Tcl/Tk path issues on Windows with virtual environments
if sys.platform == "win32" and hasattr(sys, 'base_prefix'):
    # Get the base Python installation path
    base_python = sys.base_prefix
    tcl_path = os.path.join(base_python, 'tcl')
    
    # Set Tcl/Tk environment variables if not already set
    if os.path.exists(tcl_path) and 'TCL_LIBRARY' not in os.environ:
        # Find tcl8.6 directory
        tcl_dirs = [d for d in os.listdir(tcl_path) if d.startswith('tcl8')]
        tk_dirs = [d for d in os.listdir(tcl_path) if d.startswith('tk8')]
        
        if tcl_dirs:
            os.environ['TCL_LIBRARY'] = os.path.join(tcl_path, tcl_dirs[0])
        if tk_dirs:
            os.environ['TK_LIBRARY'] = os.path.join(tcl_path, tk_dirs[0])

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import clips


class CovidExpertSystem:
    """COVID-19 Expert System using CLIPS"""
    
    def __init__(self):
        self.env = clips.Environment()
        self.setup_rules()
    
    def setup_rules(self):
        """Define the knowledge base with rules for COVID-19 diagnosis"""
        
        # Define templates for facts
        self.env.build("(deftemplate patient (slot name (type STRING)) (slot fever (type SYMBOL) (allowed-symbols yes no)) (slot cough (type SYMBOL) (allowed-symbols yes no)) (slot breathing-difficulty (type SYMBOL) (allowed-symbols yes no)) (slot fatigue (type SYMBOL) (allowed-symbols yes no)) (slot loss-of-taste-smell (type SYMBOL) (allowed-symbols yes no)) (slot contact-with-positive (type SYMBOL) (allowed-symbols yes no)))")
        
        self.env.build("(deftemplate diagnosis (slot patient-name (type STRING)) (slot result (type STRING)) (slot recommendation (type STRING)) (slot risk-level (type SYMBOL) (allowed-symbols low medium high critical)))")
        
        # Rule 1: Critical Case Detection - Most severe, checked first
        # If patient has fever + cough + breathing difficulty + fatigue
        self.env.build("""
(defrule critical-case
    "Detects critical cases requiring immediate medical attention"
    (patient 
        (name ?name)
        (fever yes)
        (cough yes)
        (breathing-difficulty yes)
        (fatigue yes))
    =>
    (assert (diagnosis
        (patient-name ?name)
        (result "CRITICAL - Severe COVID-19 Symptoms")
        (recommendation "EMERGENCY: Seek immediate medical attention. Call emergency services. Severe respiratory distress detected.")
        (risk-level critical))))
""")
        
        # Rule 2: High Risk COVID-19 - Breathing difficulty variant
        # If patient has fever + cough + breathing difficulty (but not all 4 critical symptoms)
        self.env.build("""
(defrule high-risk-covid-breathing
    "Detects high-risk COVID-19 cases with breathing issues"
    (patient 
        (name ?name)
        (fever yes)
        (cough yes)
        (breathing-difficulty yes))
    (not (diagnosis (patient-name ?name) (risk-level critical)))
    =>
    (assert (diagnosis
        (patient-name ?name)
        (result "HIGH RISK for COVID-19")
        (recommendation "URGENT: Get PCR test immediately. Self-isolate. Contact healthcare provider. Monitor oxygen levels.")
        (risk-level high))))
""")
        
        # Rule 3: High Risk COVID-19 - Loss of taste/smell variant
        # If patient has fever + cough + loss of taste/smell
        self.env.build("""
(defrule high-risk-covid-taste-smell
    "Detects high-risk COVID-19 cases with loss of taste or smell"
    (patient 
        (name ?name)
        (fever yes)
        (cough yes)
        (loss-of-taste-smell yes))
    (not (diagnosis (patient-name ?name)))
    =>
    (assert (diagnosis
        (patient-name ?name)
        (result "HIGH RISK for COVID-19")
        (recommendation "URGENT: Get PCR test immediately. Self-isolate. Contact healthcare provider. Monitor symptoms closely.")
        (risk-level high))))
""")
        
        # Rule 4: Medium Risk - Fever and fatigue
        self.env.build("""
(defrule medium-risk-fever-fatigue
    "Detects medium-risk cases with fever and fatigue"
    (patient 
        (name ?name)
        (fever yes)
        (fatigue yes))
    (not (diagnosis (patient-name ?name)))
    =>
    (assert (diagnosis
        (patient-name ?name)
        (result "MEDIUM RISK for COVID-19")
        (recommendation "Get tested for COVID-19. Self-monitor symptoms. Avoid contact with others. Rest and stay hydrated.")
        (risk-level medium))))
""")
        
        # Rule 5: Medium Risk - Cough and fatigue
        self.env.build("""
(defrule medium-risk-cough-fatigue
    "Detects medium-risk cases with cough and fatigue"
    (patient 
        (name ?name)
        (cough yes)
        (fatigue yes))
    (not (diagnosis (patient-name ?name)))
    =>
    (assert (diagnosis
        (patient-name ?name)
        (result "MEDIUM RISK for COVID-19")
        (recommendation "Get tested for COVID-19. Self-monitor symptoms. Avoid contact with others. Rest and stay hydrated.")
        (risk-level medium))))
""")
        
        # Rule 6: Medium Risk - Contact with positive case and fever
        self.env.build("""
(defrule medium-risk-contact-fever
    "Detects medium-risk cases with contact history and fever"
    (patient 
        (name ?name)
        (contact-with-positive yes)
        (fever yes))
    (not (diagnosis (patient-name ?name)))
    =>
    (assert (diagnosis
        (patient-name ?name)
        (result "MEDIUM RISK for COVID-19")
        (recommendation "Get tested for COVID-19 due to exposure. Self-isolate until test results. Monitor symptoms daily.")
        (risk-level medium))))
""")
        
        # Rule 7: Medium Risk - Contact with positive case and cough
        self.env.build("""
(defrule medium-risk-contact-cough
    "Detects medium-risk cases with contact history and cough"
    (patient 
        (name ?name)
        (contact-with-positive yes)
        (cough yes))
    (not (diagnosis (patient-name ?name)))
    =>
    (assert (diagnosis
        (patient-name ?name)
        (result "MEDIUM RISK for COVID-19")
        (recommendation "Get tested for COVID-19 due to exposure. Self-isolate until test results. Monitor symptoms daily.")
        (risk-level medium))))
""")
        
        # Rule 8: Low Risk Assessment - Default rule
        self.env.build("""
(defrule low-risk-assessment
    "Provides assessment for low-risk cases"
    (patient (name ?name))
    (not (diagnosis (patient-name ?name)))
    =>
    (assert (diagnosis
        (patient-name ?name)
        (result "LOW RISK for COVID-19")
        (recommendation "Symptoms appear mild. Continue monitoring. Practice good hygiene. Consult doctor if symptoms worsen.")
        (risk-level low))))
""")
    
    def diagnose(self, patient_data):
        """
        Run diagnosis on patient data
        
        Args:
            patient_data: Dictionary containing patient information and symptoms
            
        Returns:
            Dictionary with diagnosis results
        """
        # Reset the environment
        self.env.reset()
        
        # Assert patient facts
        fact_string = f"""(patient
            (name "{patient_data['name']}")
            (fever {patient_data['fever']})
            (cough {patient_data['cough']})
            (breathing-difficulty {patient_data['breathing_difficulty']})
            (fatigue {patient_data['fatigue']})
            (loss-of-taste-smell {patient_data['loss_of_taste_smell']})
            (contact-with-positive {patient_data['contact_with_positive']})
        )"""
        
        self.env.assert_string(fact_string)
        
        # Run the rules
        self.env.run()
        
        # Extract diagnosis
        results = []
        for fact in self.env.facts():
            if fact.template.name == 'diagnosis':
                results.append({
                    'patient_name': fact['patient-name'],
                    'result': fact['result'],
                    'recommendation': fact['recommendation'],
                    'risk_level': str(fact['risk-level'])
                })
        
        return results[0] if results else {
            'patient_name': patient_data['name'],
            'result': 'Unable to diagnose',
            'recommendation': 'Please consult a healthcare professional',
            'risk_level': 'unknown'
        }


class CovidDiagnosisGUI:
    """Tkinter GUI for COVID-19 Expert System"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("COVID-19 Diagnosis Expert System - AI Medical Assistant")
        self.root.geometry("750x750")
        self.root.resizable(True, True)
        
        # Set window icon behavior
        try:
            self.root.iconbitmap('default')
        except:
            pass
        
        # Initialize expert system
        self.expert_system = CovidExpertSystem()
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        
        # Configure root window
        self.root.configure(bg='#f0f0f0')
        
        # Main container with background
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=30, pady=20)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Header section with colored background
        header_frame = tk.Frame(main_frame, bg='#2c3e50', padx=20, pady=15)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Title
        title_label = tk.Label(
            header_frame, 
            text="🏥 COVID-19 Diagnosis Expert System",
            font=('Arial', 20, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame,
            text="Rule-Based Symptom Assessment Tool",
            font=('Arial', 11, 'italic'),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Instruction section
        instruction_frame = tk.Frame(main_frame, bg='#e8f4f8', bd=1, relief=tk.SOLID, padx=15, pady=10)
        instruction_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        instruction_label = tk.Label(
            instruction_frame,
            text="📋 Please provide patient information and answer all symptom questions accurately",
            font=('Arial', 10),
            bg='#e8f4f8',
            fg='#2c3e50',
            wraplength=600,
            justify=tk.LEFT
        )
        instruction_label.pack()
        
        # Patient Information Section
        patient_frame = tk.LabelFrame(
            main_frame, 
            text=" 👤 Patient Information ",
            font=('Arial', 11, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50',
            padx=15,
            pady=10
        )
        patient_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        tk.Label(
            patient_frame, 
            text="Patient Name:", 
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0',
            fg='#34495e'
        ).grid(row=0, column=0, sticky=tk.W, pady=8)
        
        self.name_entry = tk.Entry(
            patient_frame, 
            width=35, 
            font=('Arial', 11),
            bd=2,
            relief=tk.GROOVE
        )
        self.name_entry.grid(row=0, column=1, sticky=tk.W, pady=8, padx=(15, 0))
        
        # Symptom Assessment Section
        symptom_frame = tk.LabelFrame(
            main_frame,
            text=" 🩺 Symptom Assessment ",
            font=('Arial', 11, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50',
            padx=15,
            pady=10
        )
        symptom_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.symptom_vars = {}
        symptoms = [
            ("fever", "🌡️ Do you have fever (≥37.8°C/100°F)?"),
            ("cough", "😷 Do you have a persistent cough?"),
            ("breathing_difficulty", "💨 Do you have difficulty breathing or shortness of breath?"),
            ("fatigue", "😴 Are you experiencing unusual tiredness or fatigue?"),
            ("loss_of_taste_smell", "👃 Have you lost your sense of taste or smell?"),
            ("contact_with_positive", "🤝 Have you been in close contact with a confirmed COVID-19 case?")
        ]
        
        row = 0
        for idx, (key, question) in enumerate(symptoms):
            # Alternate background colors for better readability
            bg_color = '#ffffff' if idx % 2 == 0 else '#f8f9fa'
            
            question_frame = tk.Frame(symptom_frame, bg=bg_color, padx=10, pady=8)
            question_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
            
            tk.Label(
                question_frame, 
                text=question, 
                font=('Arial', 10),
                bg=bg_color,
                fg='#2c3e50',
                anchor='w'
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            var = tk.StringVar(value="no")
            self.symptom_vars[key] = var
            
            radio_frame = tk.Frame(question_frame, bg=bg_color)
            radio_frame.pack(side=tk.RIGHT, padx=10)
            
            yes_radio = tk.Radiobutton(
                radio_frame, 
                text="Yes", 
                variable=var, 
                value="yes",
                font=('Arial', 9, 'bold'),
                bg=bg_color,
                fg='#e74c3c',
                selectcolor='white',
                activebackground=bg_color
            )
            yes_radio.pack(side=tk.LEFT, padx=8)
            
            no_radio = tk.Radiobutton(
                radio_frame, 
                text="No", 
                variable=var, 
                value="no",
                font=('Arial', 9, 'bold'),
                bg=bg_color,
                fg='#27ae60',
                selectcolor='white',
                activebackground=bg_color
            )
            no_radio.pack(side=tk.LEFT, padx=8)
            
            row += 1
        
        # Action Buttons
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.grid(row=4, column=0, columnspan=2, pady=25)
        
        self.diagnose_btn = tk.Button(
            button_frame,
            text="🔍 GET DIAGNOSIS",
            command=self.run_diagnosis,
            font=('Arial', 16, 'bold'),
            bg='#3498db',
            fg='white',
            activebackground='#2980b9',
            activeforeground='white',
            width=25,
            height=2,
            cursor='hand2',
            relief=tk.RAISED,
            bd=4
        )
        self.diagnose_btn.pack(pady=10)
        
        self.reset_btn = tk.Button(
            button_frame,
            text="🔄 Reset Form",
            command=self.reset_form,
            font=('Arial', 11),
            bg='#95a5a6',
            fg='white',
            activebackground='#7f8c8d',
            activeforeground='white',
            padx=20,
            pady=8,
            cursor='hand2',
            relief=tk.RAISED,
            bd=3
        )
        self.reset_btn.pack(pady=5)
        
        # Disclaimer
        disclaimer_frame = tk.Frame(main_frame, bg='#fff3cd', bd=1, relief=tk.SOLID, padx=10, pady=8)
        disclaimer_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        disclaimer = tk.Label(
            disclaimer_frame,
            text="⚠️  DISCLAIMER: This is an educational tool for learning purposes only.\n"
                 "Always consult qualified healthcare professionals for medical advice and COVID-19 testing.",
            font=('Arial', 9, 'italic'),
            bg='#fff3cd',
            fg='#856404',
            wraplength=630,
            justify=tk.CENTER
        )
        disclaimer.pack()
    
    def run_diagnosis(self):
        """Run the expert system diagnosis"""
        # Validate input
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter patient name")
            return
        
        # Collect patient data
        patient_data = {
            'name': name,
            'fever': self.symptom_vars['fever'].get(),
            'cough': self.symptom_vars['cough'].get(),
            'breathing_difficulty': self.symptom_vars['breathing_difficulty'].get(),
            'fatigue': self.symptom_vars['fatigue'].get(),
            'loss_of_taste_smell': self.symptom_vars['loss_of_taste_smell'].get(),
            'contact_with_positive': self.symptom_vars['contact_with_positive'].get()
        }
        
        # Run diagnosis
        try:
            diagnosis = self.expert_system.diagnose(patient_data)
            self.show_results_window(diagnosis)
        except Exception as e:
            messagebox.showerror("Error", f"Diagnosis failed: {str(e)}")
    
    def show_results_window(self, diagnosis):
        """Show diagnosis results in a new window"""
        from datetime import datetime
        
        # Create new window
        results_window = tk.Toplevel(self.root)
        results_window.title("Diagnosis Report - COVID-19 Expert System")
        results_window.geometry("800x700")
        results_window.resizable(False, False)
        results_window.configure(bg='#f0f0f0')
        
        # Make window modal
        results_window.transient(self.root)
        results_window.grab_set()
        
        risk_level = diagnosis['risk_level']
        
        # Risk level colors
        risk_colors = {
            'critical': '#c0392b',
            'high': '#d35400',
            'medium': '#f39c12',
            'low': '#27ae60'
        }
        
        risk_bg_colors = {
            'critical': '#fadbd8',
            'high': '#fde3cf',
            'medium': '#fef5e7',
            'low': '#d5f4e6'
        }
        
        main_color = risk_colors.get(risk_level, '#34495e')
        bg_color = risk_bg_colors.get(risk_level, '#ffffff')
        
        # Header with risk-based color
        header_frame = tk.Frame(results_window, bg=main_color, padx=20, pady=20)
        header_frame.pack(fill=tk.X)
        
        risk_icons = {
            'critical': '🚨',
            'high': '⚠️',
            'medium': '⚡',
            'low': '✅'
        }
        icon = risk_icons.get(risk_level, '📋')
        
        tk.Label(
            header_frame,
            text=f"{icon} DIAGNOSIS REPORT",
            font=('Arial', 24, 'bold'),
            bg=main_color,
            fg='white'
        ).pack()
        
        tk.Label(
            header_frame,
            text=f"Risk Level: {risk_level.upper()}",
            font=('Arial', 14, 'bold'),
            bg=main_color,
            fg='white'
        ).pack(pady=(5, 0))
        
        # Main content frame
        content_frame = tk.Frame(results_window, bg='#f0f0f0', padx=30, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Patient Information Section
        patient_frame = tk.LabelFrame(
            content_frame,
            text=" 👤 Patient Information ",
            font=('Arial', 12, 'bold'),
            bg='#ffffff',
            fg='#2c3e50',
            padx=20,
            pady=15
        )
        patient_frame.pack(fill=tk.X, pady=(0, 15))
        
        info_text = tk.Text(
            patient_frame,
            height=3,
            font=('Arial', 11),
            bg='#ffffff',
            fg='#2c3e50',
            bd=0,
            wrap=tk.WORD
        )
        info_text.pack(fill=tk.X)
        info_text.insert(tk.END, f"Name: {diagnosis['patient_name']}\n")
        info_text.insert(tk.END, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        info_text.insert(tk.END, f"Assessment ID: COVID-{datetime.now().strftime('%Y%m%d%H%M%S')}")
        info_text.config(state=tk.DISABLED)
        
        # Diagnosis Section
        diagnosis_frame = tk.LabelFrame(
            content_frame,
            text=f" {icon} Diagnosis Result ",
            font=('Arial', 12, 'bold'),
            bg=bg_color,
            fg=main_color,
            padx=20,
            pady=15
        )
        diagnosis_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            diagnosis_frame,
            text=diagnosis['result'],
            font=('Arial', 16, 'bold'),
            bg=bg_color,
            fg=main_color,
            wraplength=700,
            justify=tk.CENTER
        ).pack(pady=10)
        
        # Risk meter
        risk_bars = {
            'low': '█░░░░',
            'medium': '███░░',
            'high': '████░',
            'critical': '█████'
        }
        
        tk.Label(
            diagnosis_frame,
            text=f"Risk Meter: [{risk_bars.get(risk_level, '░░░░░')}]",
            font=('Consolas', 14, 'bold'),
            bg=bg_color,
            fg=main_color
        ).pack()
        
        # Recommendations Section
        rec_frame = tk.LabelFrame(
            content_frame,
            text=" 💊 Medical Recommendations ",
            font=('Arial', 12, 'bold'),
            bg='#ffffff',
            fg='#2c3e50',
            padx=20,
            pady=15
        )
        rec_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        rec_text = scrolledtext.ScrolledText(
            rec_frame,
            height=6,
            font=('Arial', 11),
            bg='#ffffff',
            fg='#2c3e50',
            wrap=tk.WORD,
            bd=0,
            padx=10,
            pady=5
        )
        rec_text.pack(fill=tk.BOTH, expand=True)
        rec_text.insert(tk.END, diagnosis['recommendation'])
        rec_text.config(state=tk.DISABLED)
        
        # Footer note
        note_frame = tk.Frame(content_frame, bg='#e8f4f8', bd=1, relief=tk.SOLID, padx=15, pady=10)
        note_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            note_frame,
            text="📝 This assessment is generated using CLIPS expert system with rule-based AI logic.\n"
                 "⚠️ For medical advice, please consult qualified healthcare professionals.",
            font=('Arial', 9, 'italic'),
            bg='#e8f4f8',
            fg='#2c3e50',
            justify=tk.CENTER
        ).pack()
        
        # Close button
        close_btn = tk.Button(
            content_frame,
            text="✓ Close Report",
            command=results_window.destroy,
            font=('Arial', 13, 'bold'),
            bg='#34495e',
            fg='white',
            activebackground='#2c3e50',
            activeforeground='white',
            padx=40,
            pady=12,
            cursor='hand2',
            relief=tk.RAISED,
            bd=3
        )
        close_btn.pack(pady=10)
        
        # Center the window
        results_window.update_idletasks()
        x = (results_window.winfo_screenwidth() // 2) - (results_window.winfo_width() // 2)
        y = (results_window.winfo_screenheight() // 2) - (results_window.winfo_height() // 2)
        results_window.geometry(f'+{x}+{y}')
    
    def reset_form(self):
        """Reset all form fields"""
        self.name_entry.delete(0, tk.END)
        for var in self.symptom_vars.values():
            var.set("no")
        messagebox.showinfo("Form Reset", "All fields have been reset successfully!")


def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = CovidDiagnosisGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
