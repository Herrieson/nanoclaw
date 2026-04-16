import os
import json

def verify():
    base_dir = "."
    report_path = os.path.join(base_dir, "reports", "classic_readers.json")
    
    state = {
        "report_exists": False,
        "is_valid_json": False,
        "expected_data_matches": False,
        "details": {}
    }
    
    # Expected calculations:
    # Classics: Moby Dick, The Great Gatsby, 1984, The Odyssey, Pride and Prejudice
    # Alice: Moby Dick (120) + 1984 (30) = 150m = 2.5 hours
    # Bob: The Great Gatsby (45) + The Odyssey (15) = 60m = 1.0 hours
    # Diana: 1984 (90) = 90m = 1.5 hours
    # Eve: Moby Dick (60) = 60m = 1.0 hours
    # Grace: Pride and Prejudice (180) = 180m = 3.0 hours
    # Charlie, Frank, Henry read non-classics.
    
    expected_data = {
        "Alice": 2.5,
        "Bob": 1.0,
        "Diana": 1.5,
        "Eve": 1.0,
        "Grace": 3.0
    }
    
    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                actual_data = json.load(f)
            state["is_valid_json"] = True
            
            # Check if dict matches expected exactly
            if actual_data == expected_data:
                state["expected_data_matches"] = True
            else:
                state["details"]["actual_data"] = actual_data
                state["details"]["expected_data"] = expected_data
        except Exception as e:
            state["details"]["error"] = str(e)
            
    # Save the output for the LLM judge
    with open(os.path.join(base_dir, "verify_result.json"), "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
