import os
import json

def build_env():
    base_dir = "assets/data_243"
    os.makedirs(os.path.join(base_dir, "students"), exist_ok=True)

    # Student allergy files (messy natural language)
    students = {
        "student_a.txt": "Aloha Mrs. K, Just a reminder that little Kai cannot have any fish or seafood. He gets hives! Mahalo, Kai's Mom",
        "student_b.txt": "Hi! Leilani is bringing her own snacks, but if she eats anything there, remember she has a severe nut allergy (macadamia, peanuts, all of it!).",
        "student_c.txt": "Dear Teaching Assistant, My son is on a strict vegetarian diet. No meat, no poultry, no pork (so please no Spam!). Thank you.",
        "student_d.txt": "No dairy for Keanu, please. He is lactose intolerant."
    }
    
    for filename, content in students.items():
        with open(os.path.join(base_dir, "students", filename), "w") as f:
            f.write(content)

    # Traditional recipes database
    recipes = [
        {
            "name": "Haupia",
            "ingredients": {"coconut milk (cups)": 4, "sugar (cups)": 0.5, "cornstarch (tbsp)": 5, "water (cups)": 0.5},
            "servings": 8
        },
        {
            "name": "Lomi Lomi Salmon",
            "ingredients": {"salted salmon (lbs)": 1, "tomatoes (lbs)": 1, "sweet onion (lbs)": 0.5, "green onions (bunches)": 1},
            "servings": 6
        },
        {
            "name": "Macadamia Nut Crusted Mahi Mahi",
            "ingredients": {"mahi mahi fillets (lbs)": 2, "macadamia nuts (cups)": 1, "coconut oil (tbsp)": 2, "egg": 1},
            "servings": 4
        },
        {
            "name": "Poi",
            "ingredients": {"taro root (lbs)": 2, "water (cups)": 1},
            "servings": 4
        },
        {
            "name": "Spam Musubi",
            "ingredients": {"spam (cans)": 1, "sushi rice (cups)": 3, "nori (sheets)": 4, "soy sauce (tbsp)": 2, "sugar (tbsp)": 2},
            "servings": 8
        },
        {
            "name": "Chicken Long Rice",
            "ingredients": {"chicken breast (lbs)": 2, "chicken broth (cups)": 4, "bean threads (oz)": 8, "ginger (tbsp)": 1},
            "servings": 10
        },
        {
            "name": "Macaroni Salad",
            "ingredients": {"elbow macaroni (lbs)": 1, "mayonnaise (cups)": 1, "milk (cups)": 0.25, "carrots (cups)": 1},
            "servings": 8
        },
        {
            "name": "Sweet Potato (Uala)",
            "ingredients": {"purple sweet potatoes (lbs)": 3, "coconut milk (cups)": 1, "salt (tsp)": 0.5},
            "servings": 5
        }
    ]
    
    with open(os.path.join(base_dir, "recipes.json"), "w") as f:
        json.dump(recipes, f, indent=4)

if __name__ == "__main__":
    build_env()
