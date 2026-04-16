import os
import csv

def build_env():
    base_dir = "assets/data_418"
    os.makedirs(base_dir, exist_ok=True)

    # Data Part 1
    csv1_path = os.path.join(base_dir, "loans_part1.csv")
    with open(csv1_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['applicant_id', 'income', 'credit_score', 'demographic_category', 'base_risk'])
        writer.writerow(['A001', '25000', '600', 'Group_A', '0.5'])
        writer.writerow(['A002', '100000', '750', 'Group_A', '0.2'])
        writer.writerow(['A003', '50000', '650', 'Group_B', '0.4'])

    # Data Part 2
    csv2_path = os.path.join(base_dir, "loans_part2.csv")
    with open(csv2_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['applicant_id', 'income', 'credit_score', 'demographic_category', 'base_risk'])
        writer.writerow(['A004', '40000', '620', 'Group_B', '0.45'])
        writer.writerow(['A005', '80000', '710', 'Group_C', '0.3'])
        writer.writerow(['A006', '30000', '580', 'Group_C', '0.55'])

    # Corrupted Python Script
    py_content = """import os
import glob
import json
# import pandas as pd  <-- I don't use pandas, just standard csv module!

def process_data():
    all_records = []
    
    # Read all csvs
    for file in glob.glob('loans_part*.csv'):
        with open(file, 'r') as f:
            lines = f.readlines()
            headers = lines[0].strip().split(',')
            for line in lines[1:]:
                if not line.strip(): continue
                parts = line.strip().split(',')
                all_records.append(dict(zip(headers, parts)))

    grouped = {}
    
    for row in all_records:
        demo = row['demographic_category']
        base = float(row['base_risk'])
        cred = float(row['credit_score'])
        inc = float(row['income'])
        
        # TODO: adjusted_risk should be: base_risk minus (credit_score divided by 1000) plus (50000 divided by income)
        # to ensure fair weighting for lower income applicants
        
        adfasdf234234  # my daughter typed this!!!!
        adjusted_risk = base + (cred / 1000) - (inc / 50000)   # wait is this right???
        
        if demo not in grouped
            grouped[demo] = []
        grouped[demo].append(adjusted_risk)

    results = {}
    for k, v in grouped.items()
        results[k] = sum(v) / len(v)

    # write to fairness_report.json
    with open('fairness_report.json', 'w') as out:
        json.dump(results, out)

if __name__ == '__main__':
    process_data()
"""
    py_path = os.path.join(base_dir, "model_prep.py")
    with open(py_path, 'w') as f:
        f.write(py_content)

if __name__ == "__main__":
    build_env()
