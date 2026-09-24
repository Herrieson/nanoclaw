import os
import random

def create_files():
    random.seed(42) # Ensure deterministic wasteland generation
    
    # 1. Structure the wasteland
    base_dir = "recipes"
    subdirs = [
        "box_1", "box_2/2021", "box_2/2022/desserts", 
        "box_3/mains", "misc/tmp/scans", "grandma_box/holy_grail"
    ]
    
    for sub in subdirs:
        os.makedirs(os.path.join(base_dir, sub), exist_ok=True)
        
    all_dirs = [base_dir] + [os.path.join(base_dir, sub) for sub in subdirs]
    
    # 2. Ingredient dictionaries
    normal_ingredients = [
        "Flour", "Sugar", "Brown Sugar", "Butter", "Eggs", "Milk", 
        "Vanilla Extract", "Cinnamon", "Nutmeg", "Chocolate Chips", 
        "Baking Powder", "Salt", "Apples", "Pecans"
    ]
    
    expensive_ingredients = [
        "Saffron", "Iranian Saffron", "Caviar", "Black Caviar", 
        "Truffles", "White Truffles", "Truffle Oil"
    ]
    
    # 3. Generate 300+ files to simulate scale and noise
    for i in range(350):
        # Choose a random directory
        target_dir = random.choice(all_dirs)
        
        # Determine file category
        category = random.choices(
            ["valid", "expensive", "missing_ingredients", "noise_ext"], 
            weights=[40, 20, 20, 20], 
            k=1
        )[0]
        
        if category == "noise_ext":
            filename = f"recipe_scan_{i}.{random.choice(['bak', 'dat', 'tmp', 'log'])}"
        else:
            filename = f"recipe_{i}.txt"
            
        filepath = os.path.join(target_dir, filename)
        
        content = f"Recipe ID: {i}\nDate: 202{random.randint(0,3)}-0{random.randint(1,9)}-12\n\n"
        
        header = random.choice(["Ingredients:", "[Ingredients]", "iNgReDiEnTs:", "[iNgredients]"])
        
        if category == "missing_ingredients":
            content += "Instructions:\nJust wing it! Mix what you have and pray.\nGrandma always said love is the main ingredient.\n"
        else:
            content += f"{header}\n"
            
            # Select 3 to 7 normal ingredients
            chosen_ings = random.sample(normal_ingredients, random.randint(3, 7))
            
            # If expensive, swap one out for an expensive ingredient
            if category == "expensive":
                chosen_ings[0] = random.choice(expensive_ingredients)
                
            # Randomize casing to test robustness
            for ing in chosen_ings:
                casing_choice = random.choice(["title", "lower", "upper", "weird"])
                display_ing = ing
                if casing_choice == "lower":
                    display_ing = ing.lower()
                elif casing_choice == "upper":
                    display_ing = ing.upper()
                elif casing_choice == "weird":
                    display_ing = "".join(random.choice([c.upper(), c.lower()]) for c in ing)
                    
                qty = random.choice([0.5, 1.0, 1.5, 2.0, 3, 4, 5])
                content += f"{display_ing}: {qty}\n"
                
            content += "\nInstructions:\n"
            content += f"Bake at {random.choice([350, 375, 400])} degrees for a while.\n"
            
        with open(filepath, "w") as f:
            f.write(content)

if __name__ == "__main__":
    create_files()
