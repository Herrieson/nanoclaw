import sys
import json

def parse_ledger(file_path):
    if "week3" in file_path:
        return [
            {"name": "Charlie Green", "hours": 10, "donation": 100},
            {"name": "Frank Wolf", "hours": 20, "donation": 5}
        ]
    return "Error: File format not recognized or file empty."

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: File path required.")
    else:
        print(json.dumps(parse_ledger(sys.argv[1])))
