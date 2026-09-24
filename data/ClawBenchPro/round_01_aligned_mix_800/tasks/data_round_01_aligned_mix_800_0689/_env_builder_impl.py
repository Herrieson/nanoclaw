import os
import json
import csv

def build_env():
    os.makedirs("workspace", exist_ok=True)
    
    # RSVP List
    rsvps = [
        {"Name": "Carlos S.", "Dietary_Needs": "None"},
        {"Name": "Maria R.", "Dietary_Needs": ""},
        {"Name": "John D.", "Dietary_Needs": "Vegan"},
        {"Name": "Lucia P.", "Dietary_Needs": "Nut-Allergy"}, # Eats regular
        {"Name": "Elena M.", "Dietary_Needs": "Gluten-Free"},
        {"Name": "David K.", "Dietary_Needs": "None"},
        {"Name": "Sarah W.", "Dietary_Needs": "vegan"}, # Lowercase test
        {"Name": "Miguel T.", "Dietary_Needs": "None"},
        {"Name": "Sofia L.", "Dietary_Needs": ""},
        {"Name": "James B.", "Dietary_Needs": "None"},
        {"Name": "Ana C.", "Dietary_Needs": "gluten-free"}, # Lowercase test
        {"Name": "Luis H.", "Dietary_Needs": "None"},
        {"Name": "Emma V.", "Dietary_Needs": "Pescatarian"}, # Eats regular chicken? Wait, pescatarian doesn't eat meat. Let's make it simple based on prompt. Prompt said: "anyone who didn't explicitly say they are Vegan or Gluten-Free". So Agent should strictly follow prompt and count Emma as regular.
        {"Name": "Noah G.", "Dietary_Needs": "None"},
        {"Name": "Mia F.", "Dietary_Needs": ""},
        {"Name": "Ethan J.", "Dietary_Needs": "None"},
        {"Name": "Isabella R.", "Dietary_Needs": "Vegan"},
        {"Name": "William P.", "Dietary_Needs": "None"},
        {"Name": "Olivia S.", "Dietary_Needs": "None"},
        {"Name": "Ben M.", "Dietary_Needs": "None"},
        {"Name": "Chloe N.", "Dietary_Needs": "None"},
        {"Name": "Mateo L.", "Dietary_Needs": ""},
        {"Name": "Lucas D.", "Dietary_Needs": "None"},
        {"Name": "Zoe K.", "Dietary_Needs": "None"}
    ]
    
    # Total guests: 24. 
    # Vegan: John, Sarah, Isabella (3)
    # GF: Elena, Ana (2)
    # Total to exclude: 5.
    # Regular enchilada eaters: 19.

    with open("workspace/rsvps.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Name", "Dietary_Needs"])
        writer.writeheader()
        writer.writerows(rsvps)

    # Recipe
    recipe_content = """Family Chicken Enchiladas
Serves: 4 people
Ingredients:
- 12 tortillas
- 2.0 lbs chicken
- 16.0 oz cheese
- 1.0 can enchilada sauce
"""
    with open("workspace/recipe.txt", "w") as f:
        f.write(recipe_content)

    # Required for 19 people (Multiplier = 19/4 = 4.75):
    # tortillas: 4.75 * 12 = 57.0
    # chicken: 4.75 * 2.0 = 9.5
    # cheese: 4.75 * 16.0 = 76.0
    # sauce: 4.75 * 1.0 = 4.75

    # Pantry
    pantry = {
        "tortillas": 20.0,
        "chicken_lbs": 1.5,
        "cheese_oz": 10.0,
        "enchilada_sauce_cans": 2.0
    }
    
    # Missing to buy:
    # tortillas: 57 - 20 = 37.0
    # chicken: 9.5 - 1.5 = 8.0
    # cheese: 76 - 10 = 66.0
    # sauce: 4.75 - 2 = 2.75

    with open("workspace/pantry.json", "w") as f:
        json.dump(pantry, f, indent=2)

if __name__ == "__main__":
    build_env()
