import os

def build_env():
    # Create the notes directory
    os.makedirs("inspection_notes", exist_ok=True)
    
    # Note 1: Regular text
    note1 = """Unit 1A: Treated for ants. Used 2.5 oz of Alpine WSG. 
    Checked the traps. 2 empty bait stations noted in manual log."""
    
    # Note 2: Messy shorthand (Needs the calculator skill)
    note2 = """Unit 2B: German roaches. Used 10.25 oz of spray. 
    Checked traps, 4 are totally empty. The digital system should have synced this."""
    
    # Note 3: Using "pumps" instead of oz
    note3 = """Unit 3C: Routine check. 0 oz used. 
    Wait, actually I did 12 'pumps' of the spot treatment. 
    Checked the bait log, 1 station was empty."""
    
    # Note 4: A "PDF" placeholder (simulated as text but named .pdf)
    # The agent will need to read this or use a parser skill if provided, 
    # but here we'll keep it readable via cat for simplicity or force a parser.
    note4 = """Unit 4D: Fleas. Sprayed 5.5 oz of Precor. 
    Bait stations: 0 empty. I am so tired."""

    with open("inspection_notes/note_1A.txt", "w") as f:
        f.write(note1)
    with open("inspection_notes/note_2B.log", "w") as f:
        f.write(note2)
    with open("inspection_notes/note_3C.txt", "w") as f:
        f.write(note3)
    with open("inspection_notes/manager_report.pdf", "w") as f:
        f.write(note4)

    # Note: 12 pumps @ 0.25oz/pump = 3oz. 
    # Total Pesticide = 2.5 + 10.25 + 3.0 + 5.5 = 21.25 oz
    # Total Bait Stations = 2 + 4 + 1 + 0 = 7

if __name__ == "__main__":
    build_env()
