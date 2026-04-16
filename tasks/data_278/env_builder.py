import os
import shutil

def main():
    base_dir = "assets/data_278/community_music"
    
    # Clean up if exists
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
        
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(os.path.join(base_dir, "sheets"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "audio"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "old_stuff", "nested"), exist_ok=True)
    
    # Create some draft files (to be deleted)
    draft_files = [
        "draft_notes.txt",
        "audio/Track1_Draft.mp3",
        "sheets/final_DRAFT_v2.pdf",
        "old_stuff/nested/ignore_draft.txt"
    ]
    
    for df in draft_files:
        path = os.path.join(base_dir, df)
        with open(path, "w") as f:
            f.write("This is a draft.\n")
            
    # Create valid files
    valid_files = [
        ("audio/track1.mp3", "dummy mp3 content"),
        ("audio/klezmer_dance.mp3", "dance"),
        ("sheets/sonata.pdf", "dummy pdf content"),
        ("old_stuff/random.log", "just a log file"),
        ("notes.txt", "Just a random note about the event."),
    ]
    
    for vf, content in valid_files:
        path = os.path.join(base_dir, vf)
        with open(path, "w") as f:
            f.write(content)
            
    # Create .txt files that need checking
    
    # 1. Mentions 'piano' and has the typo
    with open(os.path.join(base_dir, "sheets", "piano_score.txt"), "w") as f:
        f.write("This is a beautiful piano piece.\nMake sure to play the ending very Pianisimo.\nAnother Pianisimo here.")

    # 2. Mentions 'klezmer' and has the typo
    with open(os.path.join(base_dir, "klezmer_notes.txt"), "w") as f:
        f.write("Traditional klezmer music guide.\nThe clarinet goes loud, then the accompaniment should be Pianisimo.")
        
    # 3. Mentions 'piano' but spelled correctly
    with open(os.path.join(base_dir, "sheets", "piano_lesson.txt"), "w") as f:
        f.write("For this piano lesson, remember to observe the Pianissimo markings.")
        
    # 4. Has the typo, but does NOT mention 'piano' or 'klezmer' (Should NOT be modified)
    with open(os.path.join(base_dir, "old_stuff", "guitar.txt"), "w") as f:
        f.write("Guitar tabs. Strum softly, almost Pianisimo.")
        
    # 5. Just a normal file with no keywords
    with open(os.path.join(base_dir, "sheets", "violin.txt"), "w") as f:
        f.write("Violin sheet music notes. Play with vibrato.")
        
if __name__ == "__main__":
    main()
