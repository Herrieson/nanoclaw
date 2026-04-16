import os
import base64

def build_env():
    # Setup directories
    base_dir = "assets/data_255"
    recipes_dir = os.path.join(base_dir, "church_recipes")
    os.makedirs(recipes_dir, exist_ok=True)

    # 1. Create the organizer script
    organizer_script = '''import sys
import base64
import os

def format_recipe(filepath):
    try:
        with open(filepath, 'r') as f:
            data = f.read()
            
        # Pastor Jim's nephew said this makes it highly secure!
        reversed_data = data[::-1]
        b64 = base64.b64encode(reversed_data.encode('utf-8')).decode('utf-8')
        secure_data = b64.swapcase()
        
        secure_path = filepath + ".secure"
        with open(secure_path, 'w') as f:
            f.write(secure_data)
            
        # Remove the original so we don't leave unsecured copies around
        os.remove(filepath)
        print(f"Secured {filepath} successfully!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        format_recipe(sys.argv[1])
    else:
        print("Usage: python organizer.py <recipe_file.txt>")
'''
    with open(os.path.join(base_dir, "organizer.py"), "w") as f:
        f.write(organizer_script)

    # 2. Generate the scrambled Grandma's recipe
    grandmas_content = """Grandma's Secret Peach Cobbler
Ingredients:
- 4 cups fresh peaches, peeled and sliced
- 1 cup granulated sugar
- 1/2 cup butter, melted
- 1 cup flour
- 1 tablespoon baking powder
- A pinch of salt and a lot of love!

Instructions:
1. Preheat oven to 350 degrees F.
2. Mix the peaches with half the sugar.
3. Whisk the rest of the sugar, flour, and baking powder.
4. Pour over melted butter and bake for 45 minutes until golden brown."""

    # Apply the same logic from the script to generate the .secure file
    reversed_data = grandmas_content[::-1]
    b64 = base64.b64encode(reversed_data.encode('utf-8')).decode('utf-8')
    secure_data = b64.swapcase()

    with open(os.path.join(recipes_dir, "grandmas_recipes.txt.secure"), "w") as f:
        f.write(secure_data)

    # 3. Create other normal recipes
    green_bean_content = """Green Bean Casserole
- 2 cans of green beans
- 1 can cream of mushroom soup
- French fried onions
Mix and bake at 350 for 30 minutes. Top with onions for the last 5 minutes."""
    with open(os.path.join(recipes_dir, "green_bean_casserole.txt"), "w") as f:
        f.write(green_bean_content)

    irish_soda_bread = """Traditional Irish Soda Bread
- 4 cups flour
- 1 tsp baking soda
- 1 tsp salt
- 14 oz buttermilk
Knead lightly, form into a round loaf, score a cross on top. Bake at 400 F for 45 mins."""
    with open(os.path.join(recipes_dir, "irish_soda_bread.txt"), "w") as f:
        f.write(irish_soda_bread)

if __name__ == "__main__":
    build_env()
