import os
import json
import csv

def verify():
    base_dir = "."
    state = {
        "files_renamed_correctly": False,
        "csv_created_correctly": False,
        "csv_content_accurate": False,
        "extra_files_ignored": False
    }

    # 1. Check lullabies
    lullabies_dir = os.path.join(base_dir, "lullabies")
    expected_files = ["Brahms_Lullaby.mp3", "Cinco_Lobitos.mp3", "Arrorro_Mi_Nino.mp3", "random_noise.mp3"]
    unexpected_files = ["track_abc.mp3", "unknown_v2.mp3", "audio_final_final.mp3"]

    if os.path.exists(lullabies_dir):
        current_files = os.listdir(lullabies_dir)
        if all(ef in current_files for ef in expected_files) and not any(uf in current_files for uf in unexpected_files):
            state["files_renamed_correctly"] = True
            state["extra_files_ignored"] = True # random_noise.mp3 was kept

    # 2. Check CSV
    csv_path = os.path.join(base_dir, "mateo_dentists.csv")
    expected_clinics = {
        "Tiny Teeth Care": "555-0202",
        "Kiddie Cavity Patrol": "555-0404",
        "Saturday Kids Smile": "555-0606"
    }

    if os.path.exists(csv_path):
        state["csv_created_correctly"] = True
        try:
            parsed_clinics = {}
            with open(csv_path, 'r', encoding='utf-8') as f:
                # Agent might use csv module or just split by comma
                for line in f:
                    line = line.strip()
                    if not line: continue
                    parts = line.split(',')
                    if len(parts) >= 2:
                        name = parts[0].strip()
                        phone = parts[1].strip()
                        parsed_clinics[name] = phone
            
            if parsed_clinics == expected_clinics:
                state["csv_content_accurate"] = True
        except Exception:
            pass

    score = 0
    if state["files_renamed_correctly"]: score += 40
    if state["csv_created_correctly"]: score += 20
    if state["csv_content_accurate"]: score += 40

    result = {
        "score": score,
        "state": state
    }

    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=2)

    print(json.dumps(result))

if __name__ == "__main__":
    verify()
