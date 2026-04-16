import os
import json
import csv

def verify():
    base_dir = "."
    output_file = os.path.join(base_dir, "portfolio_forecast.csv")
    
    state = {
        "output_file_exists": False,
        "has_correct_columns": False,
        "contains_only_targets": False,
        "correct_values": False,
        "sorted_correctly": False,
        "errors": []
    }

    expected_profits = {
        "Lettuce Entertain You": (8000+8200+8500+9000) - (6500+6600+6800+7000), # 33700 - 26900 = 6800
        "Boka Restaurant Group": (2500+2600+2700+3000) - (1900+2000+2100+2200), # 10800 - 8200 = 2600
        "Alinea Group": (1200+1300+1400+1600) - (800+850+900+1000), # 5500 - 3550 = 1950
        "Smyth and The Loyalist": (900+950+1000+1200) - (700+720+750+800) # 4050 - 2970 = 1080
    }
    
    if os.path.exists(output_file):
        state["output_file_exists"] = True
        try:
            with open(output_file, "r") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                
                if header == ["Company_Name", "Projected_Profit"]:
                    state["has_correct_columns"] = True
                else:
                    state["errors"].append(f"Incorrect header: {header}")

                rows = list(reader)
                
                parsed_data = []
                for row in rows:
                    if len(row) == 2:
                        try:
                            parsed_data.append((row[0], float(row[1])))
                        except ValueError:
                            state["errors"].append(f"Non-numeric profit value: {row[1]}")
                
                actual_companies = set([r[0] for r in parsed_data])
                expected_companies = set(expected_profits.keys())
                
                if actual_companies == expected_companies:
                    state["contains_only_targets"] = True
                else:
                    state["errors"].append(f"Companies mismatch. Found: {actual_companies}")

                values_correct = True
                for comp, prof in parsed_data:
                    if comp in expected_profits:
                        if abs(expected_profits[comp] - prof) > 0.01:
                            values_correct = False
                            state["errors"].append(f"Incorrect profit for {comp}: expected {expected_profits[comp]}, got {prof}")
                
                if values_correct and state["contains_only_targets"]:
                    state["correct_values"] = True

                # Check sorting (descending)
                profits = [r[1] for r in parsed_data]
                if profits == sorted(profits, reverse=True) and len(profits) > 0:
                    state["sorted_correctly"] = True
                else:
                    state["errors"].append("Data is not sorted in descending order.")

        except Exception as e:
            state["errors"].append(f"Error reading CSV: {str(e)}")

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
