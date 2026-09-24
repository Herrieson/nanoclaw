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

    # 2. Create Transcripts in .cad (Proprietary format, mocked as unreadable bytes/text)
    # The actual readable text is stored in the tool's mapping.
    
    # Transcript A: Matches Smith v. State 10-01
    with open("case_files/deposition_transcripts/depo_20231001_smith.cad", "wb") as f:
        f.write(b"\x00\x01CAD_FORMAT_V2\xFF\xAA\xBB\xCC\xDD_ENCRYPTED_AUDIO_STREAM_001")

    # Transcript B: Unauthorized entry (Miller in Smith v. State) 
    with open("case_files/deposition_transcripts/depo_20231002_smith_extra.cad", "wb") as f:
        f.write(b"\x00\x01CAD_FORMAT_V2\xFF\xAA\xBB\xCC\xDD_ENCRYPTED_AUDIO_STREAM_002")

    # Transcript C: Mismatched case (Transcript exists but not in schedule for this date/case)
    with open("case_files/deposition_transcripts/depo_20231002_doe.cad", "wb") as f:
        f.write(b"\x00\x01CAD_FORMAT_V2\xFF\xAA\xBB\xCC\xDD_ENCRYPTED_AUDIO_STREAM_003")

    # Missing: 2023-10-02 Roe v. Inc (Scheduled but no transcript)
    # Missing: 2023-10-03 Smith v. State (Scheduled but no transcript)

    # 3. Add some noise/junk files
    with open("case_files/deposition_transcripts/notes.tmp", "w") as f:
        f.write("Coffee stains on page 3. The scanner is broken again.")

if __name__ == "__main__":
    build_env()
