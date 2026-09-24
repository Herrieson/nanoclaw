import os
import csv

def build_env():
    # Create directory structure
    os.makedirs("case_files/deposition_transcripts", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. Create Master Schedule
    # Cases: Smith v. State, Doe v. City, Roe v. Inc
    master_schedule = [
        ["Date", "Case_Name", "Attorney", "Room"],
        ["2023-10-01", "Smith v. State", "Siobhan O'Malley", "Room 402"],
        ["2023-10-01", "Doe v. City", "Siobhan O'Malley", "Room 101"],
        ["2023-10-02", "Roe v. Inc", "Marcus Thorne", "Room 305"],
        ["2023-10-03", "Smith v. State", "Siobhan O'Malley", "Room 402"]
    ]
    with open("case_files/master_schedule.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(master_schedule)

    # 2. Create Transcripts (The messy logs)
    # Transcript A: Matches Smith v. State 10-01
    with open("case_files/deposition_transcripts/depo_20231001_smith.txt", "w") as f:
        f.write("DEPOSITION TRANSCRIPT\nCase: Smith v. State\nDate: 2023-10-01\nPresent: Siobhan O'Malley, Witness A.\nText: ...")

    # Transcript B: Unauthorized entry (Miller in Smith v. State) - This is the "Paralegal Miller" issue
    with open("case_files/deposition_transcripts/depo_20231002_smith_extra.txt", "w") as f:
        f.write("DEPOSITION TRANSCRIPT\nCase: Smith v. State\nDate: 2023-10-02\nPresent: Paralegal Miller, Witness B.\nNote: Unscheduled session.")

    # Transcript C: Mismatched case (Transcript exists but not in schedule for this date/case)
    with open("case_files/deposition_transcripts/depo_20231002_doe.txt", "w") as f:
        f.write("DEPOSITION TRANSCRIPT\nCase: Doe v. City\nDate: 2023-10-02\nPresent: Siobhan O'Malley.\nText: ...")

    # Missing: 2023-10-02 Roe v. Inc (Scheduled but no transcript)
    # Missing: 2023-10-03 Smith v. State (Scheduled but no transcript)

    # 3. Add some noise/junk files
    with open("case_files/deposition_transcripts/notes.tmp", "w") as f:
        f.write("Coffee stains on page 3.")

if __name__ == "__main__":
    build_env()
