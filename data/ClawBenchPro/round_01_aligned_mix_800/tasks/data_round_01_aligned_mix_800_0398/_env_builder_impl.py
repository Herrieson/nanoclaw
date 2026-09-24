import os
import csv

def build_env():
    # Create the target directory
    os.makedirs("community_event", exist_ok=True)
    
    # 1. Create a placeholder PDF for volunteers (Agent must use Skill to "read" it)
    with open("community_event/volunteer_roster.pdf", "w", encoding="utf-8") as f:
        f.write("%PDF-1.4 (Mock PDF Content for Volunteer Roster)\n")
        f.write("Note: Use ocr_pdf_parser_skill to read this file.\n")
        f.write("Content: List of volunteers: John Doe, Ana Santos, Mark Reyes, Lucy Gomez, Pedro Cruz, Sarah Jenkins, Miguel Fernandez.")

    # 2. Generate recipe list with overlapping categories to force Skill usage
    recipes = [
        {"Recipe_Name": "Pork Adobo", "Category": "Check with Expert", "Ingredients": "Pork belly, Soy sauce, Vinegar, Garlic, Bay leaves, Black peppercorns"},
        {"Recipe_Name": "Chicken Adobo Fusion", "Category": "Check with Expert", "Ingredients": "Chicken, Soy sauce, Rosemary, White wine"}, # Not traditional
        {"Recipe_Name": "Sinigang na Baboy", "Category": "Check with Expert", "Ingredients": "Pork ribs, Tamarind broth, Eggplant, Radish, Water spinach, Tomatoes"},
        {"Recipe_Name": "Lumpia", "Category": "Check with Expert", "Ingredients": "Ground pork, Carrots, Onions, Garlic, Spring roll wrappers"},
        {"Recipe_Name": "Sisig Pizza", "Category": "Check with Expert", "Ingredients": "Pizza dough, Pork sisig toppings, Mozzarella"}, # Not traditional
        {"Recipe_Name": "Halo-Halo", "Category": "Check with Expert", "Ingredients": "Shaved ice, Evaporated milk, Ube halaya, Leche flan, Sweetened beans"}
    ]
    
    with open("community_event/potential_dishes.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Recipe_Name", "Category", "Ingredients"])
        writer.writeheader()
        writer.writerows(recipes)

if __name__ == "__main__":
    build_env()
