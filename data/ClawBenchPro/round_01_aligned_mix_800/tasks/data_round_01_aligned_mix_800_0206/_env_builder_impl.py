import os
import json
import csv

def build_env():
    # Create necessary directories
    os.makedirs("fundraiser_logs", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # File 1: CSV from Room 1 - Removed category, forced classification
    with open("fundraiser_logs/room1_parents.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "ItemDonated"])
        writer.writerow(["Sarah Connor", "Goodnight Moon"]) # Children
        writer.writerow(["Sarah Connor", "Vegan Brownies"]) # Baked
        writer.writerow(["John Smith", "The Shining"])      # Adult
        writer.writerow(["John Smith", "Cupcakes"])         # Baked
        writer.writerow(["Alice Johnson", "Charlotte's Web"]) # Children

    # File 2: Unstructured Text Notes
    with open("fundraiser_logs/front_desk_notes.txt", "w", encoding="utf-8") as f:
        f.write("Notes from Tuesday morning:\n")
        f.write("- Beatrice brought a whole box! 4 ChildrensBooks (all Dr. Seuss titles: 'The Cat in the Hat', 'Green Eggs and Ham', 'One Fish Two Fish', 'Lorax') and a huge BakedGood (Apple Pie).\n")
        f.write("- Marcus dropped off 2 AdultBooks: 'American Psycho' and 'It'. No treats from him.\n")

    # File 3: Messy JSON with Transaction IDs
    # Eleanor donated 3 kids books. Tom donated 1 adult book + 1 baked good.
    data = [
        {
            "parent_name": "Eleanor", 
            "transaction_id": "TXN_9901" 
        },
        {
            "parent_name": "Tom", 
            "transaction_id": "TXN_4402"
        }
    ]
    with open("fundraiser_logs/online_forms.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    build_env()
