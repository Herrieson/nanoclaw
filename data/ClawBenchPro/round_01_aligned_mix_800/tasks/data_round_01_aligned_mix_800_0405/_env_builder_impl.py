import os
import csv
import random
import json

def build_env():
    # Set seed for reproducible environment generation
    random.seed(42)
    
    # Create directories
    os.makedirs('shop_notes', exist_ok=True)
    os.makedirs('front_desk', exist_ok=True)
    os.makedirs('office_reports', exist_ok=True)

    # Categories and weights
    categories = ['Transmission', 'Engine', 'Brakes', 'Suspension', 'Electrical']
    
    # Generate 1000 Work Orders for the year
    work_orders = {}
    for i in range(1001, 2001):
        cat = random.choices(categories, weights=[25, 30, 20, 15, 10])[0]
        work_orders[f"WO-{i}"] = cat

    # Write the Master CSV (The Source of Truth)
    master_csv_path = os.path.join('front_desk', 'master_work_orders_2023.csv')
    with open(master_csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['WO_ID', 'Customer_Name', 'Vehicle_Make', 'Job_Category'])
        for wo, cat in work_orders.items():
            writer.writerow([wo, f"Customer_{random.randint(100,999)}", random.choice(['Ford', 'Chevy', 'Dodge', 'Toyota', 'Honda']), cat])

    # Write Decoy CSVs (Noise)
    decoy_csv_path = os.path.join('front_desk', 'draft_wos_2023_backup_DO_NOT_USE.csv')
    with open(decoy_csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['WO_ID', 'Job_Category'])
        for wo in work_orders.keys():
            # Randomly corrupt the category to mislead the agent if they use the wrong file
            writer.writerow([wo, random.choice(categories)])

    # Mechanic's Rants (Noise text)
    rants = [
        "Boss is complaining about taxes again, like that's anything new.",
        "The 4-year-old was driving me crazy last night, didn't get a wink of sleep.",
        "People just don't take care of their cars anymore. I swear.",
        "Bolts were rusted tight. Had to bust out the blowtorch.",
        "Thinking about packing up the RV for Ocala tonight.",
        "Government taking half my paycheck, for what? Potholes everywhere.",
        "Customer complained about a squeak. It was a damn acorn in the blower motor.",
        "Need to get out to the woods so the kids can burn off that energy."
    ]

    # Generate daily logs deep in directories
    wo_list = list(work_orders.keys())
    wo_index = 0
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    for month_idx, month in enumerate(months):
        month_dir = os.path.join('shop_notes', f"{month_idx+1:02d}_{month}")
        os.makedirs(month_dir, exist_ok=True)
        
        # 28 days per month to simplify
        for day in range(1, 29):
            if wo_index >= len(wo_list):
                break
                
            day_file = os.path.join(month_dir, f"day_{day:02d}.txt")
            
            # 2 to 4 WOs per day
            daily_wos_count = random.randint(2, 4)
            daily_content = []
            
            for _ in range(daily_wos_count):
                if wo_index >= len(wo_list):
                    break
                
                wo = wo_list[wo_index]
                cat = work_orders[wo]
                wo_index += 1
                
                # Assign hours and quarts
                hrs = round(random.uniform(0.5, 8.0), 1)
                qts = round(random.uniform(0.0, 15.0), 1)
                
                rant1 = random.choice(rants)
                rant2 = random.choice(rants)
                
                # Different templates so regex needs to be slightly robust
                templates = [
                    f"Worked on {wo} today. {rant1} Took me {hrs} hours. Used {qts} quarts of fluid. {rant2}",
                    f"[{wo}] {rant1} Labor: {hrs} hrs. Fluid: {qts} qts. {rant2}",
                    f"{rant1} Finally finished {wo}. That's {hrs} hours of my life I won't get back. Poured in {qts} quarts.",
                    f"Job {wo}: {hrs} hours spent. Added {qts} quarts. {rant2}"
                ]
                
                daily_content.append(random.choice(templates))
            
            with open(day_file, 'w') as f:
                # Separate WO logs by double newlines to ensure clean paragraph parsing
                f.write("\n\n".join(daily_content))

if __name__ == '__main__':
    build_env()
