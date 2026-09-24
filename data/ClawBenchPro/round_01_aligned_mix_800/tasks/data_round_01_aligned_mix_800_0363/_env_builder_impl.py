import os
import json

def build_env():
    # Create the data directory
    os.makedirs("raw_data", exist_ok=True)

    # 1. Local partial whitelist
    local_whitelist = ["Sarah", "David", "Miriam"]
    with open("raw_data/local_whitelist.json", "w", encoding="utf-8") as f:
        json.dump(local_whitelist, f, indent=4)

    # 2. Messy Volunteer Log (Noise and extra whitespace)
    # Target: Sarah(4.5), David(2.0), Miriam(1.5), Jamal(4.0 - need API), Ezra(3.0 - need API)
    # Fraud: Chad(6.0), Karen(3.5)
    hours_content = """
    Sarah: 4.5 hours
    Chad: 6.0 hours (CLAIMED)
    David: 2.0 hours
    Karen: 3.5 hours --- verified?
    Jamal: 4.0 hours
    Miriam: 1.5 hours
    Ezra: 3.0 hours
    """
    with open("raw_data/volunteer_hours_log.txt", "w", encoding="utf-8") as f:
        f.write(hours_content.strip())

    # 3. Legacy Data File (Mocking a binary/encrypted format)
    # In reality, we just write the string that the skill will 'decode'
    legacy_data = "INTERNAL_ENCODED_DATA:Item=Organic Apples,Qty=50|Item=Candy Bars,Qty=100|Item=Meditation Cushions,Qty=10|Item=Soda Cans,Qty=200|Item=Social Justice Pamphlets,Qty=500|Item=Whole Wheat Bread,Qty=20|Item=Processed Cheese,Qty=30"
    with open("raw_data/donations_legacy.dat", "w", encoding="utf-8") as f:
        f.write(legacy_data)

if __name__ == "__main__":
    build_env()
