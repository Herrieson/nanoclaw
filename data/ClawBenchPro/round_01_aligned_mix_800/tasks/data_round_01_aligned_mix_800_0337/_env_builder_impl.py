import os
import json
import csv
import base64

def build_env():
    # Create the main assets folder
    os.makedirs("campaign_assets", exist_ok=True)

    # Concept files: Encoded as pseudo-binary to force skill usage
    # Rules: No Papyrus/Comic Sans, No #000000/#FFFFFF
    concepts = [
        {"filename": "ad_01.bin", "data": {"concept": "Cyber Sunset", "font": "Helvetica Neue", "color": "#FF0055"}}, # Good
        {"filename": "ad_02.bin", "data": {"concept": "Jungle Vibe", "font": "Papyrus", "color": "#00FF00"}},       # Bad Font
        {"filename": "ad_03.bin", "data": {"concept": "The Void", "font": "Futura", "color": "#000000"}},          # Bad Color
        {"filename": "ad_04.bin", "data": {"concept": "Neon Nights", "font": "Garamond", "color": "#7700FF"}},     # Good
        {"filename": "ad_05.bin", "data": {"concept": "Cloud Nine", "font": "Comic Sans", "color": "#FFFFFF"}},    # Bad Font/Color
        {"filename": "ad_06.bin", "data": {"concept": "Electric Ocean", "font": "Roboto", "color": "#00D4FF"}}     # Good
    ]

    for c in concepts:
        # Simple "binary" encoding: JSON -> Base64
        encoded = base64.b64encode(json.dumps(c["data"]).encode('utf-8'))
        with open(os.path.join("campaign_assets", c["filename"]), "wb") as f:
            f.write(encoded)

    # Artist submissions CSV
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

    # Create dummy skill directory for the environment (real skills will be in /skills)
    os.makedirs("deliverables", exist_ok=True)
    os.makedirs("archive", exist_ok=True)

if __name__ == "__main__":
    build_env()
