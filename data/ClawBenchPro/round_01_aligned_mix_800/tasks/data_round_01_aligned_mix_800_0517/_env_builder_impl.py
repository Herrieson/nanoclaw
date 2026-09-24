import os
import json
import csv
import random
from datetime import datetime, timedelta

def build_env():
    # Set deterministic seed so verify_rules.py can mathematically verify the exact sums
    random.seed(1334)
    
    # Create the wasteland directory structure
    dirs = [
        "hospital_data/hr",
        "hospital_data/timecards",
        "hospital_data/email_backups",
        "hospital_data/patients",
        "board_submission"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 1. Generate HR Master Registry (Noise + Targets)
    hr_registry = []
    
    # Target approved staff (CLEARED and ACTIVE)
    approved_staff = [
        {"Staff_ID": "STF-001", "Name": "Dr. Adams", "Background_Check": "CLEARED", "Status": "ACTIVE"},
        {"Staff_ID": "STF-015", "Name": "Nurse Sarah", "Background_Check": "CLEARED", "Status": "ACTIVE"},
        {"Staff_ID": "STF-042", "Name": "Dr. Chen", "Background_Check": "CLEARED", "Status": "ACTIVE"},
        {"Staff_ID": "STF-088", "Name": "Paramedic Joe", "Background_Check": "CLEARED", "Status": "ACTIVE"},
        {"Staff_ID": "STF-102", "Name": "Dr. Tariq", "Background_Check": "CLEARED", "Status": "ACTIVE"}
    ]
    
    # Decoy staff (Partial match or invalid)
    decoy_staff = [
        {"Staff_ID": "STF-002", "Name": "Fake Volunteer", "Background_Check": "PENDING", "Status": "ACTIVE"},
        {"Staff_ID": "STF-016", "Name": "Old Doc", "Background_Check": "CLEARED", "Status": "RETIRED"},
        {"Staff_ID": "STF-043", "Name": "Shady Medic", "Background_Check": "FAILED", "Status": "ACTIVE"},
        {"Staff_ID": "STF-099", "Name": "Random Guy", "Background_Check": "PENDING", "Status": "INACTIVE"}
    ]
    
    # Generate 150 random noise staff members
    for i in range(200, 350):
        status = random.choice(["ACTIVE", "INACTIVE", "RETIRED", "SUSPENDED"])
        bg = random.choice(["CLEARED", "PENDING", "FAILED"])
        # Deliberately ensure none of the randoms are BOTH Cleared and Active to keep the math predictable for the evaluator
        if status == "ACTIVE" and bg == "CLEARED":
            status = "PENDING"
        decoy_staff.append({
            "Staff_ID": f"STF-{i}",
            "Name": f"Temp_Staff_{i}",
            "Background_Check": bg,
            "Status": status
        })

    hr_registry.extend(approved_staff)
    hr_registry.extend(decoy_staff)
    random.shuffle(hr_registry)

    with open("hospital_data/hr/hr_master_registry.json", "w", encoding="utf-8") as f:
        json.dump(hr_registry, f, indent=4)

    # 2. Generate Timecards (Scale Simulation: 365 daily files)
    start_date = datetime(2023, 1, 1)
    all_staff_ids = [s["Staff_ID"] for s in hr_registry]
    
    for i in range(365):
        current_date = start_date + timedelta(days=i)
        file_path = f"hospital_data/timecards/shift_{current_date.strftime('%Y%m%d')}.csv"
        
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Staff_ID", "Hours_Worked", "Department", "Notes"])
            
            # Each day has 5 to 15 shift records
            num_shifts = random.randint(5, 15)
            for _ in range(num_shifts):
                staff_id = random.choice(all_staff_ids)
                hours = random.randint(1, 12)
                dept = random.choice(["ER", "Pediatrics", "Surgery", "Triage"])
                writer.writerow([current_date.strftime('%Y-%m-%d'), staff_id, hours, dept, "Standard shift"])

    # 3. Generate Patient Database (Noise + Target)
    patients = []
    # Generate 500 fake patients
    for i in range(1000, 1500):
        patients.append([f"PT-{i}", f"Patient_{i}", random.choice(["Flu", "Broken Arm", "Checkup"]), f"555-01{random.randint(10,99)}"])
    
    # Inject the Luthier target
    patients.append(["PT-8892-LUTH", "Kareem Al-Oud", "Carpal Tunnel - Hand Surgery", "+1-800-555-9999"])
    random.shuffle(patients)

    with open("hospital_data/patients/patient_db.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Patient_ID", "Name", "Condition", "Phone_Number"])
        writer.writerows(patients)

    # 4. Generate Email Backups (Fragmentation + Decoys)
    # Generate 150 noise emails
    for i in range(1, 151):
        with open(f"hospital_data/email_backups/email_{i:03d}.txt", "w", encoding="utf-8") as f:
            f.write(f"Subject: Routine Update {i}\nFrom: admin@hospital.org\nTo: dr.tariq@hospital.org\n\nJust a standard automated system ping. ID: {random.randint(1000,9999)}")
            
    # Decoy Email (Mentions Oud, but useless)
    with open("hospital_data/email_backups/email_042_decoy.txt", "w", encoding="utf-8") as f:
        f.write(
            "Subject: Your package arrived\n"
            "From: Nurse Sarah\n"
            "To: Dr. Tariq\n\n"
            "Hey Tariq, just letting you know that the replacement strings for your personal Oud arrived at the front desk. "
            "I put them in your locker. Try not to play it during shift hours!\n- Sarah"
        )

    # Target Email (Contains the multi-hop clue)
    with open("hospital_data/email_backups/email_113_important.txt", "w", encoding="utf-8") as f:
        f.write(
            "Subject: Re: Custom Oud maker referral\n"
            "From: Nurse Sarah\n"
            "To: Dr. Tariq\n\n"
            "Hi Tariq,\n"
            "I finally managed to register the Egyptian luthier who makes those custom Ouds into our system for his hand surgery. "
            "His official Patient ID is PT-8892-LUTH.\n"
            "You can look him up in the master patient database CSV to get his direct phone number so you can call him.\n"
            "Talk soon!\n- Sarah"
        )

if __name__ == "__main__":
    build_env()
