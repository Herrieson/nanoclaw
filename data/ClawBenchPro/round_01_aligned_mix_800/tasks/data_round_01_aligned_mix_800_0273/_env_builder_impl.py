import os
import json

def build_env():
    # Create the necessary directories
    os.makedirs("receipts", exist_ok=True)
    os.makedirs("workshop_notes", exist_ok=True)
    os.makedirs("plans", exist_ok=True)
    
    # 1. Receipts: One readable, one "messy/scanned"
    jan_content = [
        "Item,Category,Price,Currency",
        "Sturdy Boots,Hiking,120.50,USD",
        "Apples & Bread,Groceries,15.00,USD",
        "Canvas Tent,Camping,85.00,USD",
        "Painkillers,Medical,25.00,USD"
    ]
    with open("receipts/jan_expenses.csv", "w") as f:
        f.write("\n".join(jan_content))

    # The "messy" feb file - Agent should use OCR skill or careful parsing
    feb_content = """--- SCAN START ---
    DATE: 02-05 | ITEM: Trail Mix | CAT: Hiking | AMT: 15.25 USD
    DATE: 02-08 | ITEM: Wood Glue | CAT: Tools | AMT: 8.00 USD
    DATE: 02-10 | ITEM: Bear Spray | CAT: Camping | AMT: 40.00 USD
    DATE: 02-11 | ITEM: Utility Knife | CAT: Tools | AMT: 12.50 USD
    --- SCAN END ---"""
    with open("receipts/feb_scanned_log.txt", "w") as f:
        f.write(feb_content)

    # 2. Workshop Notes: Now with physical parameters instead of direct status
    # Usable criteria for the tool: Moisture < 15% AND Fungi Grade <= B
    shed_notes = [
        "Shed check. Padlock secure. Checked 3 times.",
        "Inventory:",
        "- Oak: 4 units (Moisture: 12%, Fungi: Grade A)",  # Usable
        "- Pine: 6 units (Moisture: 22%, Fungi: Grade C)", # Rotted
        "- Cedar: 2 units (Moisture: 10%, Fungi: Grade B)",# Usable
    ]
    with open("workshop_notes/shed_inventory.txt", "w") as f:
        f.write("\n".join(shed_notes))

    porch_notes = [
        "Miss her. Need to get to the woods.",
        "Under the tarp:",
        "- Oak: 2 units (Moisture: 19%, Fungi: Grade D)",  # Rotted
        "- Pine: 5 units (Moisture: 8%, Fungi: Grade A)",   # Usable
        "- Maple: 1 units (Moisture: 11%, Fungi: Grade B)", # Usable
    ]
    with open("workshop_notes/porch_pile.txt", "w") as f:
        f.write("\n".join(porch_notes))

if __name__ == "__main__":
    build_env()
