import os
import csv
import json

def build_env():
    # Create the class roster
    roster_students = ["Emma", "Liam", "Noah", "Olivia", "Ava"]
    with open("class_roster.txt", "w") as f:
        f.write("AP Environmental Science - Fall Roster\n")
        f.write("--------------------------------------\n")
        for student in roster_students:
            f.write(f"- {student}\n")
            
    # Create submissions directory
    os.makedirs("submissions", exist_ok=True)
    
    # 1. Emma (CSV)
    with open("submissions/emma_log.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Category", "Weight_lbs"])
        writer.writerow(["Recycling", 10])
        writer.writerow(["Compost", 5])
        writer.writerow(["Landfill", 2])

    # 2. Liam (JSON)
    with open("submissions/liam.json", "w") as f:
        json.dump({
            "student": "Liam",
            "waste_data": {
                "recycling": 8,
                "compost": 2,
                "landfill": 5
            }
        }, f, indent=2)

    # 3. Noah (TXT - Unstructured but parseable)
    with open("submissions/noah_data.txt", "w") as f:
        f.write("Hey Mrs. O'Connor, sorry this is late. Here is my waste log for the week:\n")
        f.write("Recycling: 5 lbs\n")
        f.write("Compost: 3 lbs\n")
        f.write("Landfill: 4 lbs\n")
        f.write("I promise I'll use the CSV template next time.\n")

    # 4. Olivia (CSV)
    with open("submissions/olivia.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Category", "Weight_lbs"])
        writer.writerow(["Recycling", 12])
        writer.writerow(["Compost", 6])
        writer.writerow(["Landfill", 1])

    # 5. Ava (CSV)
    with open("submissions/ava.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Category", "Weight_lbs"])
        writer.writerow(["Recycling", 7])
        writer.writerow(["Compost", 4])
        writer.writerow(["Landfill", 3])

    # 6. Mason (Intruder - CSV)
    with open("submissions/mason_guest.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Category", "Weight_lbs"])
        writer.writerow(["Recycling", 20])
        writer.writerow(["Compost", 0])
        writer.writerow(["Landfill", 10])

    # 7. Sophia (Intruder - JSON)
    with open("submissions/sophia.json", "w") as f:
        json.dump({
            "student": "Sophia",
            "waste_data": {
                "recycling": 5,
                "compost": 5,
                "landfill": 5
            }
        }, f, indent=2)

if __name__ == "__main__":
    build_env()
