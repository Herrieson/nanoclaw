import os
import json

def build_env():
    base_dir = "assets/data_390"
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Create messages.txt
    messages_content = """Hey Maria! I will definitely be there. Looking forward to it! - John (Allergic to peanuts)
Mabuhay! Sorry, I have a shift at the hospital and can't make it. - Sarah (Allergic to pork)
Count me in! Just a reminder that I'm lactose intolerant, so absolutely no dairy for me. - Mrs. Smith
I'll be there! Can't wait. - Lito (Allergic to shrimp)
I'm out of town this weekend, sorry! - Ana
"""
    with open(os.path.join(base_dir, "messages.txt"), "w", encoding="utf-8") as f:
        f.write(messages_content)
        
    # 2. Create recipes
    recipes_dir = os.path.join(base_dir, "recipes")
    os.makedirs(recipes_dir, exist_ok=True)
    
    recipes = {
        "adobo.json": {
            "name": "Chicken Adobo",
            "ingredients": [
                {"item": "chicken", "amount": 1, "unit": "kg"},
                {"item": "soy sauce", "amount": 100, "unit": "ml"},
                {"item": "garlic", "amount": 5, "unit": "cloves"},
                {"item": "vinegar", "amount": 50, "unit": "ml"}
            ]
        },
        "sinigang.json": {
            "name": "Pork Sinigang",
            "ingredients": [
                {"item": "pork", "amount": 1, "unit": "kg"},
                {"item": "tamarind paste", "amount": 50, "unit": "g"},
                {"item": "tomato", "amount": 2, "unit": "pcs"},
                {"item": "water spinach", "amount": 1, "unit": "bunch"},
                {"item": "garlic", "amount": 3, "unit": "cloves"}
            ]
        },
        "biko.json": {
            "name": "Biko",
            "ingredients": [
                {"item": "glutinous rice", "amount": 500, "unit": "g"},
                {"item": "coconut milk", "amount": 400, "unit": "ml"},
                {"item": "brown sugar", "amount": 200, "unit": "g"}
            ]
        },
        "kare_kare.json": {
            "name": "Kare-Kare",
            "ingredients": [
                {"item": "beef", "amount": 1, "unit": "kg"},
                {"item": "peanut butter", "amount": 200, "unit": "g"},
                {"item": "eggplant", "amount": 2, "unit": "pcs"},
                {"item": "string beans", "amount": 1, "unit": "bunch"}
            ]
        },
        "leche_flan.json": {
            "name": "Leche Flan",
            "ingredients": [
                {"item": "eggs", "amount": 6, "unit": "pcs"},
                {"item": "condensed milk", "amount": 300, "unit": "ml"},
                {"item": "evaporated milk", "amount": 300, "unit": "ml"},
                {"item": "sugar", "amount": 150, "unit": "g"}
            ]
        },
        "pancit.json": {
            "name": "Pancit Palabok",
            "ingredients": [
                {"item": "rice noodles", "amount": 400, "unit": "g"},
                {"item": "shrimp", "amount": 200, "unit": "g"},
                {"item": "eggs", "amount": 2, "unit": "pcs"},
                {"item": "garlic", "amount": 4, "unit": "cloves"}
            ]
        }
    }
    
    for filename, data in recipes.items():
        with open(os.path.join(recipes_dir, filename), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

if __name__ == "__main__":
    build_env()
