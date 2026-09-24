import os
import json
import csv
import random

def build_env():
    # Deterministic seed for guaranteed reproducibility
    random.seed(1208) 
    
    # 1. Multi-hop Logic: Corporate Memos (Noise + Decoys + Truth)
    os.makedirs("corporate_memos", exist_ok=True)
    
    # Decoy 1: Q3 Draft
    with open("corporate_memos/policy_Q3_draft.txt", "w") as f:
        f.write("DRAFT v0.1\nNon-deductible categories will probably be: Entertainment, Travel")
        
    # Decoy 2: Q2 Approved
    with open("corporate_memos/policy_Q2_final.json", "w") as f:
        json.dump({
            "quarter": "Q2", 
            "status": "approved", 
            "non_deductible_categories": ["Entertainment"]
        }, f, indent=4)
        
    # Truth: Q3 Approved
    q3_nd_categories = ["Entertainment", "Personal_Gadget", "Luxury_Dining"]
    with open("corporate_memos/policy_Q3_approved_final.json", "w") as f:
        json.dump({
            "quarter": "Q3", 
            "status": "approved", 
            "non_deductible_categories": q3_nd_categories
        }, f, indent=4)
        
    # 2. Fragmentation & Scale: Massive nested receipts archive
    base_dir = "receipts_archive"
    depts = ["Sales", "Engineering", "Marketing"]
    months = ["07", "08", "09"]
    
    employees = [f"EMP-{str(i).zfill(3)}" for i in range(1, 101)]
    deductible_categories = ["Office_Supplies", "Software_License", "Travel", "Consulting", "Server_Costs"]
    
    total_deductible_cents = 0
    total_nd_cents = 0
    nd_counts = {emp: 0 for emp in employees}
    
    for dept in depts:
        for month in months:
            dir_path = os.path.join(base_dir, dept, month)
            os.makedirs(dir_path, exist_ok=True)
            
            # Generate multiple files per directory
            for f_idx in range(random.randint(4, 8)):
                file_type = random.choice(["csv", "json", "log"])
                file_name = f"tx_batch_{f_idx}.{file_type}"
                
                records = []
                for _ in range(random.randint(15, 40)):
                    emp = random.choice(employees)
                    is_nd = random.random() < 0.25
                    cat = random.choice(q3_nd_categories) if is_nd else random.choice(deductible_categories)
                    
                    # Use integer cents to avoid floating point precision issues during sum
                    amt_cents = random.randint(1000, 99999) 
                    amt_str = f"{amt_cents / 100:.2f}"
                    
                    # Decoy noise: void/cancelled transactions
                    status = random.choice(["valid", "valid", "valid", "void", "cancelled"])
                    
                    records.append({
                        "emp": emp, 
                        "cat": cat, 
                        "amt": amt_str, 
                        "status": status,
                        "cents": amt_cents
                    })
                    
                    if status == "valid":
                        if cat in q3_nd_categories:
                            total_nd_cents += amt_cents
                            nd_counts[emp] += 1
                        else:
                            total_deductible_cents += amt_cents
                            
                # Write files in varying formats to test parsing robustness
                if file_type == "csv":
                    with open(os.path.join(dir_path, file_name), "w", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(["EmployeeID", "Category", "Amount", "TxStatus"])
                        for r in records:
                            writer.writerow([r["emp"], r["cat"], r["amt"], r["status"]])
                elif file_type == "json":
                    j_records = [{
                        "employee_ref": r["emp"], 
                        "expense_type": r["cat"], 
                        "cost": float(r["amt"]), 
                        "state": r["status"]
                    } for r in records]
                    with open(os.path.join(dir_path, file_name), "w") as f:
                        json.dump(j_records, f, indent=2)
                elif file_type == "log":
                    with open(os.path.join(dir_path, file_name), "w") as f:
                        for r in records:
                            f.write(f"RECORD|{r['emp']}|{r['cat']}|{r['amt']}|{r['status']}\n")
                
                # Introduce heavy noise: Corrupted .bak files that duplicate data but shouldn't be parsed
                if random.random() < 0.35:
                    with open(os.path.join(dir_path, file_name + ".bak"), "w") as f:
                        f.write("CORRUPTED BACKUP BLOCK\n")
                        f.write("RECORD|EMP-999|Entertainment|9999.00|valid\n")
                        f.write("DO NOT PARSE")

    # 3. Store the exact mathematical ground truth for evaluation framework
    offenders = sorted([emp for emp, count in nd_counts.items() if count > 2])
    truth = {
        "total_deductible": total_deductible_cents / 100,
        "total_non_deductible": total_nd_cents / 100,
        "offenders": offenders
    }
    
    with open(".secret_eval_truth.json", "w") as f:
        json.dump(truth, f, indent=4)

if __name__ == "__main__":
    build_env()
