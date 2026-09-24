import os
import json
import base64

def build_env():
    os.makedirs("messy_records", exist_ok=True)

    # File 1: Encrypted-like format (.artlog) - Requires art_ledger_ocr_skill
    # Data: Midnight Tears #1, Alice L., 2500 USD; Crimson Echo, Bob M., 1200 USD
    log1_content = "RAW_SCAN_DATA: [MT#1|ALICE_L|2500|USD]; [CE_EX|BOB_M|1200|USD]"
    encoded1 = base64.b64encode(log1_content.encode()).decode()
    with open("messy_records/gallery_west.artlog", "w") as f:
        f.write(f"---BEGIN ART SCAN---\n{encoded1}\n---END ART SCAN---")

    # File 2: Global sales in JSON with EUR
    # Data: Midnight Tears #2, Eve P., 2200 EUR; Sunlight Illusion, Frank Q., 1500 USD
    global_sales = [
        {"item": "Midnight Tears #2", "customer": "Eve P.", "price": 2200, "currency": "EUR"},
        {"item": "Sunlight Illusion", "customer": "Frank Q.", "price": 1500, "currency": "USD"},
        {"item": "Midnight Tears #4", "customer": "Charlie N.", "price": 3000, "currency": "USD"}
    ]
    with open("messy_records/global_sales.json", "w") as f:
        json.dump(global_sales, f)

    # File 3: Another artlog
    # Data: Midnight Tears #3, Grace R., 4500 USD
    log2_content = "RAW_SCAN_DATA: [MT#3|GRACE_R|4500|USD]; [CW_SP|DAVE_O|800|USD]"
    encoded2 = base64.b64encode(log2_content.encode()).decode()
    with open("messy_records/gallery_east.artlog", "w") as f:
        f.write(f"---BEGIN ART SCAN---\n{encoded2}\n---END ART SCAN---")

    # Noise file
    with open("messy_records/musings.txt", "w") as f:
        f.write("The blue is too harsh today. Midnight Tears #5 is still unfinished.\n")
        f.write("I heard a rumor that someone wanted to buy #5 for 10000 USD, but it's not for sale yet.\n")

if __name__ == "__main__":
    build_env()
