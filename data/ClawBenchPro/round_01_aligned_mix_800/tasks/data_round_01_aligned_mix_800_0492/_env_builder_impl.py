import os
import json
import csv
import random
import datetime

def build_env():
    random.seed(42)

    # 1. Create sys_configs with decoys and one true active config
    os.makedirs("sys_configs", exist_ok=True)
    for i in range(1, 51):
        is_active = (i == 37) # Only file 37 is the active one
        
        status = "active" if is_active else random.choice(["archived", "deprecated", "draft", "pending"])
        
        if is_active:
            restricted = ["B-101", "B-205", "B-333", "B-404", "B-777", "B-999"]
        else:
            restricted = [f"B-{random.randint(100, 999)}" for _ in range(random.randint(3, 8))]
            
        config_data = {
            "backup_id": f"bkp_{1000+i}",
            "generated_by": "system_auto",
            "status": status,
            "library_settings": {
                "max_checkout_days": 14,
                "restricted_items": restricted,
                "fine_per_day": 0.50
            }
        }
        with open(f"sys_configs/config_v{i}_{random.randint(1000,9999)}.json", "w") as f:
            json.dump(config_data, f, indent=4)

    # 2. Create voice_transcripts
    os.makedirs("voice_transcripts", exist_ok=True)
    months = [f"{m:02d}" for m in range(1, 13)]
    
    # We will embed specific checkout and return events.
    # The true restricted items: ["B-101", "B-205", "B-333", "B-404", "B-777", "B-999"]
    # Scenario setups:
    # B-101: Checked out by Alice, due 2023-09-15. NOT returned. (OVERDUE) -> Cost 850.00
    # B-205: Checked out by Bob, due 2023-08-10. RETURNED. (Ignored)
    # B-333: Checked out by Charlie, due 2023-10-05. NOT returned. (NOT overdue)
    # B-404: Checked out by David, due 2023-09-29. NOT returned. (OVERDUE) -> Cost 1,200.50
    # B-777: Checked out by Eve, due 2023-05-01. RETURNED. (Ignored)
    # B-999: Checked out by Frank, due 2023-09-01. NOT returned. (OVERDUE) -> Cost 4,500.00
    # Decoys (not restricted): B-500 checked out by Grace, due 2023-08-01. NOT returned. 
    
    events = [
        {"date": "2023-08-15", "type": "checkout", "book": "B-101", "student": "Alice Vance", "due": "2023-09-15"},
        {"date": "2023-07-20", "type": "checkout", "book": "B-205", "student": "Bobby Tables", "due": "2023-08-10"},
        {"date": "2023-08-12", "type": "return", "book": "B-205"},
        {"date": "2023-09-20", "type": "checkout", "book": "B-333", "student": "Charlie Brown", "due": "2023-10-05"},
        {"date": "2023-09-10", "type": "checkout", "book": "B-404", "student": "David Smith", "due": "2023-09-29"},
        {"date": "2023-04-15", "type": "checkout", "book": "B-777", "student": "Eve Johnson", "due": "2023-05-01"},
        {"date": "2023-05-05", "type": "return", "book": "B-777"},
        {"date": "2023-08-01", "type": "checkout", "book": "B-999", "student": "Frank Castle", "due": "2023-09-01"},
        {"date": "2023-07-15", "type": "checkout", "book": "B-500", "student": "Grace Hopper", "due": "2023-08-01"}
    ]
    
    event_dict = {}
    for ev in events:
        d = ev["date"]
        if d not in event_dict:
            event_dict[d] = []
        event_dict[d].append(ev)

    ramblings = [
        "The hydrangeas are looking particularly lovely today.",
        "I need to remind the pastor about the bake sale on Sunday.",
        "Oh, my husband forgot his lunch again. Typical.",
        "Why is the library so dusty? I should ask the janitor to sweep.",
        "I spent three hours arranging the hymnals this morning.",
        "A stray cat got into the courtyard today, quite a fuss."
    ]

    start_date = datetime.date(2023, 1, 1)
    for i in range(365):
        current_date = start_date + datetime.timedelta(days=i)
        date_str = current_date.strftime("%Y-%m-%d")
        month_dir = current_date.strftime("%m")
        day_str = current_date.strftime("%d")
        
        mdir = os.path.join("voice_transcripts", f"2023_{month_dir}")
        os.makedirs(mdir, exist_ok=True)
        
        filepath = os.path.join(mdir, f"log_{day_str}.txt")
        
        daily_text = [random.choice(ramblings)]
        
        if date_str in event_dict:
            for ev in event_dict[date_str]:
                if ev["type"] == "checkout":
                    daily_text.append(f"Student {ev['student']} insisted on checking out {ev['book']}. I set the due date to {ev['due']}.")
                elif ev["type"] == "return":
                    daily_text.append(f"Good news, {ev['book']} was returned! Bless their hearts.")
                    
        daily_text.append(random.choice(ramblings))
        
        with open(filepath, "w") as f:
            f.write("\n".join(daily_text))

    # 3. Create district_procurements (fragmented CSV files)
    os.makedirs("district_procurements", exist_ok=True)
    
    # Target prices
    # B-101: 850.00
    # B-404: 1,200.50
    # B-999: 4,500.00
    
    target_books = {
        "B-101": "$850.00",
        "B-404": " $ 1,200.50 ",
        "B-999": "$4,500.00"
    }
    
    headers_variations = [
        ["ItemID", "Title", "Cost", "Vendor"],
        ["RefNumber", "BookName", "ReplacementValue", "Notes"],
        ["ID", "Description", "Price", "DateAcquired"]
    ]
    
    file_count = 200
    for i in range(file_count):
        header = random.choice(headers_variations)
        rows = [header]
        
        # Inject random garbage books
        for _ in range(random.randint(5, 20)):
            r_id = f"B-{random.randint(1000, 9999)}"
            r_title = f"Random Title {random.randint(1, 100)}"
            r_price = f"${random.randint(10, 100)}.00"
            r_extra = "N/A"
            rows.append([r_id, r_title, r_price, r_extra])
            
        # Inject target books in specific files to spread them out
        if i == 42:
            rows.append(["B-101", "Pilgrim's Progress", target_books["B-101"], "Antique Dealer"])
        if i == 115:
            rows.append(["B-404", "Gutenberg Leaf", target_books["B-404"], "Auction"])
        if i == 189:
            rows.append(["B-999", "Signed Mockingbird", target_books["B-999"], "Donation"])
            
        random.shuffle(rows[1:]) # shuffle rows except header
        
        with open(f"district_procurements/batch_{i:03d}.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)

if __name__ == "__main__":
    build_env()
