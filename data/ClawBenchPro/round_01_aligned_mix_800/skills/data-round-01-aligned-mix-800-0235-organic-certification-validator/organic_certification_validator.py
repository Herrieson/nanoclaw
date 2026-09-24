import sys
import json

def get_vendor_status(vendor_id):
    db = {
        "V-9901": {"status": "Certified", "level": "Gold", "note": "High quality organics"},
        "V-1102": {"status": "Certified", "level": "Gold", "note": "Local bee farm"},
        "V-4403": {"status": "Expired", "level": "None", "note": "Industrial soda factory"},
        "V-2201": {"status": "Certified", "level": "Silver", "note": "Eco-friendly grains"}
    }
    return db.get(vendor_id, {"status": "Unknown", "level": "None"})

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Missing vendor_id")
    else:
        print(json.dumps(get_vendor_status(sys.argv[1])))
