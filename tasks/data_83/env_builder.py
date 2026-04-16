import os
import sqlite3

def build():
    base_dir = "assets/data_83"
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Create chat logs
    logs = """[18:00] Admin: The principal just announced the new book ban. We can't let this happen. Walkout tomorrow. Who is with me?
[18:01] Tyler2008: This is messed up.
[18:01] JayDash: I'm in!
[18:02] Marcus_King: Count me in!
[18:03] ChloeBear: My parents will kill me if I get suspended.
[18:05] Trey_T: I'm in!
[18:06] Sarah_Smiles: Count me in!
[18:07] BigMike: I have a math test, sorry bro.
[18:08] Jamal_99: I'm in!
"""
    with open(os.path.join(base_dir, "server_logs.txt"), "w") as f:
        f.write(logs)
        
    # 2. Create SQLite DB
    db_path = os.path.join(base_dir, "server_data.db")
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE users
                      (id INTEGER PRIMARY KEY, username TEXT, email TEXT, is_snitch INTEGER)''')
    
    users = [
        ("Tyler2008", "tyler.w@test.com", 0),
        ("JayDash", "jay.dash@test.com", 0),
        ("Marcus_King", "marcus.k@test.com", 0),
        ("ChloeBear", "chloe.b@test.com", 0),
        ("Trey_T", "trey.snitch@test.com", 1), # Snitch!
        ("Sarah_Smiles", "sarah.s@test.com", 0),
        ("BigMike", "mike.b@test.com", 0),
        ("Jamal_99", "jamal.99@test.com", 0)
    ]
    
    cursor.executemany("INSERT INTO users (username, email, is_snitch) VALUES (?, ?, ?)", users)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    build()
