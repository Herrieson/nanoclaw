import os
import csv
import json
import random

def build_env():
    # Create directories
    os.makedirs("shift_logs", exist_ok=True)
    os.makedirs("personnel", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. Staff Whitelist (The "Approved" list)
    staff_data = [
        ["id", "name", "role", "unit"],
        ["N-201", "Marie Celestin", "Nursing Assistant", "ICU"],
        ["N-202", "James Wilson", "Registered Nurse", "ICU"],
        ["N-203", "Sarah Miller", "Nursing Assistant", "ICU"],
        ["D-101", "Dr. Aristhène", "Attending Physician", "ICU"],
        ["A-505", "David Brown", "Administrator", "Admin"]
    ]
    with open("personnel/authorized_list.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(staff_data)

    # 2. Shift Logs (The "Messy" data)
    # Includes authorized entries, unauthorized entries, and duplicates
    log_entries = [
        ["timestamp", "badge_id", "staff_name", "action", "hours_claimed"],
        ["2023-10-21 19:00", "N-201", "Marie Celestin", "Clock-In", "0"],
        ["2023-10-21 23:30", "X-999", "Unknown Person", "Access-Attempt", "0"], # Unauthorized
        ["2023-10-22 07:00", "N-201", "Marie Celestin", "Clock-Out", "12.0"],
        ["2023-10-22 19:00", "N-201", "Marie Celestin", "Clock-In", "0"],
        ["2023-10-23 07:00", "N-201", "Marie Celestin", "Clock-Out", "12.0"],
        ["2023-10-22 20:00", "N-202", "James Wilson", "Clock-In", "0"],
        ["2023-10-23 04:00", "N-202", "James Wilson", "Clock-Out", "8.0"],
        ["2023-10-22 21:00", "Z-404", "Ghost User", "Access-Attempt", "0"], # Unauthorized
        ["2023-10-23 19:00", "N-203", "Sarah Miller", "Clock-In", "0"],
        ["2023-10-24 07:00", "N-203", "Sarah Miller", "Clock-Out", "12.0"],
        # Duplicate entry for Sarah Miller (simulating error)
        ["2023-10-24 07:00", "N-203", "Sarah Miller", "Clock-Out", "12.0"] 
    ]
    
    with open("shift_logs/log_october_week3.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(log_entries)

    # 3. Extra Distraction: Self-care notes (related to persona's hobbies)
    with open("self_care_reminder.txt", "w") as f:
        f.write("Remember to pick up the herbal tea and skin moisturizer after the shift. Keep calm, focus on the patients.")

if __name__ == "__main__":
    build_env()
