import os
import csv

def build_env():
    base_dir = "assets/data_321"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Messy Inventory
    inventory_content = """
    Box 1: Lisinopril 10mg - qty: 50 pills total inside.
    Found some Metformin 500mg... looks like 100 units.
    Amoxicillin 250mg (20 capsules)
    Wait, another box of Lisinopril 10mg, qty: 15.
    """
    with open(os.path.join(base_dir, "inventory.txt"), "w") as f:
        f.write(inventory_content.strip())

    # 2. Patient CSV
    patients = [
        ["Patient_Name", "Drug_Requested", "Qty_Requested"],
        ["John Doe", "Lisinopril 10mg", "30"],
        ["Jane Smith", "Metformin 500mg", "120"],
        ["Bob Lee", "Amoxicillin 250mg", "30"],
        ["Alice Joy", "Lisinopril 10mg", "40"],
        ["Charlie Brown", "Metformin 500mg", "20"]
    ]
    with open(os.path.join(base_dir, "clinic_patients.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(patients)

    # 3. Buggy Python Script
    buggy_script = """import json

# Max safety limits for the clinic
LIMITS = {
    "Lisinopril 10mg": 30,
    "Metformin 500mg": 90,
    "Amoxicillin 250mg": 40
}

def apply_safety_caps(input_file, output_file):
    with open(input_file, 'r') as f:
        data = json.load(f)
        
    # Read the original requests to know what drug they mapped to
    # Actually, let's just cheat and hardcode the mapping for this script based on the CSV I remember
    patient_drugs = {
        "John Doe": "Lisinopril 10mg",
        "Jane Smith": "Metformin 500mg",
        "Bob Lee": "Amoxicillin 250mg",
        "Alice Joy": "Lisinopril 10mg",
        "Charlie Brown": "Metformin 500mg"
    }
    
    safe_data = {}
    for patient, qty in data.items():
        drug = patient_drugs.get(patient)
        if drug in LIMITS:
            # BUG 1: Logic error, should be min(qty, LIMITS[drug])
            safe_qty = max(qty, LIMITS[drug]) 
        else:
            safe_qty = qty
        safe_data[patient] = safe_qty
        
    # BUG 2: Syntax / Name Error (using jsons instead of json, and wrong file mode)
    with open(output_file, 'r') as out:
        jsons.dump(safe_data, out, indent=4)

if __name__ == "__main__":
    apply_safety_caps("distribution_list.json", "final_cleared_list.json")
"""
    with open(os.path.join(base_dir, "verify_safety.py"), "w") as f:
        f.write(buggy_script)

if __name__ == "__main__":
    build_env()
