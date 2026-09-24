import sys

def execute(item_code):
    database = {
        "#PX-992": {"status": "Employee Buy-back", "cost": 15.00, "notes": "Reinforced Chassis Block"},
        "#PX-104": {"status": "Factory Scrap", "cost": 0.00, "notes": "High-temp Resin residue"},
        "#PX-551": {"status": "Internal Use Only", "cost": 999, "notes": "Safety Gear"}
    }
    
    code = item_code.strip()
    if code in database:
        res = database[code]
        return f"CODE: {code} | STATUS: {res['status']} | COST: ${res['cost']:.2f} | INFO: {res['notes']}"
    else:
        return f"Error: Item code {code} not found in factory database."

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(execute(sys.argv[1]))
