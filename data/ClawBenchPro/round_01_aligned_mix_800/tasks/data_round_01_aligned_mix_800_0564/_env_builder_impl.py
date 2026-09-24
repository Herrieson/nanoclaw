import os
import json
import random
import datetime

def build_env():
    # Setup directory structure
    dirs = [
        "archive_recovery/scheduling_backups",
        "archive_recovery/raw_transcripts/cache",
        "archive_recovery/raw_transcripts/temp_recovery",
        "final_drop"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 1. Create fragmented Master Schedules (Noise & Decoys)
    schedules = [
        ("schedule_v1_draft.json", "Preliminary", "2023-01-01"),
        ("schedule_old_backup.json", "Archive", "2023-05-10"),
        ("master_schedule_FINAL_v3.json", "Final Verified Version", "2023-10-20")
    ]
    
    # The Real Schedule Data
    official_events = [
        {"date": "2023-11-01", "case": "Smith v. State", "attorney": "Siobhan O'Malley"},
        {"date": "2023-11-01", "case": "Doe v. City", "attorney": "Siobhan O'Malley"},
        {"date": "2023-11-02", "case": "Roe v. Inc", "attorney": "Marcus Thorne"},
        {"date": "2023-11-03", "case": "Smith v. State", "attorney": "Siobhan O'Malley"},
        {"date": "2023-11-04", "case": "Zeta v. Omega", "attorney": "Marcus Thorne"}
    ]

    for filename, status, date_str in schedules:
        data = {
            "metadata": {"status": status, "updated_at": date_str},
            "entries": official_events if status == "Final Verified Version" else []
        }
        with open(f"archive_recovery/scheduling_backups/{filename}", "w") as f:
            json.dump(data, f)

    # 2. Create Transcripts with heavy noise
    # Valid Transcripts (Matches Schedule)
    valid_sessions = [
        ("2023-11-01", "Smith v. State", "Siobhan O'Malley", "SID-9901"),
        ("2023-11-02", "Roe v. Inc", "Marcus Thorne", "SID-9902")
    ]
    
    # Missing from schedule: 2023-11-01 (Doe), 2023-11-03 (Smith), 2023-11-04 (Zeta)
    
    # Unscheduled (Ghost) Session
    ghost_sessions = [
        ("2023-11-05", "Alpha v. Beta", "Marcus Thorne", "SID-8801")
    ]
    
    # Unauthorized Miller Sessions (In Smith v. State)
    miller_sessions = [
        ("2023-11-06", "Smith v. State", "Paralegal Miller", "SID-7701") # Ghost + Unauthorized
    ]

    all_real_logs = valid_sessions + ghost_sessions + miller_sessions

    # Generate hundreds of noise files
    for i in range(200):
        noise_name = f"tmp_log_{random.getrandbits(32)}.txt"
        target_dir = random.choice(["archive_recovery/raw_transcripts/cache", "archive_recovery/raw_transcripts/temp_recovery"])
        with open(os.path.join(target_dir, noise_name), "w") as f:
            f.write("ERROR: Corrupt data segment " + str(random.random()))

    # Generate actual logs hidden in the mess
    for date, case, lead, sid in all_real_logs:
        # Mix formats: some hex names, some date names
        if random.random() > 0.5:
            fname = f"rec_{sid}_{random.randint(100,999)}.log"
        else:
            fname = f"log_{date.replace('-', '')}.txt"
        
        target_dir = "archive_recovery/raw_transcripts/temp_recovery"
        content = f"""
        --- DEPOSITION RECORD ---
        Verification-Stamp: VERIFIED_AUTH_2023
        Session-ID: {sid}
        Date: {date}
        Case_Title: {case}
        Lead_Interrogator: {lead}
        Transcript_Body: [REDACTED TEXT]
        --------------------------
        """
        with open(os.path.join(target_dir, fname), "w") as f:
            f.write(content)

if __name__ == "__main__":
    build_env()
