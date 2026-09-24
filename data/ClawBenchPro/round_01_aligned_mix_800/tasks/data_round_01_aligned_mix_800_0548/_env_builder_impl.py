import os
import csv
import json
import random

def build_env():
    # Set fixed seed for absolute determinism
    random.seed(1492)

    # 1. Create directories
    regions = ["North", "South", "East", "West"]
    weeks = ["Week_1", "Week_2", "Week_3", "Week_4"]
    
    os.makedirs("records/roster", exist_ok=True)
    os.makedirs("records/compliance_logs", exist_ok=True)
    os.makedirs("finances/receipts/2023/Q3", exist_ok=True)
    os.makedirs("finances/receipts/2023/Q4", exist_ok=True)
    
    for r in regions:
        for w in weeks:
            os.makedirs(f"records/timesheets/Region_{r}/{w}", exist_ok=True)

    # 2. Generate Roster (400 Volunteers)
    first_names = ["Alice", "Bob", "Charlie", "Diana", "Evan", "Fiona", "George", "Hannah", "Ivan", "Julia", 
                   "Kevin", "Luna", "Mason", "Nora", "Oscar", "Penny", "Quinn", "Rachel", "Sam", "Tina"]
    last_names = ["Smith", "Jones", "Williams", "Brown", "Taylor", "Davies", "Evans", "Thomas", "Roberts", "White",
                  "Martin", "Thompson", "Garcia", "Martinez", "Robinson", "Clark", "Rodriguez", "Lewis", "Lee", "Walker"]
    
    volunteers = {}
    v_ids = []
    
    roster_data = []
    for i in range(1, 401):
        vid = f"V{i:04d}"
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        # Ensure unique full names for the puzzle's sake to avoid sorting ambiguity
        while f"{fn} {ln}" in volunteers.values():
            fn = random.choice(first_names)
            ln = random.choice(last_names)
        
        full_name = f"{fn} {ln}"
        volunteers[vid] = full_name
        v_ids.append(vid)
        roster_data.append({"Vol_ID": vid, "First_Name": fn, "Last_Name": ln, "Email": f"{fn.lower()}.{ln.lower()}@example.com"})

    with open("records/roster/master_roster.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Vol_ID", "First_Name", "Last_Name", "Email"])
        writer.writeheader()
        writer.writerows(roster_data)

    # 3. Generate Compliance Logs (Background Checks with overlapping events)
    base_time = 1690000000
    events = []
    
    # Decide true final statuses
    # 60% Cleared, 20% Pending, 10% Rejected, 10% No record
    for vid in v_ids:
        fate = random.random()
        if fate < 0.10:
            continue # No record
        elif fate < 0.20:
            events.append({"vid": vid, "status": "PENDING", "timestamp": base_time + random.randint(100, 5000)})
            events.append({"vid": vid, "status": "REJECTED", "timestamp": base_time + random.randint(10000, 20000)})
        elif fate < 0.40:
            events.append({"vid": vid, "status": "PENDING", "timestamp": base_time + random.randint(100, 50000)})
        else:
            events.append({"vid": vid, "status": "PENDING", "timestamp": base_time + random.randint(100, 5000)})
            events.append({"vid": vid, "status": "CLEARED", "timestamp": base_time + random.randint(10000, 30000)})
            # Some get a weird third update just to test latest timestamp
            if random.random() < 0.1:
                events.append({"vid": vid, "status": "CLEARED", "timestamp": base_time + random.randint(35000, 40000)})

    random.shuffle(events)
    
    # Split events into 8 batch files
    chunk_size = len(events) // 8
    for i in range(8):
        batch = events[i*chunk_size : (i+1)*chunk_size]
        with open(f"records/compliance_logs/batch_{i+1:02d}.json", "w", encoding="utf-8") as f:
            json.dump({"batch_id": i+1, "events": batch}, f, indent=4)
            
    # Add a decoy text file
    with open("records/compliance_logs/readme.txt", "w") as f:
        f.write("Do not use legacy system statuses. Trust only these JSON batches based on timestamp.\n")

    # 4. Generate Timesheets
    # Spread ~1500 timesheet entries across the regions and weeks
    for r in regions:
        for w in weeks:
            num_files = random.randint(3, 7)
            for file_idx in range(num_files):
                filepath = f"records/timesheets/Region_{r}/{w}/day_{file_idx}.csv"
                entries = []
                for _ in range(random.randint(10, 30)):
                    vid = random.choice(v_ids)
                    hours = round(random.uniform(1.0, 8.0), 1)
                    entries.append({"Date": f"2023-10-{random.randint(1,28):02d}", "Vol_ID": vid, "Hours_Worked": hours})
                
                with open(filepath, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=["Date", "Vol_ID", "Hours_Worked"])
                    writer.writeheader()
                    writer.writerows(entries)
            
            # Decoy file
            with open(f"records/timesheets/Region_{r}/{w}/.DS_Store", "w") as f:
                f.write("junk data")

    # 5. Generate Finances (Messy formatting)
    statuses = ["VERIFIED", "DRAFT", "VOID", "REJECTED"]
    currencies = ["$", "USD ", " USD", "", "$ "]
    
    for q in ["Q3", "Q4"]:
        for batch in ["A", "B", "C"]:
            expense_data = []
            for txn in range(random.randint(40, 80)):
                raw_amt = round(random.uniform(5.0, 5000.0), 2)
                # Messy formatting
                amt_str = f"{raw_amt:,.2f}" # with comma
                if random.choice([True, False]):
                    amt_str = f"{raw_amt:.2f}" # without comma
                
                prefix = random.choice(currencies)
                suffix = random.choice(currencies) if prefix == "" else ""
                
                messy_amt = f"{prefix}{amt_str}{suffix}"
                if random.random() < 0.1:
                    messy_amt = f"  {messy_amt}  " # add spaces
                
                expense_data.append({
                    "Txn_ID": f"TXN-{q}-{batch}-{txn:04d}",
                    "Category": random.choice(["Supplies", "Venue", "Ads", "Food"]),
                    "Amount": messy_amt,
                    "Status": random.choices(statuses, weights=[0.5, 0.2, 0.2, 0.1])[0]
                })
                
            with open(f"finances/receipts/2023/{q}/expenses_batch_{batch}.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["Txn_ID", "Category", "Amount", "Status"])
                writer.writeheader()
                writer.writerows(expense_data)

if __name__ == "__main__":
    build_env()
