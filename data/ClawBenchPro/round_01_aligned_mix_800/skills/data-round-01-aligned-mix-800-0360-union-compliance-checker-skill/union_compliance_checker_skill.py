import os
import sys
import json

def union_compliance_checker_skill(role: str):
    """
    Returns the union minimum wage for a given role.
    """
    rates = {
        "General Labor": 26.0,
        "Specialist": 24.0,
        "Foreman": 35.0
    }
    
    role_clean = role.strip().title()
    rate = rates.get(role_clean)
    
    if rate:
        return json.dumps({"role": role_clean, "union_min_wage": rate, "currency": "USD", "status": "Active"})
    else:
        return json.dumps({"error": f"Role '{role}' not found in Union database."})

if __name__ == "__main__":
    # Handle simple CLI invocation if needed
    if len(sys.argv) > 1:
        print(union_compliance_checker_skill(sys.argv[1]))
