import os
import json

def build_env():
    base_dir = "assets/data_228"
    recipes_dir = os.path.join(base_dir, "recipes")
    os.makedirs(recipes_dir, exist_ok=True)

    # 1. Create Market Inventory JSON
    market_inventory = {
        "Chicken breast": 5.50,
        "Organic carrots": 1.20,
        "Yellow onions": 0.80,
        "Pork shoulder": 7.00,
        "Russet potatoes": 2.50,
        "Black truffle": 50.00,
        "Prime beef": 15.00,
        "Fresh garlic": 0.50,
        "Vine tomatoes": 2.00,
        "Basil leaves": 1.50
    }
    
    with open(os.path.join(base_dir, "market_inventory.json"), "w", encoding="utf-8") as f:
        json.dump(market_inventory, f, indent=4)

    # 2. Create Recipe HTML files
    # Recipe 1: Truffle Beef Delight (Expensive: 15.00 + 50.00 + 0.50 = 65.50)
    html_1 = """
    <html>
    <body>
        <h1 class="recipe-title">Truffle Beef Delight</h1>
        <ul class="ingredients">
            <li>Prime beef</li>
            <li>Black truffle</li>
            <li>Fresh garlic</li>
        </ul>
    </body>
    </html>
    """
    
    # Recipe 2: Tropical Surprise (Missing ingredients: Dragonfruit, Mango)
    html_2 = """
    <html>
    <body>
        <h1 class="recipe-title">Tropical Surprise</h1>
        <ul class="ingredients">
            <li>Dragonfruit</li>
            <li>Mango</li>
            <li>Basil leaves</li>
        </ul>
    </body>
    </html>
    """
    
    # Recipe 3: Classic Chicken Stew (Cheapest valid: 5.50 + 1.20 + 0.80 + 0.50 = 8.00)
    html_3 = """
    <html>
    <body>
        <h1 class="recipe-title">Classic Chicken Stew</h1>
        <ul class="ingredients">
            <li>Chicken breast</li>
            <li>Organic carrots</li>
            <li>Yellow onions</li>
            <li>Fresh garlic</li>
        </ul>
    </body>
    </html>
    """
    
    # Recipe 4: Pork and Mash (Valid but more expensive: 7.00 + 2.50 + 0.50 = 10.00)
    html_4 = """
    <html>
    <body>
        <h1 class="recipe-title">Pork and Mash</h1>
        <ul class="ingredients">
            <li>Pork shoulder</li>
            <li>Russet potatoes</li>
            <li>Fresh garlic</li>
        </ul>
    </body>
    </html>
    """

    recipes = [
        ("recipe_1.html", html_1),
        ("recipe_2.html", html_2),
        ("recipe_3.html", html_3),
        ("recipe_4.html", html_4)
    ]

    for filename, content in recipes:
        with open(os.path.join(recipes_dir, filename), "w", encoding="utf-8") as f:
            f.write(content.strip())

if __name__ == "__main__":
    build_env()
