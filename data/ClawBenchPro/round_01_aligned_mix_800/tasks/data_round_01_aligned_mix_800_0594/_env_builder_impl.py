import os
import random
import json
import csv
import yaml

def build_env():
    # Set a fixed seed for deterministic generation
    random.seed(1652)

    # 1. calendar.yaml
    events = [
        {"name": "Wine Tasting", "date": "2023-10-01"},
        {"name": "Midnight Art", "date": "2023-10-14"},
        {"name": "Jazz Night", "date": "2023-10-20"},
        {"name": "Halloween Bash", "date": "2023-10-31"}
    ]
    with open("calendar.yaml", "w", encoding="utf-8") as f:
        yaml.dump({"events": events}, f)

    # 2. receipts/
    os.makedirs("receipts", exist_ok=True)
    dates = ["2023-10-01", "2023-10-14", "2023-10-20", "2023-10-31", "2023-09-15"]
    
    total_expenses_14 = 0
    for i in range(500):
        d = random.choice(dates)
        # Using integers to avoid floating point precision issues
        cost1 = random.randint(10, 500)
        cost2 = random.randint(10, 500)
        if d == "2023-10-14":
            total_expenses_14 += cost1 + cost2
        
        rcpt = {
            "receipt_id": f"R{i:04d}",
            "date": d,
            "items": [
                {"desc": f"Item_{random.randint(1,100)}", "cost": cost1},
                {"desc": f"Item_{random.randint(101,200)}", "cost": cost2}
            ]
        }
        with open(f"receipts/rcpt_{i:04d}.json", "w", encoding="utf-8") as f:
            json.dump(rcpt, f, indent=2)

    # 3. emails/
    os.makedirs("emails", exist_ok=True)
    vips = [
        "Julian Vance", "Sophia Sterling", "Marcus Reed", "Isabella Torres", 
        "Mr. Anderson", "Lucia Gomez", "Carlos Sainz", "Lando Norris", 
        "Charles Leclerc", "Max Verstappen"
    ]
    
    for i in range(120):
        if i == 73:
            content = "Subject: CONFIRMED VIPs\n\nHey Mateo,\n\nHere is the final list for the Midnight Art event:\n" + "\n".join(vips) + "\n\nDon't lose this again.\n"
        else:
            subjects = ['Catering bill', 'DJ playlist', 'Lighting setup', 'Guest complaints', 'Shift swap']
            content = f"Subject: Re: {random.choice(subjects)}\n\nJust some random noise and everyday chatter."
        with open(f"emails/email_{i:03d}.txt", "w", encoding="utf-8") as f:
            f.write(content)

    # 4. tips_logs/
    os.makedirs("tips_logs", exist_ok=True)
    statuses = ["CLEARED", "FAILED", "PENDING"]
    
    transactions = []
    
    # Predefined VIP amounts to ensure exact logic hits
    vip_amounts = {
        "Julian Vance": (" $1200 ", "CLEARED"),       # VIP, > 500, Cleared (Valid)
        "Sophia Sterling": ("USD 600", "CLEARED"),    # VIP, > 500, Cleared (Valid)
        "Marcus Reed": (" $400 ", "CLEARED"),         # VIP, <= 500, Cleared
        "Isabella Torres": ("700", "PENDING"),        # VIP, > 500, Pending
        "Mr. Anderson": (" $800 ", "CLEARED"),        # VIP, > 500, Cleared (Valid)
        "Lucia Gomez": (" $50 ", "CLEARED"),          # VIP, <= 500, Cleared
        "Carlos Sainz": ("501", "CLEARED"),           # VIP, > 500, Cleared (Valid)
        "Lando Norris": ("1000", "FAILED"),           # VIP, > 500, Failed
        "Charles Leclerc": (" $500 ", "CLEARED"),     # VIP, exactly 500, Cleared
        "Max Verstappen": (" 550 ", "CLEARED")        # VIP, > 500, Cleared (Valid)
    }
    
    for vip, (amt_str, status) in vip_amounts.items():
        transactions.append({
            "Guest_Name": vip,
            "Amount": amt_str,
            "Status": status
        })

    # Noise transactions
    for i in range(2500):
        status = random.choice(statuses)
        val = random.randint(10, 1000)
        fmt = random.choice(["${}", " USD {}", " {} "])
        amt_str = fmt.format(val)
        
        transactions.append({
            "Guest_Name": f"Guest_{i}",
            "Amount": amt_str,
            "Status": status
        })
            
    # Shuffle and split into 50 CSVs
    random.shuffle(transactions)
    
    rows_per_csv = len(transactions) // 50
    for i in range(50):
        chunk = transactions[i*rows_per_csv:(i+1)*rows_per_csv]
        with open(f"tips_logs/tips_batch_{i:03d}.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Transaction_ID", "Guest_Name", "Amount", "Status"])
            for idx, t in enumerate(chunk):
                writer.writerow([f"T{i}_{idx}", t["Guest_Name"], t["Amount"], t["Status"]])

if __name__ == "__main__":
    build_env()
