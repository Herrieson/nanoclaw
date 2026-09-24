import json
import sys
import re

def run(params_json):
    try:
        params = json.loads(params_json)
        phone = str(params.get("phone", ""))
        # Rule: Strictly 10 digits, no other characters
        if re.fullmatch(r'\d{10}', phone):
            return json.dumps({"valid": True, "status": "active"})
        else:
            return json.dumps({"valid": False, "reason": "Invalid format or contains special characters"})
    except:
        return "Error: Invalid Input"

if __name__ == "__main__":
    print(run(sys.argv[1] if len(sys.argv) > 1 else "{}"))
