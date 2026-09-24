import os
import json
import csv

def build_env():
    # Create necessary directories
    os.makedirs("fundraiser_logs", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # File 1: CSV from Room 1
    with open("fundraiser_logs/room1_parents.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Category", "Item"])
        writer.writerow(["Sarah Connor", "ChildrensBook", "Goodnight Moon"])
        writer.writerow(["Sarah Connor", "BakedGood", "Vegan Brownies"])
        writer.writerow(["John Smith", "AdultBook", "The Shining"])
        writer.writerow(["John Smith", "BakedGood", "Cupcakes"])
        writer.writerow(["Alice Johnson", "ChildrensBook", "Charlotte's Web"])

    # File 2: Unstructured Text Notes
    with open("fundraiser_logs/front_desk_notes.txt", "w", encoding="utf-8") as f:
        f.write("Notes from Tuesday morning:\n")
        f.write("- Beatrice brought a whole box! 4 ChildrensBooks (all Dr. Seuss) and a huge BakedGood (Apple Pie).\n")
        f.write("- Marcus dropped off 2 AdultBooks. No treats from him.\n")

    # File 3: Messy JSON from online forms
    data = [
        {
            "parent_name": "Eleanor", 
            "items_donated": ["ChildrensBook", "ChildrensBook", "ChildrensBook"]
        },
        {
            "parent_name": "Tom", 
            "items_donated": ["AdultBook", "BakedGood"]
        }
    ]
    with open("fundraiser_logs/online_forms.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    build_env()
