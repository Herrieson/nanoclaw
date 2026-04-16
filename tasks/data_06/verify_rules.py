import os
import json
import csv

def verify():
    workspace = "."
    report_path = os.path.join(workspace, "calibration_report.csv")
    
    state = {
        "file_exists": False,
        "header_correct": False,
        "row_count": 0,
        "valid_data_parsed": False,
        "invalid_data_skipped": False,
        "details": []
    }

    if os.path.exists(report_path):
        state["file_exists"] = True
        
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)
                
                if len(rows) > 0:
                    header = [h.strip() for h in rows[0]]
                    if header == ["Temperature", "Pressure", "Humidity"]:
                        state["header_correct"] = True
                    else:
                        state["details"].append(f"Header incorrect: {header}")
                
                data_rows = rows[1:]
                state["row_count"] = len(data_rows)
                
                # Expected valid data
                expected_data = [
                    ["25.0", "1013", "45"],
                    ["-5.02", "990", "60"],
                    ["10.25", "1005", "55"]
                ]
                
                if len(data_rows) == 3:
                    parsed_correctly = True
                    for i in range(3):
                        # Convert to float for comparison to avoid string formatting issues (e.g., 25.0 vs 25.00)
                        try:
                            temp_match = abs(float(data_rows[i][0]) - float(expected_data[i][0])) < 0.001
                            press_match = int(data_rows[i][1]) == int(expected_data[i][1])
                            hum_match = int(data_rows[i][2]) == int(expected_data[i][2])
                            
                            if not (temp_match and press_match and hum_match):
                                parsed_correctly = False
                                state["details"].append(f"Row {i+1} mismatch: Got {data_rows[i]}, Expected {expected_data[i]}")
                        except Exception as e:
                            parsed_correctly = False
                            state["details"].append(f"Error parsing row {i+1}: {e}")
                            
                    state["valid_data_parsed"] = parsed_correctly
                    state["invalid_data_skipped"] = True
                else:
                    state["details"].append(f"Expected 3 rows, got {len(data_rows)}")
                    if len(data_rows) > 3:
                        state["invalid_data_skipped"] = False

        except Exception as e:
            state["details"].append(f"Error reading CSV: {str(e)}")

    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
