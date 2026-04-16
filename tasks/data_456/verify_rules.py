import os
import json
import re

def verify():
    base_dir = "."
    result = {
        "work_total_correct": False,
        "carne_asada_dir_exists": False,
        "correct_recipes_copied": False,
        "no_junk_copied": False
    }

    # 1. Check work expenses
    # Expected: log_march_22.txt (CON-Site) -> $25.00, $15.50
    # Expected: notes_misc.log (jefe's tools) -> $105.00, $40.00, $145.00
    # Total sum: 25.00 + 15.50 + 105.00 + 40.00 + 145.00 = 330.50
    total_file = os.path.join(base_dir, "work_total.txt")
    if os.path.exists(total_file):
        with open(total_file, "r") as f:
            content = f.read().strip()
            # extract the number
            match = re.search(r'330\.50', content)
            if match:
                result["work_total_correct"] = True

    # 2. Check recipes
    prep_dir = os.path.join(base_dir, "carne_asada_prep")
    if os.path.isdir(prep_dir):
        result["carne_asada_dir_exists"] = True
        
        files_in_dir = set(os.listdir(prep_dir))
        expected_files = {"salsa_verde.txt", "tamales_prep.md"}
        
        if expected_files.issubset(files_in_dir):
            result["correct_recipes_copied"] = True
            
        junk_files = {"burger_recipe.txt", "shopping_list.txt", "corrupted_img.bin", "log_march_22.txt", "notes_misc.log", "random_thoughts.txt"}
        if len(files_in_dir.intersection(junk_files)) == 0:
            result["no_junk_copied"] = True

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
