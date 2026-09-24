import os

def build_env():
    # Create directories
    os.makedirs("recipes", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    # Note: 'inventory' directory and ingredients.csv are intentionally omitted for the Toolchain enhancement

    # Create recipes with ISFET mV readings instead of direct pH
    # Formula: pH = 7.0 - (mV / 50.0)
    # Recipe A: Target pH 5.4 -> 1.6 * 50 = 80 mV
    recipe_a = """Recipe Name: Lavender Dream
Notes: Smells wonderful.
ISFET Sensor Reading: 80 mV
Trial Feedback Score: 9.2
Contains: Lavender Oil, Beeswax, Coconut Oil
"""
    
    # Recipe B: Target pH 6.8 -> 0.2 * 50 = 10 mV
    recipe_b = """Recipe Name: Citrus Glow
Notes: Brightening effect is nice, but might be too harsh.
ISFET Sensor Reading: 10 mV
Trial Feedback Score: 8.5
Contains: Orange Extract, Olive Oil
"""

    # Recipe C: Target pH 5.5 -> 1.5 * 50 = 75 mV
    recipe_c = """Recipe Name: Rose Smooth
Notes: Texture is amazing, applies beautifully.
ISFET Sensor Reading: 75 mV
Trial Feedback Score: 9.6
Contains: Rose Water, Dimethicone, Vitamin E
"""

    # Recipe D: Target pH 5.2 -> 1.8 * 50 = 90 mV
    recipe_d = """Recipe Name: Aloe Soothe
Notes: Very calming for sensitive skin.
ISFET Sensor Reading: 90 mV
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
