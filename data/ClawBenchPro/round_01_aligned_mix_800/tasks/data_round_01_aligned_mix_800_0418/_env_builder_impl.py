import os
import json
import random
import uuid

def build_env():
    # 1. Create directory structures
    os.makedirs("patient_intake/Cardiology", exist_ok=True)
    os.makedirs("patient_intake/Neurology", exist_ok=True)
    os.makedirs("patient_intake/ER", exist_ok=True)
    os.makedirs("patient_intake/Pediatrics", exist_ok=True)
    os.makedirs("nutrition_orders", exist_ok=True)
    os.makedirs("system_updates", exist_ok=True)
    os.makedirs("nursing_station", exist_ok=True)

    wards = ["Cardiology", "Neurology", "ER", "Pediatrics"]
    first_names = ["James", "Maria", "John", "Betty", "Carlos", "Jane", "Emily", "Luis", "Tom", "Rosa", "Liam", "Olivia", "Noah", "Emma", "Oliver", "Ava", "Elijah", "Charlotte", "Mateo", "Sophia"]
    last_names = ["Smith", "Garcia", "Johnson", "White", "Perez", "Doe", "Davis", "Rodriguez", "Wilson", "Martinez", "Brown", "Jones", "Miller", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin"]
    
    languages = [
        "English", "English (US)", "English (UK)", 
        "Spanish", "ES", "Español", "Spanish (Mexico)", 
        "French", "Mandarin", "Arabic"
    ]
    
    diets = [
        "Regular", "None", "N/A", "Regular Diet", # No restrictions
        "Diabetic", "Low Sodium", "Peanut Allergy", "Gluten Free", "Vegan", "Liquid Diet", "Soft Foods" # Restrictions
    ]

    all_patients = []
    discharged_patients_for_log = []

    # 2. Generate massive fragmented data
    for i in range(1, 401): # 400 patients
        patient_id = f"PT-{i:04d}"
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        ward = random.choice(wards)
        lang = random.choice(languages)
        status = random.choices(["Active", "Discharged", "Transferred"], weights=[0.7, 0.2, 0.1])[0]
        nut_id = f"NUT-{uuid.uuid4().hex[:8].upper()}"
        diet = random.choice(diets)
        
        # Keep track of active ones that get discharged in the daily log
        if status == "Active":
            # 20% chance an active patient was actually discharged today
            if random.random() < 0.2:
                discharged_patients_for_log.append(patient_id)
        
        all_patients.append({
            "id": patient_id,
            "name": name,
            "ward": ward,
            "lang": lang,
            "status": status,
            "nut_id": nut_id,
            "diet": diet
        })

        # Write patient intake JSON
        file_path = f"patient_intake/{ward}/{patient_id}.json"
        patient_data = {
            "patient_id": patient_id,
            "full_name": name,
            "demographics": {
                "primary_language": lang,
                "age": random.randint(1, 99)
            },
            "admission_status": status,
            "nutrition_order_id": nut_id
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(patient_data, f, indent=2)
            
        # Add some noise/backup files
        if random.random() < 0.1:
            with open(f"patient_intake/{ward}/{patient_id}.json.bak", "w", encoding="utf-8") as f:
                f.write("OLD SYSTEM BACKUP - CORRUPTED")

        # Write nutrition order TXT
        nut_path = f"nutrition_orders/{nut_id}.txt"
        with open(nut_path, "w", encoding="utf-8") as f:
            # Add some variability and noise to the text file
            f.write(f"ORDER ID: {nut_id}\n")
            f.write(f"ISSUED TO: {patient_id}\n")
            f.write("-" * 20 + "\n")
            f.write(f"DIETARY INSTRUCTIONS: {diet}\n")
            f.write("NOTES: Please ensure compliance.\n")

    # 3. Generate the daily discharge log (Crucial override info)
    log_path = "system_updates/daily_discharge.log"
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("=== HOSPITAL DAILY DISCHARGE & TRANSFER LOG ===\n")
        f.write("The following patients have left the facility in the last 12 hours.\n\n")
        # Add real discharges and some fake noise
        log_entries = discharged_patients_for_log + ["PT-9999", "PT-8888"]
        random.shuffle(log_entries)
        for pid in log_entries:
            action = random.choice(["discharged home", "transferred to acute care", "transferred to hospice"])
            f.write(f"[{random.randint(8,18)}:00] Notice: Patient {pid} was {action}.\n")
            
if __name__ == "__main__":
    build_env()
