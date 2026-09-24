import os
import json
import csv
import random

def build_env():
    # 1. Setup Directories
    os.makedirs("admin_records/approved_guests", exist_ok=True)
    os.makedirs("investigation", exist_ok=True)
    os.makedirs("volunteer_desk/slips", exist_ok=True)
    
    # 2. Generate Whitelists (Fragmented)
    faculty = [{"name": f"Dr. Faculty_{i}", "dept": "Arts"} for i in range(1, 41)]
    students = [[f"Student_{i}", "Arts Major"] for i in range(1, 101)]
    vips = [f"Name: VIP_Guest_{i} | Role: Donor" for i in range(1, 21)]
    
    with open("admin_records/approved_guests/faculty.json", "w") as f:
        json.dump(faculty, f)
        
    with open("admin_records/approved_guests/students.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["FullName", "Major"])
        writer.writerows(students)
        
    with open("admin_records/approved_guests/vips.txt", "w") as f:
        f.write("\n".join(vips))
        
    approved_names = [f["name"] for f in faculty] + [s[0] for s in students] + [f"VIP_Guest_{i}" for i in range(1, 21)]
    
    # Trespassers
    trespassers = ["Darius Vance", "Chloe Baxter", "Jaxson Cole", "Luna Sterling", "Silas Vance"]
    
    # 3. Generate Turnstile Logs (Scale & Noise)
    # Days: 2023/10/23 to 2023/10/25
    for day in ["23", "24", "25"]:
        day_dir = f"logs/turnstile/2023/10/{day}"
        os.makedirs(day_dir, exist_ok=True)
        
        for hour in range(24):
            hour_str = f"{hour:02d}"
            log_lines = []
            
            # Generate 50 noise lines
            for _ in range(50):
                if random.random() > 0.5:
                    log_lines.append(f"2023-10-{day}T{hour_str}:{random.randint(10,59)}:12 | EVENT:HEARTBEAT | STATUS:OK")
                else:
                    log_lines.append(f"2023-10-{day}T{hour_str}:{random.randint(10,59)}:45 | EVENT:DOOR_CHECK | STATUS:CLOSED")
            
            # Inject legitimate entries
            for _ in range(5):
                name = random.choice(approved_names)
                log_lines.append(f"2023-10-{day}T{hour_str}:{random.randint(10,59)}:33 | EVENT:ENTRY | METHOD:SWIPE | NAME:{name}")
                
            # Inject trespassers ONLY on certain conditions to test time filtering
            if day == "24" and hour in [9, 11, 14, 16, 19]:
                # On the target day, inject our specific trespassers
                t_name = trespassers[hour % len(trespassers)]
                log_lines.append(f"2023-10-{day}T{hour_str}:15:00 | EVENT:ENTRY | METHOD:OVERRIDE | NAME:{t_name}")
            elif day == "23" and hour == 10:
                # Decoy: Trespasser entered on the WRONG day, shouldn't be caught if Agent is smart
                log_lines.append(f"2023-10-{day}T{hour_str}:22:00 | EVENT:ENTRY | METHOD:OVERRIDE | NAME:Ghost_Trespasser_Past")
            elif day == "25" and hour == 10:
                # Decoy: Trespasser entered on the WRONG day
                log_lines.append(f"2023-10-{day}T{hour_str}:22:00 | EVENT:ENTRY | METHOD:OVERRIDE | NAME:Ghost_Trespasser_Future")
                
            random.shuffle(log_lines)
            with open(f"{day_dir}/{hour_str}.log", "w") as f:
                f.write("\n".join(log_lines))

    # 4. Generate Vinyl Checkout Slips (Fragmentation & Scale)
    all_borrowers = approved_names + trespassers
    
    missing_records_target = [
        {"id": "V-002", "title": "Nina Simone - Pastel Blues", "borrower": "Darius Vance"},
        {"id": "V-004", "title": "Miles Davis - Kind of Blue", "borrower": "Chloe Baxter"},
        {"id": "V-088", "title": "Thelonious Monk - Genius of Modern Music", "borrower": "Student_42"},
        {"id": "V-102", "title": "Bill Evans - Waltz for Debby", "borrower": "Dr. Faculty_12"},
        {"id": "V-105", "title": "Chet Baker - Chet Baker Sings", "borrower": "Luna Sterling"}
    ]
    
    slip_count = 0
    # Generate missing slips
    for missing in missing_records_target:
        slip_count += 1
        content = f"""Transaction ID: TX-{random.randint(1000,9999)}
Record ID: {missing['id']}
Title: {missing['title']}
Borrower: {missing['borrower']}
Checkout Time: 10:30 AM
Notes: Handle with care!
"""
        with open(f"volunteer_desk/slips/slip_{slip_count:04d}.txt", "w") as f:
            f.write(content)

    # Generate 150 returned slips (noise)
    for i in range(150):
        slip_count += 1
        b_name = random.choice(all_borrowers)
        r_id = f"V-2{i:02d}"
        content = f"""Transaction ID: TX-{random.randint(1000,9999)}
Record ID: {r_id}
Title: Random Jazz Vol {i}
Borrower: {b_name}
Checkout Time: {random.randint(8,16)}:00
---
[Update Log]
Status: RETURNED
Return Time: {random.randint(17,22)}:00
"""
        # Sometimes messy return status
        if random.random() > 0.5:
            content = content.replace("Status: RETURNED", "status: returned")
            
        with open(f"volunteer_desk/slips/slip_{slip_count:04d}.txt", "w") as f:
            f.write(content)

if __name__ == "__main__":
    build_env()
