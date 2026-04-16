import os
import sqlite3
import json
import csv

def build_env():
    base_dir = "assets/data_113"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Create the messy notes
    notes_dir = os.path.join(base_dir, "my_messy_notes")
    os.makedirs(notes_dir, exist_ok=True)

    with open(os.path.join(notes_dir, "monday_walk.txt"), "w") as f:
        f.write("It was a lovely morning. Saw a Kirtland's Warbler right away! Also spotted 3 Blue Jays playing around, and a Piping Plover near the water. Oh, on the way back, heard another Kirtland's Warbler singing from the pines.\n")

    with open(os.path.join(notes_dir, "tuesday_records.csv"), "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["bird_name", "count", "notes"])
        writer.writerow(["Cerulean Warbler", "2", "High in the canopy"])
        writer.writerow(["American Robin", "5", "On the lawn"])
        writer.writerow(["Piping Plover", "1", "Resting"])

    with open(os.path.join(notes_dir, "weekend_data.json"), "w") as f:
        json.dump([
            {"species": "Whooping Crane", "spotted": 1, "location": "Marsh"},
            {"species": "Rock Pigeon", "spotted": 20, "location": "City border"}
        ], f)

    with open(os.path.join(notes_dir, "random_thoughts.log"), "w") as f:
        f.write("2023-10-24 14:00 - I think I heard a Cerulean Warbler again. Yes, definitely just one. The weather is getting colder.\n")

    # 2. Create the SQLite database of endangered species
    db_path = os.path.join(base_dir, "mi_endangered_species.sqlite3")
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE species (
            id INTEGER PRIMARY KEY,
            common_name TEXT NOT NULL,
            scientific_name TEXT,
            status TEXT
        )
    ''')
    
    endangered_birds = [
        ("Kirtland's Warbler", "Setophaga kirtlandii", "Endangered"),
        ("Piping Plover", "Charadrius melodus", "Endangered"),
        ("Cerulean Warbler", "Setophaga cerulea", "Threatened"),
        ("Whooping Crane", "Grus americana", "Endangered"),
        ("Bald Eagle", "Haliaeetus leucocephalus", "Recovered"), # Just to add noise
        ("Peregrine Falcon", "Falco peregrinus", "Endangered")
    ]
    
    cursor.executemany('INSERT INTO species (common_name, scientific_name, status) VALUES (?, ?, ?)', endangered_birds)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    build_env()
