import os
import json
import csv

def build_env():
    # Write official tenants
    with open('official_tenants.txt', 'w', encoding='utf-8') as f:
        f.write("Margaret O'Brien\nThomas Aquinas\nJoan Arc\nPeter Peter\n")

    # Write approved vendors
    with open('approved_vendors.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['VendorID', 'VendorName', 'Category'])
        writer.writerow(['V01', 'Faithful Plumbers', 'Plumbing'])
        writer.writerow(['V02', 'Liberty Electric', 'Electrical'])
        writer.writerow(['V03', 'Patriot Landscaping', 'Grounds'])

    # Write tenant checkins log
    log_content = """[08:00] Checkin: Margaret O'Brien - clear
[09:15] Checkin: Thomas Aquinas - clear
[10:30] Checkin: Heathen Hank - FLAG: unknown
[11:00] Checkin: Joan Arc - clear
[14:20] Checkin: Sneaky Sally - FLAG: unknown
[18:45] Checkin: Peter Peter - clear
"""
    with open('tenant_checkins.log', 'w', encoding='utf-8') as f:
        f.write(log_content)

    # Create maintenance logs directory and files
    os.makedirs('maintenance_logs', exist_ok=True)

    week1_data = [
        {"vendor": "Faithful Plumbers", "invoice_amount": 150.00, "status": "paid"},
        {"vendor": "Shady Steve Repairs", "invoice_amount": 450.75, "status": "pending"}
    ]
    with open('maintenance_logs/week1.json', 'w', encoding='utf-8') as f:
        json.dump(week1_data, f, indent=2)

    week2_data = [
        {"vendor": "Liberty Electric", "invoice_amount": 200.00, "status": "paid"},
        {"vendor": "Communist Carpentry", "invoice_amount": 999.25, "status": "pending"},
        {"vendor": "Patriot Landscaping", "invoice_amount": 100.00, "status": "paid"}
    ]
    with open('maintenance_logs/week2.json', 'w', encoding='utf-8') as f:
        json.dump(week2_data, f, indent=2)

if __name__ == "__main__":
    build_env()
