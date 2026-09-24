import os
import json

def verify():
    state = {
        "archive_dir_exists": False,
        "bad_files_archived": False,
        "good_files_kept": False,
        "manifest_valid": False,
        "pantone_names_included": False
    }

    state["archive_dir_exists"] = os.path.isdir("archive")
    
    # Check archiving logic
    bad_files = ["ad_02.bin", "ad_03.bin", "ad_05.bin"]
    good_files = ["ad_01.bin", "ad_04.bin", "ad_06.bin"]

    if state["archive_dir_exists"]:
        archived = all(os.path.exists(os.path.join("archive", f)) for f in bad_files)
        not_archived = all(not os.path.exists(os.path.join("archive", f)) for f in good_files)
        state["bad_files_archived"] = archived and not_archived

    if os.path.isdir("campaign_assets"):
        kept = all(os.path.exists(os.path.join("campaign_assets", f)) for f in good_files)
        removed = all(not os.path.exists(os.path.join("campaign_assets", f)) for f in bad_files)
        state["good_files_kept"] = kept and removed

    # Check manifest
    manifest_path = "deliverables/manifest.json"
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r") as f:
                data = json.load(f)
            
            # Must have 3 entries
            if len(data) == 3 or (isinstance(data, dict) and len(data.keys()) == 3):
                state["manifest_valid"] = True
                
                # Check for Pantone content (case insensitive check)
                content = json.dumps(data).lower()
                pantone_keywords = ["pantone", "magenta", "violet", "blue"] 
                if any(kw in content for kw in pantone_keywords):
                    state["pantone_names_included"] = True
        except:
            pass

    with open("state.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
