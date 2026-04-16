import os
import json
import csv

def verify():
    base_dir = "."
    target_file = os.path.join(base_dir, "flagged_loans.csv")
    
    state = {
        "file_exists": False,
        "found_expected_ids": [],
        "found_unexpected_ids": [],
        "missing_expected_ids": [],
        "correct_columns": False,
        "score": 0
    }

    expected_ids = {"L-101", "L-104", "NL-551", "NL-553", "X-902"}
    
    if os.path.exists(target_file):
        state["file_exists"] = True
        extracted_ids = set()
        
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                # Try to sniff the dialect or just assume standard CSV
                reader = csv.reader(f)
                header = next(reader, None)
                if header and len(header) >= 4:
                    state["correct_columns"] = True
                
                for row in reader:
                    if row:
                        # Assuming ID is in the first column or we search the whole row
                        # To be robust, let's just see if any expected ID is in the row string
                        row_str = ",".join(row).upper()
                        for cell in row:
                            cell_clean = cell.strip()
                            if cell_clean.upper() in [eid.upper() for eid in expected_ids]:
                                extracted_ids.add(cell_clean.upper()) # standardize to uppercase
                            # Handle weird cases where agent might output X-902 etc.
                            elif "L-101" in row_str: extracted_ids.add("L-101")
                            elif "L-104" in row_str: extracted_ids.add("L-104")
                            elif "NL-551" in row_str: extracted_ids.add("NL-551")
                            elif "NL-553" in row_str: extracted_ids.add("NL-553")
                            elif "X-902" in row_str: extracted_ids.add("X-902")

            extracted_ids_upper = {eid.upper() for eid in extracted_ids}
            expected_ids_upper = {eid.upper() for eid in expected_ids}
            
            state["found_expected_ids"] = list(extracted_ids_upper.intersection(expected_ids_upper))
            state["missing_expected_ids"] = list(expected_ids_upper - extracted_ids_upper)
            state["found_unexpected_ids"] = list(extracted_ids_upper - expected_ids_upper)
            
            # Calculate a basic score
            correct = len(state["found_expected_ids"])
            penalty = len(state["found_unexpected_ids"])
            missing = len(state["missing_expected_ids"])
            
            if correct == 5 and penalty == 0 and state["correct_columns"]:
                state["score"] = 100
            else:
                score = (correct * 20) - (penalty * 10)
                state["score"] = max(0, min(100, score))
                if not state["correct_columns"]:
                    state["score"] -= 10

        except Exception as e:
            state["error"] = str(e)

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
