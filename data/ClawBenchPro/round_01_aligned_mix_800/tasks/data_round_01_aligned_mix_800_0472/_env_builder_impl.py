import os
import json
import csv
import random

def build_env():
    random.seed(42)
    os.makedirs('financial_exports/2023', exist_ok=True)
    os.makedirs('inventory_master', exist_ok=True)
    os.makedirs('finished_plan', exist_ok=True)

    # 1. Generate 1000 noise parts in inventory master
    for i in range(1000):
        part_id = f"P-RND-{i:04d}"
        origin = random.choice(['Retail', 'Hardware_Store', 'Online', 'Unknown', 'Factory_Scrap', 'Plastics_Plant'])
        with open(f'inventory_master/{part_id}.ini', 'w', encoding='utf-8') as f:
            f.write(f"[Info]\nPartID={part_id}\nName=RandomPart_{i}\nOrigin={origin}\n")

    # 2. Define specific Kart Parts (The Needles)
    kart_parts = {
        "P-K-101": "Retail_Store",       # Valid Paid
        "P-K-102": "Hardware_Store",     # Valid Paid
        "P-K-103": "Online_Retailer",    # Valid Paid
        "P-K-104": "Factory_Scrap",      # Factory Scrap (Must Ignore)
        "P-K-105": "Plastics_Plant",     # Factory Scrap (Must Ignore)
        "P-K-106": "Retail_Store",       # Valid origin, but marked returned (Must Ignore)
        "P-K-107": "Hardware_Store"      # Valid origin, but marked returned (Must Ignore)
    }

    for pid, origin in kart_parts.items():
        with open(f'inventory_master/{pid}.ini', 'w', encoding='utf-8') as f:
            f.write(f"[Info]\nPartID={pid}\nName=KartComponent\nOrigin={origin}\n")

    # 3. Generate Transactions
    months = [f"{m:02d}" for m in range(1, 13)]
    all_txns = []

    # Injecting the specific kart transactions
    # Valid Txns Total = 35.50 + 85.00 + 95.00 = 215.50 (Busted the $200 budget)
    all_txns.append({'type': 'json', 'month': '03', 'data': {"txn_id": "T-K1", "amount": 35.50, "item_code": "P-K-101", "metadata": {"project": "kids-kart", "status": "completed"}}})
    all_txns.append({'type': 'csv',  'month': '05', 'data': ["T-K2", 85.00, "P-K-102", "Go-Kart Build", "No"]})
    all_txns.append({'type': 'json', 'month': '08', 'data': {"txn_id": "T-K3", "amount": 95.00, "item_code": "P-K-103", "metadata": {"project": "kart-project", "status": "delivered"}}})
    
    # Scrap Txns (Nominal amounts, but must be filtered out via INI lookup)
    all_txns.append({'type': 'json', 'month': '02', 'data': {"txn_id": "T-K4", "amount": 150.00, "item_code": "P-K-104", "metadata": {"project": "kart", "status": "completed"}}}) 
    all_txns.append({'type': 'csv',  'month': '06', 'data': ["T-K5", 40.00, "P-K-105", "diy-kart", "No"]}) 
    
    # Returned Txns (Valid parts, but refunded)
    all_txns.append({'type': 'json', 'month': '09', 'data': {"txn_id": "T-K6", "amount": 25.00, "item_code": "P-K-106", "metadata": {"project": "karting", "status": "returned"}}}) 
    all_txns.append({'type': 'csv',  'month': '11', 'data': ["T-K7", 12.00, "P-K-107", "KART", "Yes"]}) 

    # Generate noise transactions
    for i in range(1000):
        month = random.choice(months)
        part_id = f"P-RND-{random.randint(0, 999):04d}"
        amt = round(random.uniform(5.0, 500.0), 2)
        project_tag = random.choice(["kitchen_remodel", "groceries", "bills", "misc", "vacation"])
        
        if random.choice([True, False]):
            all_txns.append({'type': 'json', 'month': month, 'data': {"txn_id": f"T-R-{i}", "amount": amt, "item_code": part_id, "metadata": {"project": project_tag, "status": random.choice(["completed", "returned"])}}})
        else:
            all_txns.append({'type': 'csv', 'month': month, 'data': [f"T-R-{i}", amt, part_id, project_tag, random.choice(["Yes", "No"])]})

    random.shuffle(all_txns)

    # 4. Scatter transactions into deep directories
    for month in months:
        os.makedirs(f'financial_exports/2023/{month}', exist_ok=True)
        month_txns = [t for t in all_txns if t['month'] == month]
        json_txns = [t['data'] for t in month_txns if t['type'] == 'json']
        csv_txns = [t['data'] for t in month_txns if t['type'] == 'csv']

        # Scatter JSONs
        for i in range(0, len(json_txns), 12):
            chunk = json_txns[i:i+12]
            if chunk:
                with open(f'financial_exports/2023/{month}/export_batch_{i}.json', 'w', encoding='utf-8') as f:
                    json.dump(chunk, f, indent=2)

        # Scatter CSVs
        for i in range(0, len(csv_txns), 18):
            chunk = csv_txns[i:i+18]
            if chunk:
                with open(f'financial_exports/2023/{month}/log_batch_{i}.csv', 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Transaction_ID", "Cost", "Part_Number", "Category", "Is_Refunded"])
                    writer.writerows(chunk)

if __name__ == '__main__':
    build_env()
