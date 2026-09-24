import sys
import json

def analyze(code):
    grading_map = {
        "KN-0": "Furniture Grade",
        "CR-1": "Furniture Grade",
        "RO-9": "Rejected",
        "SP-5": "Rejected"
    }
    status = grading_map.get(code.upper(), "Rejected")
    return json.dumps({"status": status, "code": code, "notes": "Automated grading system response."})

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(analyze(sys.argv[1]))
    else:
        print(json.dumps({"error": "Missing defect_code"}))
