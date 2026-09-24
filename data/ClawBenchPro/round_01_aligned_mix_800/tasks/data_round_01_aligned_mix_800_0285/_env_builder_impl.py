import os
import base64

def build_env():
    os.makedirs("recipes", exist_ok=True)
    os.makedirs("kitchen_prep", exist_ok=True)
    
    # We no longer generate suppliers.csv to force the use of the API skills.

    recipes = {
        "Traditional_Lechon": """Recipe: Traditional_Lechon
Man, this is a classic, but meat is heavy on the earth.
Ingredients:
- Pork: 3
- Garlic: 5
- Onion: 2
""",
        "Eco_Plantain_Bowl": """Recipe: Eco_Plantain_Bowl
This one is my favorite experiment! Super green and fresh.
Ingredients:
- Plantain: 4
- BlackBeans: 3
- Rice: 2
- OrganicAvocado: 1
""",
        "Fancy_Seafood_Paella": """Recipe: Fancy_Seafood_Paella
Boss might like this, but saffron is crazy expensive.
Ingredients:
- Shrimp: 5
- Rice: 3
- Saffron: 1
""",
        "Chicken_Mojo": """Recipe: Chicken_Mojo
A safe bet, everyone loves chicken.
Ingredients:
- Chicken: 3
- Garlic: 4
- Onion: 2
- Rice: 2
"""
    }

    # Encode recipes into the proprietary .cba format
    for name, content in recipes.items():
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        with open(f"recipes/{name}.cba", "w") as f:
            f.write(encoded_content)

if __name__ == "__main__":
    build_env()
