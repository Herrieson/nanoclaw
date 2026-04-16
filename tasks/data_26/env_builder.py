import os
import csv

def build_env():
    base_dir = "assets/data_26"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Create properties.csv
    properties = [
        {"Property_ID": "P-001", "Expected_Rent": 1500},
        {"Property_ID": "P-002", "Expected_Rent": 2200},
        {"Property_ID": "P-003", "Expected_Rent": 1800},
        {"Property_ID": "P-004", "Expected_Rent": 900},
        {"Property_ID": "P-005", "Expected_Rent": 3500},
        {"Property_ID": "P-006", "Expected_Rent": 1100},
    ]
    
    with open(os.path.join(base_dir, "properties.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Property_ID", "Expected_Rent"])
        writer.writeheader()
        writer.writerows(properties)

    # 2. Create payment_logs.txt with messy data, typos (like 'O' instead of '0', commas in numbers), and multiple payments
    logs_content = """
    === RENT LOGS MONTH END ===
    Payment received from tenant at P-001: 1500 USD. All good.
    Acct P-002 credit transaction: 1000.00
    Oh wait, tenant for P-002 came back and gave cash: 12OO.00  (note: written with O's by mistake maybe?)
    P-003 rent drop off in the mailbox: $1,800
    P-004 ... tenant called, said they lost their job. 0 paid.
    P-005 partial payment cleared wire transfer: 2000
    P-006 paid $5OO and then another $5OO. Still short.
    End of logs.
    """
    
    with open(os.path.join(base_dir, "payment_logs.txt"), "w") as f:
        f.write(logs_content)

if __name__ == "__main__":
    build_env()
