import os
import json

def build_env():
    os.makedirs("my_recipes", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    
    rsvps_content = """Hey! Here are the RSVPs for the dinner:

1. Rosa (she said she's strictly vegan)
2. Juan (eat anything)
3. Miguel - has a peanut-allergy!!
4. Elena -> vegan and peanut-allergy
5. Luis (no restrictions)
6. Blanca ... dairy-free
7. Chloe: dairy-free & vegan
8. Mateo (none)

Let me know if you need help setting up!"""
    
    with open("rsvps.txt", "w", encoding="utf-8") as f:
        f.write(rsvps_content)
        
    recipe1 = {
      "name": "Cheese Enchiladas",
      "servings": 4,
      "suitable_for": ["peanut-allergy", "vegetarian"],
      "ingredients": {"cheese (lbs)": 1, "tortillas": 8, "enchilada sauce (cans)": 1}
    }
    
    recipe2 = {
      "name": "Jackfruit Carnitas Tacos",
      "servings": 4,
      "suitable_for": ["vegan", "peanut-allergy", "dairy-free"],
      "ingredients": {"jackfruit (cans)": 2, "tortillas": 8, "onion": 1, "cilantro (bunch)": 0.5}
    }
    
    recipe3 = {
      "name": "Mango Avocado Salad",
      "servings": 2,
      "suitable_for": ["vegan", "peanut-allergy", "dairy-free", "gluten-free"],
      "ingredients": {"mango": 1, "avocado": 1, "lime": 1}
    }
    
    recipe4 = {
      "name": "Chicken Mole",
      "servings": 8,
      "suitable_for": ["dairy-free"],
      "ingredients": {"chicken (lbs)": 2, "mole paste (jar)": 1, "peanuts (cups)": 1}
    }
    
    with open("my_recipes/recipe1_enchiladas.json", "w", encoding="utf-8") as f:
        json.dump(recipe1, f, indent=2)
    with open("my_recipes/recipe2_vegan_tacos.json", "w", encoding="utf-8") as f:
        json.dump(recipe2, f, indent=2)
    with open("my_recipes/recipe3_salad.json", "w", encoding="utf-8") as f:
        json.dump(recipe3, f, indent=2)
    with open("my_recipes/recipe4_mole.json", "w", encoding="utf-8") as f:
        json.dump(recipe4, f, indent=2)

if __name__ == "__main__":
    build_env()
