import os

def create_files():
    os.makedirs("recipes", exist_ok=True)
    
    recipe1 = """Aunt Sally's Pie
Ingredients:
Apples: 3
Flour: 2
Sugar: 1
Butter: 1

Instructions:
Bake it well.
"""
    with open("recipes/aunt_sallys_pie.txt", "w") as f:
        f.write(recipe1)

    recipe2 = """Wild Experiment 7
Ingredients:
Flour: 1
Saffron: 2
Eggs: 3

Instructions:
Mix and pray.
"""
    with open("recipes/wild_experiment_7.txt", "w") as f:
        f.write(recipe2)

    recipe3 = """Church Cookies
Ingredients:
Flour: 1
Butter: 1
Sugar: 0.5
Vanilla: 1

Instructions:
Sweet and simple.
"""
    with open("recipes/church_cookies.txt", "w") as f:
        f.write(recipe3)

    recipe4 = """Mystery Cake
Instructions:
Just mix the wet and dry ingredients and bake at 350 for an hour.
Wait, where did the ingredients go?
"""
    with open("recipes/mystery_cake.txt", "w") as f:
        f.write(recipe4)

    recipe5 = """Fancy Truffle Bites
Ingredients:
Chocolate: 2
Truffle: 1
Cream: 1

Instructions:
Too expensive to make.
"""
    with open("recipes/fancy_truffle_bites.txt", "w") as f:
        f.write(recipe5)

if __name__ == "__main__":
    create_files()
