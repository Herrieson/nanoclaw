import os
import csv

def build_env():
    base_dir = "assets/data_377"
    os.makedirs(base_dir, exist_ok=True)

    notes_content = """May 12: Saw a beautiful Northern Cardinal this morning.
Apples (Fuji): 10
Organic Milk (Gallon): 4
Don't forget to refill the suet feeder! The starlings are eating it all.
Whole Wheat Bread: 18
May 13: The Blue Jays are so aggressive today, chased away a sparrow.
Carrots (1lb bag): 25
Free-Range Eggs (Dozen): 8
Local Honey: 2
May 14: Heard a Wood Thrush!
Oats (Rolled): 14
Bananas: 50
Almond Butter: 5
"""
    
    with open(os.path.join(base_dir, "notes_mixed.txt"), "w") as f:
        f.write(notes_content)

    catalog_data = [
        ["Item Name", "Price"],
        ["Fuji Apples", "0.50"],
        ["Organic Whole Milk (Gallon)", "4.50"],
        ["Whole Wheat Bread", "3.00"],
        ["Carrots (1lb bag)", "1.20"],
        ["Free-Range Eggs (Dozen)", "5.00"],
        ["Local Raw Honey", "8.00"],
        ["Rolled Oats", "2.50"],
        ["Bananas", "0.20"],
        ["Almond Butter", "6.00"]
    ]

    with open(os.path.join(base_dir, "green_earth_catalog.csv"), "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(catalog_data)

if __name__ == "__main__":
    build_env()
