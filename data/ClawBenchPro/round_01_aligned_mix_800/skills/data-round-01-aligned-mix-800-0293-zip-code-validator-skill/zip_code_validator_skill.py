import sys
import json

def validate_zip(zip_code):
    # Mock database
    discontinued_zips = ["99999", "00000", "12345"]
    active_zips = ["90210", "33101", "80000", "90001"]
    
    zip_code = str(zip_code).strip()
    
    if len(zip_code) != 5 or not zip_code.isdigit():
        return json.dumps({"zip": zip_code, "status": "Invalid Format"})
    
    if zip_code in discontinued_zips:
        return json.dumps({"zip": zip_code, "status": "Discontinued"})
    
    return json.dumps({"zip": zip_code, "status": "Active"})

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(validate_zip(sys.argv[1]))
    else:
        print("Error: No ZIP code provided.")
