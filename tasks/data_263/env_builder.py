import os
import csv

def build_env():
    base_dir = "assets/data_263"
    os.makedirs(base_dir, exist_ok=True)
    music_dump_dir = os.path.join(base_dir, "music_dump")
    os.makedirs(music_dump_dir, exist_ok=True)

    # Write faves.txt
    faves = [
        "Kendrick Lamar",
        "Megan Thee Stallion",
        "GloRilla",
        "Chief Keef",
        "Lil Uzi Vert"
    ]
    with open(os.path.join(base_dir, "faves.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(faves) + "\n")

    # Write dj_mike.txt
    dj_mike_content = """
Song: Not Like Us | Artist: Kendrick Lamar | Time: 4:34 | BPM: 130
Song: Rich Spirit | Artist: Kendrick Lamar | Time: 3:22 | BPM: 90
Song: HISS | Artist: Megan Thee Stallion | Time: 3:12 | BPM: 140
Song: Yeah Glo! | Artist: GloRilla | Time: 2:45 | BPM: 110
Song: Just Wanna Rock | Artist: Lil Uzi Vert | Time: 2:03 | BPM: 150
Song: Some Random Song | Artist: Unknown | Time: 3:00 | BPM: 125
Song: Don't Stop | Artist: Megan Thee Stallion | Time: 3:07 | BPM: 105
"""
    with open(os.path.join(music_dump_dir, "dj_mike.txt"), "w", encoding="utf-8") as f:
        f.write(dj_mike_content.strip())

    # Write club_set.csv
    with open(os.path.join(music_dump_dir, "club_set.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Artist", "Length", "BPM"])
        writer.writerow(["Love Sosa", "Chief Keef", "4:06", "132"])
        writer.writerow(["Savage", "Megan Thee Stallion", "2:35", "169"])
        writer.writerow(["TGIF", "GloRilla", "2:50", "125"])
        writer.writerow(["Slow Jam", "Chief Keef", "3:00", "85"])
        writer.writerow(["Family Ties", "Baby Keem & Kendrick Lamar", "4:12", "134"]) # Should be skipped because artist is not exact match
        writer.writerow(["DNA.", "Kendrick Lamar", "3:05", "135"])
        writer.writerow(["Fake Track", "Lil Uzi Vert", "2:20", "120"]) # BPM not strictly > 120

if __name__ == "__main__":
    build_env()
