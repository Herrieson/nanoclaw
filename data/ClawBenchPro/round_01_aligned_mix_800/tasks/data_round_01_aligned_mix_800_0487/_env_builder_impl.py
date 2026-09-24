import os
import json
import csv
import random
import uuid

def build_env():
    random.seed(42) # Ensure reproducibility but the logic is deterministic anyway
    
    # Create directory structure
    os.makedirs("governance/policies", exist_ok=True)
    os.makedirs("hr_data", exist_ok=True)
    for week in range(1, 5):
        os.makedirs(f"timesheets/week_{week}", exist_ok=True)
        
    # --- 1. Generate Policy Data (Noise & Real) ---
    with open("governance/policies/draft_v1_old.txt", "w", encoding="utf-8") as f:
        f.write("UNIVERSITY PROCEDURAL GUIDELINE - TIME ALLOCATION (DRAFT)\nAdmin cap proposed at 25%.")
        
    with open("governance/policies/draft_union_counter_proposal.md", "w", encoding="utf-8") as f:
        f.write("# Union Proposal\nWe demand the administrative cap be raised to 30% to account for email overload.")
        
    signed_decree = {
        "document_status": "OFFICIAL_SIGNED",
        "date": "2023-11-12",
        "department_caps": {
            "Liberal Arts": {"admin_cap_pct": 15}, # 15% is the magic number
            "Engineering": {"admin_cap_pct": 10},
            "Sciences": {"admin_cap_pct": 12}
        }
    }
    with open("governance/policies/signed_decree_nov12.json", "w", encoding="utf-8") as f:
        json.dump(signed_decree, f, indent=2)

    # --- 2. Generate HR Data ---
    departments = ["Liberal Arts", "Engineering", "Sciences", "Business"]
    first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]
    
    active_staff = []
    archived_staff = []
    
    # We will track the specific Liberal Arts employees to control their stats
    la_active_ids = []
    la_violators = []
    
    emp_counter = 10000
    for _ in range(150): # 150 Active employees
        emp_id = str(emp_counter)
        emp_counter += 1
        dept = random.choice(departments)
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        active_staff.append([emp_id, name, dept])
        
        if dept == "Liberal Arts":
            la_active_ids.append(emp_id)

    for _ in range(50): # 50 Archived/Terminated employees (Noise)
        emp_id = str(emp_counter)
        emp_counter += 1
        dept = random.choice(departments)
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        archived_staff.append([emp_id, name, dept, "Terminated"])

    with open("hr_data/active_personnel.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["EmpID", "FullName", "Department"])
        writer.writerows(active_staff)
        
    with open("hr_data/archived_personnel.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["EmpID", "FullName", "Department", "Status"])
        writer.writerows(archived_staff)

    # Select 5 LA employees to be clear violators
    random.shuffle(la_active_ids)
    la_violators = set(la_active_ids[:5])

    # --- 3. Generate Timesheets (Fragmentation & Scale) ---
    activities = ["Teaching", "Research", "Admin"]
    
    def generate_daily_logs(emp_id, is_violator):
        logs = []
        num_entries = random.randint(2, 4)
        for _ in range(num_entries):
            act = random.choice(activities)
            
            # Control the distribution for Liberal Arts
            if is_violator is True:
                # Force heavy Admin
                if random.random() < 0.6: act = "Admin"
                else: act = random.choice(["Teaching", "Research"])
            elif is_violator is False:
                # Force low Admin
                if random.random() < 0.9: act = random.choice(["Teaching", "Research"])
                else: act = "Admin"
            
            # Base minutes (30 to 180)
            mins = random.randint(1, 6) * 30 
            
            # Fragment the units randomly
            if random.choice([True, False]):
                logs.append({"activity": act, "duration_minutes": mins})
            else:
                logs.append({"activity": act, "duration_hours": mins / 60.0})
        return logs

    # Generate 20 days (4 weeks * 5 days) of logs for everyone
    for week in range(1, 5):
        for day in range(1, 6):
            # All active staff
            for emp in active_staff:
                emp_id = emp[0]
                dept = emp[2]
                
                is_vi = None
                if dept == "Liberal Arts":
                    is_vi = (emp_id in la_violators)
                    
                logs = generate_daily_logs(emp_id, is_vi)
                
                # Introduce some noise files that are just empty or invalid occasionally, but keep it mostly clean structure
                if random.random() < 0.01:
                    continue # Employee forgot to log this day
                
                file_name = f"ts_{emp_id}_{uuid.uuid4().hex[:8]}.json"
                file_path = os.path.join(f"timesheets/week_{week}", file_name)
                
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump({
                        "emp_id": emp_id,
                        "date": f"2023-10-{week*5+day:02d}",
                        "entries": logs
                    }, f)

            # Generate some logs for archived staff just to mess with them
            for emp in archived_staff:
                if random.random() < 0.2: # Occasionally they have legacy logs
                    emp_id = emp[0]
                    logs = generate_daily_logs(emp_id, None)
                    file_name = f"ts_{emp_id}_{uuid.uuid4().hex[:8]}.json"
                    file_path = os.path.join(f"timesheets/week_{week}", file_name)
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump({"emp_id": emp_id, "date": f"2023-09-{(week*5+day):02d}", "entries": logs}, f)

if __name__ == "__main__":
    build_env()
