import os
import json
import csv
import shutil

def main():
    base_dir = "assets/data_410"
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(base_dir, exist_ok=True)
    
    requests_dir = os.path.join(base_dir, "requests")
    os.makedirs(requests_dir, exist_ok=True)

    # 1. Create catalog.json
    catalog = {
        "Charlotte's Web": 8.50,
        "1984": 15.00,
        "The Hobbit": 20.00,
        "To Kill a Mockingbird": 12.00,
        "Fahrenheit 451": 14.50,
        "The Great Gatsby": 10.00
    }
    with open(os.path.join(base_dir, "catalog.json"), "w") as f:
        json.dump(catalog, f, indent=4)

    # 2. Create budget.csv
    budgets = [
        ["Grade", "AllocatedBudget"],
        ["Grade 6", "100.00"],
        ["Grade 7", "150.00"],
        ["Grade 8", "120.00"],
        ["Grade 9", "50.00"]  # Intentionally low to cause a rejection
    ]
    with open(os.path.join(base_dir, "budget.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(budgets)

    # 3. Create request files (messy formats)
    req1 = """Teacher: Mrs. Smith
Grade: Grade 6
Books requested:
Charlotte's Web (Qty: 5)
The Hobbit (Qty: 2)
Notes: Please deliver by Monday!
"""
    # Grade 6 total: 5*8.5 + 2*20 = 42.5 + 40 = 82.5 (Under 100) -> Approved

    req2 = """Name - Mr. Jones
Grade Level -> Grade 7
We need:
1984 - Qty: 4
Fahrenheit 451 - Qty: 3
"""
    # Grade 7 total: 4*15 + 3*14.5 = 60 + 43.5 = 103.5 (Under 150) -> Approved

    req3 = """TEACHER: Davis
GRADE: Grade 9
BOOK LIST:
The Great Gatsby (Qty: 6)
"""
    # Grade 9 total: 6*10 = 60 (Over 50) -> Rejected

    req4 = """From: Ms. Miller
Grade: Grade 8
Books:
To Kill a Mockingbird (Qty: 10)
"""
    # Grade 8 total: 10*12 = 120 (Exactly 120) -> Approved

    req5 = """Teacher: Mr. Brown
Grade: Grade 6
Extra books:
Charlotte's Web (Qty: 1)
"""
    # Grade 6 total goes to 82.5 + 8.5 = 91.0 (Still under 100) -> Approved

    requests_data = {
        "req_smith.txt": req1,
        "req_jones.txt": req2,
        "req_davis.txt": req3,
        "req_miller.txt": req4,
        "req_brown.txt": req5
    }

    for filename, content in requests_data.items():
        with open(os.path.join(requests_dir, filename), "w") as f:
            f.write(content)

if __name__ == "__main__":
    main()
