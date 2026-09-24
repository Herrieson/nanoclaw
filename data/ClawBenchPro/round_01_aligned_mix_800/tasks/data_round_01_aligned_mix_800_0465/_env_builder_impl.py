import os
import csv
import json
import random

def build_env():
    # 1. Create directory structure
    dirs = [
        "state_db/rosters",
        "state_db/profiles",
        "desk_report"
    ]
    
    for day in range(27, 31):
        for dist in range(1, 6):
            dirs.append(f"dispatch_archives/2023/10/{day}/district_{dist}")
            
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 2. Build the fragmented Watchlist Rosters (Noise & Targets)
    # The decoy roster (Morning)
    with open("state_db/rosters/roster_2023-10-27_0800.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Offender_ID", "Status"])
        writer.writerows([["0105", "ACTIVE"], ["0312", "ACTIVE"], ["0789", "ACTIVE"], ["0888", "ACTIVE"]])
        
    # The TARGET roster (Friday 17:00) - Notice 0789 (Miguel) is missing/inactive here!
    with open("state_db/rosters/roster_2023-10-27_1700.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Offender_ID", "Status"])
        writer.writerows([
            ["0105", "ACTIVE"], # Carlos (Target)
            ["0312", "ACTIVE"], # Sarah (Target)
            ["0555", "ACTIVE"], # Jimmy (Decoy - wrong crime)
            ["0888", "ACTIVE"], # Elena (Decoy - wrong date)
            ["0999", "ACTIVE"], # Bob (Target)
            ["0789", "INACTIVE"]# Miguel (Decoy - inactive on correct roster)
        ])
        
    # A corrupted weekend roster
    with open("state_db/rosters/roster_2023-10-28_0800.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Offender_ID", "Status"])
        writer.writerows([["GHOST_DATA", "ERR"], ["0999", "ACTIVE"]])

    # 3. Build Profiles (Hundreds of scattered JSONs to enforce scale/scripting)
    target_profiles = {
        "0105": "Carlos Mendez",
        "0312": "Sarah Smith",
        "0555": "Jimmy O'Connor",
        "0789": "Miguel Santos",
        "0888": "Elena Rostova",
        "0999": "Bob Builder"
    }
    
    # Generate 500 noise profiles
    random.seed(42)
    for i in range(1000, 1500):
        _id = str(i)
        with open(f"state_db/profiles/{_id}.json", "w") as f:
            json.dump({"id": _id, "name": f"Unknown_{i}", "risk": random.choice(["Low", "Med", "High"])}, f)
            
    # Write target profiles
    for _id, name in target_profiles.items():
        with open(f"state_db/profiles/{_id}.json", "w") as f:
            json.dump({"id": _id, "name": name, "risk": "High"}, f)

    # 4. Build Dispatch Logs (Messy, semi-structured text)
    def generate_log_block(incident_id, timestamp, code, desc, sub_id, sub_name, remarks):
        return f"""
=========================================
INCIDENT REPORT #{incident_id}
TIMESTAMP: {timestamp}
OFFICER_REMARKS: {remarks}
CODE: {code} - {desc}
INVOLVED_SUBJECT_ID: {sub_id}
INVOLVED_SUBJECT_NAME: {sub_name}
=========================================
"""

    def write_shift_log(path, blocks):
        with open(path, "w") as f:
            f.write(">>> DISPATCH SYSTEM AUTO-LOG <<<\n")
            # add random noise logs
            for _ in range(random.randint(5, 15)):
                f.write(generate_log_block(
                    random.randint(10000, 99999),
                    "2023-10-XX XX:XX:XX",
                    random.choice(["112", "999", "505"]),
                    "Routine",
                    "UNKNOWN",
                    "N/A",
                    "All clear."
                ))
            for b in blocks:
                f.write(b)
                
    # Place target & decoy events
    # Carlos: Target (Sat, Code 415)
    b_carlos = generate_log_block("88101", "2023-10-28 22:15:00", "415", "Noise Complaint", "0105", "Carlos Mendez", "Loud music.")
    write_shift_log("dispatch_archives/2023/10/28/district_2/shift_evening.log", [b_carlos])

    # Sarah: Target (Sun, Code 332)
    b_sarah = generate_log_block("88202", "2023-10-29 09:30:00", "332", "Illegal Dumping", "0312", "Sarah Smith", "Dumped tires near river.")
    write_shift_log("dispatch_archives/2023/10/29/district_4/shift_morning.log", [b_sarah])

    # Bob: Target (Sat, Code 332)
    b_bob = generate_log_block("88303", "2023-10-28 14:20:00", "332", "Illegal Dumping", "0999", "Bob Builder", "Construction waste dumping.")
    write_shift_log("dispatch_archives/2023/10/28/district_5/shift_morning.log", [b_bob])

    # Jimmy: Decoy (Sat, Code 211 - Robbery, wrong crime)
    b_jimmy = generate_log_block("88404", "2023-10-28 01:10:00", "211", "Robbery", "0555", "Jimmy O'Connor", "Stole goods.")
    write_shift_log("dispatch_archives/2023/10/28/district_1/shift_night.log", [b_jimmy])

    # Miguel: Decoy (Sun, Code 415 - correct crime/date, but INACTIVE on the 17:00 roster)
    b_miguel = generate_log_block("88505", "2023-10-29 23:45:00", "415", "Noise Complaint", "0789", "Miguel Santos", "Party.")
    write_shift_log("dispatch_archives/2023/10/29/district_3/shift_night.log", [b_miguel])

    # Elena: Decoy (Friday, Code 415 - correct crime/roster, but WRONG DATE)
    b_elena = generate_log_block("88606", "2023-10-27 20:00:00", "415", "Noise Complaint", "0888", "Elena Rostova", "Screaming.")
    write_shift_log("dispatch_archives/2023/10/27/district_2/shift_night.log", [b_elena])

    # Fill remaining dirs with pure noise files
    for day in range(27, 31):
        for dist in range(1, 6):
            target_path = f"dispatch_archives/2023/10/{day}/district_{dist}/shift_morning.log"
            if not os.path.exists(target_path):
                write_shift_log(target_path, [])

if __name__ == "__main__":
    build_env()
