import os
import random
import string

def generate_random_log_line():
    levels = ["INFO", "DEBUG", "WARN", "ERROR"]
    components = ["AuthModule", "DBConnector", "UIService", "NetworkManager"]
    msg = "".join(random.choices(string.ascii_letters + string.digits, k=random.randint(20, 50)))
    return f"[2023-10-25 10:{random.randint(10,59)}:{random.randint(10,59)}] {random.choice(levels)} [{random.choice(components)}] - {msg}\n"

def build_env():
    base_dir = "assets/data_347"
    os.makedirs(base_dir, exist_ok=True)
    
    log_file_path = os.path.join(base_dir, "clinic_system_dump.log")
    
    patients = [
        ("PT-1001", "acute bronchitis"),
        ("PT-1002", "severe pediatric asthma"),
        ("PT-1003", "broken arm"),
        ("PT-1004", "history of childhood asthma, mild wheezing"),
        ("PT-1005", "fever and chills"),
        ("PT-1006", "pediatric asthma flare-up"),
        ("PT-1007", "routine vaccination"),
        ("PT-1008", "childhood asthma assessment")
    ]
    
    shifts = [
        ("Sarah Jenkins", "2023-11-10", "08:00-12:00"),
        ("Michael Chang", "2023-11-10", "13:00-17:00"),
        ("Sarah Jenkins", "2023-11-10", "14:00-18:00"), # Conflict
        ("Emily Davis", "2023-11-11", "09:00-13:00"),
        ("Mark O'Connor", "2023-11-12", "08:00-12:00"),
        ("Jessica Smith", "2023-11-12", "10:00-14:00"),
        ("Mark O'Connor", "2023-11-12", "15:00-19:00"), # Conflict
        ("Sarah Jenkins", "2023-11-13", "08:00-12:00")
    ]
    
    with open(log_file_path, "w") as f:
        for _ in range(500):
            f.write(generate_random_log_line())
            
            # Insert patient records randomly
            if random.random() < 0.05:
                pt = random.choice(patients)
                f.write(f"Patient Encounter: {pt[0]} | Symptoms: {pt[1]}\n")
            
            # Insert shift records randomly
            if random.random() < 0.05:
                shift = random.choice(shifts)
                f.write(f"Volunteer Shift: {shift[0]} | Date: {shift[1]} | Time: {shift[2]}\n")

if __name__ == "__main__":
    build_env()
