import os
import json
import base64

def build_env():
    # Create necessary directories directly in the current working directory
    os.makedirs("records", exist_ok=True)
    os.makedirs("supplies", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # Generate Volunteer Data (Names and IDs only)
    volunteers_txt = """Mike Smith - ID: V-8472
Jenny Lee - ID: V-1193
Tom Hanks - ID: V-4002
Linda Chen - ID: V-9931
Bob Dylan - ID: V-2204
Sarah Connor - ID: V-7742
David Webb - ID: V-8891
"""
    with open("records/volunteers.txt", "w") as f:
        f.write(volunteers_txt)

    # Generate Supply Receipts Data and encode it
    supplies = [
        {"item": "Tents", "price": 120.50, "qty": 4},
        {"item": "Trail Mix", "price": 15.25, "qty": 10},
        {"item": "First Aid Kits", "price": 35.00, "qty": 3},
        {"item": "Bug Spray", "price": 8.75, "qty": 5},
        {"item": "Camp Lanterns", "price": 22.00, "qty": 2}
    ]
    supplies_json = json.dumps(supplies)
    encoded_supplies = base64.b64encode(supplies_json.encode('utf-8')).decode('utf-8')
    
    # Add a fake header to make the proprietary format look real
    ezpos_content = f"EZPOS-SECURE-RECEIPT-V2.1\nPAYLOAD:{encoded_supplies}\nEOF"
    
    with open("supplies/receipts.ezpos", "w") as f:
        f.write(ezpos_content)

    # Add some noise
    with open("records/note_from_principal.txt", "w") as f:
        f.write("Please ensure we stay under the $1000 budget for the trip. - Principal")

if __name__ == "__main__":
    build_env()
