import os
import csv

def build():
    # Create directories
    os.makedirs("notes", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # 1. Create messy recipe notes
    recipe_content = """
    RECIPE BRAINSTORMING YAY!!! 🌟
    
    Meal 1: ThreeSistersStew (Cherokee inspired!)
    - Needs to be hearty.
    - Sweet_Corn: 1.5 units per serving
    - Pinto_Beans: 2.0 units per serving
    - Winter_Squash: 1.0 units per serving
    (Note: don't forget to soak the beans overnight!)

    Meal 2: Progressive Veggie Bake (Discarded idea - too mushy)
    - Carrots: 3 units
    - Potatoes: 2 units

    Meal 3: BisonSliders (The kids will LOVE this!)
    - Ground_Bison: 2.0 units per serving
    - Whole_Wheat_Buns: 1.0 units per serving
    - Secret_Zesty_Sauce: 0.5 units per serving
    (Keep the sauce mild for the kindergarteners)
    """
    with open("notes/recipe_ideas.txt", "w", encoding="utf-8") as f:
        f.write(recipe_content)

    # 2. Create vendor database
    vendor_data = [
        ["Ingredient", "Cost_Per_Unit", "Calories_Per_Unit"],
        ["Sweet_Corn", "0.50", "50"],
        ["Pinto_Beans", "0.30", "80"],
        ["Winter_Squash", "0.80", "40"],
        ["Ground_Bison", "3.00", "200"],
        ["Whole_Wheat_Buns", "0.50", "150"],
        ["Secret_Zesty_Sauce", "0.20", "50"],
        ["Carrots", "0.15", "20"],
        ["Potatoes", "0.25", "90"]
    ]
    with open("data/vendor_db.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(vendor_data)

if __name__ == "__main__":
    build()
