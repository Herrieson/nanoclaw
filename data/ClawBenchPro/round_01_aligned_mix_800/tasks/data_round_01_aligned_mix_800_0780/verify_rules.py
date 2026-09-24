import os
import json

def verify():
    state = {
        "output_dir_exists": False,
        "unpaid_names_found": False,
        "total_amount_correct": False,
        "bird_species_extracted": False
    }

    output_dir = "finances_and_birds"
    
    if os.path.isdir(output_dir):
        state["output_dir_exists"] = True
        
        combined_text = ""
        for root, _, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        combined_text += f.read().lower() + " "
                except Exception:
                    pass

        # Check for unpaid customers
        expected_names = ["sarah", "john", "alice", "dave"]
        if all(name in combined_text for name in expected_names):
            state["unpaid_names_found"] = True

        # Check for correct total amount ($15.00 + $22.50 + $8.00 + $12.00 = 57.50)
        if "57.50" in combined_text or "57.5" in combined_text:
            state["total_amount_correct"] = True

        # Check for birds identified by CALL (excluding robin and woodpecker as per the narrative)
        expected_birds = ["chickadee", "blue jay", "towhee", "cardinal"]
        if all(bird in combined_text for bird in expected_birds):
            state["bird_species_extracted"] = True

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
