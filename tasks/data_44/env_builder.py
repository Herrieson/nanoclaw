import os
import shutil

def build_env():
    base_dir = "assets/data_44"
    reg_dir = os.path.join(base_dir, "registrations")
    
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(reg_dir)

    # 1. Valid - Not urgent
    # 2. Urgent - BP Systolic > 140
    # 3. Urgent - BP Diastolic > 90
    # 4. Urgent - HR > 100
    # 5. Corrupted data (Missing HR, invalid BP)
    # 6. Valid - Borderline not urgent (140/90, HR 100)
    
    logs = [
        # Safe
        "System init...\n[INFO] REGISTRATION: Name: Alice Smith | Age: 45 | BP: 120/80 | HR: 75 | Phone: 555-0101\nDone.",
        # Urgent Systolic
        "Warning: low battery\n[INFO] REGISTRATION: Name: Bob Johnson | Age: 62 | BP: 145/85 | HR: 80 | Phone: 555-0102\nNetwork error.",
        # Urgent Diastolic
        "[INFO] REGISTRATION: Name: Charlie Nguyen | Age: 34 | BP: 135/95 | HR: 90 | Phone: 555-0103\n",
        # Urgent HR
        "[INFO] REGISTRATION: Name: Diana Prince | Age: 29 | BP: 110/70 | HR: 105 | Phone: 555-0104\n",
        # Corrupt / Missing
        "[INFO] REGISTRATION: Name: Edward Elric | Age: N/A | BP: ERROR | HR: N/A | Phone: None\n",
        # Borderline (Not strictly over, so Safe)
        "[INFO] REGISTRATION: Name: Fiona Gallagher | Age: 50 | BP: 140/90 | HR: 100 | Phone: 555-0106\n",
        # Safe with spaces
        "[INFO] REGISTRATION: Name: George Clark | Age: 40 | BP: 115 / 75 | HR: 60 | Phone: 555-0107\n",
        # Urgent Both BP and HR
        "[INFO] REGISTRATION: Name: Hannah Abbott | Age: 71 | BP: 160/100 | HR: 110 | Phone: 555-0108\n",
        # Safe
        "[INFO] REGISTRATION: Name: Ian Malcolm | Age: 55 | BP: 139/89 | HR: 99 | Phone: 555-0109\n",
        # Urgent Diastolic with weird spacing
        "[INFO] REGISTRATION: Name: Jane Doe | Age: 33 | BP: 125 /92 | HR: 85 | Phone: 555-0110\n"
    ]

    for i, log_content in enumerate(logs):
        file_path = os.path.join(reg_dir, f"server_log_{i:03d}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(log_content)

if __name__ == "__main__":
    build_env()
