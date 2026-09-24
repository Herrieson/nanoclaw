import os
import csv
import json
import random

def build_env():
    # Set fixed seed for deterministic validation
    random.seed(42)
    
    os.makedirs("desk", exist_ok=True)
    
    # 1. Build Financials Wasteland
    categories = [
        "Food-Lunch", "Food-Dinner", "Beverage-Wine", "Beverage-Water", 
        "Decor-Lights", "Speaker-Fee", "Venue-Rental", "Food-Snacks", "Security"
    ]
    
    for q in ["Q1", "Q2", "Q3", "Q4"]:
        for w in ["week1", "week2", "week3", "week4"]:
            dir_path = os.path.join("financials", q, w)
            os.makedirs(dir_path, exist_ok=True)
            
            # Generate 10-25 files per week directory
            for i in range(random.randint(10, 25)):
                is_json = random.choice([True, False])
                is_verified = random.random() < 0.25  # Only 25% are VERIFIED
                status_txt = "VERIFIED" if is_verified else random.choice(["PENDING", "REJECTED", "DRAFT"])
                
                items = []
                # Use strict .25, .50, .75, .00 to avoid IEEE 754 float precision nightmare during sums
                for _ in range(random.randint(1, 6)):
                    cat = random.choice(categories)
                    cost = random.choice([10.50, 20.00, 100.25, 50.75, 500.00])
                    items.append((cat, cost))
                
                file_id = random.randint(1000, 9999)
                if is_json:
                    file_name = f"invoice_{i}_{file_id}.json"
                    data = {
                        "status": status_txt,
                        "id": f"INV-{file_id}",
                        "items": [{"name": c, "cost": cost} for c, cost in items]
                    }
                    with open(os.path.join(dir_path, file_name), "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2)
                else:
                    file_name = f"receipt_{i}_{file_id}.txt"
                    content = f"STATUS: {status_txt}\n"
                    content += f"ID: REC-{file_id}\n"
                    content += "Items:\n"
                    for c, cost in items:
                        content += f"- Item: {c} | Amount: ${cost:.2f}\n"
                    with open(os.path.join(dir_path, file_name), "w", encoding="utf-8") as f:
                        f.write(content)

    # 2. Build Registrations Wasteland
    os.makedirs("registrations", exist_ok=True)
    first_names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Heidi", "Ivan", "Judy", "Mallory", "Victor", "Trent", "Peggy", "Sybil"]
    last_names = ["Smith", "Doe", "Johnson", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Atwood", "Baldwin"]
    ticket_types = ["VIP", "General", "Speaker", "Sponsor", "V.I.P", "vip", "VIP Guest"]
    valid_diets = ["Vegan", "Vegetarian", "Nut Allergy", "Halal", "Kosher", "Pescatarian"]
    invalid_diets = ["None", "N/A", "none", "n/a", "", " ", "  ", "n/A", "NONE"]
    
    for batch in range(1, 51):
        file_name = f"batch_{batch:03d}.csv"
        with open(os.path.join("registrations", file_name), "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["reg_id", "full_name", "ticket_type", "diet_notes"])
            
            for r in range(random.randint(20, 50)):
                name = f"{random.choice(first_names)} {random.choice(last_names)}"
                
                # Introduce intentional noise and targets
                scenario = random.random()
                if scenario < 0.05:
                    # TARGET: True VIP with bad diet
                    ttype = "VIP"
                    diet = random.choice(invalid_diets)
                elif scenario < 0.15:
                    # DECOY: True VIP with GOOD diet
                    ttype = "VIP"
                    diet = random.choice(valid_diets)
                elif scenario < 0.25:
                    # DECOY: Fake VIP with bad diet
                    ttype = random.choice(["V.I.P", "vip", "VIP Guest"])
                    diet = random.choice(invalid_diets)
                else:
                    # NORMAL: General attendees
                    ttype = random.choice(["General", "Speaker", "Sponsor"])
                    diet = random.choice(valid_diets + invalid_diets)
                
                writer.writerow([f"REG-{batch}-{r}", name, ttype, diet])

if __name__ == "__main__":
    build_env()
