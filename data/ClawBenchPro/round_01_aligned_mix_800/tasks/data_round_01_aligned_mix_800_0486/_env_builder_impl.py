import os
import json
import csv
import random
import uuid

def build_env():
    random.seed(1213)
    
    # 1. Base Directories
    base_dirs = [
        "district_system/volunteer_portal/signups",
        "district_system/security_audits",
        "district_system/student_profiles",
        "district_system/medical_evaluations",
        "district_system/policies/accessibility"
    ]
    for d in base_dirs:
        os.makedirs(d, exist_ok=True)
        
    # --- VOLUNTEER DATA GENERATION ---
    volunteers = []
    # Generate 300 total volunteers (mix of valid/invalid year/event)
    for i in range(300):
        vol_id = f"V-{random.randint(10000, 99999)}"
        name = f"Parent_{uuid.uuid4().hex[:6].upper()}"
        year = random.choice([2021, 2022, 2023, 2024, 2024]) # Bias towards 2024
        event = random.choice(["Spring_Showcase", "Winter_Play", "Bake_Sale", "Spring_Showcase"])
        volunteers.append({"vol_id": vol_id, "name": name, "year": year, "event": event})
        
    # Scatter signups in subdirectories
    zones = ["zone_north", "zone_south", "zone_east", "zone_west", "legacy_archive"]
    months = [f"month_{str(m).zfill(2)}" for m in range(1, 13)]
    
    for i, vol in enumerate(volunteers):
        z = random.choice(zones)
        m = random.choice(months)
        target_dir = f"district_system/volunteer_portal/signups/{z}/{m}"
        os.makedirs(target_dir, exist_ok=True)
        
        file_format = random.choice(["json", "csv"])
        filename = f"batch_{uuid.uuid4().hex[:8]}.{file_format}"
        filepath = os.path.join(target_dir, filename)
        
        if file_format == "json":
            data = {"vol_id": vol["vol_id"], "full_name": vol["name"], "signup_year": vol["year"], "target_event": vol["event"]}
            with open(filepath, 'w') as f:
                json.dump(data, f)
        else:
            file_exists = os.path.exists(filepath)
            with open(filepath, 'a', newline='') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["id", "name", "year", "event"])
                writer.writerow([vol["vol_id"], vol["name"], vol["year"], vol["event"]])

    # Generate Security Logs
    valid_target_volunteers = [v for v in volunteers if v["year"] == 2024 and v["event"] == "Spring_Showcase"]
    cleared_vol_ids = set()
    
    # Randomly select some target volunteers to be cleared, others uncleared
    for v in valid_target_volunteers:
        if random.random() > 0.4: # 60% chance to be cleared
            cleared_vol_ids.add(v["vol_id"])
            
    with open("district_system/security_audits/sys_audit_01.log", "w") as f1, \
         open("district_system/security_audits/sys_audit_02.log", "w") as f2:
        
        for i in range(1000): # Noise logs
            f1.write(f"[202{random.randint(0,4)}-{random.randint(1,12):02d}-01] INFO - SYSTEM - CPU Load {random.randint(10,90)}%\n")
            f2.write(f"[202{random.randint(0,4)}-{random.randint(1,12):02d}-15] WARN - MEMORY - Garbage collection run\n")
            
        for vol in volunteers:
            target_f = f1 if random.random() > 0.5 else f2
            if vol["vol_id"] in cleared_vol_ids:
                # Give them a valid clearance
                valid_year = random.choice([2024, 2025, 2026])
                target_f.write(f"[2023-11-05] INFO - SEC_CHECK - VERIFICATION ID: {vol['vol_id']} - STATUS: CLEARED - VALID_UNTIL: {valid_year}-12-31\n")
            else:
                # Give them an expired clearance, or rejected, or pending
                state = random.choice(["EXPIRED", "REJECTED", "PENDING"])
                if state == "EXPIRED":
                    target_f.write(f"[2021-01-05] INFO - SEC_CHECK - VERIFICATION ID: {vol['vol_id']} - STATUS: CLEARED - VALID_UNTIL: 2023-01-01\n")
                else:
                    target_f.write(f"[2024-01-05] INFO - SEC_CHECK - VERIFICATION ID: {vol['vol_id']} - STATUS: {state} - VALID_UNTIL: N/A\n")
            
            # More noise
            target_f.write(f"[2024-02-14] DEBUG - APP - Checked profile {uuid.uuid4().hex}\n")

    # --- STUDENT DATA GENERATION ---
    instruments = {
        "LEVEL_1": ["INST-101", "INST-102", "INST-103"], # Tambourine, Triangle, Castanets
        "LEVEL_2": ["INST-201", "INST-202", "INST-203"], # Keyboard, Xylophone, Autoharp
        "LEVEL_3": ["INST-301", "INST-302", "INST-303"]  # Drums, Guitar, Flute
    }
    
    # Write Policies
    for lvl, codes in instruments.items():
        with open(f"district_system/policies/accessibility/{lvl}_policy.json", "w") as f:
            json.dump({"motor_level": lvl, "allowed_instruments": codes, "desc": "Official Policy"}, f)
            
    # Write noisy policy
    with open("district_system/policies/accessibility/LEVEL_X_draft.yaml", "w") as f:
        f.write("level: LEVEL_X\nallowed_instruments: [INST-999]\nstatus: DRAFT")

    students = []
    for i in range(200):
        stu_id = f"S-{random.randint(1000, 9999)}"
        name = f"Student_{uuid.uuid4().hex[:5].capitalize()}"
        status = random.choice(["active", "active", "graduated", "transferred"])
        
        motor_lvl = random.choice(list(instruments.keys()))
        has_request = random.random() > 0.3
        
        if has_request:
            if random.random() > 0.5:
                # Valid request
                requested_inst = random.choice(instruments[motor_lvl])
            else:
                # Invalid request (needs consultation)
                wrong_lvls = [l for l in instruments.keys() if l != motor_lvl]
                requested_inst = random.choice(instruments[random.choice(wrong_lvls)])
        else:
            requested_inst = None
            
        students.append({
            "stu_id": stu_id, "name": name, "status": status, 
            "motor_lvl": motor_lvl, "requested_inst": requested_inst
        })

    # Generate Student Profiles
    for stu in students:
        profile = {
            "student_id": stu["stu_id"],
            "name": stu["name"],
            "status": stu["status"],
            "metadata": {"enrolled_year": 2020}
        }
        if stu["requested_inst"]:
            profile["showcase_request"] = {"instrument_code": stu["requested_inst"]}
            
        # Add noise files
        if random.random() > 0.8:
            with open(f"district_system/student_profiles/{stu['stu_id']}_backup.bak", "w") as f:
                f.write("JUNK DATA")
                
        with open(f"district_system/student_profiles/{stu['stu_id']}_profile.json", "w") as f:
            json.dump(profile, f)

    # Generate Medical Evaluations
    eval_folders = ["clinic_A", "clinic_B", "archived_evals"]
    for folder in eval_folders:
        os.makedirs(f"district_system/medical_evaluations/{folder}", exist_ok=True)
        
    for stu in students:
        target_folder = random.choice(eval_folders)
        content = f"""MEDICAL EVALUATION RECORD
Date: 2023-08-15
Patient_ID: {stu['stu_id']}
Attending: Dr. Smith
---------------------------
Clearance: YES
Motor_Skill_Level: {stu['motor_lvl']}
Notes: Patient shows excellent progress.
"""
        with open(f"district_system/medical_evaluations/{target_folder}/eval_{stu['stu_id']}.txt", "w") as f:
            f.write(content)

if __name__ == "__main__":
    build_env()
