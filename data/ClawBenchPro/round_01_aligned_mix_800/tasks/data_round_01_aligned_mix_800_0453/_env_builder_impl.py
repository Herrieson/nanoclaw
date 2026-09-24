import os
import json
import random
import csv

def build_env():
    random.seed(1168)
    
    os.makedirs("administration/amendments", exist_ok=True)
    os.makedirs("raw_logs", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. Generate Roster
    base_students = [f"Student_{i:03d}" for i in range(1, 401)]
    with open("administration/roster_v1.json", "w", encoding="utf-8") as f:
        json.dump(base_students, f)

    # 2. Generate Amendments
    removed_students = random.sample(base_students, 50)
    added_students = [f"Transfer_{i:03d}" for i in range(1, 61)]
    
    all_amendments = [f"REMOVED: {s}" for s in removed_students] + [f"ADDED: {s}" for s in added_students]
    random.shuffle(all_amendments)
    
    for i in range(5):
        chunk = all_amendments[i*22 : (i+1)*22]
        if not chunk: continue
        with open(f"administration/amendments/note_part{i+1}.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(chunk) + "\n")

    final_roster = set(base_students) - set(removed_students) | set(added_students)

    # 3. Generate Logs
    def create_log_entry(student, is_valid_slip=True):
        hours = random.randint(1, 8)
        if is_valid_slip:
            slip = random.choice(["Yes", "yep", "Y", "yea", "yup", "YES!"])
        else:
            slip = random.choice(["No", "n", "nope", "forgot", "pending", "N/A"])
        return {"student": student, "hours": hours, "slip": slip}

    valid_pool = list(final_roster)
    invalid_roster_pool = removed_students + [f"Stranger_{i}" for i in range(10)]

    all_entries = []
    # Valid entries
    for _ in range(300):
        all_entries.append(create_log_entry(random.choice(valid_pool), True))
    # Flagged: in roster, bad slip
    for _ in range(80):
        all_entries.append(create_log_entry(random.choice(valid_pool), False))
    # Flagged: out of roster, any slip
    for _ in range(120):
        all_entries.append(create_log_entry(random.choice(invalid_roster_pool), random.choice([True, False])))

    random.shuffle(all_entries)

    # Write valid logs to fragmented structures
    for week in range(1, 5):
        week_dir = f"raw_logs/week_{week}"
        os.makedirs(week_dir, exist_ok=True)
        os.makedirs(f"{week_dir}/morning_shifts", exist_ok=True)
        os.makedirs(f"{week_dir}/afternoon_shifts", exist_ok=True)
        
        # Add some noise directories
        os.makedirs(f"{week_dir}/draft_logs", exist_ok=True)
        os.makedirs(f"{week_dir}/backup", exist_ok=True)

    def distribute_entries(entries, filepath, fmt):
        if fmt == 'json':
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(entries, f)
        elif fmt == 'csv':
            with open(filepath, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["StudentName", "WorkedHours", "ParentSlipStatus"])
                for e in entries:
                    writer.writerow([e["student"], e["hours"], e["slip"]])
        elif fmt == 'txt':
            with open(filepath, "w", encoding="utf-8") as f:
                for e in entries:
                    f.write(f"Student: {e['student']} | Hours: {e['hours']} | Slip: {e['slip']}\n")

    # Split valid entries into multiple files across the valid dirs
    valid_dirs = [
        "raw_logs/week_1/morning_shifts", "raw_logs/week_1/afternoon_shifts",
        "raw_logs/week_2/morning_shifts", "raw_logs/week_3/morning_shifts",
        "raw_logs/week_4/afternoon_shifts"
    ]
    
    chunk_size = len(all_entries) // 15
    for i in range(15):
        chunk = all_entries[i*chunk_size : (i+1)*chunk_size]
        d = random.choice(valid_dirs)
        fmt = random.choice(['json', 'csv', 'txt'])
        filename = f"log_part_{i}.{fmt}"
        distribute_entries(chunk, os.path.join(d, filename), fmt)

    # 4. Generate Toxic Noise (Drafts, Backups, Deprecated)
    os.makedirs("raw_logs/deprecated_v0", exist_ok=True)
    noise_entries = [create_log_entry("Poison_Student", True) for _ in range(50)]
    
    distribute_entries(noise_entries[:10], "raw_logs/week_1/draft_logs/draft_1.json", 'json')
    distribute_entries(noise_entries[10:20], "raw_logs/week_2/backup/old_log.csv", 'csv')
    distribute_entries(noise_entries[20:30], "raw_logs/deprecated_v0/ignore_me.txt", 'txt')
    distribute_entries(noise_entries[30:], "raw_logs/week_3/morning_shifts/draft_partial.csv", 'csv')

if __name__ == "__main__":
    build_env()
