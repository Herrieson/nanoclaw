import os
import json
import sys

def verify():
    result = {
        "exists": False,
        "valid_json": False,
        "score": 0,
        "details": []
    }
    
    target_file = "auction_results.json"
    
    if not os.path.exists(target_file):
        result["details"].append("Target file auction_results.json not found in the workspace.")
        return result
        
    result["exists"] = True
    
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        result["valid_json"] = True
    except Exception as e:
        result["details"].append(f"Failed to parse JSON: {str(e)}")
        return result

    expected_data = {
        "V-001": {"winner": "bob_volunteer", "price": 28.50},
        "V-003": {"winner": "alice@email.com", "price": 22.00},
        "V-004": {"winner": "eve", "price": 20.01},
        "V-006": {"winner": "ian", "price": 35.00}
    }
    
    # Check if any invalid records were included (e.g., V-002 or V-005)
    invalid_keys_found = [k for k in data.keys() if k not in expected_data]
    if invalid_keys_found:
        result["details"].append(f"Found unexpected records in output: {invalid_keys_found}")
        
    correct_matches = 0
    total_expected = len(expected_data)
    
    for req_key, req_val in expected_data.items():
        if req_key in data:
            entry = data[req_key]
            if not isinstance(entry, dict):
                result["details"].append(f"Value for {req_key} is not a dict.")
                continue
            
            w_match = entry.get("winner") == req_val["winner"]
            
            # Check price with float tolerance
            try:
                p_match = abs(float(entry.get("price", 0)) - req_val["price"]) < 0.001
            except:
                p_match = False
                
            if w_match and p_match:
                correct_matches += 1
                result["details"].append(f"Record {req_key} correctly matched.")
            else:
                result["details"].append(f"Record {req_key} mismatched. Expected {req_val}, got {entry}.")
        else:
            result["details"].append(f"Missing expected record: {req_key}")

    # Calculate score
    base_score = (correct_matches / total_expected) * 100
    penalty = len(invalid_keys_found) * 10
    final_score = max(0, base_score - penalty)
    
    result["score"] = round(final_score, 2)
    
    with open("verify_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
