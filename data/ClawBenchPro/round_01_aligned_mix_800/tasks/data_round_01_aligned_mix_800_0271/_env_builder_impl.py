import os
import csv

def build_env():
    # Create the target directory
    os.makedirs("field_trip_logs", exist_ok=True)
    
    # 1. Official Roster as PDF (Mocked as text file for simplicity but named .pdf)
    # In a real env, we'd use FPDF, but here we provide a text-readable PDF or use simple content
    roster_content = [
        "Student ID,Full Name,Grade",
        "S001,Alice Johnson,8",
        "S002,Bob Smith,8",
        "S003,Charlie Brown,8",
        "S004,Daisy Miller,8",
        "S005,Ethan Hunt,8",
        "S006,Fiona Gallagher,8",
        "S007,George Costanza,8",
        "S008,Hannah Abbott,8"
    ]
    with open("field_trip_logs/official_roster.pdf", "w") as f:
        f.write("\n".join(roster_content))

    # 2. Response Batch 1 (CSV)
    batch_1 = [
        ["name", "status", "package", "base_fee"],
        ["Alice Johnson", "Paid", "Standard", "500"],
        ["Bob Smith", "Paid", "Premium", "600"], 
        ["Zoe Saldana", "Paid", "Standard", "500"], # Interloper 1
    ]
    with open("field_trip_logs/response_batch_1.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(batch_1)
        
    # 3. Scanned Response Batch 2 (Placeholder for OCR)
    # The actual content is hidden; the OCR skill will return the real data.
    with open("field_trip_logs/scanned_responses_batch_2.jpg", "wb") as f:
        f.write(b"FAKE_IMAGE_DATA_FOR_OCR")

    # Logic Reference for Verify:
    # Valid & Paid: 
    # Alice (Batch 1, Standard, 500) -> 0% fund (if tool says so)
    # Bob (Batch 1, Premium, 600) -> 10% fund = 60
    # Charlie (OCR, Standard, 500) -> 0% fund
    # Daisy (OCR, Premium, 600) -> 10% fund = 60
    # Fiona (OCR, Premium, 700) -> 10% fund = 70
    # Interlopers: Zoe Saldana, Jack Sparrow
    # Total Fund: 60 + 60 + 70 = 190 (Assuming Tool says Premium=10%, Standard=0%)

if __name__ == "__main__":
    build_env()
