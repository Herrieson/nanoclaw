import os
import csv

def build_env():
    base_dir = "assets/data_361"
    os.makedirs(base_dir, exist_ok=True)
    
    # 模拟客户数据：其中只有部分客户拥有 Adventure Package 并在 2023-10 续保
    clients = [
        {"First_Name": "John", "Last_Name": "Doe", "Email": "john@example.com", "Policy_Type": "Auto", "Renewal_Date": "2023-10-12", "Current_Premium": "500"},
        {"First_Name": "Alice", "Last_Name": "Smith", "Email": "alice@example.com", "Policy_Type": "Adventure Package", "Renewal_Date": "2023-10-05", "Current_Premium": "1200"},
        {"First_Name": "Bob", "Last_Name": "Johnson", "Email": "bob@example.com", "Policy_Type": "Family Package", "Renewal_Date": "2023-11-01", "Current_Premium": "1500"},
        {"First_Name": "Carol", "Last_Name": "Williams", "Email": "carol@example.com", "Policy_Type": "Adventure Package", "Renewal_Date": "2023-10-20", "Current_Premium": "900"},
        {"First_Name": "Dave", "Last_Name": "Brown", "Email": "dave@example.com", "Policy_Type": "Adventure Package", "Renewal_Date": "2023-09-15", "Current_Premium": "1000"},
        {"First_Name": "Eve", "Last_Name": "Davis", "Email": "eve@example.com", "Policy_Type": "Adventure Package", "Renewal_Date": "2023-10-25", "Current_Premium": "1100"},
        {"First_Name": "Frank", "Last_Name": "Miller", "Email": "frank@example.com", "Policy_Type": "Home", "Renewal_Date": "2023-10-10", "Current_Premium": "800"},
        {"First_Name": "Grace", "Last_Name": "Wilson", "Email": "grace@example.com", "Policy_Type": "Adventure Package", "Renewal_Date": "2023-10-31", "Current_Premium": "1300"},
        {"First_Name": "Heidi", "Last_Name": "Moore", "Email": "heidi@example.com", "Policy_Type": "Adventure Package", "Renewal_Date": "2024-10-05", "Current_Premium": "1200"},
        {"First_Name": "Ivan", "Last_Name": "Taylor", "Email": "ivan@example.com", "Policy_Type": "Adventure Package", "Renewal_Date": "2023-10-01", "Current_Premium": "850"}
    ]
    
    csv_path = os.path.join(base_dir, "clients.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["First_Name", "Last_Name", "Email", "Policy_Type", "Renewal_Date", "Current_Premium"])
        writer.writeheader()
        for c in clients:
            writer.writerow(c)

if __name__ == "__main__":
    build_env()
