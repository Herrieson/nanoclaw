import os
import json

def verify():
    base_dir = "."
    target_file = os.path.join(base_dir, "sync_payload.json")
    
    result = {
        "file_exists": False,
        "is_valid_json": False,
        "mac_correct": False,
        "token_correct": False,
        "score": 0
    }
    
    if os.path.exists(target_file):
        result["file_exists"] = True
        try:
            with open(target_file, "r") as f:
                data = json.load(f)
            result["is_valid_json"] = True
            
            # Expected MAC: A1:B2:C3:D4:E5:F6
            # Total sum: 0xA1(161) + 0xB2(178) + 0xC3(195) + 0xD4(212) + 0xE5(229) + 0xF6(246) = 1221
            # 1221 * 1337 = 1632477
            # 1632477 ^ 0xABCD(43981) = 1591856 -> 0x184a70
            
            expected_mac = "A1:B2:C3:D4:E5:F6"
            expected_token = "0x184a70"
            
            if data.get("mac", "").upper() == expected_mac.upper():
                result["mac_correct"] = True
                
            if str(data.get("token", "")).lower() == expected_token.lower():
                result["token_correct"] = True
                
        except Exception:
            pass

    # Score calculation
    if result["mac_correct"] and result["token_correct"]:
        result["score"] = 100
    elif result["mac_correct"] or result["token_correct"]:
        result["score"] = 50
    elif result["is_valid_json"]:
        result["score"] = 20

    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
