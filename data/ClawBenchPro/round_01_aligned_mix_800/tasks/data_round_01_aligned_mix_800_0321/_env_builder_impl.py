import os
import csv

def build_env():
    # Create necessary directories
    os.makedirs("records", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    
    # Information-stripped data: missing product_name, quantity, and unit_price
    # Agent MUST use the skills to retrieve this missing data.
    data = [
        {"order_id": "1001", "customer_email": "alice@example.com", "customer_message": "Can this help my indoor garden?"},
        {"order_id": "1002", "customer_email": "bob@example.com", "customer_message": "I love wellness tech and drinking clean water."},
        {"order_id": "1003", "customer_email": "charlie@test.com", "customer_message": "Just ship it fast please."},
        {"order_id": "1004", "customer_email": "diana@mail.com", "customer_message": "Health is wealth! Using this for my workout."},
        {"order_id": "1005", "customer_email": "edward@example.com", "customer_message": "Need this for the tomatoes."},
        {"order_id": "1006", "customer_email": "frank@test.com", "customer_message": "Cancel this order, I changed my mind."}, 
    ]
    
    # Write to CSV
    file_path = os.path.join("records", "inbox_export.csv")
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["order_id", "customer_email", "customer_message"])
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    build_env()
