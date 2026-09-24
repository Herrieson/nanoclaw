import os
import csv
import json
import base64

def build_env():
    # Create directories
    os.makedirs("raw_logs", exist_ok=True)
    os.makedirs("party_plan", exist_ok=True)

    # 1. Encrypted Whitelist (Base64 simulated QR)
    whitelist_names = [
        "Chad",
        "Big Mike",
        "Father Tom",
        "Gunner",
        "Dave from Receiving"
    ]
    encoded_content = base64.b64encode("\n".join(whitelist_names).encode()).decode()
    with open("raw_logs/official_invitees_encrypted.qr", "w") as f:
        f.write(f"---WHS-QR-v2---\n{encoded_content}\n---END---")

    # 2. Distribution Rules JSON
    rules = {
        "per_person_rations": {
            "burgers": 2,
            "hotdogs": 1,
            "beers": 4
        },
        "event_type": "Tailgate",
        "location": "Supercenter Warehouse Parking"
    }
    with open("raw_logs/distribution_rules.json", "w") as f:
        json.dump(rules, f, indent=4)

    # 3. Messy RSVP data
    rsvp_data = [
        ["Name", "Plus_Ones", "Bringing", "Age_Status"],
        ["Chad", "1", "Chips", "Adult"],
        ["Big Mike", "3", "Soda", "Adult"],
        ["Sneaky Pete", "5", "Nothing", "Adult"], # Crasher
        ["Gunner", "0", "Ice", "Adult"],
        ["Father Tom", "0", "Blessings", "Clergy"],
        ["Gym Bro Steve", "2", "Protein Powder", "Adult"], # Crasher
        ["Dave from Receiving", "2", "Napkins", "Adult"]
    ]

    with open("raw_logs/messy_rsvps.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rsvp_data)

    # 4. A distractor file
    with open("raw_logs/emergency_contacts.txt", "w") as f:
        f.write("In case of forklift accident, call 911.\nFor minor cuts, see Aisle 4 first aid kit.")

if __name__ == "__main__":
    build_env()
