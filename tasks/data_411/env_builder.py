import os
import json

def build_env():
    base_dir = "assets/data_411"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Messy Nurse Log
    nurse_log_content = """
*** DISTRICT HEALTH SYSTEM - EXPORT 2023 ***
ERR: Connection timeout on port 8080.
Student ID 1042: Parent reported severe reaction to [Peanuts] last Tuesday.
Note to cafeteria: Grade 3 has a strict no-[Dairy] policy this year due to multiple sensitivities.
...
Checking database integrity... OK.
Update from clinic: Student 992 requires epinephrine for [Shellfish] exposure.
Reminder: Tomorrow is spirit day.
Also, please ensure no [Soy] is used in the main cafeteria line for the kindergarteners.
*** END OF REPORT ***
"""
    with open(os.path.join(base_dir, "nurse_allergy_log.txt"), "w", encoding="utf-8") as f:
        f.write(nurse_log_content)

    # 2. Recipe Book
    recipes = [
        {
            "name": "Three Sisters Stew",
            "ingredients": ["corn", "beans", "squash", "vegetable broth", "spices"],
            "nutrition": {"protein": 12.0, "carbs": 30.0}
        },
        {
            "name": "Peanut Butter Cornbread",
            "ingredients": ["cornmeal", "flour", "peanuts", "butter", "egg"],
            "nutrition": {"protein": 18.0, "carbs": 45.0}
        },
        {
            "name": "Venison & Wild Rice",
            "ingredients": ["venison", "wild rice", "onion", "garlic"],
            "nutrition": {"protein": 29.0, "carbs": 25.0}
        },
        {
            "name": "Creamy Pumpkin Soup",
            "ingredients": ["pumpkin", "dairy", "nutmeg", "cinnamon", "sugar"],
            "nutrition": {"protein": 8.0, "carbs": 20.0}
        },
        {
            "name": "Sunflower Seed Crusted Fish",
            "ingredients": ["whitefish", "sunflower seeds", "shellfish stock", "lemon"],
            "nutrition": {"protein": 22.0, "carbs": 5.0}
        },
        {
            "name": "Berry Frybread",
            "ingredients": ["flour", "water", "berries", "honey", "oil"],
            "nutrition": {"protein": 5.0, "carbs": 40.0}
        },
        {
            "name": "Tofu Scramble",
            "ingredients": ["soy", "turmeric", "spinach", "tomato"],
            "nutrition": {"protein": 14.0, "carbs": 10.0}
        }
    ]
    with open(os.path.join(base_dir, "leos_new_recipes.json"), "w", encoding="utf-8") as f:
        json.dump(recipes, f, indent=4)

if __name__ == "__main__":
    build_env()
