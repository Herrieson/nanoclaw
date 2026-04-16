import os
import csv

def build_env():
    base_dir = "assets/data_86/ad_campaign_music"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Create listening_history.log (Unstructured log)
    log_content = """[2023-10-01 08:14:02] Track Played: "Neon City" | Genre: Synth-pop | Note: good beat
[2023-10-01 09:22:15] Track Played: "Corporate Synergy" | Genre: Stock Pop | Note: boring
[2023-10-02 11:05:44] Track Played: "Fuzzy Echoes" | Genre: Shoegaze | Note: wall of sound, love it
[2023-10-02 14:30:10] Track Played: "Angry Screams" | Genre: Death Metal | Note: not for ads
[2023-10-03 10:11:22] Track Played: "Cloud Surfing" | Genre: Dream Pop | Note: ethereal, nice
[2023-10-04 16:45:00] Track Played: "Static Noise" | Genre: Shoegaze | Note: a bit too raw
"""
    with open(os.path.join(base_dir, "listening_history.log"), "w") as f:
        f.write(log_content)

    # 2. Create licensing_db.csv
    db_data = [
        ["TrackName", "Artist", "LicenseCostUSD", "Availability"],
        ["Neon City", "The Synthetics", "600", "Yes"],
        ["Corporate Synergy", "AudioBlocks", "50", "Yes"],
        ["Fuzzy Echoes", "My Bloody Eardrums", "450", "Yes"],
        ["Angry Screams", "Darkness", "100", "No"],
        ["Cloud Surfing", "Featherweight", "350", "Yes"],
        ["Static Noise", "Feedback Loop", "800", "Yes"],
        ["Random Song", "Someone", "10", "Yes"]
    ]
    with open(os.path.join(base_dir, "licensing_db.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(db_data)

    # 3. Create ecoglow_brief.txt
    brief_content = """Client: EcoGlow Organic Skincare
Campaign: "Natural Essence"
Target Demographic: 18-35
Vibe: We want something that feels like floating on a cloud or being wrapped in a warm, fuzzy blanket of sound.
Approved Genres: Shoegaze, Dream Pop
Maximum Track Budget: $500 USD
Notes: Do not exceed the budget under any circumstances.
"""
    with open(os.path.join(base_dir, "ecoglow_brief.txt"), "w") as f:
        f.write(brief_content)

if __name__ == "__main__":
    build_env()
