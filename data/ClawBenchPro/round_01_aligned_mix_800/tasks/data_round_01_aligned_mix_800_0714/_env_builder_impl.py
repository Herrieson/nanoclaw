import os
import csv
import json

def build_env():
    # Create necessary directories
    os.makedirs("support_tickets", exist_ok=True)
    
    # Generate support tickets
    tickets = [
        {"id": "ticket_01", "order_id": "ORD-110", "customer": "Isabella Cortez", "content": "This is ridiculous! Where is my package? I want my money back immediately. Give me a refund!"},
        {"id": "ticket_02", "order_id": "ORD-111", "customer": "Mike Johnson", "content": "Tracking hasn't updated. I know there's a storm, but I'm getting annoyed. Please check on this."},
        {"id": "ticket_03", "order_id": "ORD-112", "customer": "Chloe Smith", "content": "I am traveling soon and need this. If it doesn't arrive by tomorrow, I expect a full refund."},
        {"id": "ticket_04", "order_id": "ORD-113", "customer": "David Kim", "content": "Can I cancel and get a refund? It's taking way too long."},
        {"id": "ticket_05", "order_id": "ORD-114", "customer": "Sophia Rodriguez", "content": "The box arrived crushed! I demand a refund."}
    ]
    
    for ticket in tickets:
        file_path = os.path.join("support_tickets", f"{ticket['id']}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"Order: {ticket['order_id']}\nCustomer: {ticket['customer']}\nMessage: {ticket['content']}\n")
            
    # Generate shipping logs
    shipping_data = [
        ["order_number", "destination", "delay_days"],
        ["ORD-110", "Texas", "5"],  # Requested refund + delayed > 3 -> Yes
        ["ORD-111", "California", "4"], # Delayed > 3 but no refund requested -> No
        ["ORD-112", "Florida", "2"], # Requested refund but delayed <= 3 -> No
        ["ORD-113", "New York", "6"], # Requested refund + delayed > 3 -> Yes
        ["ORD-114", "Nevada", "0"] # Not delayed (arrived), although refund requested -> No
    ]
    
    with open("shipping_logs.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(shipping_data)

if __name__ == "__main__":
    build_env()
