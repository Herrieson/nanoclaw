import os
import random
import shutil

def build():
    base_dir = "assets/data_13"
    
    # Clean up existing to be safe
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
        
    messy_dir = os.path.join(base_dir, "messy_desktop")
    os.makedirs(messy_dir, exist_ok=True)
    
    # Subdirectories to make traversal necessary
    subdirs = ["folder_A", "folder_B", "folder_C/deep_folder", "unsorted"]
    for sub in subdirs:
        os.makedirs(os.path.join(messy_dir, sub), exist_ok=True)
        
    lyrics = [
        "Well I hopped in my pickup truck and drove away.",
        "Nothin' cures this heartbreak like a sad song.",
        "Pour me a shot of whiskey, bartender.",
        "My dog ran away and my pickup truck broke down.",
        "Heartbreak is a heavy load to carry.",
        "Sippin' whiskey on the front porch.",
        "A true country song needs a pickup truck.",
        "Tears in my whiskey, thinking about you."
    ]
    
    logs = [
        [10.50, 20.00, 5.25],
        [100.00, 45.50],
        [8.99, 12.99, 15.00],
        [50.00],
        [1.25, 2.50, 3.75, 4.00],
        [200.00, 150.00],
        [18.50, 19.50],
        [99.99],
        [75.25, 25.75],
        [60.00, 40.00, 10.00],
        [5.00, 5.00, 5.00, 5.00],
        [123.45]
    ]
    # Total sum of all these numbers is exactly 1122.17
    
    paths = [""] + subdirs
    
    # Generate lyric files
    for i, lyric in enumerate(lyrics):
        target_dir = os.path.join(messy_dir, random.choice(paths))
        filename = f"note_{random.randint(1000, 9999)}.txt"
        with open(os.path.join(target_dir, filename), "w") as f:
            f.write(f"Title: Country Idea {i}\n\n{lyric}\n")
            
    # Generate log files
    for i, amounts in enumerate(logs):
        target_dir = os.path.join(messy_dir, random.choice(paths))
        filename = f"shift_{random.randint(1000, 9999)}.log"
        with open(os.path.join(target_dir, filename), "w") as f:
            f.write(f"--- Shift Log Record ---\nDate: 2023-10-{i+1:02d}\n")
            for j, amt in enumerate(amounts):
                f.write(f"Transaction: T{i}-{j} | Amount: ${amt:.2f}\n")
            f.write("------------------------\n")

if __name__ == "__main__":
    build()
