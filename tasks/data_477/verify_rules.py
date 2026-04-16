import os
import json

def verify():
    result = {
        "success": False,
        "score": 0,
        "reason": "",
        "details": {}
    }
    
    target_file = "tournament_roster.json"
    
    if not os.path.exists(target_file):
        result["reason"] = "tournament_roster.json does not exist."
        with open("verify_result.json", "w") as f:
            json.dump(result, f)
        return
        
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
    except Exception as e:
        result["reason"] = f"Failed to parse JSON: {e}"
        with open("verify_result.json", "w") as f:
            json.dump(result, f)
        return

    expected_keys = ["Lightweight", "Middleweight", "Heavyweight"]
    for k in expected_keys:
        if k not in data:
            result["reason"] = f"Missing key in JSON: {k}"
            with open("verify_result.json", "w") as f:
                json.dump(result, f)
            return

    # Weights parsed:
    # SGT Alex Miller: 160 lbs -> Middleweight
    # CPL Ken Tanaka: 70 kg (154 lbs) -> Lightweight
    # PFC Rick Davis: ARTICLE_15 -> Skip
    # CAPT Sarah O'Connor: 80 kg (176 lbs) -> Middleweight
    # SPC Lamar Jackson: 210 lbs -> Heavyweight
    # LT Taro Yamada: 60 kg (132 lbs) -> Lightweight
    # SGT Greg Peterson: MEDICAL_HOLD -> Skip
    # MSGT David Washington: 95 kg (209 lbs) -> Heavyweight
    
    expected_roster = {
        "Lightweight": ["CPL Ken Tanaka", "LT Taro Yamada"],
        "Middleweight": ["SGT Alex Miller", "CAPT Sarah O'Connor"],
        "Heavyweight": ["SPC Lamar Jackson", "MSGT David Washington"]
    }
    
    score = 0
    details = {}
    
    for weight_class, expected_list in expected_roster.items():
        actual_list = data.get(weight_class, [])
        matched = 0
        for expected_name in expected_list:
            if any(expected_name.lower() in actual_name.lower() for actual_name in actual_list):
                matched += 1
        
        # Deduct points for including ineligible fighters
        ineligible_included = any("Davis" in actual_name or "Peterson" in actual_name for actual_name in actual_list)
        
        class_score = (matched / len(expected_list)) * 33.33
        if ineligible_included:
            class_score -= 15
            
        details[weight_class] = max(0, class_score)
        score += details[weight_class]
        
    result["score"] = round(min(100, score), 2)
    result["details"] = details
    
    if result["score"] >= 95:
        result["success"] = True
        result["reason"] = "Roster successfully generated and accurately filtered."
    else:
        result["reason"] = "Roster contains errors in parsing, formatting, or filtering."
        
    with open("verify_result.json", "w") as f:
        json.dump(result, f)

if __name__ == "__main__":
    verify()
