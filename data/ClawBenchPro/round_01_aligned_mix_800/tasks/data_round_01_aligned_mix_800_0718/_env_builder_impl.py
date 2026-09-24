import os
import csv

def build_env():
    # Create directories
    os.makedirs("recipes", exist_ok=True)
    os.makedirs("inventory", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # Create ingredients dictionary
    ingredients = [
        ["Ingredient", "Type"],
        ["Lavender Oil", "natural"],
        ["Beeswax", "natural"],
        ["Coconut Oil", "natural"],
        ["Orange Extract", "natural"],
        ["Olive Oil", "natural"],
        ["Rose Water", "natural"],
        ["Dimethicone", "synthetic"],
        ["Parabens", "synthetic"],
        ["Aloe Vera", "natural"],
        ["Shea Butter", "natural"],
        ["Vitamin E", "natural"]
    ]
    with open("inventory/ingredients.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(ingredients)

    # Create recipes
    recipe_a = """Recipe Name: Lavender Dream
Notes: Smells wonderful.
pH test result: 5.4
Trial Feedback Score: 9.2
Contains: Lavender Oil, Beeswax, Coconut Oil
"""
    
    recipe_b = """Recipe Name: Citrus Glow
Notes: Brightening effect is nice, but might be too harsh.
pH test result: 6.8
Trial Feedback Score: 8.5
Contains: Orange Extract, Olive Oil
"""

    recipe_c = """Recipe Name: Rose Smooth
Notes: Texture is amazing, applies beautifully.
pH test result: 5.5
Trial Feedback Score: 9.6
Contains: Rose Water, Dimethicone, Vitamin E
"""

    recipe_d = """Recipe Name: Aloe Soothe
Notes: Very calming for sensitive skin.
pH test result: 5.2
Trial Feedback Score: 9.4
Contains: Aloe Vera, Shea Butter, Beeswax
"""

    with open("recipes/recipe_a.txt", "w", encoding="utf-8") as f:
        f.write(recipe_a)
    with open("recipes/recipe_b.txt", "w", encoding="utf-8") as f:
        f.write(recipe_b)
    with open("recipes/recipe_c.txt", "w", encoding="utf-8") as f:
        f.write(recipe_c)
    with open("recipes/recipe_d.txt", "w", encoding="utf-8") as f:
        f.write(recipe_d)

if __name__ == "__main__":
    build_env()
