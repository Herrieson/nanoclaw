import os

def build_env():
    # 1. Create directory for submissions
    os.makedirs("student_submissions", exist_ok=True)
    
    # 2. Create Master Roster
    roster = ["Alice", "Bob", "Charlie", "Daisy", "Ethan", "Fiona", "George", "Hannah"]
    with open("master_roster.txt", "w") as f:
        f.write("\n".join(roster))
        
    # 3. Create dummy image files (placeholders)
    # The actual data is hidden in the Skill's Mock logic based on these filenames
    photos = [
        "IMG_9821_Alice.jpg",   # Sego Lily (Native), 3.5
        "IMG_9822_Bob.jpg",     # Sagebrush (Native), 4.0
        "IMG_9823_Charlie.jpg", # Russian Thistle (Invasive), 12.0
        "IMG_9824_Daisy.jpg",   # Sego Lily (Native), 2.0
        "IMG_9825_George.jpg",  # Cheatgrass (Invasive), 8.5
        "IMG_9826_Hannah.jpg"   # Bitterbrush (Native), 5.5
    ]
    
    for photo in photos:
        with open(f"student_submissions/{photo}", "w") as f:
            f.write(f"Image data for {photo}")

if __name__ == "__main__":
    build_env()
