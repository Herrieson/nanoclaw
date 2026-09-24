import os
import json

def build_env():
    # Create the directory for the raw logs
    os.makedirs("collection_logs", exist_ok=True)

    # Batch 1: CSV format (Monday logs)
    csv_content = """Patient Name,Brand,Frames Count
Bobby Jo,WoodSpecs,2
Sue Ellen,RayBan,1
Jim Bob,OceanPlastics Co.,1
Cletus,FastFashion,5
"""
    with open("collection_logs/monday_batch.csv", "w", encoding="utf-8") as f:
        f.write(csv_content)

    # Batch 2: JSON format (Wednesday logs)
    json_content = [
        {"patient": "Mary", "brand": "LeafFrames", "quantity": 4},
        {"patient": "Billy", "brand": "WoodSpecs", "quantity": 3},
        {"patient": "Doc", "brand": "EcoGaze", "quantity": 2},
        {"patient": "Unknown", "brand": "CheapoPlastics", "quantity": 2}
    ]
    with open("collection_logs/wednesday_batch.json", "w", encoding="utf-8") as f:
        json.dump(json_content, f, indent=2)

    # Official Eco-Brands List
    brands_list = """WoodSpecs
OceanPlastics Co.
LeafFrames
EcoGaze
"""
    with open("eco_brands_list.txt", "w", encoding="utf-8") as f:
        f.write(brands_list)

if __name__ == "__main__":
    build_env()
