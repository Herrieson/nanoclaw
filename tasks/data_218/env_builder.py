import os
import sqlite3

def build_env():
    base_dir = "assets/data_218"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Create the messy log file
    log_content = """2023-04-10 08:15:00 - System startup
2023-04-10 09:00:00 - Alice asked about lunch menu
2023-04-10 09:15:00 - Alice signed up for Spring Bird Watching
2023-04-10 10:20:00 - Mr. Henderson checked out
2023-04-11 11:00:00 - Bob signed up for Spring Bird Watching
2023-04-11 11:30:00 - Charlie signed up for Spring Bird Watching
2023-04-11 14:00:00 - Diana requested Spring Bird Watching
2023-04-12 09:00:00 - Edward enrolled in Spring Bird Watching
2023-04-12 10:00:00 - Fiona expressed interest and signed up for Spring Bird Watching
2023-04-12 11:00:00 - George confirmed for Spring Bird Watching
2023-04-12 12:00:00 - Harry wants to join Knitting Class
2023-04-12 13:00:00 - End of shift report generated
"""
    with open(f"{base_dir}/signups.log", "w") as f:
        f.write(log_content)

    # 2. Create the SQLite database
    db_path = f"{base_dir}/clinic.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Table: residents
    c.execute("CREATE TABLE residents (id INTEGER PRIMARY KEY, name TEXT, health_status TEXT)")
    residents_data = [
        (1, 'Alice', 'OK'),
        (2, 'Bob', 'Restricted'),
        (3, 'Charlie', 'Needs Escort'),
        (4, 'Diana', 'Needs Escort'),
        (5, 'Edward', 'OK'),
        (6, 'Fiona', 'Needs Escort'),
        (7, 'George', 'Needs Escort'),
        (8, 'Harry', 'OK')
    ]
    c.executemany("INSERT INTO residents VALUES (?,?,?)", residents_data)

    # Table: staff
    c.execute("CREATE TABLE staff (id INTEGER PRIMARY KEY, name TEXT, available INTEGER)")
    staff_data = [
        (1, 'Nurse_Sarah', 1),
        (2, 'Nurse_John', 0),
        (3, 'Orderly_Mike', 1),
        (4, 'Orderly_Anna', 1)
    ]
    c.executemany("INSERT INTO staff VALUES (?,?,?)", staff_data)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    build_env()
