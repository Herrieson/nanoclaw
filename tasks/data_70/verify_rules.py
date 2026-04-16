import os
import json
import csv

def verify():
    result = {
        "score": 0,
        "details": [],
        "file_exists": False,
        "header_correct": False,
        "rows_correct": False,
        "values_correct": False
    }

    target_file = "home_lab/high_gc_sequences.csv"
    
    if not os.path.exists(target_file):
        result["details"].append("The expected output file 'high_gc_sequences.csv' was not found in the home_lab directory.")
        return result
    
    result["file_exists"] = True
    
    try:
        with open(target_file, "r") as f:
            reader = csv.reader(f)
            rows = list(reader)
            
            if not rows:
                result["details"].append("The CSV file is empty.")
                return result
                
            header = rows[0]
            if header == ["ID", "GC_Content"]:
                result["header_correct"] = True
            else:
                result["details"].append(f"Incorrect header: {header}. Expected ['ID', 'GC_Content'].")
                
            data = rows[1:]
            
            expected_data = {
                "SEQ_002": "80.00",
                "SEQ_004": "100.00",
                "SEQ_007": "58.33"
            }
            
            actual_data = {}
            for row in data:
                if len(row) == 2:
                    actual_data[row[0]] = row[1]
                    
            if set(actual_data.keys()) == set(expected_data.keys()):
                result["rows_correct"] = True
            else:
                result["details"].append(f"Incorrect rows. Found IDs: {list(actual_data.keys())}, Expected: {list(expected_data.keys())}.")
                
            all_values_correct = True
            for k, v in expected_data.items():
                if actual_data.get(k) != v:
                    all_values_correct = False
                    result["details"].append(f"Incorrect GC_Content for {k}. Found {actual_data.get(k)}, Expected {v}.")
                    
            if all_values_correct:
                result["values_correct"] = True
                
    except Exception as e:
        result["details"].append(f"Error parsing CSV: {str(e)}")

    # Calculate final score out of 100
    score = 0
    if result["file_exists"]: score += 20
    if result["header_correct"]: score += 20
    if result["rows_correct"]: score += 30
    if result["values_correct"]: score += 30
    
    result["score"] = score
    if score == 100:
        result["details"].append("All verifications passed successfully.")

    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
