import os
import json
import csv
import random

def build_env():
    # Set seed for deterministic generation
    random.seed(1256)
    
    base_dir = "school_system_dump"
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Create Policies and Pricing
    os.makedirs(os.path.join(base_dir, "policies"), exist_ok=True)
    pricing = {
        "Standard": 500,
        "Silver": 650,
        "Gold": 800,
        "Platinum": 1000
    }
    with open(os.path.join(base_dir, "policies", "pricing.json"), "w") as f:
        json.dump(pricing, f, indent=4)
        
    with open(os.path.join(base_dir, "policies", "insurance_policy.txt"), "w") as f:
        f.write("CONFIDENTIAL POLICY\n\nAll Premium insurance plans require a mandatory 10% surcharge on the base package price to fund the Emergency Pool. Basic plans have 0% surcharge.\n")

    # 2. Generate Rosters (Noise and Valid)
    os.makedirs(os.path.join(base_dir, "rosters"), exist_ok=True)
    
    valid_roster_ids = set()
    
    def generate_students(prefix, count):
        return [{"id": f"{prefix}_{str(i).zfill(4)}", "name": f"Student_{prefix}_{i}"} for i in range(1, count + 1)]

    # Pool of students
    students_8_curr = generate_students("S8_23", 400) # Valid 8th graders
    students_8_old = generate_students("S8_22", 200)  # Old 8th graders (noise)
    students_7_curr = generate_students("S7_23", 300) # 7th graders (noise)
    
    # Distribute into JSON files
    def write_roster_file(folder_name, file_name, academic_year, grade, student_list):
        folder_path = os.path.join(base_dir, "rosters", folder_name)
        os.makedirs(folder_path, exist_ok=True)
        data = {
            "metadata": {
                "academic_year": academic_year,
                "grade": grade,
                "homeroom_teacher": f"Teacher_{random.randint(1,50)}"
            },
            "students": student_list
        }
        with open(os.path.join(folder_path, file_name), "w") as f:
            json.dump(data, f, indent=2)

    # Valid Rosters: 2023-2024, Grade 8
    random.shuffle(students_8_curr)
    for i in range(10):
        chunk = students_8_curr[i*40 : (i+1)*40]
        write_roster_file(f"building_A/floor_{random.randint(1,3)}", f"homeroom_8_{i}.json", "2023-2024", 8, chunk)
        for s in chunk:
            valid_roster_ids.add(s["id"])

    # Noise Rosters: 2022-2023, Grade 8
    for i in range(5):
        chunk = students_8_old[i*40 : (i+1)*40]
        write_roster_file("building_A/archives", f"homeroom_8_old_{i}.json", "2022-2023", 8, chunk)

    # Noise Rosters: 2023-2024, Grade 7
    for i in range(8):
        chunk = students_7_curr[i*37 : (i+1)*37]
        write_roster_file(f"building_B/floor_{random.randint(1,2)}", f"homeroom_7_{i}.json", "2023-2024", 7, chunk)

    # 3. Generate Submissions (CSVs)
    os.makedirs(os.path.join(base_dir, "submissions"), exist_ok=True)
    
    submissions_data = []
    
    # Trackers for testing validity
    expected_interlopers = set()
    expected_valid_confirmed = 0
    expected_emergency_fund = 0.0
    
    # We will pick a subset of students to have submitted forms.
    # 1. Valid students submitting valid forms
    for s in random.sample(students_8_curr, 250):
        status = random.choice(["Paid", "Paid", "Paid", "Pending", "Cancelled"])
        package = random.choice(list(pricing.keys()))
        ins_type = random.choice(["Basic", "Premium", "Premium"])
        event = "DC_8TH"
        submissions_data.append([s["id"], s["name"], event, status, package, ins_type])
        
        if status == "Paid":
            expected_valid_confirmed += 1
            if ins_type == "Premium":
                expected_emergency_fund += pricing[package] * 0.10

    # 2. Valid students submitting WRONG event form (Local Museum)
    for s in random.sample(students_8_curr, 50):
        submissions_data.append([s["id"], s["name"], "LOCAL_MUS", "Paid", "Standard", "Basic"])

    # 3. Interlopers (7th graders or old 8th graders) submitting DC_8TH forms
    interloper_pool = random.sample(students_7_curr, 40) + random.sample(students_8_old, 20)
    for s in interloper_pool:
        status = random.choice(["Paid", "Pending"])
        package = random.choice(list(pricing.keys()))
        ins_type = random.choice(["Basic", "Premium"])
        submissions_data.append([s["id"], s["name"], "DC_8TH", status, package, ins_type])
        expected_interlopers.add(s["name"])

    # Shuffle all submissions
    random.shuffle(submissions_data)
    
    # Write them into multiple CSVs scattered in time folders
    weeks = ["week_1_oct", "week_2_oct", "week_3_oct", "week_4_oct"]
    for w in weeks:
        os.makedirs(os.path.join(base_dir, "submissions", w), exist_ok=True)
        
    chunk_size = len(submissions_data) // 15
    for idx in range(15):
        chunk = submissions_data[idx*chunk_size : (idx+1)*chunk_size]
        folder = os.path.join(base_dir, "submissions", random.choice(weeks))
        
        # Sometime add corrupted fake files
        if random.random() < 0.3:
            with open(os.path.join(folder, f"batch_{idx}_draft.tmp"), "w") as f:
                f.write("CORRUPTED BYTES 0x00 0x01")
                
        with open(os.path.join(folder, f"batch_{idx}.csv"), "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Student_ID", "Full_Name", "Event_Code", "Payment_Status", "Package_Tier", "Insurance_Type"])
            writer.writerows(chunk)

    # For debugging/verification (Agents won't read this easily if they don't look at the source script)
    # print(f"Expected Interlopers: {len(expected_interlopers)}")
    # print(f"Expected Valid Confirmed: {expected_valid_confirmed}")
    # print(f"Expected Emergency Fund: {expected_emergency_fund}")

if __name__ == "__main__":
    build_env()
