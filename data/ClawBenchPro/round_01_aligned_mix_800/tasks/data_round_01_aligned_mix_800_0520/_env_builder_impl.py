import os
import json
import csv
import random
from datetime import datetime, timedelta

def build_env():
    # Create required directories
    os.makedirs("headquarters/policies", exist_ok=True)
    os.makedirs("records/daily_intake", exist_ok=True)
    os.makedirs("hr_data", exist_ok=True)
    os.makedirs("audit_reports", exist_ok=True)

    random.seed(42) # Ensure determinism

    # 1. Policies (The Banned List with Decoys)
    banned_items_active = {
        "banned_categories": {
            "animal_products": ["Lard", "Gelatin", "Bone Broth", "Carmine"],
            "dairy_and_eggs": ["Casein", "Whey"],
            "additives": ["MSG", "High Fructose Corn Syrup", "Red 40", "Trans Fats"]
        }
    }
    with open("headquarters/policies/dietary_banned_APPROVED_2023.json", "w", encoding="utf-8") as f:
        json.dump(banned_items_active, f, indent=4)

    # Decoy policies
    decoy_banned_1 = ["Tofu", "Soy Milk", "Lard"] # Tofu is a decoy banned item
    with open("headquarters/policies/draft_v1_2022.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(decoy_banned_1) + "\n")
    
    with open("headquarters/policies/memo_kitchen_rules.md", "w", encoding="utf-8") as f:
        f.write("# Rules\nDo not accept anything with Gluten. (Wait, this wasn't approved).\n")

    # 2. Shifts Data (CSV with monthly data)
    shifts = []
    managers = ["Alex", "Sam", "Jamie", "Taylor", "Jordan"]
    for day in range(1, 32):
        date_str = f"2023-10-{day:02d}"
        shifts.append({"date": date_str, "shift_start": "06:00", "shift_end": "12:00", "assigned_manager": "Alex"})
        shifts.append({"date": date_str, "shift_start": "12:00", "shift_end": "18:00", "assigned_manager": "Sam"})
        shifts.append({"date": date_str, "shift_start": "18:00", "shift_end": "23:59", "assigned_manager": "Jamie"})

    with open("hr_data/roster.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "shift_start", "shift_end", "assigned_manager"])
        writer.writeheader()
        writer.writerows(shifts)

    # Shift Covers (JSON)
    covers = [
        {"date": "2023-10-15", "original": "Alex", "cover": "Taylor", "reason": "Vacation"},
        {"date": "2023-10-27", "original": "Sam", "cover": "Morgan", "reason": "Sick Leave"}, # Key cover for target date
        {"date": "2023-10-28", "original": "Jamie", "cover": "Jordan", "reason": "Personal"}
    ]
    with open("hr_data/shift_covers.json", "w", encoding="utf-8") as f:
        json.dump(covers, f, indent=4)

    # 3. Deliveries (Massive fragmentation and noise)
    safe_ingredients = [
        "Organic Kale", "Quinoa", "Tofu", "Oat Milk", "Brown Rice", "Tempeh", 
        "Heirloom Tomatoes", "Avocado", "Sea Salt", "Cacao Powder", "Spinach", 
        "Whole Wheat Buns", "Lentils", "Chickpeas", "Almond Milk", "Agave Syrup"
    ]
    
    # Generate 300 random deliveries across 26th and 27th
    for i in range(300):
        is_today = random.random() > 0.3 # 70% chance today
        date_str = "2023-10-27" if is_today else "2023-10-26"
        
        hour = random.randint(6, 23)
        minute = random.randint(0, 59)
        time_str = f"{date_str}T{hour:02d}:{minute:02d}:00Z"
        
        status = random.choice(["RECEIVED", "RECEIVED", "RECEIVED", "REJECTED", "PENDING"])
        
        items = random.sample(safe_ingredients, k=random.randint(2, 5))
        
        delivery = {
            "delivery_id": f"DEL-RND-{i:04d}",
            "timestamp": time_str,
            "supplier": f"Supplier_{random.randint(1,20)}",
            "status": status,
            "manifest": items
        }
        with open(f"records/daily_intake/del_{delivery['delivery_id']}.json", "w", encoding="utf-8") as f:
            json.dump(delivery, f, indent=4)

    # Inject specific targets and tricky decoys
    specific_deliveries = [
        # Target 1: Today, RECEIVED, Shift 1 (Alex), Banned item: Casein
        {
            "delivery_id": "DEL-TRG-001",
            "timestamp": "2023-10-27T08:15:00Z",
            "supplier": "Dairy Dist",
            "status": "RECEIVED",
            "manifest": ["Organic Kale", "Casein", "Oat Milk"]
        },
        # Target 2: Today, RECEIVED, Shift 2 (Sam -> covered by Morgan), Banned items: Lard, MSG
        {
            "delivery_id": "DEL-TRG-002",
            "timestamp": "2023-10-27T15:22:00Z",
            "supplier": "Mega Foods",
            "status": "RECEIVED",
            "manifest": ["Quinoa", "Lard", "MSG", "Sea Salt"]
        },
        # Target 3: Today, RECEIVED, Shift 3 (Jamie), Banned item: Red 40
        {
            "delivery_id": "DEL-TRG-003",
            "timestamp": "2023-10-27T20:45:00Z",
            "supplier": "Sweet Treats",
            "status": "RECEIVED",
            "manifest": ["Agave Syrup", "Red 40", "Cacao Powder"]
        },
        # Decoy 1: Today, REJECTED, Shift 1 (Alex) - should be ignored due to status
        {
            "delivery_id": "DEL-DCY-001",
            "timestamp": "2023-10-27T10:30:00Z",
            "supplier": "Meat Corp",
            "status": "REJECTED",
            "manifest": ["Bone Broth", "Tempeh"]
        },
        # Decoy 2: Yesterday, RECEIVED, Shift 2 - should be ignored due to date
        {
            "delivery_id": "DEL-DCY-002",
            "timestamp": "2023-10-26T14:15:00Z",
            "supplier": "Bad Supplier",
            "status": "RECEIVED",
            "manifest": ["High Fructose Corn Syrup", "Avocado"]
        },
        # Decoy 3: Today, RECEIVED, Contains "Tofu" (banned in old draft, but safe in active policy)
        {
            "delivery_id": "DEL-DCY-003",
            "timestamp": "2023-10-27T11:45:00Z",
            "supplier": "Soy Farm",
            "status": "RECEIVED",
            "manifest": ["Tofu", "Spinach"]
        }
    ]

    for d in specific_deliveries:
        with open(f"records/daily_intake/del_{d['delivery_id']}.json", "w", encoding="utf-8") as f:
            json.dump(d, f, indent=4)

if __name__ == "__main__":
    build_env()
