import os
import csv

def build_env():
    os.makedirs('store_data', exist_ok=True)
    
    # Dirty complaint logs - NOTE: The 'customer_complaint' column has been removed 
    # to force the agent to use the API tools. Manager names are also purely IDs now.
    logs = [
        {"ticket_id": "T-5001", "product_category": "Global Heritage", "status": "Closed", "refund_amount": "0.00", "manager_id": "M-0881"},
        {"ticket_id": "T-5002", "product_category": "Basic Essentials", "status": "Closed", "refund_amount": "0", "manager_id": "M-0881"},
        {"ticket_id": "T-5003", "product_category": "GLOBAL HERITAGE", "status": "Closed", "refund_amount": " 0 ", "manager_id": "M-0922"},
        {"ticket_id": "T-5004", "product_category": "Global Heritage", "status": "Closed", "refund_amount": "45.50", "manager_id": "M-1003"},
        {"ticket_id": "T-5005", "product_category": "global heritage", "status": "Open", "refund_amount": "0.00", "manager_id": "M-1044"},
        {"ticket_id": "T-5006", "product_category": "Tech Gadgets", "status": "Closed", "refund_amount": "12.00", "manager_id": "M-0922"}
    ]
    
    with open('store_data/tickets_raw_export.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["ticket_id", "product_category", "status", "refund_amount", "manager_id"])
        writer.writeheader()
        writer.writerows(logs)

if __name__ == "__main__":
    build_env()
