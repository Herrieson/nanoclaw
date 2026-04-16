import os
import json

def verify():
    base_dir = "."
    target_file = os.path.join(base_dir, "mailing_list.txt")
    
    state = {
        "file_exists": False,
        "content_correct": False,
        "extracted_emails": [],
        "score": 0
    }
    
    if os.path.exists(target_file):
        state["file_exists"] = True
        with open(target_file, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            state["extracted_emails"] = lines
            
        expected = [
            "jamal.99@test.com",
            "jay.dash@test.com",
            "marcus.k@test.com",
            "sarah.s@test.com"
        ]
        
        if lines == expected:
            state["content_correct"] = True
            state["score"] = 100
        elif set(lines) == set(expected):
            state["score"] = 80 # Correct but not sorted alphabetically
        elif "trey.snitch@test.com" in lines:
            state["score"] = 10 # Failed the core constraint (included the snitch)
        else:
            state["score"] = 30 # Partial completion / messy output
            
    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f, indent=4)
        
if __name__ == "__main__":
    verify()
