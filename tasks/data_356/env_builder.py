import os
import json

def build_env():
    base_dir = "assets/data_356"
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Create the suppliers.json
    suppliers_data = [
        {"product_id": "PROD-001", "name": "Ocean-Safe Water Bottle", "supplier": "EcoGear Co", "certification": "EcoCert"},
        {"product_id": "PROD-002", "name": "Heavy Duty Garden Trowel", "supplier": "YardWorks", "certification": "None"},
        {"product_id": "PROD-003", "name": "Urban Compost Bin", "supplier": "GreenLife", "certification": "GreenLeaf"},
        {"product_id": "PROD-004", "name": "Bamboo Water Bottle", "supplier": "NaturePath", "certification": "Self-Declared"},
        {"product_id": "PROD-005", "name": "Reusable Hemp Tote Bags", "supplier": "EcoGear Co", "certification": "EcoCert"},
        {"product_id": "PROD-006", "name": "Solar Pathway Lights", "supplier": "SunPower", "certification": "GreenLeaf"},
        {"product_id": "PROD-007", "name": "Plastic Planter Pot", "supplier": "YardWorks", "certification": "Pending"}
    ]
    
    with open(os.path.join(base_dir, "suppliers.json"), "w", encoding="utf-8") as f:
        json.dump(suppliers_data, f, indent=4)
        
    # 2. Create the messy feedback_logs.txt
    feedback_text = """
    LOG EXPORT: 2023-10-24
    System: RetailCS-9000
    
    Customer 1092: Love my new bottle! Prod: PROD-001 | Rating: 5
    Customer 1093: Broke immediately. product #PROD-001, 2/5 stars. Customer service was nice though.
    Customer 1094: Great trowel. rating for PROD-002 is 4. I use it in my garden every day.
    Customer 1095: Best compost bin ever! PROD-003 gets a 5/5 from me. No smells.
    Customer 1096: Decent size, PROD-003 rating: 4. A bit hard to open.
    Customer 1097: PROD-004 is okay, 4 stars. Not sure if it's really bamboo.
    Customer 1098: Wow, PROD-005 - 5 stars! Fits all my groceries.
    Customer 1099: PROD-005 is solid. 5/5 stars.
    Customer 1100: PROD-006 lights are dim. rating: 2.
    Customer 1101: Very bright! PROD-006, 5/5.
    Customer 1102: PROD-007 melted in the sun. 1/5 stars.
    Customer 1103: Pretty good bottle. PROD-001 rating: 4.
    Customer 1104: PROD-003: 5 stars.
    """
    
    with open(os.path.join(base_dir, "feedback_logs.txt"), "w", encoding="utf-8") as f:
        f.write(feedback_text.strip())

if __name__ == "__main__":
    build_env()
