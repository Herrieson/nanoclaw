import os
import json
import random
import datetime
import uuid
import string

def build_env():
    # 1. Create directory structure
    os.makedirs("config", exist_ok=True)
    terminals = ["T01", "T02", "T03", "T04", "T05"]
    for t in terminals:
        os.makedirs(f"kiosk_data/terminals/{t}", exist_ok=True)
        
    # 2. Generate Config files
    # dept mapping
    with open("config/dept_mapping.csv", "w", encoding="utf-8") as f:
        f.write("Department_Name,Dept_Code,Status\n")
        f.write("HR Programs,HRP-802,Active\n")
        f.write("HR Programs,HRP-000,Deprecated\n")
        f.write("DMV,DMV-101,Active\n")
        f.write("Parks,PRK-202,Active\n")
        f.write("Sanitation,SAN-303,Active\n")

    # terminal status
    with open("config/terminal_status.json", "w", encoding="utf-8") as f:
        json.dump({
            "T01": {"status": "ACTIVE", "ip": "192.168.1.10"},
            "T02": {"status": "ACTIVE", "ip": "192.168.1.11"},
            "T03": {"status": "ACTIVE", "ip": "192.168.1.12"},
            "T04": {"status": "MAINTENANCE", "ip": "192.168.1.13", "error": "Liquid Damage"},
            "T05": {"status": "ACTIVE", "ip": "192.168.1.14"}
        }, f, indent=4)
        
    # escalation keywords
    keywords = ["health insurance", "medical coverage", "dental plan", "copay dispute", "benefits escalation"]
    with open("config/escalation_keywords.txt", "w", encoding="utf-8") as f:
        f.write("# Memorandum: Watch out for these terms\n")
        for k in keywords:
            f.write(f"{k}\n")
            
    # 3. Data Generation Generators
    random.seed(1156)
    base_date = datetime.datetime(2024, 11, 5, 8, 0, 0)
    
    first_names = ["John", "Jane", "Alice", "Bob", "Charlie", "Eve", "Gregory", "Sarah", "Tom", "Oliver", "Emma", "Liam", "Ava", "Noah"]
    last_names = ["Doe", "Smith", "Jones", "Brown", "Davis", "Evans", "House", "Connor", "Clark", "Miller", "Taylor", "Anderson"]
    
    normal_reasons_hr = ["Standard application follow-up.", "Final interview for the clerk position.", "General payroll inquiry.", "Updating direct deposit forms.", "Need new ID badge.", "Asking about leave of absence."]
    insurance_reasons = [
        "Confusing health insurance question.",
        "My medical coverage was denied!",
        "Need to add spouse to dental plan.",
        "Copay dispute for recent pharmacy visit.",
        "I need a benefits escalation immediately."
    ]
    other_reasons = ["Renew driver's license.", "Vehicle registration.", "Submitting a public park event permit.", "Garbage not picked up.", "Paying a parking ticket."]
    
    def random_time():
        delta_seconds = random.randint(0, 10 * 3600) # 8 AM to 6 PM
        return base_date + datetime.timedelta(seconds=delta_seconds)

    def format_time(dt):
        fmt = random.choice([
            lambda d: str(int(d.timestamp())), # Unix timestamp
            lambda d: d.isoformat() + "Z", # ISO
            lambda d: d.strftime("%m/%d/%Y %I:%M:%S %p"), # 12-hour US
            lambda d: d.strftime("%Y-%m-%d %H:%M:%S") # 24-hour Standard
        ])
        return fmt(dt)

    def generate_record(is_dirty=False):
        dt = random_time()
        time_str = format_time(dt)
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        
        if is_dirty:
            # Generate garbage for Maintenance terminal
            return {
                "t": time_str,
                "c": random.choice(["HRP-802", "DMV-101", "UNK-999", "ERR-000"]),
                "u": "".join(random.choices(string.ascii_letters, k=10)),
                "m": "TEST_DATA_NULL_POINTER_EXCEPTION"
            }
        
        # Decide if this is HR or not
        if random.random() < 0.4:
            dept_code = "HRP-802"
            if random.random() < 0.3:
                reason = random.choice(insurance_reasons)
            else:
                reason = random.choice(normal_reasons_hr)
        else:
            dept_code = random.choice(["DMV-101", "PRK-202", "SAN-303"])
            reason = random.choice(other_reasons)
            
        return {
            "t": time_str,
            "c": dept_code,
            "u": name,
            "m": reason
        }

    # 4. Write Data to terminals
    for t in terminals:
        num_files = random.randint(5, 10)
        is_maintenance = (t == "T04")
        
        for i in range(num_files):
            file_type = random.choice([".txt", ".json"])
            num_records = random.randint(15, 30)
            records = [generate_record(is_dirty=is_maintenance) for _ in range(num_records)]
            
            file_path = f"kiosk_data/terminals/{t}/chunk_{i:03d}{file_type}"
            
            if file_type == ".json":
                # Write as JSON array
                json_records = []
                for r in records:
                    json_records.append({
                        "timestamp": r["t"],
                        "dept_code": r["c"],
                        "visitor_name": r["u"],
                        "inquiry_text": r["m"]
                    })
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(json_records, f, indent=2)
            else:
                # Write as custom text format
                with open(file_path, "w", encoding="utf-8") as f:
                    for r in records:
                        f.write(f"[{r['t']}] ID:{uuid.uuid4().hex[:8]} | CODE:{r['c']} | USR:{r['u']} | MSG:{r['m']}\n")

if __name__ == "__main__":
    build_env()
