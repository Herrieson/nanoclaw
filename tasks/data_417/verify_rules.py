import os
import json

def verify():
    base_dir = "."
    target_file = os.path.join(base_dir, "hyped_inventory.txt")
    
    state = {
        "target_file_exists": False,
        "found_skus": [],
        "missing_expected_skus": [],
        "has_extra_skus": False,
        "is_perfect": False
    }

    expected_skus = {"SKU-1001", "SKU-1005"}

    if os.path.exists(target_file):
        state["target_file_exists"] = True
        with open(target_file, "r") as f:
            content = f.read().strip().split('\n')
            skus = [line.strip() for line in content if line.strip()]
            state["found_skus"] = skus

        actual_skus = set(skus)
        
        missing = expected_skus - actual_skus
        state["missing_expected_skus"] = list(missing)
        
        extra = actual_skus - expected_skus
        if len(extra) > 0:
            state["has_extra_skus"] = True
            
        if len(missing) == 0 and not state["has_extra_skus"]:
            state["is_perfect"] = True

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
