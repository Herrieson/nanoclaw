import os
import json
import csv

def build_env():
    # Create the data directory
    os.makedirs("pharmacy_data", exist_ok=True)
    
    # 1. Start of month counts (JSON)
    # Mapping:
    # Amoxicillin: NDC-001
    # Oxycodone: NDC-002
    # Lisinopril: NDC-003
    # Adderall: NDC-004
    # Diazepam: NDC-005
    # Ibuprofen: NDC-006
    start_counts = {
        "Amoxicillin": 1500,
        "Oxycodone": 200,
        "Lisinopril": 800,
        "Adderall": 300,
        "Diazepam": 150,
        "Ibuprofen": 2000
    }
    with open("pharmacy_data/start_of_month.json", "w") as f:
        json.dump(start_counts, f, indent=4)
        
    # 2. System Dispensed logs (CSV)
    dispensed_data = [
        ["drug_name", "ndc_code", "quantity_dispensed"],
        ["Amoxicillin", "NDC-001", 450],
        ["Oxycodone", "NDC-002", 80],
        ["Lisinopril", "NDC-003", 200],
        ["Adderall", "NDC-004", 110],
        ["Diazepam", "NDC-005", 40],
        ["Ibuprofen", "NDC-006", 800]
    ]
    with open("pharmacy_data/system_dispensed.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(dispensed_data)
        
    # 3. Physical Counts (PDF)
    # We simulate a PDF by writing a text file that the Agent must use a tool to "parse" 
    # Or in this case, we use a mock PDF parser skill.
    # Logic:
    # Amoxicillin (NDC-001): 1500-450 = 1050. Actual 1050 (OK)
    # Oxycodone (NDC-002): 200-80 = 120. Actual 115 (Deficit 5)
    # Adderall (NDC-004): 300-110 = 190. Actual 180 (Deficit 10)
    
    physical_content = (
        "PHYSICAL INVENTORY TALLY SHEET\n"
        "LOCATION: REAR VAULT\n"
        "------------------------------\n"
        "NDC-001: 1050\n"
        "NDC-002: 115\n"
        "NDC-003: 600\n"
        "NDC-004: 180\n"
        "NDC-005: 110\n"
        "NDC-006: 1200\n"
        "------------------------------\n"
        "Counted by: Admin"
    )
    
    # We save it as a file named .pdf, but it's text-based to ensure the Agent uses the PDF skill
    with open("pharmacy_data/physical_counts.pdf", "w") as f:
        f.write(physical_content)

if __name__ == "__main__":
    build_env()
