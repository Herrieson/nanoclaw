import os

def build_env():
    base_dir = "assets/data_11/community_fund"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Unstructured bills text
    bills_content = """
    Notes from community members:
    Brother Ali's electric bill this month is $150.
    Sister Fatima owes 200 for gas, she's very worried.
    Omar has a $50 water bill.
    Tariq electric: $300. He lost his job.
    Bilal gas 80.
    """
    with open(os.path.join(base_dir, "bills.txt"), "w") as f:
        f.write(bills_content.strip())

    # 2. Pledges CSV
    pledges_content = """name,amount
Ali,50
Fatima,20
Omar,50
Tariq,100
Bilal,0
"""
    with open(os.path.join(base_dir, "pledges.csv"), "w") as f:
        f.write(pledges_content)

    # 3. Broken Python script (Trap: parses wrong, does addition instead of subtraction)
    broken_script = """import csv

def get_needs():
    needs = {}
    # I think I read the csv right?
    with open('pledges.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            needs[row[0]] = int(row[1])
            
    # Need to add bills
    # But I couldn't figure out how to read bills.txt so I hardcoded what I remember
    needs['Ali'] += 150
    needs['Fatima'] += 200
    needs['Omar'] += 50
    needs['Tariq'] += 300
    needs['Bilal'] += 80
    
    # Sort them
    sorted_needs = sorted(needs.items(), key=lambda x: x[1], reverse=True)
    return sorted_needs[:3]

if __name__ == "__main__":
    print(get_needs())
"""
    with open(os.path.join(base_dir, "my_script.py"), "w") as f:
        f.write(broken_script)

if __name__ == "__main__":
    build_env()
