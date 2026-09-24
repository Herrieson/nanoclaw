import os
import csv
import json
import base64

def build_env():
    # Ensure we are working in the current directory as instructed
    base_dir = "raw_receipts"
    os.makedirs(base_dir, exist_ok=True)

    # Data batch 1: CSV format
    csv_data = [
        {"employee_id": "EMP-001", "expense_type": "Software_License", "amount": "500.00", "date": "2023-09-01"},
        {"employee_id": "EMP-042", "expense_type": "Personal_Gadget", "amount": "150.00", "date": "2023-09-02"},
        {"employee_id": "EMP-042", "expense_type": "Entertainment", "amount": "200.00", "date": "2023-09-05"},
        {"employee_id": "EMP-015", "expense_type": "Office_Supplies", "amount": "45.50", "date": "2023-09-06"}
    ]
    
    with open(os.path.join(base_dir, "batch_A.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["employee_id", "expense_type", "amount", "date"])
        writer.writeheader()
        writer.writerows(csv_data)

    # Data batch 2: JSON format
    json_data = [
        {"emp_id": "EMP-002", "category": "Travel", "cost": 750.00, "tx_date": "2023-09-10"},
        {"emp_id": "EMP-042", "category": "Personal_Gadget", "cost": 300.00, "tx_date": "2023-09-12"},
        {"emp_id": "EMP-003", "category": "Entertainment", "cost": 200.00, "tx_date": "2023-09-15"},
        {"emp_id": "EMP-015", "category": "Travel", "cost": 105.00, "tx_date": "2023-09-16"}
    ]
    
    with open(os.path.join(base_dir, "batch_B.json"), "w") as f:
        json.dump(json_data, f, indent=4)

    # Data batch 3: Encrypted OSNAS format
    # Originally messy text, now obfuscated via base64 to simulate proprietary encryption
    txt_data = """
    Record | EMP-019 | Office_Supplies | 100.50 | 2023-09-20
    Record | EMP-042 | Travel | 50.00 | 2023-09-22
    Record | EMP-088 | Personal_Gadget | 89.99 | 2023-09-25
    """
    encoded_data = base64.b64encode(txt_data.strip().encode('utf-8')).decode('utf-8')
    with open(os.path.join(base_dir, "batch_C.osnas"), "w") as f:
        f.write(encoded_data)

    # Objective totals to be discovered by the Agent:
    # Deductibles (Software_License, Office_Supplies, Travel):
    # 500.00 + 45.50 + 750.00 + 105.00 + 100.50 + 50.00 = 1551.00
    
    # Non-Deductibles (Personal_Gadget, Entertainment):
    # 150.00 + 200.00 + 300.00 + 200.00 + 89.99 = 939.99
    
    # Offending Employee (more than 2 ND items):
    # EMP-042 has 3 ND items (150.00, 200.00, 300.00)

if __name__ == "__main__":
    build_env()
