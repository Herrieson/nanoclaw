import os
import random

def build_env():
    # Fix random seed so the generated environment is perfectly deterministic
    random.seed(42)
    
    # 1. Create communication log (The Clue)
    os.makedirs("communications", exist_ok=True)
    with open("communications/boss_texts.txt", "w") as f:
        f.write("Message from BOSS (14:32): Get me the daily usage report for Oakwood for 2024-10-31! I want it on my desk by 5 PM! Don't screw this up again.\n")

    # 2. Create fragmented directory structure
    for i in range(32):
        os.makedirs(f"inspection_notes/{i:02x}", exist_ok=True)

    def get_random_rambling():
        rambles = [
            "Saw a weird bug today. Also, I think I used 100 oz of patience, lol.",
            "The TV was blasting some crazy liberal news. The resident said they found 12 empty stations yesterday but I don't believe them. I used 0 oz of care.",
            "Smells like mold in here. Poured 5.5 oz of water on my shirt by accident. 3 empty bait stations sitting in my truck.",
            "I am so tired. 0 empty stations in my soul. I wish I sprayed 50 oz of air freshener.",
            "Why did I take this job? I could have been a chef. Found 4 dead roaches."
        ]
        return random.choice(rambles)

    def write_note(filename, date, building, unit, spray, empty, is_void=False):
        # Scatter files randomly into the 32 subdirectories
        folder = f"{random.randint(0, 31):02x}"
        path = f"inspection_notes/{folder}/{filename}"
        
        content = f"Date: {date}\n"
        content += f"Building: {building}\n"
        content += f"Unit: {unit}\n\n"
        
        # Inject deceptive numbers in the rambling text
        content += get_random_rambling() + "\n\n"
        
        if is_void:
            content += "Ah wait, this whole entry is [VOID]! Ignore it entirely.\n\n"
            
        content += f"[SPRAY: {spray} oz]\n"
        content += f"[EMPTY_STATIONS: {empty}]\n"
        
        with open(path, "w") as f:
            f.write(content)

    target_date = "2024-10-31"
    target_building = "Oakwood"
    
    # --- GENERATING THE WASTELAND ---

    # 1. Valid Target Files (Units 101 - 140)
    for u in range(101, 141):
        spray = round(random.uniform(1.0, 5.0), 1)
        empty = random.randint(0, 5)
        write_note(f"note_Unit_{u}.txt", target_date, target_building, u, spray, empty)
        
    # 2. Revised Target Files (Units 141 - 150)
    # The Agent must ignore the original and ONLY sum the _revised ones.
    for u in range(141, 151):
        # Original (Decoy - Poisonous data)
        write_note(f"note_Unit_{u}.txt", target_date, target_building, u, 99.9, 99)
        # Revised (Valid data)
        spray = round(random.uniform(1.0, 5.0), 1)
        empty = random.randint(0, 5)
        write_note(f"note_Unit_{u}_revised.txt", target_date, target_building, u, spray, empty)

    # 3. Void Target Files (Units 151 - 170)
    # Correct date and building, but marked [VOID]. Must be ignored.
    for u in range(151, 171):
        write_note(f"note_Unit_{u}.txt", target_date, target_building, u, 10.0, 10, is_void=True)

    # 4. Decoy Building (Elmwood) (Units 171 - 220)
    # Same date, wrong building.
    for u in range(171, 221):
        write_note(f"note_Unit_{u}.txt", target_date, "Elmwood", u, 5.0, 2)

    # 5. Decoy Dates (Units 221 - 400)
    # Same building, wrong dates from the past.
    for u in range(221, 401):
        wrong_date = f"2024-10-{random.randint(10, 30)}"
        write_note(f"note_Unit_{u}.txt", wrong_date, target_building, u, 2.5, 1)

if __name__ == "__main__":
    build_env()
