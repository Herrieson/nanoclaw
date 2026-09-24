import sys
import json

# Approved members in the "Cloud Database"
APPROVED_MEMBERS = [
    "Alice Henderson", "Bob Jenkins", "Clara Smith", 
    "Diane O'Connor", "Earl Thompson"
]

def check_member(name):
    if not name:
        return "Error: No name provided."
    
    name = name.strip()
    if name in APPROVED_MEMBERS:
        return json.dumps({"name": name, "status": "APPROVED", "role": "Vested Member"})
    else:
        return json.dumps({"name": name, "status": "UNAUTHORIZED", "warning": "Not found in church records."})

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python member_identity_validator_skill.py <name>")
    else:
        print(check_member(sys.argv[1]))
