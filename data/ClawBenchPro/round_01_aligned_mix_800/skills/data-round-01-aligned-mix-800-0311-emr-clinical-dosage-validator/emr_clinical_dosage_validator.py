import sys
import json

def resolve_code(code):
    mapping = {
        "D-CODE: H-750": "7500 units",
        "D-CODE: H-1000": "10000 units",
        "D-CODE: H-500": "5000 units"
    }
    # Standardize input
    clean_code = code.strip().upper()
    return mapping.get(clean_code, "Error: Unknown Clinical Code. Please contact Pharmacy.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(resolve_code(sys.argv[1]))
