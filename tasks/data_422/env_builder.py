import os
import json
import csv

def build_env():
    base_dir = "assets/data_422/messy_downloads"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Recipe Text
    with open(os.path.join(base_dir, "recipe_pasta_carbonara.txt"), "w") as f:
        f.write("Classic Carbonara\nIngredients: Eggs, Pecorino Romano, Guanciale, Black Pepper, Pasta.\nBoil pasta. Fry guanciale. Mix eggs and cheese. Combine off heat.")

    # 2. Recipe JSON
    with open(os.path.join(base_dir, "spicy_tacos.json"), "w") as f:
        json.dump({"title": "Spicy Beef Tacos", "prep_time": "20 mins", "ingredients": ["beef", "chili powder", "tortillas", "salsa"]}, f)

    # 3. Bank CSV 1
    with open(os.path.join(base_dir, "batch_log_A.csv"), "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["txn_id", "account", "amount", "status", "timestamp"])
        writer.writerow(["TXN-001", "ACC-123456", "500.00", "SUCCESS", "2023-10-20T10:00:00Z"])
        writer.writerow(["TXN-101", "ACC-778291", "3450.25", "FAILED", "2023-10-20T10:05:00Z"]) # TARGET
        writer.writerow(["TXN-003", "ACC-999888", "20.50", "FLAGGED", "2023-10-20T10:10:00Z"])
        writer.writerow(["TXN-004", "ACC-778291", "100.00", "SUCCESS", "2023-10-20T10:15:00Z"]) # IGNORE

    # 4. Bank JSON
    with open(os.path.join(base_dir, "sys_export_2023.log"), "w") as f:
        data = {
            "export_date": "2023-10-21",
            "records": [
                {"txn": "TXN-099", "acc": "ACC-111111", "amt": 5000.00, "stat": "FAILED"},
                {"txn": "TXN-205", "acc": "ACC-778291", "amt": 1200.00, "stat": "FLAGGED"} # TARGET
            ]
        }
        json.dump(data, f)

    # 5. Bank Pipe Delimited
    with open(os.path.join(base_dir, "legacy_dump.txt"), "w") as f:
        f.write("HEADER|ID|ACCT|VAL|ST\n")
        f.write("ROW|TXN-300|ACC-222333|45.00|SUCCESS\n")
        f.write("ROW|TXN-412|ACC-778291|8000.50|FAILED\n") # TARGET
        f.write("ROW|TXN-413|ACC-778291|90.00|SUCCESS\n") # IGNORE

    # 6. Another Recipe
    with open(os.path.join(base_dir, "thai_green_curry_notes.txt"), "w") as f:
        f.write("Note to self: add more coconut milk next time. The ACC-778291 brand of curry paste is too spicy! Just kidding, it's a bank account.")

    print("Environment built successfully at assets/data_422/messy_downloads")

if __name__ == "__main__":
    build_env()
