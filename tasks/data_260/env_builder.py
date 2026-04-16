import os
import sqlite3

def build_env():
    base_dir = "assets/data_260"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Create the messy log file
    log_content = """[LOG 08:45] System boot sequence initiated. Workspace arrangement: Optimal.
[LOG 09:00] Artifact #4492: Shinto shrine mirror, bronze. Needs meticulous polishing.
[LOG 09:05] Chatting with Apollo. He seems agitated today. Weekly req: 15 units of Quail.
[LOG 09:12] Artifact #112: Tokugawa era coins. 45 pieces.
[LOG 09:15] Kitsune is pacing. I promised her I'd note her needs. She requires 5 units of FoxKibble this week.
[LOG 09:22] Note to self: The Meiji exhibit lighting is off by 2 degrees. Must fix.
[LOG 09:30] Hachiko is such a good boy, leaning against the enclosure. Weekly diet is 14 units of DogFood.
[LOG 09:35] Artifact #88: Jomon pottery fragment.
[LOG 09:40] Wait, did I order enough food? The system is freezing...
[ERR 09:41] SEGFAULT. Core dumped.
"""
    with open(os.path.join(base_dir, "workspace_dump.txt"), "w") as f:
        f.write(log_content)

    # 2. Create the SQLite database
    db_path = os.path.join(base_dir, "supply_room.db")
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE inventory (
            item_name TEXT PRIMARY KEY,
            stock INTEGER
        )
    ''')
    
    # Insert initial stock
    inventory_data = [
        ('Quail', 5),
        ('FoxKibble', 10),
        ('DogFood', 2),
        ('BronzePolish', 1),
        ('DisplayLights', 4)
    ]
    
    cursor.executemany('INSERT INTO inventory (item_name, stock) VALUES (?, ?)', inventory_data)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    build_env()
