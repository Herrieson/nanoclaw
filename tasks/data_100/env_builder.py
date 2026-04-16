import os
import json
import csv
import random
import string

def setup_env():
    base_dir = "assets/data_100"
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Create book catalog (book_catalog.json)
    books = {
        "978-0141439518": {"title": "Pride and Prejudice", "price": 25.50},
        "978-0451524935": {"title": "1984", "price": 18.00},
        "978-0743273565": {"title": "The Great Gatsby", "price": 30.00},
        "978-0316769488": {"title": "The Catcher in the Rye", "price": 22.75},
        "978-0060935467": {"title": "To Kill a Mockingbird", "price": 20.00},
        "978-0544003415": {"title": "The Lord of the Rings", "price": 65.00},
        "978-0439023481": {"title": "The Hunger Games", "price": 15.20}
    }
    with open(os.path.join(base_dir, "book_catalog.json"), "w") as f:
        json.dump(books, f, indent=4)
        
    # 2. Create shipping addresses (shipping_addresses.csv)
    users = [
        {"user_id": "USR-1092", "name": "Alice Wonderland", "address": "123 Rabbit Hole Ln, CT"},
        {"user_id": "USR-4431", "name": "Bob Builder", "address": "456 Construction Rd, NY"},
        {"user_id": "USR-9920", "name": "Charlie Brown", "address": "789 Peanut St, MA"},
        {"user_id": "USR-0045", "name": "Diana Prince", "address": "1 Themyscira Ave, VA"},
        {"user_id": "USR-7734", "name": "Evan Hansen", "address": "321 Broadway, NY"}
    ]
    with open(os.path.join(base_dir, "shipping_addresses.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["user_id", "name", "address"])
        writer.writeheader()
        writer.writerows(users)
        
    # 3. Create messy logs (server_logs.txt)
    # Target truths to hide:
    # USR-1092 bought 978-0141439518
    # USR-9920 bought 978-0743273565
    # USR-0045 bought 978-0544003415
    # USR-7734 bought 978-0439023481
    
    target_orders = [
        ("USR-1092", "978-0141439518"),
        ("USR-9920", "978-0743273565"),
        ("USR-0045", "978-0544003415"),
        ("USR-7734", "978-0439023481")
    ]
    
    logs = []
    for _ in range(500):
        # Generate some noise
        rand_str = ''.join(random.choices(string.ascii_letters + string.digits, k=15))
        logs.append(f"[INFO] System check heartbeat OK {rand_str} - load: 0.0{random.randint(1,9)}\n")
        if random.random() < 0.1:
            logs.append(f"[DEBUG] Cache miss for item {random.randint(1000, 9999)}\n")
            
    # Inject target orders randomly into the logs
    for uid, isbn in target_orders:
        insert_idx = random.randint(0, len(logs) - 1)
        # Obfuscated but parsable format
        log_entry = f"[ORDER_PROC] transaction_initiated:: payload={{'buyer_hash': '{uid}', 'item_code': 'ISBN:{isbn}', 'status': 'PAID'}} -- signature_valid\n"
        logs.insert(insert_idx, log_entry)
        
    with open(os.path.join(base_dir, "server_logs.txt"), "w") as f:
        f.writelines(logs)

if __name__ == "__main__":
    setup_env()
