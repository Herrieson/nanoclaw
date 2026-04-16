import os
import json
import csv

def verify():
    base_dir = "."
    target_csv = os.path.join(base_dir, "sync_folder", "recovered_samples.csv")
    
    state = {
        "file_exists": False,
        "has_header": False,
        "correct_records_count": 0,
        "details": []
    }

    expected_data = {
        "Maria G.": {"Test": "CBC", "Tube_Color": "Lavender", "Barcode": "BCD-19283"},
        "John Doe": {"Test": "CMP", "Tube_Color": "Gold", "Barcode": "BCD-55421"},
        "Sarah T.": {"Test": "PT", "Tube_Color": "Light Blue", "Barcode": "BCD-99012"},
        "Mark W.": {"Test": "Lactic", "Tube_Color": "Grey", "Barcode": "BCD-33214"},
        "Elena R.": {"Test": "Lipid", "Tube_Color": "Tiger Top", "Barcode": "BCD-77654"}
    }

    if os.path.exists(target_csv):
        state["file_exists"] = True
        try:
            with open(target_csv, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if header and [h.strip() for h in header] == ["Patient_Name", "Test", "Tube_Color", "Barcode"]:
                    state["has_header"] = True
                
                for row in reader:
                    if len(row) == 4:
                        p_name, test, color, barcode = [x.strip() for x in row]
                        if p_name in expected_data:
                            exp = expected_data[p_name]
                            is_correct = (test == exp["Test"] and color == exp["Tube_Color"] and barcode == exp["Barcode"])
                            if is_correct:
                                state["correct_records_count"] += 1
                            state["details"].append(f"{p_name}: {'Correct' if is_correct else 'Mismatch'}")
                        else:
                            state["details"].append(f"{p_name}: Unknown Patient")
        except Exception as e:
            state["details"].append(f"Error reading CSV: {str(e)}")

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
