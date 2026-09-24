import os
import json
import random
import csv
from datetime import datetime

def build_env():
    base_dir = "archive_1438"
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Fragmented Intake Records (The Allergy Source)
    # Strategy: Split child data into multiple tiny JSON/CSV files with decoys
    intake_dir = os.path.join(base_dir, "intake_fragments")
    os.makedirs(intake_dir, exist_ok=True)
    
    children_data = [
        {"name": "Noah", "allergy": "Peanuts", "active": True},
        {"name": "Emma", "allergy": "None", "active": True},
        {"name": "Liam", "allergy": "Dairy", "active": True},
        {"name": "Chloe", "allergy": "Gluten", "active": True},
        {"name": "Mason", "allergy": "Shellfish", "active": True},
        {"name": "Jacob", "allergy": "Soy", "active": False}, # Decoy: Inactive
    ]
    
    for i, child in enumerate(children_data):
        # Mix formats and add noise
        filename = f"child_rec_{1000 + i}.json" if i % 2 == 0 else f"entry_{i}_primary.csv"
        path = os.path.join(intake_dir, filename)
        if filename.endswith(".json"):
            with open(path, "w") as f:
                json.dump(child, f)
        else:
            with open(path, "w") as f:
                f.write(f"name,allergy,status\n{child['name']},{child['allergy']},active")

    # Add 50 decoy intake files
    for i in range(50):
        with open(os.path.join(intake_dir, f"temp_draft_{i}.txt"), "w") as f:
            f.write("DRAFT RECORD: VOID")

    # 2. Fragmented Daily Logs (The Activity & Snack Source)
    # Strategy: Massive directory tree, date-based filtering, rambling text
    log_dir = os.path.join(base_dir, "daily_logs")
    os.makedirs(log_dir, exist_ok=True)
    
    dates = ["2023-10-25", "2023-10-26", "2023-10-27"] # Target is Oct 27
    activities = ["Indoor Play", "Nap Time", "Garden Time", "Story Hour"]
    snacks = ["Apple Slices", "Celery Sticks", "Carrot Sticks", "Rice Cakes", "Yogurt"]

    content_templates = [
        "{name} had a wonderful time with {activity}. I made sure they had {snack} as a safe snack.",
        "During {activity}, {name} was very helpful. Served {snack} afterwards.",
        "{name} was grexing during {activity}, but cheered up after eating {snack}."
    ]

    for date in dates:
        date_folder = os.path.join(log_dir, f"logs_{date}")
        os.makedirs(date_folder, exist_ok=True)
        
        # Target data for 2023-10-27
        if date == "2023-10-27":
            # Noah: Allergy (Peanuts), Garden, Snack (Celery Sticks) -> TARGET
            # Emma: No Allergy, Garden, Snack (Graham Crackers) -> NO (No Allergy)
            # Liam: Allergy (Dairy), Inside, Snack (Apples) -> NO (Not Garden)
            # Chloe: Allergy (Gluten), Garden, Snack (Carrot Sticks) -> TARGET
            # Mason: Allergy (Shellfish), Napping -> NO (Not Garden)
            
            day_data = [
                ("Noah", "Garden Time", "Celery Sticks"),
                ("Emma", "Garden Time", "Graham Crackers"),
                ("Liam", "Indoor Reading", "Apple Slices"),
                ("Chloe", "Garden Time", "Carrot Sticks"),
                ("Mason", "Nap Time", "None")
            ]
        else:
            # Old noise data
            day_data = [("Noah", "Garden Time", "Old Snack")] * 5

        for i, (name, activity, snack) in enumerate(day_data):
            # Bury the real data in 100 random log files per day
            for j in range(20):
                log_file = os.path.join(date_folder, f"entry_shift_{i}_{j}.log")
                with open(log_file, "w") as f:
                    if j == 7: # Hide the needle in the haystack
                        f.write(random.choice(content_templates).format(name=name, activity=activity, snack=snack))
                    else:
                        f.write("Nothing much happened. Just redding up the kitchen.")

    # 3. Hidden Hint (Metas)
    with open(os.path.join(base_dir, "metadata.txt"), "w") as f:
        f.write("System Note: Daily Logs are stored by date. Today's date is 2023-10-27. Use shift_7 entry logs for primary activity summaries.")

if __name__ == "__main__":
    build_env()
