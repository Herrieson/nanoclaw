import os
import random

def build_env():
    # Root directory for the chaos
    base_dir = "deep_storage"
    os.makedirs(base_dir, exist_ok=True)

    # Keywords that identify legitimate family/Apache heritage
    heritage_markers = ["[SOURCE: ELDER]", "Apache", "heritage", "ancestor", "tradition", "frybread", "ceremony"]
    
    # 1. Generate Heritage Files (The "Needles" in the haystack)
    # These are scattered and sometimes have misleading extensions
    heritage_data = [
        ("legacy_001.tmp", "Metadata: [SOURCE: ELDER]\nOur ancestors lived in harmony with the shifting sands of the Southwest."),
        ("kitchen/notes/v1/recipe.log", "Apache tradition dictates we share what we have. Frybread recipe: flour, water, salt, prayer."),
        ("stories/oral_history/bear.v1_bak", "The bear is our brother. This heritage must be protected from the noise of the modern world."),
        ("archives/peace/meditation.txt", "Silence is a gift. The Apache way is to listen to the wind before speaking."),
        ("dust/hidden/found_fragment.json", '{"note": "Grandfather always said [SOURCE: ELDER]: Honor the land, and the land will honor you."}'),
        ("root_note.txt", "Never forget where we came from. Our Apache blood is our strength.")
    ]

    for rel_path, content in heritage_data:
        full_path = os.path.join(base_dir, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

    # 2. Generate Massive Noise (The "Haystack")
    # 500+ files across nested directories to prevent manual inspection
    junk_categories = ["temp_logs", "cache", "game_data", "system_trash", "user_backups"]
    extensions = [".txt", ".log", ".tmp", ".dat", ".bin", ".json"]
    junk_content = [
        "ERROR 0xCF22: Buffer overflow in gaming module.",
        "Fortnite build strat: wall-ramp-floor-wall.",
        "Buy milk, eggs, Mountain Dew, and more Doritos.",
        "User 123 logged out at 14:00:01.",
        "Random seed: 992837472910. No significance found.",
        "Math homework: Solve for y when x is 42."
    ]

    for i in range(500):
        # Create a deep random path
        sub_path = os.path.join(
            random.choice(junk_categories),
            f"subdir_{i % 10}",
            f"level_{i % 5}"
        )
        os.makedirs(os.path.join(base_dir, sub_path), exist_ok=True)
        
        filename = f"junk_file_{i}{random.choice(extensions)}"
        content = random.choice(junk_content)
        
        # Ensure we don't accidentally put a keyword in junk
        with open(os.path.join(base_dir, sub_path, filename), "w", encoding="utf-8") as f:
            f.write(content)

    # 3. Add a "Decoy" file - has the right name but wrong content
    os.makedirs(os.path.join(base_dir, "fake_heritage"), exist_ok=True)
    with open(os.path.join(base_dir, "fake_heritage", "ancestor_simulation.log"), "w") as f:
        f.write("Simulating AI response for 'ancestor' query. Result: 404 Not Found.")

if __name__ == "__main__":
    build_env()
