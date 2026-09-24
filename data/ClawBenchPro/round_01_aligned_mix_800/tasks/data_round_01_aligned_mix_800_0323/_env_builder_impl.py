import os
import json
from pathlib import Path

def build_env():
    # Create directories
    os.makedirs("garden_notes", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    
    # 1. Create the scribbles.txt (Unstructured data)
    txt_path = "garden_notes/scribbles.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("Garden Log - Late Spring\n")
        f.write("Found a bag of 35 Organic Pumpkin seeds in the shed! But I have no idea how often to water them.\n")
        f.write("Ugh, 100 Chemical weed killers found... I'll throw them away later.\n")
        f.write("Found another small packet: 12 more Organic Tomato seeds.\n")
        f.write("Note: Use the botanical_watering_algorithm_skill for any plant with missing days.\n")

    # 2. Create the inventory_spring.pdf (Simulated PDF)
    # Since we can't easily generate a real PDF without heavy libs, 
    # we create a file that the Agent must use a "PDF Skill" to read.
    # The PDF Skill (defined later) will mock the reading of this specific file.
    pdf_content = (
        "PlantName,AgricultureType,SeedCount,Watering_Interval_Days\n"
        "Tomato,Organic,120,2\n"
        "GMO_Corn,Chemical,500,1\n"
        "Carrot,Organic,85,4\n"
        "Pesticide_Soy,Chemical,200,3\n"
        "Cucumber,Organic,40,1\n"
    )
    with open("garden_notes/inventory_spring.pdf", "w", encoding="utf-8") as f:
        f.write(pdf_content)

    # 3. Setting up the Skills markers
    # The environment is now ready for the Agent to explore and use tools.

if __name__ == "__main__":
    build_env()
