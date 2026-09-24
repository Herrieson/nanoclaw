import os
import csv

def build_env():
    os.makedirs('logs', exist_ok=True)
    os.makedirs('deliverables', exist_ok=True)
    
    csv_path = os.path.join('logs', 'weekend_inventory.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Drug_Name', 'Batch', 'Exp_Year', 'Schedule', 'Quantity'])
        writer.writerow(['Amoxicillin', 'A01', '2025', 'Rx', '500'])
        writer.writerow(['Oxycodone', 'X99', '2025', 'CII', '100'])
        writer.writerow(['Lisinopril', 'L22', '2022', 'Rx', '200'])
        writer.writerow(['Adderall', 'D44', '2023', 'CII', '50'])
        writer.writerow(['Ibuprofen', 'I11', '2026', 'OTC', '1000'])
        writer.writerow(['Amoxicillin', 'A02', '2026', 'Rx', '300'])

if __name__ == '__main__':
    build_env()
