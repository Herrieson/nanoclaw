import os
import json
import random
from datetime import datetime, timedelta

def build_env():
    random.seed(42) # Ensure reproducibility

    # Create directory structures
    directories = [
        "audit_reports",
        "case_files/auth_policies",
        "hr_records/employees",
    ]
    for d in directories:
        os.makedirs(d, exist_ok=True)

    # 1. Generate HR Employee Records
    # Create 100 employees
    employees = {}
    first_names = ["John", "Jane", "Alice", "Bob", "Charlie", "Siobhan", "Liam", "Aisling", "Emma", "Noah", "Olivia", "William", "Sophia", "James"]
    last_names = ["Smith", "Doe", "Brown", "O'Sullivan", "Murphy", "Quinn", "Jones", "Taylor", "Williams", "Evans", "Davies"]
    
    for i in range(1, 101):
        emp_id = f"EMP_{i:03d}"
        full_name = f"{random.choice(first_names)} {random.choice(last_names)}_{i}"
        employees[emp_id] = full_name
        
        # Save each to a separate JSON file
        with open(f"hr_records/employees/{emp_id}.json", "w", encoding="utf-8") as f:
            json.dump({
                "employee_id": emp_id,
                "full_name": full_name,
                "department": random.choice(["Litigation", "Corporate", "IT", "HR", "Interns"]),
                "hired_date": "2023-01-15"
            }, f)

    # 2. Generate Auth Policies (Noise & True version)
    # True authorized staff for 2024-CV-882: EMP_012, EMP_034, EMP_077
    true_auth_staff = ["EMP_012", "EMP_034", "EMP_077"]
    
    policies = [
        # Noise 1: Wrong case
        {"case_id": "2024-CV-111", "approved": True, "authorized_emp_ids": ["EMP_001", "EMP_002"]},
        # Noise 2: Not approved
        {"case_id": "2024-CV-882", "approved": False, "authorized_emp_ids": ["EMP_012", "EMP_034", "EMP_099", "EMP_100"]},
        # Noise 3: Old draft
        {"case_id": "2024-CV-882", "approved": "pending", "authorized_emp_ids": ["EMP_012"]},
        # The truth
        {"case_id": "2024-CV-882", "approved": True, "authorized_emp_ids": true_auth_staff, "note": "Final signed by partners."}
    ]
    
    for idx, pol in enumerate(policies):
        # Mix formats (some json, some yaml-like json)
        with open(f"case_files/auth_policies/policy_doc_v{idx}.json", "w", encoding="utf-8") as f:
            json.dump(pol, f, indent=4)
            
    with open("case_files/auth_policies/readme.txt", "w") as f:
        f.write("Do not use unapproved drafts!")

    # 3. Generate Fragmented Server Logs
    start_date = datetime(2024, 5, 1)
    
    # We want to track exact values for our validation
    # total_billable_minutes = 0
    # unauthorized_users = set()
    
    for day in range(30):
        current_date = start_date + timedelta(days=day)
        date_path = current_date.strftime("%Y/%m/%d")
        log_dir = os.path.join("server_logs", date_path)
        os.makedirs(log_dir, exist_ok=True)
        
        # Multiple log files per day
        for log_idx in range(3):
            log_file_path = os.path.join(log_dir, f"access_{log_idx}.log")
            
            with open(log_file_path, "w", encoding="utf-8") as f:
                # 50-100 lines per file
                num_lines = random.randint(50, 100)
                for _ in range(num_lines):
                    is_target_case = random.random() < 0.15
                    case_id = "2024-CV-882" if is_target_case else f"2024-CV-{random.randint(100, 999)}"
                    emp_id = f"EMP_{random.randint(1, 100):03d}"
                    status = random.choice(["SUCCESS", "SUCCESS", "FAILED", "TIMEOUT", "DENIED"])
                    duration = random.randint(5, 120)
                    timestamp = current_date.strftime("%Y-%m-%dT%H:%M:%S")
                    
                    # Add some garbage noise lines occasionally
                    if random.random() < 0.05:
                        f.write(f"[{timestamp}] SYNC ERROR: Memory leak detected at 0x00F8\n")
                        continue
                        
                    # Format: [TIMESTAMP] IP_ADDR | ACTION: Read | CASE: <case_id> | USER: <emp_id> | DURATION: <mins>m | STATUS: <status>
                    log_line = f"[{timestamp}] 192.168.1.{random.randint(1,255)} | ACTION: View | CASE: {case_id} | USER: {emp_id} | DURATION: {duration}m | STATUS: {status}\n"
                    f.write(log_line)

if __name__ == "__main__":
    build_env()
