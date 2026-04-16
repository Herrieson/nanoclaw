import os
import json
import csv

def verify():
    base_dir = "."
    target_file = os.path.join(base_dir, "urgent_cats.csv")
    result = {
        "file_exists": False,
        "valid_csv": False,
        "found_cat_772": False,
        "found_fel_091": False,
        "found_cat_111": False,
        "found_cat_333": False,
        "no_dogs": True,
        "no_healthy_cats": True,
        "no_wrong_county": True,
        "correct_columns": False
    }

    if os.path.exists(target_file):
        result["file_exists"] = True
        try:
            with open(target_file, "r") as f:
                reader = csv.reader(f)
                headers = next(reader, [])
                
                # Check for required keywords in headers loosely
                headers_lower = [h.lower() for h in headers]
                if any('id' in h for h in headers_lower) and any('loc' in h for h in headers_lower) and any('injur' in h or 'desc' in h or 'cond' in h for h in headers_lower):
                    result["correct_columns"] = True

                content = " ".join([" ".join(row) for row in reader]).lower()
                result["valid_csv"] = True

                # Check targets
                if "cat-772" in content: result["found_cat_772"] = True
                if "fel-091" in content: result["found_fel_091"] = True
                if "cat-111" in content: result["found_cat_111"] = True # From corrupt JSON
                if "cat-333" in content: result["found_cat_333"] = True # From CSV

                # Check negatives
                if "dog" in content or "canine" in content: result["no_dogs"] = False
                if "cat-888" in content: result["no_healthy_cats"] = False
                if "cat-909" in content or "cat-222" in content: result["no_wrong_county"] = False

        except Exception as e:
            pass

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
