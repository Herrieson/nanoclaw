import os
import json
import shutil

def build_env():
    base_dir = "assets/data_406"
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(base_dir)

    # 1. Create Lullabies directory and files
    lullabies_dir = os.path.join(base_dir, "lullabies")
    os.makedirs(lullabies_dir)
    
    dummy_files = ["track_abc.mp3", "unknown_v2.mp3", "audio_final_final.mp3", "random_noise.mp3"]
    for f in dummy_files:
        with open(os.path.join(lullabies_dir, f), 'w') as fh:
            fh.write("dummy audio content")

    # 2. Create music_notes.txt
    notes_content = """
    Hola! Okay, let me remember... 🎵 twinkle twinkle little star 🎵
    Ah yes, the file `track_abc.mp3` should definitely be named `Brahms_Lullaby.mp3`.
    I think I saved `unknown_v2.mp3` which is actually `Cinco_Lobitos.mp3`.
    Oh! And that weird `audio_final_final.mp3` is my favorite, `Arrorro_Mi_Nino.mp3`.
    Leave `random_noise.mp3` alone, it's just white noise for the baby.
    """
    with open(os.path.join(base_dir, "music_notes.txt"), 'w') as f:
        f.write(notes_content.strip())

    # 3. Create clinics_export.json
    clinics_data = [
        {"id": 1, "name": "Happy Smiles Dental", "specialty": "General", "days_open": ["Monday", "Wednesday", "Friday"], "phone": "555-0101"},
        {"id": 2, "name": "Tiny Teeth Care", "specialty": "Pediatric", "days_open": ["Monday", "Tuesday", "Saturday"], "phone": "555-0202"},
        {"id": 3, "name": "City Center Dental", "specialty": "Orthodontics", "days_open": ["Saturday", "Sunday"], "phone": "555-0303"},
        {"id": 4, "name": "Kiddie Cavity Patrol", "specialty": "pediatric", "days_open": ["Thursday", "Friday", "Saturday"], "phone": "555-0404"},
        {"id": 5, "name": "Adult Gum Clinic", "specialty": "Periodontics", "days_open": ["Monday", "Tuesday"], "phone": "555-0505"},
        {"id": 6, "name": "Saturday Kids Smile", "specialty": "PEDIATRIC", "days_open": ["Saturday"], "phone": "555-0606"},
        {"id": 7, "name": "Weekday Kids", "specialty": "Pediatric", "days_open": ["Monday", "Tuesday"], "phone": "555-0707"}
    ]
    with open(os.path.join(base_dir, "clinics_export.json"), 'w') as f:
        json.dump(clinics_data, f, indent=2)

if __name__ == "__main__":
    build_env()
