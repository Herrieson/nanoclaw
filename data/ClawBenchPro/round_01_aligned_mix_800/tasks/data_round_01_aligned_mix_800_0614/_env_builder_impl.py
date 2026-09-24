import os
import csv
import json

def build_env():
    os.makedirs('store_data', exist_ok=True)
    
    # Manager mapping
    managers = {
        "M-0881": {"name": "Marcus Vance", "region": "South"},
        "M-0922": {"name": "Sarah Jenkins", "region": "Midwest"},
        "M-1003": {"name": "David Kim", "region": "West"},
        "M-1044": {"name": "Chloe Adams", "region": "East"}
    }
    
    with open('store_data/managers.json', 'w', encoding='utf-8') as f:
        json.dump(managers, f, indent=4)

    # Dirty complaint logs
    logs = [
        {"ticket_id": "T-5001", "product_category": "Global Heritage", "status": "Closed", "refund_amount": "0.00", "manager_id": "M-0881", "customer_complaint": "The artisan carving was completely fake plastic. Furious. No one helped me."},
        {"ticket_id": "T-5002", "product_category": "Basic Essentials", "status": "Closed", "refund_amount": "0", "manager_id": "M-0881", "customer_complaint": "T-shirt shrank after one wash."},
        {"ticket_id": "T-5003", "product_category": "GLOBAL HERITAGE", "status": "Closed", "refund_amount": " 0 ", "manager_id": "M-0922", "customer_complaint": "Received a broken ceramic bowl. Customer service hung up on me."},
        {"ticket_id": "T-5004", "product_category": "Global Heritage", "status": "Closed", "refund_amount": "45.50", "manager_id": "M-1003", "customer_complaint": "Missing the woven basket from my order. (Refund issued)"},
        {"ticket_id": "T-5005", "product_category": "global heritage", "status": "Open", "refund_amount": "0.00", "manager_id": "M-1044", "customer_complaint": "Still waiting for someone to respond about the damaged tapestry."},
        {"ticket_id": "T-5006", "product_category": "Tech Gadgets", "status": "Closed", "refund_amount": "12.00", "manager_id": "M-0922", "customer_complaint": "Cable frayed."}
    ]
    
    with open('store_data/tickets_raw_export.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["ticket_id", "product_category", "status", "refund_amount", "manager_id", "customer_complaint"])
        writer.writeheader()
        writer.writerows(logs)

if __name__ == "__main__":
    build_env()
