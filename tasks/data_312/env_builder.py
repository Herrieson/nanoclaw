import os
import shutil

def build_env():
    base_dir = "assets/data_312"
    raw_dir = os.path.join(base_dir, "literature_raw")
    
    # Clean up and recreate directories
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(raw_dir)

    texts = {
        "file1.txt": """Title: The Iron Mill
Author: John Smith

Teh factory was incredibly loud today. Smoke filled the sky, blocking out the sun completely. The engine roared with a terrible fury, whcih scared a little bird away from the window sill.""",
        
        "file2.txt": """Title: Whispers of the Forest
Author: Jane Doe

Nature is truly beautiful in the morning light. Teh tree stood tall by the winding river. A bird sang a sweet melody. Whcih tree is the oldest? That one over there.""",
        
        "file3.txt": """Title: Progress and Ruin
Author: Arthur Pendelton

Teh river was heavily polluted by the new factory. Thick smoke covered teh solitary tree on the hill. The machine was a monster, whcih slowly consumed the peaceful landscape."""
    }

    for filename, content in texts.items():
        with open(os.path.join(raw_dir, filename), "w", encoding="utf-8") as f:
            f.write(content)

    print(f"Environment built successfully at {base_dir}")

if __name__ == "__main__":
    build_env()
