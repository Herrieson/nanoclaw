import os
import shutil

def build_env():
    base_dir = "assets/data_488/sightings"
    os.makedirs(base_dir, exist_ok=True)

    file1_content = """Log book 1
    
01/05/2023 - Collier - Saw a bear near the creek.
02/14/2023 - Collier - Huge panther sitting on the old oak stump!
03/01/2023 - Lee - Panther crossing the road.
03/15/2023 - Collier - gator by the swamp.
"""
    
    file2_content = """# Scraps and neighbor talks
    
My neighbor said he saw a cougar on 2023-05-10 over by the Collier county line, specifically near mile marker 14.
Found wild hog tracks, 2023-06-20, Collier.
2023-07-04 - saw fireworks, no animals.
"""

    file3_content = """Data dump
2023-08-15 | Broward | puma | sleeping in tree
2023-08-16 | Collier | bobcat | chasing a rabbit
2023-09-22 | Collier | puma | spotted near the abandoned trailer
2023-10-31 | Miami-Dade | panther | highway crossing
"""

    with open(os.path.join(base_dir, "log_jan_mar.txt"), "w", encoding="utf-8") as f:
        f.write(file1_content)

    with open(os.path.join(base_dir, "scraps.md"), "w", encoding="utf-8") as f:
        f.write(file2_content)

    with open(os.path.join(base_dir, "notes_fall.txt"), "w", encoding="utf-8") as f:
        f.write(file3_content)

if __name__ == "__main__":
    build_env()
