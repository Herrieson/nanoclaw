import os
import json
import csv

def verify():
    state = {
        "processed_dir_exists": False,
        "appointments_csv_exists": False,
        "insurance_txt_exists": False,
        "csv_only_hr_programs": False,
        "csv_correct_row_count": False,
        "csv_is_chronologically_sorted": False,
        "insurance_complaints_accurate": False,
        "no_dmv_or_parks_in_outputs": True
    }

    processed_dir = "processed"
    csv_path = os.path.join(processed_dir, "daily_appointments.csv")
    txt_path = os.path.join(processed_dir, "insurance_complaints.txt")

    if os.path.isdir(processed_dir):
        state["processed_dir_exists"] = True

    if os.path.isfile(csv_path):
        state["appointments_csv_exists"] = True
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                content = f.read()
                
                if "DMV" in content or "Parks" in content:
                    state["no_dmv_or_parks_in_outputs"] = False
                
                f.seek(0)
                reader = list(csv.reader(f))
                
                data_rows = [row for row in reader if "John Doe" in str(row) or "Tom Clark" in str(row) or "Alice Jones" in str(row)]
                if len(data_rows) > 0:
                    state["csv_only_hr_programs"] = True
                
                # Total HR Program entries should be exactly 6 (John, Alice, Eve, Tom, Bob, Gregory)
                hr_names = ["John Doe", "Alice Jones", "Eve Evans", "Tom Clark", "Bob Brown", "Gregory House"]
                found_names = [name for name in hr_names if name in content]
                
                if len(found_names) == 6 and len(reader) in [6, 7]: # 6 rows + optional header
                    state["csv_correct_row_count"] = True
                
                # Check Chronological sorting
                idx_john = content.find("John Doe")       # 08:15 AM
                idx_alice = content.find("Alice Jones")     # 09:30 AM
                idx_eve = content.find("Eve Evans")         # 11:00 AM
                idx_tom = content.find("Tom Clark")         # 12:15 PM
                idx_bob = content.find("Bob Brown")         # 02:00 PM (14:00)
                idx_greg = content.find("Gregory House")    # 04:30 PM (16:30)
                
                if 0 <= idx_john < idx_alice < idx_eve < idx_tom < idx_bob < idx_greg:
                    state["csv_is_chronologically_sorted"] = True
        except Exception:
            pass

    if os.path.isfile(txt_path):
        state["insurance_txt_exists"] = True
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                content = f.read().lower()
                
                # Should contain Alice and Eve, but not John, Bob, Tom, or Greg
                has_alice = "alice jones" in content
                has_eve = "eve evans" in content
                has_others = any(n in content for n in ["john doe", "bob brown", "tom clark", "gregory house", "jane smith"])
                
                if has_alice and has_eve and not has_others:
                    state["insurance_complaints_accurate"] = True
                    
                if "dmv" in content or "parks" in content:
                    state["no_dmv_or_parks_in_outputs"] = False
        except Exception:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
