import os
import json
import csv
import random

def build_env():
    # Fix seed for deterministic environment generation (ensuring absolute calculability)
    random.seed(1188)
    
    # 1. Base directories setup
    os.makedirs("desk_drawer_dump/system_backups", exist_ok=True)
    os.makedirs("accountant_ready", exist_ok=True)
    
    # 2. Deep fragmentation tree creation
    folders = ["receipts", "invoices", "misc_notes", "old_logs", "bank_exports"]
    quarters = ["Q1", "Q2", "Q3", "Q4"]
    sub_dirs = ["jan_feb", "mar_apr", "may_jun", "jul_aug", "sep_oct", "nov_dec"]
    
    all_target_dirs = []
    for f in folders:
        for q in quarters:
            for s in sub_dirs:
                path = f"desk_drawer_dump/{f}/{q}/{s}"
                os.makedirs(path, exist_ok=True)
                all_target_dirs.append(path)

    # 3. Generating the "Truth" Registry (The key to the whole puzzle)
    # 300 total jobs. Only the "Completed" ones are valid.
    jobs = []
    for i in range(1000, 1300):
        status = random.choice(["Completed", "Completed", "Cancelled", "Pending", "Cancelled"])
        jobs.append({"id": f"J-{i}", "status": status})
        
    registry_path = "desk_drawer_dump/system_backups/master_registry_2023.csv"
    with open(registry_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Internal_ID", "Job_ID", "Status", "Client_Name", "Last_Updated"])
        for idx, j in enumerate(jobs):
            writer.writerow([f"UID-{idx:04d}", j["id"], j["status"], f"Client_{random.randint(1,99)}", "2023-xx-xx"])

    # 4. Spreading the data (The fragmentation)
    # To avoid floating point precision issues in python causing evaluation failure, 
    # we strictly use INTEGERS for money in the environment generation.
    golden_revenue = 0
    golden_expenses = 0
    
    for j in jobs:
        # Generate clean integer amounts
        rev = random.randint(100, 2500)
        exp = random.randint(20, min(800, rev))
        
        if j["status"] == "Completed":
            golden_revenue += rev
            golden_expenses += exp
            
        fmt = random.choice(["txt", "json", "csv"])
        target_dir = random.choice(all_target_dirs)
        
        if fmt == "txt":
            # Unstructured text format needing Regex
            content = (
                f"Job Log Update\n"
                f"Job Ref: {j['id']}\n"
                f"It was a really tough job welding that chassis.\n"
                f"Amount Billed: ${rev}.00\n"
                f"Parts Cost: ${exp}.00\n"
                f"End of report.\n"
            )
            file_name = os.path.join(target_dir, f"scratchpad_{j['id']}_{random.randint(10,99)}.txt")
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(content)
                
        elif fmt == "json":
            # Semi-structured JSON format
            data = {
                "system_metadata": "exported_from_mobile",
                "jobRef": j["id"],
                "financials": {
                    "revenue": rev,
                    "expenses": exp
                },
                "mechanic_notes": "Forgot my wrench there."
            }
            file_name = os.path.join(target_dir, f"mob_export_{j['id']}.json")
            with open(file_name, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                
        elif fmt == "csv":
            # Transaction log format (Requires grouping logic)
            file_name = os.path.join(target_dir, f"transactions.csv")
            file_exists = os.path.exists(file_name)
            with open(file_name, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["Date", "RefID", "Category", "Amount"])
                writer.writerow([f"2023-10-{random.randint(1,28):02d}", j["id"], "Revenue", rev])
                writer.writerow([f"2023-10-{random.randint(1,28):02d}", j["id"], "Expense", exp])

    # 5. Injecting Massive Noise and Decoys
    # Generate 500 garbage files to confuse brute-force scripts and LLM's context window.
    for _ in range(500):
        target_dir = random.choice(all_target_dirs)
        noise_type = random.choice(["txt", "log", "json", "csv"])
        
        if noise_type == "txt":
            # Decoy: Personal expenses without Job ID
            cost = random.randint(10, 150)
            with open(os.path.join(target_dir, f"grocery_run_{random.randint(100,999)}.txt"), "w") as f:
                f.write(f"Went to the store. Bought some beers and dog food. Cost me ${cost}.00. Not a business expense!\n")
                
        elif noise_type == "log":
            # Pure garbage log files
            with open(os.path.join(target_dir, f"system_err_{random.randint(1000,9999)}.log"), "w") as f:
                f.write("ERROR 0x00000A: FAILED TO LOAD SECTOR\n" * random.randint(5, 15))
                
        elif noise_type == "json":
            # Decoy JSON missing critical keys
            data = {"note": "Remind me to call Sarah about her tractor.", "priority": "high", "cost_estimate": 500}
            with open(os.path.join(target_dir, f"reminder_{random.randint(10,99)}.json"), "w") as f:
                json.dump(data, f)
                
        elif noise_type == "csv":
            # Personal expenses mixed into CSVs
            file_name = os.path.join(target_dir, f"transactions.csv")
            file_exists = os.path.exists(file_name)
            with open(file_name, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["Date", "RefID", "Category", "Amount"])
                writer.writerow([f"2023-11-{random.randint(1,28):02d}", "PERSONAL_NO_ID", "Expense", random.randint(10, 50)])

    # We do NOT print the answer, but the Golden Answer internally is computable.
    # The logic is perfectly deterministic and 100% solvable through code.

if __name__ == "__main__":
    build_env()
