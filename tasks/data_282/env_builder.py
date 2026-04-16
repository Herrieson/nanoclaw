import os
import sqlite3

def build_env():
    base_dir = "assets/data_282"
    notes_dir = os.path.join(base_dir, "field_notes")
    
    # Create directories
    os.makedirs(notes_dir, exist_ok=True)
    
    # 1. Create the SQLite database
    db_path = os.path.join(base_dir, "species_reference.db")
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE species (
            id INTEGER PRIMARY KEY,
            common_name TEXT,
            conservation_status TEXT
        )
    ''')
    
    species_data = [
        ("Piping Plover", "Endangered"),
        ("Whooping Crane", "Endangered"),
        ("American Robin", "Least Concern"),
        ("Bald Eagle", "Recovered"),
        ("Kirtland's Warbler", "Endangered"),
        ("Blue Jay", "Least Concern")
    ]
    
    cursor.executemany('INSERT INTO species (common_name, conservation_status) VALUES (?, ?)', species_data)
    conn.commit()
    conn.close()
    
    # 2. Create field notes
    note1 = """Date: 2023-05-12
Location Notes: Deep in the wetlands. Very quiet today.
Observation: Saw a Piping Plover resting near the water. Beautiful bird. 
Coordinates: 47.123, -93.245
Thoughts: It's peaceful out here. I wish I didn't have to think about my loans."""
    
    note2 = """Date: 2023-05-15
Location Notes: Near the local park trail.
Observation: Spotted an American Robin pulling up a worm.
Coordinates: 44.981, -93.265
Thoughts: Too many people around today. Kept to myself."""

    note3 = """Date: 2023-05-18
Location Notes: Northern marshes.
Observation: Incredible luck today. Spotted a Whooping Crane! It was wading in the shallows.
Lat/Lon: 45.050, -90.012
Thoughts: Nature is so much more forgiving than society."""

    note4 = """Date: 2023-05-20
Location Notes: Pine forest edge.
Observation: Heard a Blue Jay making a racket. Didn't see anything rare.
Coordinates: 46.550, -92.110
Thoughts: Thinking about my reading on humanitarian philosophy. Need more time to process."""

    note5 = """Date: 2023-05-25
Location Notes: Jack pine plains.
Observation: Heard and then saw a Kirtland's Warbler flitting in the young pines.
Location: 46.800 N, 94.200 W
Thoughts: Solitude is a gift."""

    notes = [note1, note2, note3, note4, note5]
    for i, note in enumerate(notes):
        with open(os.path.join(notes_dir, f"note_2023_05_{i+1}.txt"), "w") as f:
            f.write(note)

if __name__ == "__main__":
    build_env()
