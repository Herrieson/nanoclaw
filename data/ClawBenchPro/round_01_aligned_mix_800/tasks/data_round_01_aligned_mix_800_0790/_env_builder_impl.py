import os

def build_env():
    os.makedirs("inspection_notes", exist_ok=True)
    
    note1 = """Unit 1A: Treated for ants. The guy had some weird liberal news on TV, couldn't wait to get out of there. I used 2.5 oz of Alpine WSG. Checked the traps in the kitchen. 2 empty bait stations."""
    
    note2 = """Unit 2B: German roaches. Nastiest infestation yet. Poured 10.25 oz of spray into the cracks and crevices. God, my hands are still shaking from seeing that many bugs. Checked the traps, 4 are totally empty. I need a break."""
    
    note3 = """Unit 3C: Routine check. 0 oz used. Everything looked fine. Wait, let me check the log... 1 bait station was empty. I thought about replacing it, but I didn't have my tools. So count that as 1 empty. I hate my life sometimes."""
    
    note4 = """Unit 4D: Fleas! Ugh. Sprayed 5.5 oz of Precor. Checked the bait stations in the basement, but 0 empty stations down there. The old lady tried to talk to me for an hour. I just wanted to be left alone."""
    
    with open("inspection_notes/note_1A.txt", "w") as f:
        f.write(note1)
        
    with open("inspection_notes/note_2B.txt", "w") as f:
        f.write(note2)
        
    with open("inspection_notes/note_3C.txt", "w") as f:
        f.write(note3)
        
    with open("inspection_notes/note_4D.txt", "w") as f:
        f.write(note4)

if __name__ == "__main__":
    build_env()
