import os
import json
import csv
import base64

def encode_to_bdat(content: str) -> bytes:
    # A mocked proprietary format: a custom header + base64 encoded payload
    header = b"MARCUS_SCANNER_V1\n"
    payload = base64.b64encode(content.encode("utf-8"))
    return header + payload

def build_env():
    # Constructing the chaotic "glovebox"
    os.makedirs("glovebox_scans", exist_ok=True)

    # Site logs WITHOUT explicit severity markings. Agent must use the Skill to classify.
    log1 = """October 12th Log:
- Poured the foundation on the west side. Concrete looks solid.
- Observation: Crew members observed not wearing dust masks during the dry sweep.
- Observation: Scaffolding on the east wall is missing guardrails on the second tier.
- Picked up the kids early from daycare.
"""
    with open("glovebox_scans/site_log_oct12.bdat", "wb") as f:
        f.write(encode_to_bdat(log1))

    log2 = """October 14th Log:
- Rain delay in the morning.
- Observation: Exposed live wire in sector 4 near the puddle. Taped it off but need the electrician out here yesterday.
- Bought some coffee for the crew.
- Observation: Hard hats were left off during the lunch break near the crane zone. 
"""
    with open("glovebox_scans/site_log_oct14.bdat", "wb") as f:
        f.write(encode_to_bdat(log2))

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
    
    # Convert CSV to string
    import io
    csv_io = io.StringIO()
    writer = csv.writer(csv_io)
    writer.writerows(csv_data)
    csv_str = csv_io.getvalue()

    with open("glovebox_scans/receipts_crumpled.bdat", "wb") as f:
        f.write(encode_to_bdat(csv_str))

    # More mixed receipts in a JSON
    json_data = [
        {"desc": "Rebar steel", "amount": 300.00, "tag": "construction"},
        {"desc": "Assorted iron gears from junkyard", "amount": 150.00, "tag": "art"},
        {"desc": "Diapers for the little one", "amount": 42.50, "tag": "personal"}
    ]
    
    with open("glovebox_scans/digital_receipts.bdat", "wb") as f:
        f.write(encode_to_bdat(json.dumps(json_data, indent=2)))

if __name__ == "__main__":
    build_env()
