import os
import json
import csv

def create_environment():
    base_dir = "assets/data_31/recipes_dump"
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. JSON file (Target)
    json_recipe = {
        "title": "Spicy Arkansas Peach Cobbler",
        "description": "A weird but good experiment.",
        "rating": 5,
        "ingredients": ["Peaches", "Jalapeno", "Sugar", "Butter", "Flour"],
        "instructions": "Mix it all and bake at 350."
    }
    with open(os.path.join(base_dir, "spicy_peach.json"), "w") as f:
        json.dump(json_recipe, f, indent=4)
        
    # 2. Distractor JSON (Low rating)
    json_bad = {
        "title": "Boiled Chicken Casserole",
        "rating": 2,
        "ingredients": ["Chicken", "Water", "Salt"],
        "instructions": "Boil until gray."
    }
    with open(os.path.join(base_dir, "boiled_chicken.json"), "w") as f:
        json.dump(json_bad, f)

    # 3. Messy Text File (Target)
    txt_content = """
Recipe Title: Gummy Bear Brisket
Wow, what a weekend. The kids were running around, but I managed to try this.
I absolutely Loved it! 5 stars!

Ingredients needed:
- 1 whole beef brisket
- 2 bags of gummy bears (melted)
- BBQ rub

Steps:
Smother the brisket in gummy bears and smoke for 12 hours.
    """
    os.makedirs(os.path.join(base_dir, "old_notes"), exist_ok=True)
    with open(os.path.join(base_dir, "old_notes", "brisket.txt"), "w") as f:
        f.write(txt_content.strip())
        
    # 4. Distractor Text File
    txt_bad = """
Recipe Title: Sardine Smoothie
Gross. 1/5 stars.
Ingredients needed:
- Sardines
- Milk
    """
    with open(os.path.join(base_dir, "old_notes", "sardine.txt"), "w") as f:
        f.write(txt_bad.strip())

    # 5. Markdown File (Target)
    md_content = """
# Pickled Watermelon Rind Salad

This is a classic southern thing but I added pop rocks. 
**Rating: 5/5**

### Ingredients
* Watermelon rinds
* Vinegar
* Sugar
* Strawberry Pop Rocks

### Directions
Just mix it all up!
    """
    os.makedirs(os.path.join(base_dir, "downloads", "weird_stuff"), exist_ok=True)
    with open(os.path.join(base_dir, "downloads", "weird_stuff", "salad.md"), "w") as f:
        f.write(md_content.strip())

    # 6. CSV File (Distractor & Target)
    os.makedirs(os.path.join(base_dir, "spreadsheets"), exist_ok=True)
    csv_path = os.path.join(base_dir, "spreadsheets", "bulk_recipes.csv")
    with open(csv_path, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Score", "IngredientList", "Method"])
        writer.writerow(["Canned Bean Surprise", "3 stars", "Beans, Mayo", "Stir."])
        writer.writerow(["Cola Glazed Ham", "5 stars", "Ham, Cola, Brown Sugar", "Bake it."])
        writer.writerow(["Plain Toast", "1 star", "Bread", "Toast it."])

if __name__ == "__main__":
    create_environment()
