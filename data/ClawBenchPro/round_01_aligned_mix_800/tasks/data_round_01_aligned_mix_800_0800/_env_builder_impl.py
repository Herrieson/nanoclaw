import os
import csv

def build_env():
    os.makedirs("field_notes", exist_ok=True)
    os.makedirs("database", exist_ok=True)
    os.makedirs("briefing", exist_ok=True)

    with open("field_notes/shift_log_oct23.txt", "w", encoding="utf-8") as f:
        f.write("Shift Log - Officer Mateo\n")
        f.write("Date: Oct 23\n\n")
        f.write("14:00 - Routine patrol. Stopped to sketch the oak trees near sector 4G.\n")
        f.write("14:15 - Multiple unauthorized vehicles entered the restricted zone.\n")
        f.write("Tapping my foot waiting for dispatch... connection is terrible out here.\n")
        f.write("I managed to jot down these plates from the dirt bikes and lifted trucks:\n")
        f.write("- Blue Ford truck: CA-5GTR222\n")
        f.write("- Rusted Jeep, moving erratically: CA-9FAKE00 (looked like a fake plate anyway)\n")
        f.write("- Black Chevy: CA-1ABC123\n")
        f.write("- No make, moving way too fast: CA-BAD888\n")
        f.write("- White Toyota: CA-8HJK999\n\n")
        f.write("Need to check these against the state registry ASAP.\n")

    valid_plates = ["CA-5GTR222", "CA-1ABC123", "CA-8HJK999", "CA-2XYZ555", "CA-7TYU444"]
    
    with open("database/state_dmv_registry.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["plate_number", "registration_status", "owner_id"])
        for p in valid_plates:
            writer.writerow([p, "VALID", f"ID-{p[-3:]}"])

if __name__ == "__main__":
    build_env()
