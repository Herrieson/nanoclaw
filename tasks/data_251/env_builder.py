import os
import zipfile
import shutil

def build_env():
    base_dir = "assets/data_251/workspace"
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    
    os.makedirs(os.path.join(base_dir, "logs/october"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "art_projects/canvas_ideas"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "misc_notes"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "backups"), exist_ok=True)

    # File 1: Standard log
    with open(os.path.join(base_dir, "logs/october/downtown_10_12_23.txt"), "w") as f:
        f.write("Site: Downtown Project\nDate: 2023-10-12\n\nNotes:\nChecked the scaffolding on the north side. Looks okay.\nWait, CRITICAL: Missing fall protection harnesses on level 4.\nReminded the crew.")

    # File 2: Mixed with art notes
    with open(os.path.join(base_dir, "art_projects/canvas_ideas/mixed_thoughts.md"), "w") as f:
        f.write("# Ideas for the new mural\n- Use lots of cobalt blue.\n- Rough textures.\n\nOh, forgot to log the Riverside Complex walk-through from 10-15-2023.\nSaw some bad stuff. CRITICAL: Exposed electrical wiring near the main water line.\nNeed to call the sparky tomorrow.")

    # File 3: In a zip file
    zip_path = os.path.join(base_dir, "backups/old_scans.zip")
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.writestr("eastside_audit_10_20.txt", "Location: Eastside Clinic\nDate: Oct 20, 2023\n\nWalked the perimeter.\nCRITICAL: Unshored trench deeper than 5 feet on the south elevation.\nStopped work immediately.")
        zf.writestr("grocery_list.txt", "Milk\nEggs\nCanvas\nTurpentine")

    # Decoy files
    with open(os.path.join(base_dir, "logs/october/site_charlie_fine.txt"), "w") as f:
        f.write("Site Charlie. All good here. No critical issues today.")

if __name__ == "__main__":
    build_env()
