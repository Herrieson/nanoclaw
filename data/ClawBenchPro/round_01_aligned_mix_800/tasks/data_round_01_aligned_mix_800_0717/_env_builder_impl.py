import os
import csv

def build_env():
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

    # 3. Messy records - File 2: An email dump
    email_path = os.path.join("messy_records", "fw_shift_updates.txt")
    with open(email_path, "w", encoding="utf-8") as f:
        f.write(
            "From: Nurse Sarah\n"
            "To: Dr. Tariq\n"
            "Subject: RE: Hours and that patient\n\n"
            "Hi Tariq!\n"
            "Just logging my hours, I did 5 hours on Tuesday. Also Dr. Chen did 10 hours in Pediatrics.\n"
            "Oh, and before I forget, that patient who makes Ouds (the luthier you wanted to help with his hand surgery) "
            "left his direct line with me at the front desk: 555-0199-OUD. He said to call anytime.\n"
            "Talk soon, try not to stress too much!\n"
        )

    # 4. Messy records - File 3: Tariq's disorganized personal notes
    notes_path = os.path.join("messy_records", "tariq_scratchpad.log")
    with open(notes_path, "w", encoding="utf-8") as f:
        f.write(
            "10:00 AM - Meditated for 30 mins. Still anxious about the board meeting.\n"
            "10:30 AM - Need to practice the Maqam Rast on the oud tonight.\n"
            "11:00 AM - Paramedic Joe worked 15 hours this week, need to remember that.\n"
            "11:15 AM - I think someone named 'John Doe' worked 2 hours but he's not on the approved list.\n"
            "12:00 PM - Dr. Adams did another 4 hours this morning.\n"
            "12:30 PM - Why am I so disorganized?? Need more tea.\n"
        )

if __name__ == "__main__":
    build_env()
