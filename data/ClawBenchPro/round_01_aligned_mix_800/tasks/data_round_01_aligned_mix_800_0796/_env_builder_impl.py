import os
import csv

def build_env():
    # Create directories
    os.makedirs("raw_logs", exist_ok=True)
    os.makedirs("party_plan", exist_ok=True)

    # 1. Whitelist of invited friends
    whitelist = [
        "Chad",
        "Big Mike",
        "Father Tom",
        "Gunner",
        "Dave from Receiving"
    ]
    with open("raw_logs/official_invitees.txt", "w") as f:
        f.write("OFFICIAL TAILGATE LIST - DO NOT LOSE THIS BRAD\n")
        f.write("----------------------------------------------\n")
        for name in whitelist:
            f.write(name + "\n")

    # 2. Messy RSVP data
    rsvp_data = [
        ["Name", "Plus_Ones", "Bringing", "Notes"],
        ["Chad", "1", "Chips", "Stoked for the weekend!"],
        ["Big Mike", "3", "Soda", "Me and the boys are ready"],
        ["Sneaky Pete", "5", "Nothing", "Heard about this on Facebook"], # Crasher
        ["Gunner", "0", "Ice", "See ya there"],
        ["Father Tom", "0", "Blessings", "Looking forward to it, Brad."],
        ["Gym Bro Steve", "2", "Protein Powder", "Let's get massive"], # Crasher
        ["Dave from Receiving", "2", "Napkins", "Manager said I could bring my kids"]
    ]

    with open("raw_logs/messy_rsvps.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rsvp_data)

    # 3. Distractor file
    with open("raw_logs/store_inventory_notes.txt", "w") as f:
        f.write("Pallet 4A: 500 cases of water\nPallet 4B: 200 boxes of protein bars\nReminder: Brad needs to sweep aisle 7.")

if __name__ == "__main__":
    build_env()
