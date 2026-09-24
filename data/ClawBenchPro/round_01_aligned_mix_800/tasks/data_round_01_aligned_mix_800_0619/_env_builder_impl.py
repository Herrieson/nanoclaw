import os
import json
import csv

def build_env():
    # Constructing the chaotic "glovebox"
    os.makedirs("glovebox_scans", exist_ok=True)

    # Site logs with mixed severity hazards
    log1 = """October 12th Log:
- Poured the foundation on the west side. Concrete looks solid.
- Minor: Noticed a few guys not wearing dust masks during the dry sweep. Reminded them.
- CRITICAL HAZARD: Scaffolding on the east wall is missing guardrails on the second tier. Needs to be fixed ASAP.
- Picked up the kids early from daycare.
"""
    with open("glovebox_scans/site_log_oct12.txt", "w", encoding="utf-8") as f:
        f.write(log1)

    log2 = """October 14th Log:
- Rain delay in the morning.
- IMMEDIATE HAZARD: Exposed live wire in sector 4 near the puddle. Taped it off but need the electrician out here yesterday.
- Bought some coffee for the crew.
- Warning: Hard hats were left off during the lunch break near the crane zone. Not a critical violation since the crane was off, but still annoying.
"""
    with open("glovebox_scans/site_log_oct14.txt", "w", encoding="utf-8") as f:
        f.write(log2)

    # Mixed receipts in a messy CSV
    csv_data = [
        ["Item Description", "Cost", "Notes/Category"],
        ["Lumber batch A", "450.00", "Site materials"],
        ["Welding rods", "35.50", "For the yard sculpture"],
        ["Concrete mix bags", "120.00", "Job site"],
        ["Scrap copper pipes", "85.00", "Art project - making wings"],
        ["Nails and screws bulk", "15.00", "Site"],
        ["Kids snacks", "12.00", "Personal"]
    ]
    with open("glovebox_scans/receipts_crumpled.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

    # More mixed receipts in a JSON
    json_data = [
        {"desc": "Rebar steel", "amount": 300.00, "tag": "construction"},
        {"desc": "Assorted iron gears from junkyard", "amount": 150.00, "tag": "art"},
        {"desc": "Diapers for the little one", "amount": 42.50, "tag": "personal"}
    ]
    with open("glovebox_scans/digital_receipts.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2)

if __name__ == "__main__":
    build_env()
