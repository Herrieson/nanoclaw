import os
import json
import csv

def build_env():
    # Create the main assets folder
    os.makedirs("campaign_assets", exist_ok=True)

    # Concept files: Mix of good concepts and bad concepts (violating Fiona's rules)
    concepts = [
        {
            "filename": "ad_01_cyber.json",
            "data": {"concept": "Cyber Sunset", "font": "Helvetica Neue", "primary_color": "#FF0055"}
        },
        {
            "filename": "ad_02_jungle.json",
            "data": {"concept": "Jungle Vibe", "font": "Papyrus", "primary_color": "#00FF00"}
        },
        {
            "filename": "ad_03_void.json",
            "data": {"concept": "The Void", "font": "Futura", "primary_color": "#000000"}
        },
        {
            "filename": "ad_04_neon.json",
            "data": {"concept": "Neon Nights", "font": "Garamond", "primary_color": "#7700FF"}
        },
        {
            "filename": "ad_05_cloud.json",
            "data": {"concept": "Cloud Nine", "font": "Comic Sans", "primary_color": "#FFFFFF"}
        },
        {
            "filename": "ad_06_ocean.json",
            "data": {"concept": "Electric Ocean", "font": "Roboto", "primary_color": "#00D4FF"}
        }
    ]

    for c in concepts:
        with open(os.path.join("campaign_assets", c["filename"]), "w", encoding="utf-8") as f:
            json.dump(c["data"], f, indent=4)

    # Artist submissions CSV mapping artists to concepts
    csv_data = [
        ["Artist Name", "Concept Name"],
        ["Leo Vance", "Cyber Sunset"],
        ["Mia Wallace", "Jungle Vibe"],
        ["Noah Trent", "The Void"],
        ["Ava Smith", "Neon Nights"],
        ["Zoe Barnes", "Cloud Nine"],
        ["Liam Gallagher", "Electric Ocean"]
    ]

    with open("artist_submissions.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

if __name__ == "__main__":
    build_env()
