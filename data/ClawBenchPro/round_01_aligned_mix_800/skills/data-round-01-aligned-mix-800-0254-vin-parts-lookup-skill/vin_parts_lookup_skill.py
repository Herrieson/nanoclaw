import sys
import json

PARTS_DB = {
    "CH-101": "Oil Filter (High-Efficiency)",
    "CH-202": "Semi-Metallic Brake Pads",
    "CH-303": "120A Alternator",
    "CH-404": "All-Season Wiper Blades",
    "CH-505": "Iridium Spark Plugs",
    "CH-606": "Heavy Duty Battery (Group 24)"
}

def lookup(part_id):
    name = PARTS_DB.get(part_id.upper())
    if name:
        return json.dumps({"status": "Found", "part_name": name})
    return json.dumps({"status": "Not Found", "part_name": None})

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Provide ID")
    else:
        print(lookup(sys.argv[1]))
