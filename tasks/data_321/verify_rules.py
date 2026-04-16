import os
import json

def verify():
    base_dir = "."
    dist_file = os.path.join(base_dir, "distribution_list.json")
    final_file = os.path.join(base_dir, "final_cleared_list.json")
    
    state = {
        "dist_file_exists": False,
        "final_file_exists": False,
        "dist_logic_correct": False,
        "final_logic_correct": False,
        "dist_content": None,
        "final_content": None
    }
    
    # Expected Inventory:
    # Lisinopril: 50 + 15 = 65
    # Metformin: 100
    # Amoxicillin: 20
    
    # Expected Distribution (before safety limits):
    # John: 30 Lisi (65-30=35 left)
    # Jane: 100 Metf (requested 120, only 100 avail. 0 left)
    # Bob: 20 Amox (requested 30, only 20 avail. 0 left)
    # Alice: 35 Lisi (requested 40, only 35 avail. 0 left)
    # Charlie: 0 Metf (requested 20, 0 avail)
    
    expected_dist = {
        "John Doe": 30,
        "Jane Smith": 100,
        "Bob Lee": 20,
        "Alice Joy": 35,
        "Charlie Brown": 0
    }
    
    # Expected Final (after safety limits):
    # Lisi limit 30, Metf limit 90, Amox limit 40
    # John: min(30, 30) = 30
    # Jane: min(100, 90) = 90
    # Bob: min(20, 40) = 20
    # Alice: min(35, 30) = 30
    # Charlie: min(0, 90) = 0
    
    expected_final = {
        "John Doe": 30,
        "Jane Smith": 90,
        "Bob Lee": 20,
        "Alice Joy": 30,
        "Charlie Brown": 0
    }

    if os.path.exists(dist_file):
        state["dist_file_exists"] = True
        try:
            with open(dist_file, 'r') as f:
                dist_data = json.load(f)
            state["dist_content"] = dist_data
            if dist_data == expected_dist:
                state["dist_logic_correct"] = True
        except Exception:
            pass

    if os.path.exists(final_file):
        state["final_file_exists"] = True
        try:
            with open(final_file, 'r') as f:
                final_data = json.load(f)
            state["final_content"] = final_data
            if final_data == expected_final:
                state["final_logic_correct"] = True
        except Exception:
            pass

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
