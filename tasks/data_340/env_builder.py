import os
import sqlite3
import csv

def build_env():
    base_dir = "assets/data_340"
    raw_dir = os.path.join(base_dir, "raw_notes")
    
    # Create directories
    os.makedirs(raw_dir, exist_ok=True)
    
    # 1. Create the SQLite database
    db_path = os.path.join(base_dir, "master_species.sqlite")
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE species (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL
        )
    ''')
    
    valid_species = [
        ("Red-Tailed Hawk", "Fauna"),
        ("California Poppy", "Flora"),
        ("Western Fence Lizard", "Fauna"),
        ("Poison Oak", "Flora"),
        ("Banana Slug", "Fauna"),
        ("Monarch Butterfly", "Fauna"),
        ("Coast Redwood", "Flora")
    ]
    
    cursor.executemany('INSERT INTO species (name, category) VALUES (?, ?)', valid_species)
    conn.commit()
    conn.close()

    # 2. Generate messy raw notes
    
    # Timmy's messy text file
    with open(os.path.join(raw_dir, "timmy_journal.txt"), "w") as f:
        f.write("Today was so fun!! I saw a huge banana slug on a log. It was super slimy. "
                "Later I thought I saw a Dragon but Sarah said I was dumb. "
                "I also tripped and fell into some POISON OAK. My leg itches now.\n")

    # Sarah's log file
    with open(os.path.join(raw_dir, "sarah.log"), "w") as f:
        f.write("[09:00] Arrived at park.\n"
                "[09:30] Spotted a beautiful california poppy by the trail.\n"
                "[10:15] Saw a western fence lizard doing pushups on a rock!\n"
                "[11:00] Lunch time. Ate a sandwich.\n")

    # Bobby's CSV file
    with open(os.path.join(raw_dir, "group2_data.csv"), "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Student_Name", "Sighting", "Extra_Notes"])
        writer.writerow(["Bobby", "Red-Tailed Hawk", "It was flying really high up."])
        writer.writerow(["Bobby", "T-Rex", "Just kidding!"])
        writer.writerow(["Bobby", "Coast Redwood", "Tallest tree ever!"])
        writer.writerow(["Jessica", "Monarch Butterfly", "Landed on my backpack."])
        writer.writerow(["Jessica", "Unicorn", "Sparkly"])

if __name__ == "__main__":
    build_env()
