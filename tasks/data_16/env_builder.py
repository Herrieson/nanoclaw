import os
import json
import csv
import shutil

def build_env():
    base_dir = "assets/data_16/workspace"
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(base_dir)

    # Create donors.csv
    donors_path = os.path.join(base_dir, "donors_2023.csv")
    donors_data = [
        ["First Name", "Last Name", "Amount"],
        ["Robert", "Smith", "500"],
        ["Maria", "Novak", "1200"],
        ["James", "O'Connor", "300"],
        ["Linda", "Johnson", "150"]
    ]
    with open(donors_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(donors_data)

    # Create submissions directory
    sub_dir = os.path.join(base_dir, "submissions")
    os.makedirs(sub_dir)

    submissions = [
        # Match, VIP (Smith)
        {
            "type": "json",
            "dir": "sub_01",
            "data": {
                "artist_name": "Emma Smith",
                "tags": ["nature", "watercolor"],
                "description": "I love painting trees and rivers." # 6 words. 50 + 30 = 80
            }
        },
        # No match (Space)
        {
            "type": "txt",
            "dir": "sub_02",
            "data": "Name: John Doe\nArtwork Theme: Space\nStatement: Stars are very cool to look at.\n"
        },
        # Match, VIP (Novak)
        {
            "type": "json",
            "dir": "sub_03",
            "data": {
                "artist_name": "Luka Novak",
                "tags": ["Abstract", "Garden"],
                "description": "Watching plants grow teaches us patience and deep empathy." # 9 words. 50 + 45 = 95
            }
        },
        # Match, Not VIP
        {
            "type": "txt",
            "dir": "sub_04",
            "data": "Name: Alice Wonderland\nArtwork Theme: Landscape\nStatement: A beautiful mountain view from my window.\n" # 7 words. 50 + 35 = 85
        },
        # No Match (Urban)
        {
            "type": "json",
            "dir": "sub_05",
            "data": {
                "artist_name": "Peter Parker",
                "tags": ["Urban", "City"],
                "description": "The city never sleeps." 
            }
        },
        # Match, Not VIP, tricky casing
        {
            "type": "txt",
            "dir": "sub_06",
            "data": "Name: Charlie Brown\nArtwork Theme: NATURE\nStatement: Trees.\n" # 1 word. 50 + 5 = 55
        }
    ]

    for sub in submissions:
        curr_dir = os.path.join(sub_dir, sub["dir"])
        os.makedirs(curr_dir)
        
        # Add a dummy image file just to add noise
        with open(os.path.join(curr_dir, "artwork.jpg"), 'wb') as f:
            f.write(b"dummy image data")

        if sub["type"] == "json":
            with open(os.path.join(curr_dir, "metadata.json"), 'w', encoding='utf-8') as f:
                json.dump(sub["data"], f, indent=2)
        else:
            with open(os.path.join(curr_dir, "info.txt"), 'w', encoding='utf-8') as f:
                f.write(sub["data"])

if __name__ == "__main__":
    build_env()
