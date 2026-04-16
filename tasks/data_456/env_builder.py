import os
import shutil

def build_env():
    base_dir = "assets/data_456"
    backup_dir = os.path.join(base_dir, "phone_backup")
    
    # Clean up and recreate directories
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(backup_dir)

    # 1. Work files with expenses
    work_file_1 = os.path.join(backup_dir, "log_march_22.txt")
    with open(work_file_1, "w", encoding="utf-8") as f:
        f.write("Just another day at the CON-Site.\nBought some extra nails and tape: $25.00\nLunch was good.\nReplaced a broken hammer: $15.50\n")

    work_file_2 = os.path.join(backup_dir, "notes_misc.log")
    with open(work_file_2, "w", encoding="utf-8") as f:
        f.write("Need to remember to pick up groceries.\nPaid for jefe's tools repair at the shop: $105.00\nAlso gas: $40.00 (Wait, this is personal, but it's in the same file so the script should catch it if doing simple regex).\nActually, let's keep it simple: $40.00 is gas, but I asked to extract all dollar amounts in files matching the keywords. Total for this file should be 145.00.\n")

    # 2. Work files without expenses or keywords (Junk)
    work_file_3 = os.path.join(backup_dir, "random_thoughts.txt")
    with open(work_file_3, "w", encoding="utf-8") as f:
        f.write("Man, the game last night was crazy. Can't believe they missed that penalty. Spent $50.00 on drinks.")

    # 3. Recipe files that match criteria
    recipe_1 = os.path.join(backup_dir, "salsa_verde.txt")
    with open(recipe_1, "w", encoding="utf-8") as f:
        f.write("Esta es la receta de la abuela.\nYou will need: tomatillo, onion, garlic, jalapeño, cilantro.\nBlend it all together.\n")

    recipe_2 = os.path.join(backup_dir, "tamales_prep.md")
    with open(recipe_2, "w", encoding="utf-8") as f:
        f.write("Weekend tamales recipe.\nIngredients:\n- 2 lbs masa\n- pork shoulder\n- dried chiles\nMix the masa well.\n")

    # 4. Recipe files that DO NOT match criteria
    recipe_3 = os.path.join(backup_dir, "burger_recipe.txt")
    with open(recipe_3, "w", encoding="utf-8") as f:
        f.write("Good ol' American burger recipe.\nBeef, buns, cheddar cheese, ketchup.\n")

    # 5. Non-recipe files that have the ingredients (Junk)
    junk_1 = os.path.join(backup_dir, "shopping_list.txt")
    with open(junk_1, "w", encoding="utf-8") as f:
        f.write("Don't forget to buy masa, tomatillo, and some beer for the game.")

    # 6. Binary/Junk file
    with open(os.path.join(backup_dir, "corrupted_img.bin"), "wb") as f:
        f.write(b'\x00\xFF\x88\x99' * 100)

if __name__ == "__main__":
    build_env()
