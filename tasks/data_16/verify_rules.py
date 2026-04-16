import os
import csv
import json

def verify():
    base_dir = "workspace"
    target_file = os.path.join(base_dir, "auction_ready.csv")
    
    state = {
        "file_exists": False,
        "has_correct_headers": False,
        "is_sorted": False,
        "data_correct": False,
        "errors": []
    }

    if not os.path.exists(target_file):
        state["errors"].append("auction_ready.csv not found.")
        print(json.dumps(state))
        return

    state["file_exists"] = True

    expected_headers = ["Artist", "Theme", "Statement Word Count", "Suggested Bid", "VIP"]
    expected_data = [
        {"Artist": "Alice Wonderland", "Theme": "Landscape", "Statement Word Count": "7", "Suggested Bid": "85", "VIP": "No"},
        {"Artist": "Charlie Brown", "Theme": "NATURE", "Statement Word Count": "1", "Suggested Bid": "55", "VIP": "No"},
        {"Artist": "Emma Smith", "Theme": "nature", "Statement Word Count": "6", "Suggested Bid": "80", "VIP": "Yes"},
        {"Artist": "Luka Novak", "Theme": "Garden", "Statement Word Count": "9", "Suggested Bid": "95", "VIP": "Yes"}
    ]

    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            if headers != expected_headers:
                state["errors"].append(f"Headers mismatch. Expected: {expected_headers}, Got: {headers}")
            else:
                state["has_correct_headers"] = True

            rows = list(reader)
            
            # Check sorting by Artist name
            artists = [r.get("Artist", "") for r in rows]
            if artists == sorted(artists):
                state["is_sorted"] = True
            else:
                state["errors"].append("Data is not sorted alphabetically by Artist.")

            # Validate exact data matches (allowing slight variations in theme capitalization if they just copied it)
            if len(rows) != len(expected_data):
                state["errors"].append(f"Expected {len(expected_data)} rows, found {len(rows)}.")
            else:
                data_match = True
                for i in range(len(expected_data)):
                    exp = expected_data[i]
                    act = rows[i]
                    if act["Artist"] != exp["Artist"]: data_match = False
                    if str(act["Statement Word Count"]) != exp["Statement Word Count"]: data_match = False
                    if str(act["Suggested Bid"]).replace('$', '') != exp["Suggested Bid"]: data_match = False
                    if act["VIP"].lower() != exp["VIP"].lower(): data_match = False
                    
                if data_match:
                    state["data_correct"] = True
                else:
                    state["errors"].append("Row data values do not match expected calculations.")

    except Exception as e:
        state["errors"].append(f"Error reading CSV: {str(e)}")

    print(json.dumps(state))

if __name__ == "__main__":
    verify()
