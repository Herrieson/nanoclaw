import os
import json
import csv

def build_env():
    # Create required directories
    os.makedirs("stockroom_logs", exist_ok=True)
    os.makedirs("recipes", exist_ok=True)
    os.makedirs("pos_data", exist_ok=True)

    # 1. Recipe Titles (Agent needs to search for ingredients)
    with open("recipes/titles.txt", "w", encoding="utf-8") as f:
        f.write("Irish Sunrise\nMissouri Mule\nMidwest Fidget")

    # 2. Inventory Data (Base part)
    # Note: Grenadine is listed here, but the voice memo will contradict it.
    inventory_content = """
    MORNING INVENTORY - BASE LIST
    - Tequila: 2 bottles
    - Orange Juice: 5 liters
    - Vodka: 3 bottles
    - Ginger Beer: 12 cans
    - Lime Juice: 1 bottle
    - Bitters: 1 bottle
    - Simple Syrup: 2 liters
    - Grenadine: 1 bottle (Check voice memo for status!)
    - Bourbon: 0 bottles (Out of stock)
    """
    with open("stockroom_logs/morning_inventory.txt", "w", encoding="utf-8") as f:
        f.write(inventory_content)
    
    # 3. Dummy Voice Memo File
    with open("stockroom_logs/manager_note.mp4", "w") as f:
        f.write("AUDIO_DATA_PLACEHOLDER: Manager says the Grenadine was dropped and smashed, and the Simple Syrup has mold.")

    # 4. POS Tip Data
    # Danny Gross Calculation: 
    # TX_001: 100 * 0.20 = 20
    # TX_002: 250 * 0.20 = 50
    # TX_003: 50 * 0.20 = 10
    # TX_005: 1500 * 0.18 = 270
    # Total Gross = 350.00
    # Net after 12% tax = 350 * (1 - 0.12) = 308.00
    with open("pos_data/shift_closing.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["TransactionID", "Server", "Bartender_Helper", "Total_Tip", "Helper_Cut_Percentage"])
        writer.writerow(["TX_001", "Sarah", "Danny", "100.00", "20%"])
        writer.writerow(["TX_002", "Mike", "Danny", "250.00", "20%"])
        writer.writerow(["TX_003", "Sarah", "Danny", "50.00", "20%"])
        writer.writerow(["TX_004", "John", "Chris", "300.00", "20%"])
        writer.writerow(["TX_005", "Mike", "Danny", "1500.00", "18%"])

if __name__ == "__main__":
    build_env()
