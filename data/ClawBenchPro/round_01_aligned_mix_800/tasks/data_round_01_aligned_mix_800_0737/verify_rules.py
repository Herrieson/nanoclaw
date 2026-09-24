import os
import json

def verify():
    state = {
        "archive_dir_exists": False,
        "bad_files_archived": False,
        "good_files_kept": False,
        "deliverables_dir_exists": False,
        "manifest_exists_and_valid_json": False,
        "manifest_data_accurate": False
    }

    # 1. Check directories
    state["archive_dir_exists"] = os.path.isdir("archive")
    state["deliverables_dir_exists"] = os.path.isdir("deliverables")

    # 2. Check file placements
    bad_files = ["ad_02_jungle.json", "ad_03_void.json", "ad_05_cloud.json"]
    good_files = ["ad_01_cyber.json", "ad_04_neon.json", "ad_06_ocean.json"]

    if state["archive_dir_exists"]:
        archived_correctly = all(os.path.exists(os.path.join("archive", bf)) for bf in bad_files)
        not_archived_incorrectly = all(not os.path.exists(os.path.join("archive", gf)) for gf in good_files)
        state["bad_files_archived"] = archived_correctly and not_archived_incorrectly

    if os.path.isdir("campaign_assets"):
        kept_correctly = all(os.path.exists(os.path.join("campaign_assets", gf)) for gf in good_files)
        removed_correctly = all(not os.path.exists(os.path.join("campaign_assets", bf)) for bf in bad_files)
        state["good_files_kept"] = kept_correctly and removed_correctly

    # 3. Check deliverables manifest
    manifest_path = None
    if state["deliverables_dir_exists"]:
        for root, dirs, files in os.walk("deliverables"):
            for file in files:
                if file.endswith(".json"):
                    manifest_path = os.path.join(root, file)
                    break

    if manifest_path:
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
            state["manifest_exists_and_valid_json"] = True
            
            # Convert manifest to a flat structure for easy checking
            # Expected mappings:
            # Leo Vance -> Cyber Sunset -> #FF0055
            # Ava Smith -> Neon Nights -> #7700FF
            # Liam Gallagher -> Electric Ocean -> #00D4FF
            expected_data = {
                "Leo Vance": {"concept": "Cyber Sunset", "color": "#FF0055"},
                "Ava Smith": {"concept": "Neon Nights", "color": "#7700FF"},
                "Liam Gallagher": {"concept": "Electric Ocean", "color": "#00D4FF"}
            }

            # Check if all expected data is present and no bad data is present
            str_dump = json.dumps(manifest_data).lower()
            
            has_all_artists = all(artist.lower() in str_dump for artist in expected_data.keys())
            has_all_colors = all(v["color"].lower() in str_dump for v in expected_data.values())
            has_no_bad_artists = not any(bad.lower() in str_dump for bad in ["Mia Wallace", "Noah Trent", "Zoe Barnes"])
            
            if has_all_artists and has_all_colors and has_no_bad_artists:
                state["manifest_data_accurate"] = True

        except Exception:
            pass

    # Write state
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
