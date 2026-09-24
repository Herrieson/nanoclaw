import os
import csv
import random
import string

def random_plate():
    return "CA-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=7))

def build_env():
    # Create directories
    os.makedirs("field_notes", exist_ok=True)
    os.makedirs("database/shards", exist_ok=True)
    os.makedirs("briefing", exist_ok=True)

    random.seed(1709)

    # 1. Generate massive sharded DMV database
    all_dmv_plates = set()
    for i in range(1, 251):
        shard_path = f"database/shards/dmv_shard_{i:03d}.csv"
        with open(shard_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["plate_number", "registration_status", "owner_id", "issue_date"])
            # 200 records per shard = 50,000 total records
            for _ in range(200):
                plate = random_plate()
                status = random.choices(
                    ["VALID", "EXPIRED", "SUSPENDED", "STOLEN", "REVOKED"],
                    weights=[0.7, 0.1, 0.1, 0.05, 0.05],
                    k=1
                )[0]
                writer.writerow([plate, status, f"ID-{random.randint(1000, 9999)}", f"202{random.randint(0,3)}-01-15"])
                all_dmv_plates.add(plate)

    # 2. Inject target plates into a specific shard (so they can be found by diligent agents)
    target_plates_in_db = [
        ("CA-5GTR222", "VALID"),      # Valid -> Should NOT be in the final report
        ("CA-1ABC123", "EXPIRED"),    # Invalid -> SHOULD be in the final report
        ("CA-8HJK999", "VALID"),      # Valid -> Should NOT be in the final report
        ("CA-BAD888", "SUSPENDED"),   # Invalid -> SHOULD be in the final report
        ("CA-NORM111", "VALID")       # Valid, but it's a decoy from a different incident anyway
    ]
    # CA-9FAKE00 will intentionally NOT be added to any shard (Missing -> SHOULD be in report)
    
    with open("database/shards/dmv_shard_088.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for p, s in target_plates_in_db:
            writer.writerow([p, s, f"ID-{random.randint(1000, 9999)}", "2021-05-05"])

    # 3. Generate 30 days of noisy field logs
    for day in range(1, 32):
        file_path = f"field_notes/shift_log_oct{day:02d}.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"Shift Log - Officer Mateo\nDate: Oct {day}\n\n")
            
            if day == 23:
                # The target day with the specific incident
                f.write("08:15 - Coffee at the diner.\n")
                f.write("09:00 - Routine traffic stop on I-5. Speeding. Plate: CA-NORM111. Let them off with a warning.\n") # Decoy
                f.write("11:30 - Responded to a noise complaint downtown. Nothing found.\n")
                f.write("14:00 - Routine patrol. Stopped to sketch the oak trees near sector 4G (north perimeter).\n")
                f.write("14:15 - Multiple unauthorized vehicles entered the restricted zone. Dirt bikes and lifted trucks.\n")
                f.write("Plates involved in the 14:15 incident:\n")
                f.write("- Blue Ford truck: CA-5GTR222\n")
                f.write("- Rusted Jeep, moving erratically: CA-9FAKE00 (looked like a fake plate anyway)\n")
                f.write("- Black Chevy: CA-1ABC123\n")
                f.write("- No make, moving way too fast: CA-BAD888\n")
                f.write("- White Toyota: CA-8HJK999\n\n")
                f.write("Need to check these poachers against the state registry ASAP.\n")
                f.write("16:00 - Shift end.\n")
            else:
                # Noise for other days
                f.write("Routine patrol. Weather was fine.\n")
                f.write("Handed out a few parking tickets today.\n")
                for _ in range(random.randint(2, 6)):
                    f.write(f"- Ticketed parked vehicle: {random_plate()}\n")
                f.write("End of shift.\n")

if __name__ == "__main__":
    build_env()
