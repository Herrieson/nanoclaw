import sqlite3
import os

def main():
    base_dir = "assets/data_302"
    os.makedirs(os.path.join(base_dir, "logs"), exist_ok=True)

    db_path = os.path.join(base_dir, "employees.db")
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("CREATE TABLE personnel (id TEXT, name TEXT, department TEXT, team TEXT)")

    employees = [
        ("E01", "Alice", "Operations", "Strategy Optimization"),
        ("E02", "Bob", "Operations", "Strategy Optimization"),
        ("E03", "Charlie", "Operations", "Strategy Optimization"),
        ("E04", "David", "Operations", "Strategy Optimization"),
        ("E05", "Eve", "HR", "Talent Acquisition"),
        ("E06", "Frank", "IT", "Infrastructure")
    ]
    c.executemany("INSERT INTO personnel VALUES (?, ?, ?, ?)", employees)
    conn.commit()
    conn.close()

    logs = {
        "E01": "Monday\n09:00-10:00 - Daily Standup\n12:00-13:00 - Client Sync\nTuesday\n11:00-12:00 - Planning\n13:00-14:00 - Vendor Meeting\nWednesday\n12:00-13:30 - Deep Work\nThursday\n12:30-13:30 - Analytics Review\nFriday\n13:00-14:00 - Retrospective\n",
        "E02": "Monday\n12:30-14:00 - Cross-functional Sync\nTuesday\n12:00-13:00 - 1on1\nWednesday\n12:30-13:30 - Mentoring\nThursday\n13:00-14:00 - Townhall\nFriday\n12:30-13:30 - Yoga (Personal)\n",
        "E03": "Monday\n12:00-12:30 - Quick Chat\nTuesday\n12:00-12:30 - Quick Chat\nWednesday\n13:00-14:00 - Alignment\nThursday\n12:00-12:30 - Code Review\nFriday\n12:00-12:30 - Strategy Update\n",
        "E04": "Monday\n10:00-11:00 - Focus Time\nTuesday\n12:30-13:30 - Lunch and Learn\nWednesday\n12:00-12:30 - Sync\nThursday\n12:30-13:00 - Huddle\nFriday\n13:30-14:00 - Planning\n",
        "E05": "Monday\n12:00-14:00 - Recruitment Drive\n"
    }
    
    for emp_id, log_data in logs.items():
        with open(os.path.join(base_dir, "logs", f"{emp_id}.log"), "w") as f:
            f.write(log_data)

if __name__ == "__main__":
    main()
