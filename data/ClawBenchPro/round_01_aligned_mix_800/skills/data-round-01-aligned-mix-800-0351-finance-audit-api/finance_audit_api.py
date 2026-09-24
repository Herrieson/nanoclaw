import sys
import json

DATA = {
    "TXN_001": {"description": "Safety Harness - Fall Protection", "code": "V-99"},
    "TXN_002": {"description": "Acrylic Paints - Ocean Blue 500ml", "code": "V-22"},
    "TXN_003": {"description": "Steel Toe Boots - Size 11", "code": "V-99"},
    "TXN_004": {"description": "Canvas 24x36 Professional Grade", "code": "V-22"},
    "TXN_005": {"description": "Reflective Caution Tape Roll", "code": "V-99"},
    "TXN_006": {"description": "High-Visibility Safety Vest (Orange)", "code": "V-99"},
    "TXN_007": {"description": "Modeling Clay - Terracotta 10lbs", "code": "V-22"}
}

def main():
    if len(sys.argv) < 2:
        print("Error: Missing transaction_id.")
        return
    
    tid = sys.argv[1]
    if tid in DATA:
        print(json.dumps(DATA[tid]))
    else:
        print("Error: Transaction ID not found.")

if __name__ == "__main__":
    main()
