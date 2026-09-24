import os
import csv
import subprocess
import sys

def install_dependencies():
    # Ensure dependencies for the Mock LLM skills are installed
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openai", "httpx", "-q"])

def build_env():
    install_dependencies()

    # Create directories
    os.makedirs("messy_records", exist_ok=True)
    os.makedirs("board_submission", exist_ok=True)

    # 1. Approved staff list
    with open("approved_staff.txt", "w", encoding="utf-8") as f:
        f.write("Dr. Adams\nNurse Sarah\nDr. Chen\nParamedic Joe\n")

    # 2. Messy records - File 1: A standard-ish CSV but with fake names
    csv_path = os.path.join("messy_records", "week1_export.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Shift Date", "Hours Worked", "Notes"])
        writer.writerow(["Dr. Adams", "2023-10-01", "12", "ER duty"])
        writer.writerow(["Fake Volunteer", "2023-10-02", "5", "Not approved!"])
        writer.writerow(["Nurse Sarah", "2023-10-03", "8", "Triage"])
        writer.writerow(["Random Guy", "2023-10-03", "3", "Just walked in"])

    # 3. Messy records - File 2: An email dump (Now contains Patient ID instead of phone number)
    email_path = os.path.join("messy_records", "fw_shift_updates.txt")
    with open(email_path, "w", encoding="utf-8") as f:
        f.write(
            "From: Nurse Sarah\n"
            "To: Dr. Tariq\n"
            "Subject: RE: Hours and that patient\n\n"
            "Hi Tariq!\n"
            "Just logging my hours, I did 5 hours on Tuesday. Also Dr. Chen did 10 hours in Pediatrics.\n"
            "Oh, and before I forget, that patient who makes Ouds (the luthier you wanted to help with his hand surgery). "
            "I couldn't write down his number, but I registered him in the system. His Patient ID is EGY-882-OUD. "
            "You can pull his phone number from the EMR system using that ID.\n"
            "Talk soon, try not to stress too much!\n"
        )

    # 4. Messy records - File 3: Tariq's disorganized personal notes downgraded to a mock PDF
    pdf_path = os.path.join("messy_records", "tariq_scratchpad.pdf")
    with open(pdf_path, "wb") as f:
        # Create a dummy PDF file that cannot be read as plain text without the specific tool
        f.write(b"%PDF-1.4\n")
        f.write(b"%\xE2\xE3\xCF\xD3\n")
        f.write(b"1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n")
        f.write(b"% This is a scanned document of Dr. Tariq's scratchpad. \n")
        f.write(b"% An OCR tool is required to extract the text.\n")
        f.write(b"%%EOF\n")

if __name__ == "__main__":
    build_env()
