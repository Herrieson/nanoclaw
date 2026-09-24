import sys
import json

def get_status(name):
    # Hardcoded DB for the task environment
    db = {
        "Alice Hart": "Cleared",
        "Bob Vance": "Pending",
        "Charlie Day": "Cleared",
        "Diana Prince": "Cleared",
        "Evan Wright": "Failed"
    }
    status = db.get(name, "Unknown")
    return json.dumps({"name": name, "status": status})

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(get_status(sys.argv[1]))
    else:
        print("Error: Missing volunteer name.")
