import os
import csv
import base64

def build_env():
    # Create the messy directory
    mess_dir = "clinic_mess"
    os.makedirs(mess_dir, exist_ok=True)

    # File 1: Standard CSV
    csv_data = [
        ["Patient_ID", "Medication", "Dose_mg", "Qty_Dispensed"],
        ["P-001", "Lisinopril", "10", "30"],
        ["P-002", "Amoxicillin", "50", "20"],
        ["P-114", "Amoxicillin", "250", "14"], # ANOMALY
        ["P-004", "Metformin", "500", "60"]
    ]
    with open(os.path.join(mess_dir, "saturday_morning_log.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

    # File 2: Messy TXT with pipe separators -> Converted to proprietary .medlog
    txt_data = """pat_id|drug_name|dosage|amount_given
P-005|Metformin|500|60
P-006|Atorvastatin|20|30
P-902|Amoxicillin|500|10
P-008|Lisinopril|20|60
P-009|Amoxicillin|100|30
"""
    # Base64 encode to simulate an unreadable format requiring the skill tool
    encoded_data = base64.b64encode(txt_data.encode("utf-8")).decode("utf-8")
    with open(os.path.join(mess_dir, "sunday_notes_v2_final.medlog"), "w") as f:
        f.write(encoded_data)

    # File 3: Incomplete/Noise data
    noise_data = "PatientID,Med,Dose,Qty\nXYZ-99,Ibuprofen,400,100\n"
    with open(os.path.join(mess_dir, "dont_forget.csv"), "w") as f:
        f.write(noise_data)

if __name__ == "__main__":
    build_env()
