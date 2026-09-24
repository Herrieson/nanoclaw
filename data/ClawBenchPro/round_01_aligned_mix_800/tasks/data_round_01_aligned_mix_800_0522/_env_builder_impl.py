import os
import json
import random
import string

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_letters, k=length))

def build_env():
    random.seed(42) # Ensure deterministic generation

    # 1. Build the Fragmented HR Database
    hr_base_dir = "HR_database"
    os.makedirs(hr_base_dir, exist_ok=True)
    
    departments = ["HR-Core", "IT-Support", "Exec-Admin", "Finance", "Operations", "Legal", "Sanitation"]
    statuses = ["Active", "Terminated", "Inactive", "On-Leave"]

    all_employees = {}
    active_employees = []
    inactive_employees = []

    # Generate 2000 employees spread across 50 folders and 200 files
    emp_counter = 1000
    for dept_idx in range(50):
        dept_path = os.path.join(hr_base_dir, f"dept_archive_{dept_idx}")
        os.makedirs(dept_path, exist_ok=True)
        
        for file_idx in range(4): # 4 files per dept
            file_path = os.path.join(dept_path, f"records_{file_idx}.json")
            chunk = []
            for _ in range(10): # 10 employees per file
                emp_id = f"PA-{emp_counter}"
                status = random.choice(["Active", "Active", "Terminated", "Inactive"]) # 50% active
                emp_data = {
                    "emp_id": emp_id,
                    "name": f"{generate_random_string(5).capitalize()} {generate_random_string(6).capitalize()}",
                    "department": random.choice(departments),
                    "status": status,
                    "hire_date": f"20{random.randint(10,23)}-0{random.randint(1,9)}-15"
                }
                chunk.append(emp_data)
                all_employees[emp_id] = emp_data
                
                if status == "Active":
                    active_employees.append(emp_id)
                else:
                    inactive_employees.append(emp_id)
                
                emp_counter += 1
            
            with open(file_path, "w") as f:
                # Wrap in some random noise keys to prevent simple flattening
                json.dump({"metadata": {"version": "1.x", "archived": True}, "data": {"employees": chunk}}, f, indent=2)

    # 2. Build the Messy Events Logs
    events_base_dir = "events_raw"
    os.makedirs(events_base_dir, exist_ok=True)
    
    event_codes_noise = ["EVENT_CODE: FIRE-DRILL-22", "EVENT_CODE: XMAS-2021", "EVENT_CODE: HR-MEET", "EVENT_CODE: NO-CODE"]
    target_code = "EVENT_CODE: HCBL-2023"

    # We will generate 300 random log files. Only 15 will be our target event.
    target_files_count = 15
    total_files = 300
    target_indices = set(random.sample(range(total_files), target_files_count))

    # Pick attendees
    # 60 valid attendees
    valid_attendees = random.sample(active_employees, 60)
    # 15 invalid (terminated)
    terminated_attendees = random.sample(inactive_employees, 15)
    # 15 complete fakes (not in DB)
    fake_attendees = [f"PA-{random.randint(9000, 9999)}" for _ in range(15)]

    all_attendees = valid_attendees + terminated_attendees + fake_attendees
    random.shuffle(all_attendees)
    
    # Split attendees into chunks for the 15 target files
    def chunk_list(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]
            
    attendee_chunks = list(chunk_list(all_attendees, len(all_attendees)//target_files_count + 1))

    chunk_idx = 0
    for i in range(total_files):
        # Deeply nested random folders
        folder_path = os.path.join(events_base_dir, f"year_20{random.randint(18,23)}", f"month_{random.randint(1,12)}", f"loc_{random.randint(1,5)}")
        os.makedirs(folder_path, exist_ok=True)
        
        file_name = f"log_dump_{generate_random_string(4)}.txt"
        file_path = os.path.join(folder_path, file_name)
        
        with open(file_path, "w") as f:
            if i in target_indices:
                f.write(f"{target_code}\n")
                f.write("System generated log - Temp Worker Entry\n")
                f.write("----------------------------------------\n")
                # Write attendees
                if chunk_idx < len(attendee_chunks):
                    for att_id in attendee_chunks[chunk_idx]:
                        # Make up a name used at the door
                        if att_id in all_employees:
                            used_name = all_employees[att_id]["name"].split()[0] + ("_Bro" if random.random()>0.8 else "")
                        else:
                            used_name = "Gatecrasher_" + generate_random_string(3)
                        
                        # Pad with random text to simulate messy logs
                        f.write(f"Some random system output... Memory block {random.randint(100,999)}\n")
                        f.write(f"[SIGN_IN] ID: {att_id} | Name_Used: {used_name}\n")
                    chunk_idx += 1
            else:
                f.write(f"{random.choice(event_codes_noise)}\n")
                f.write("Boring irrelevant logs...\n")
                for _ in range(random.randint(2, 5)):
                    f.write(f"[SIGN_IN] ID: PA-{random.randint(1000,9999)} | Name_Used: {generate_random_string(6)}\n")

if __name__ == "__main__":
    build_env()
