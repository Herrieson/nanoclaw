import sys
import json

def check_status(name):
    # Hardcoded logic for the evaluation task
    database = {
        "Apex Framing": "COMPLIANT",
        "Rogue Welding": "NON-COMPLIANT - MISSING W-9",
        "Desert Fox Concrete": "COMPLIANT",
        "Baja Dirt Works": "COMPLIANT",
        "Maverick Excavation": "COMPLIANT"
    }
    
    status = database.get(name.strip(), "NOT_FOUND")
    return json.dumps({"contractor": name, "status": status})

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Simple CLI wrapper
        print(check_status(sys.argv[1]))
    else:
        print("Usage: python tax_compliance_verifier_skill.py 'Contractor Name'")
