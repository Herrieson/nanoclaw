import os
import csv
import json

def verify():
    base_dir = "."
    target_file = os.path.join(base_dir, "final_grades.csv")
    
    state = {
        "file_exists": False,
        "header_correct": False,
        "row_count": 0,
        "alice_correct": False,
        "bob_correct": False,
        "charlie_correct": False,
        "diana_correct": False,
        "all_correct": False
    }

    if os.path.exists(target_file):
        state["file_exists"] = True
        try:
            with open(target_file, "r") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if header and [h.strip() for h in header] == ["ID", "Name", "Final_Score"]:
                    state["header_correct"] = True
                
                rows = list(reader)
                state["row_count"] = len(rows)
                
                # Expected:
                # 101, Alice, 90 (85+5)
                # 102, Bob, 92
                # 103, Charlie, 83 (78+5)
                # 104, Diana, 88
                
                for row in rows:
                    if len(row) >= 3:
                        r_id = row[0].strip()
                        r_score = row[2].strip()
                        
                        if r_id == "101" and r_score == "90":
                            state["alice_correct"] = True
                        elif r_id == "102" and r_score == "92":
                            state["bob_correct"] = True
                        elif r_id == "103" and r_score == "83":
                            state["charlie_correct"] = True
                        elif r_id == "104" and r_score == "88":
                            state["diana_correct"] = True
                            
            if state["alice_correct"] and state["bob_correct"] and state["charlie_correct"] and state["diana_correct"]:
                state["all_correct"] = True
                
        except Exception as e:
            state["error"] = str(e)

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
