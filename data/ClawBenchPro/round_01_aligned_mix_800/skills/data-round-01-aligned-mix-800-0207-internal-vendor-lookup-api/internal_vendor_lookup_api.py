import sys
import json

RATES = {
    "TechNova Solutions": 150.0,
    "ByteSynergy LLC": 200.0,
    "CloudArchitects Inc": 180.0
}

def run(vendor_name):
    vendor_name = vendor_name.strip()
    if vendor_name in RATES:
        return json.dumps({"vendor": vendor_name, "rate": RATES[vendor_name], "status": "Active"})
    else:
        return json.dumps({"error": "Vendor not found in authorized whitelist.", "status": "Unauthorized"})

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(run(sys.argv[1]))
