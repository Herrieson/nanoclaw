import os
import json

def build_env():
    # Create the directory for the raw logs
    os.makedirs("collection_logs", exist_ok=True)

    # Monday logs: Material-based descriptions (Requires Skill)
    csv_content = """Patient Name,Material Description,Frames Count
Bobby Jo,recycled organic acetate,2
Sue Ellen,standard petroleum plastic,1
Jim Bob,recycled ocean-bound plastic,1
Cletus,cheap brittle resin,5
"""
    with open("collection_logs/monday_batch.csv", "w", encoding="utf-8") as f:
        f.write(csv_content)

    # Wednesday logs: Direct Brand names (Mixed)
    json_content = [
        {"patient": "Mary", "brand": "LeafFrames", "quantity": 4},
        {"patient": "Billy", "brand": "WoodSpecs", "quantity": 3},
        {"patient": "Doc", "brand": "EcoGaze", "quantity": 2},
        {"patient": "Unknown", "brand": "CheapoPlastics", "quantity": 2}
    ]
    with open("collection_logs/wednesday_batch.json", "w", encoding="utf-8") as f:
        json.dump(json_content, f, indent=2)

    # Friday logs: PDF format (Requires OCR Skill)
    # Creating a dummy file to represent the PDF
    with open("collection_logs/friday_receipts.pdf", "w", encoding="utf-8") as f:
        f.write("%PDF-1.4 [Internal Content: Patient: Sarah, Brand: WoodSpecs, Qty: 2; Patient: Mike, Brand: Luxottica, Qty: 10]")

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
