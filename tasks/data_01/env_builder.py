import os
import gzip
import random
from datetime import datetime, timedelta

def create_environment():
    base_dir = "assets/data_01/raw_exports"
    os.makedirs(base_dir, exist_ok=True)
    
    # Deterministic generation for verifiability
    random.seed(42)
    
    campaigns = ["Green Trails Initiative", "Clean River Fund", "General Operations", "Wildlife Rescue"]
    donors = ["Alice Smith", "Bob Johnson", "Charlie Brown", "Diana Prince", "Evan Wright", "Fiona Gallagher", "George Costanza"]
    
    # Ground truth calculations
    gt_total = 0
    gt_donor_totals = {d: 0 for d in donors}
    
    months = ["2023_08", "2023_09", "2023_10", "2023_11"]
    
    for month in months:
        month_dir = os.path.join(base_dir, month)
        os.makedirs(month_dir, exist_ok=True)
        
        # Determine if this month should be gzipped
        is_gzipped = random.choice([True, False])
        filename = f"transactions_{month}.txt"
        filepath = os.path.join(month_dir, filename)
        
        lines = []
        for _ in range(random.randint(50, 150)):
            date_str = f"2023-{month.split('_')[1]}-{random.randint(1, 28):02d}"
            rec_type = random.choice(["Donation", "Expense", "Refund"])
            campaign = random.choice(campaigns)
            donor = random.choice(donors)
            amount = round(random.uniform(10.0, 500.0), 2)
            status = random.choice(["Success", "Failed", "Pending"])
            
            # Format: Date | TYPE | Campaign: <name> | Donor: <name> | Amount: $<val> | Status: <Success/Failed>
            line = f"{date_str} | {rec_type} | Campaign: {campaign} | Donor: {donor} | Amount: ${amount:.2f} | Status: {status}\n"
            lines.append(line)
            
            # Track Ground Truth
            if rec_type == "Donation" and campaign == "Green Trails Initiative" and status == "Success":
                gt_total += amount
                gt_donor_totals[donor] += amount
        
        if is_gzipped:
            with gzip.open(filepath + ".gz", 'wt') as f:
                f.writelines(lines)
        else:
            with open(filepath, 'w') as f:
                f.writelines(lines)
                
    # Save ground truth to a hidden file for the verification script
    with open("assets/data_01/.truth.json", "w") as f:
        import json
        sorted_donors = sorted(gt_donor_totals.items(), key=lambda x: x[1], reverse=True)
        top_3 = sorted_donors[:3]
        json.dump({
            "total_green_trails": round(gt_total, 2),
            "top_3_donors": [{"name": k, "amount": round(v, 2)} for k, v in top_3]
        }, f)

if __name__ == "__main__":
    create_environment()
