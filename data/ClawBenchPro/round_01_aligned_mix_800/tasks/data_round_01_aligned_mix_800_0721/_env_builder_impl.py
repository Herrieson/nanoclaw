import os
import csv

def build_env():
    # Create necessary directories
    os.makedirs("records", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    
    # Dirty data simulating the messy export
    data = [
        {"order_id": "1001", "customer_email": "alice@example.com", "product_name": "Smart Soil Monitor", "quantity": "2", "unit_price": "$25.00", "customer_message": "Can this help my indoor garden?"},
        {"order_id": "1002", "customer_email": "bob@example.com", "product_name": "UV Water Sanitizer", "quantity": "1", "unit_price": "$30.00", "customer_message": "I love wellness tech and drinking clean water."},
        {"order_id": "1003", "customer_email": "charlie@test.com", "product_name": "Smart Soil Monitor", "quantity": "1", "unit_price": "25.00", "customer_message": "Just ship it fast please."},
        {"order_id": "1004", "customer_email": "diana@mail.com", "product_name": "Bluetooth Speaker", "quantity": "1", "unit_price": "$50.00", "customer_message": "Health is wealth! Using this for my workout."},
        {"order_id": "1005", "customer_email": "edward@example.com", "product_name": "Smart Soil Monitor", "quantity": "3", "unit_price": " $25.00 ", "customer_message": "Need this for the tomatoes."},
        {"order_id": "1006", "customer_email": "frank@test.com", "product_name": "Smart Soil Monitor", "quantity": "0", "unit_price": "$25.00", "customer_message": "Cancel this order, I changed my mind."}, 
    ]
    
    # Write to CSV
    file_path = os.path.join("records", "inbox_export.csv")
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["order_id", "customer_email", "product_name", "quantity", "unit_price", "customer_message"])
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    build_env()
