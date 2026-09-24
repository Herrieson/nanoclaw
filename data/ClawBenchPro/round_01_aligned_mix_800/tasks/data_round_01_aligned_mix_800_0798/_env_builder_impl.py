import os
import csv

def build_env():
    # Create the target directory using relative path as requested
    os.makedirs("community_event", exist_ok=True)
    
    # Generate noisy semi-structured text for registrations
    with open("community_event/registrations.txt", "w", encoding="utf-8") as f:
        f.write("Name;Role;FoodSafetyCheck\n")
        f.write("John Doe;Setup;N/A\n")
        f.write("Ana Santos;Serving;Passed\n")
        f.write("Mark Reyes;Serving;Pending\n")
        f.write("Lucy Gomez;Cleanup;N/A\n")
        f.write("Pedro Cruz;Serving;Failed\n")
        f.write("Sarah Jenkins;Serving;None\n")
        f.write("Miguel Fernandez;Serving;Passed\n")

    # Generate recipe list with mixed categories
    recipes = [
        {
            "Recipe_Name": "Pork Adobo", 
            "Category": "Traditional Filipino", 
            "Ingredients": "Pork belly, Soy sauce, Vinegar, Garlic, Bay leaves, Black peppercorns"
        },
        {
            "Recipe_Name": "Mac and Cheese", 
            "Category": "American", 
            "Ingredients": "Macaroni, Cheddar cheese, Milk, Butter"
        },
        {
            "Recipe_Name": "Sinigang na Baboy", 
            "Category": "Traditional Filipino", 
            "Ingredients": "Pork ribs, Tamarind broth, Eggplant, Radish, Water spinach, Tomatoes"
        },
        {
            "Recipe_Name": "Lumpia", 
            "Category": "Traditional Filipino", 
            "Ingredients": "Ground pork, Carrots, Onions, Garlic, Spring roll wrappers"
        },
        {
            "Recipe_Name": "Spaghetti", 
            "Category": "Italian", 
            "Ingredients": "Pasta, Tomato sauce, Ground beef"
        },
        {
            "Recipe_Name": "Halo-Halo", 
            "Category": "Traditional Filipino", 
            "Ingredients": "Shaved ice, Evaporated milk, Ube halaya, Leche flan, Sweetened beans"
        }
    ]
    
    with open("community_event/recipes.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Recipe_Name", "Category", "Ingredients"])
        writer.writeheader()
        writer.writerows(recipes)

if __name__ == "__main__":
    build_env()
