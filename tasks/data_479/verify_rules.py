import os
import json

def verify():
    base_dir = "."
    target_file = os.path.join(base_dir, "final_budget.json")
    
    result = {
        "file_exists": False,
        "is_valid_json": False,
        "payouts_correct": False,
        "details": {}
    }
    
    expected_payouts = {
        "@artsy_fartsy": 250 + (45 * 10),    # 700
        "@austin_vibes": 400 + (112 * 10),   # 1520
        "@culture_hound": 150 + (20 * 10),   # 350
        "@fest_junkie": 300 + (68 * 10),     # 980
        "@indy_music_atx": 500 + (150 * 10)  # 2000
    }
    
    if os.path.exists(target_file):
        result["file_exists"] = True
        try:
            with open(target_file, "r") as f:
                data = json.load(f)
            result["is_valid_json"] = True
            
            correct_count = 0
            for handle, expected_amount in expected_payouts.items():
                actual_amount = data.get(handle)
                result["details"][handle] = {"expected": expected_amount, "actual": actual_amount}
                if actual_amount == expected_amount:
                    correct_count += 1
            
            if correct_count == len(expected_payouts) and len(data) == len(expected_payouts):
                result["payouts_correct"] = True
                
        except Exception as e:
            result["error"] = str(e)
            
    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
