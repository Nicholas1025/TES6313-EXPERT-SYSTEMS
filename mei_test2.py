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
from tkinter import messagebox
from clips import Environment

# Initialize CLIPS
env = Environment()

# ---------------------------------------------------
# Templates
# ---------------------------------------------------
env.build("(deftemplate symptom (slot name) (slot value))")
env.build("(deftemplate diagnosis (slot value))")

# ---------------------------------------------------
# Rules
# ---------------------------------------------------
# Rule 1: COVID if fever=yes and cough=yes
env.build(
    "(defrule covid-rule "
    "(symptom (name fever) (value yes)) "
    "(symptom (name cough) (value yes)) "
    "=> "
    "(assert (diagnosis (value covid)))"
    ")"
)

# Rule 2: Healthy if fever=no and cough=no
env.build(
    "(defrule healthy-rule "
    "(symptom (name fever) (value no)) "
    "(symptom (name cough) (value no)) "
    "=> "
    "(assert (diagnosis (value healthy)))"
    ")"
)

# ---------------------------------------------------
# Diagnosis function
# ---------------------------------------------------
def diagnose():
    env.reset()

    # Insert facts based on user input
    env.assert_string(f"(symptom (name fever) (value {fever_var.get()}))")
    env.assert_string(f"(symptom (name cough) (value {cough_var.get()}))")

    # Run rules
    env.run()

    # Get diagnosis
    diagnosis = None
    for fact in env.facts():
        if fact.template.name == "diagnosis":
            diagnosis = fact["value"]

    if diagnosis is None:
        diagnosis = "Unknown / low risk"

    messagebox.showinfo("Diagnosis Result", f"Diagnosis: {diagnosis}")

# ---------------------------------------------------
# GUI
# ---------------------------------------------------
window = tk.Tk()
window.title("COVID-19 Expert System")
window.geometry("300x220")

tk.Label(window, text="COVID-19 Expert System", font=("Arial", 14, "bold")).pack(pady=10)

fever_var = tk.StringVar(value="no")
cough_var = tk.StringVar(value="no")

tk.Label(window, text="Fever?").pack()
tk.OptionMenu(window, fever_var, "yes", "no").pack()

tk.Label(window, text="Cough?").pack()
tk.OptionMenu(window, cough_var, "yes", "no").pack()

tk.Button(window, text="Diagnose", command=diagnose, bg="blue", fg="white").pack(pady=15)

window.mainloop()
