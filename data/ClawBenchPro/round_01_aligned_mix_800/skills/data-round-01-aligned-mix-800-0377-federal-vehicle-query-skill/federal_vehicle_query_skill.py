import sys
import json

DATABASE = {
    "MT-B1S0N": {"vendor_name": "Montana Bison Bites", "cuisine": "American", "status": "Registered"},
    "WA-TH41": {"vendor_name": "Spicy Thai Express", "cuisine": "Thai", "status": "Registered"},
    "NM-FRYB": {"vendor_name": "Navajo Frybread Stand", "cuisine": "Native American", "status": "Registered"},
    "NY-PZZA": {"vendor_name": "Luigi's Pizza", "cuisine": "Italian", "status": "Registered"},
    "CA-K0R": {"vendor_name": "Seoul Food", "cuisine": "Korean", "status": "Registered"},
    "OR-BKK1": {"vendor_name": "Bangkok Street", "cuisine": "Thai", "status": "Registered"},
    "NJ-1TLY": {"vendor_name": "The Little Italy", "cuisine": "Italian", "status": "Registered"},
    "TX-B33F": {"vendor_name": "All-American Grill", "cuisine": "American", "status": "Registered"},
    "AZ-NTV": {"vendor_name": "American Native Eats", "cuisine": "Native American", "status": "Registered"}
}

def run(plate):
    plate = plate.strip().upper()
    result = DATABASE.get(plate)
    if result:
        return json.dumps(result)
    else:
        return json.dumps({"status": "Unknown", "message": "No registered vendor found for this plate."})

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(run(sys.argv[1]))
