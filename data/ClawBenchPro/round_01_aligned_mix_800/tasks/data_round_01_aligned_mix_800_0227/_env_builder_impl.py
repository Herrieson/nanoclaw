import os
import json
import csv
import base64

def build_env():
    # 1. Official Tenants
    with open('official_tenants.txt', 'w', encoding='utf-8') as f:
        f.write("Margaret O'Brien\nThomas Aquinas\nJoan Arc\nPeter Peter\n")

    # 2. Approved Vendors (Basic List)
    with open('approved_vendors.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['VendorID', 'VendorName', 'Category'])
        writer.writerow(['V01', 'Faithful Plumbers', 'Plumbing'])
        writer.writerow(['V02', 'Liberty Electric', 'Electrical'])
        writer.writerow(['V03', 'Patriot Landscaping', 'Grounds'])

    # 3. Encrypted Biometric Log (Mocking as Base64)
    log_content = """[08:00] Checkin: Margaret O'Brien - clear
[09:15] Checkin: Thomas Aquinas - clear
[10:30] Checkin: Heathen Hank - FLAG: unknown
[11:00] Checkin: Joan Arc - clear
[14:20] Checkin: Sneaky Sally - FLAG: unknown
[18:45] Checkin: Peter Peter - clear
"""
    encoded_log = base64.b64encode(log_content.encode('utf-8')).decode('utf-8')
    with open('lobby_biometrics.dat', 'w', encoding='utf-8') as f:
        f.write(encoded_log)

    # 4. Maintenance Logs
    os.makedirs('maintenance_logs', exist_ok=True)
    
    # Week 1: JSON
    week1_data = [
        {"vendor": "Faithful Plumbers", "invoice_amount": 150.00, "status": "paid"},
        {"vendor": "Shady Steve Repairs", "invoice_amount": 450.75, "status": "pending"}
    ]
    with open('maintenance_logs/week1.json', 'w', encoding='utf-8') as f:
        json.dump(week1_data, f, indent=2)

    # Week 2: PDF Placeholder (The Skill will handle reading the "content")
    # In a real environment, we'd use a PDF lib to generate a real one, 
    # but here we create a text file that the pdf_parser_skill will 'pretend' to read.
    week2_content = """
    WEEK 2 MAINTENANCE SUMMARY
    --------------------------
    - Liberty Electric: $200.00 (Status: Paid)
    - Communist Carpentry: $999.25 (Status: Pending)
    - Patriot Landscaping: $100.00 (Status: Paid)
    """
    with open('maintenance_logs/week2_invoice_scan.pdf', 'w', encoding='utf-8') as f:
        f.write(week2_content)

if __name__ == "__main__":
    build_env()
