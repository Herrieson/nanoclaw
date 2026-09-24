import os
import csv

def build():
    # Create directories
    os.makedirs("notes", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # 1. Create vendor database
    vendor_data = [
        ["Ingredient", "Cost_Per_Unit", "Calories_Per_Unit"],
        ["Sweet_Corn", "0.50", "50"],
        ["Pinto_Beans", "0.30", "80"],
        ["Winter_Squash", "0.80", "40"],
        ["Ground_Bison", "3.00", "200"],
        ["Whole_Wheat_Buns", "0.50", "150"],
        ["Secret_Zesty_Sauce", "0.20", "50"]
    ]
    with open("data/vendor_db.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(vendor_data)

    # 2. Create Recipe Notes (simulating a PDF file)
    # Since we might not have fpdf in the builder env, we create a text-based PDF or a simple file
    # For the sake of the evaluation environment stability, we will generate a text file 
    # but the prompt tells the agent it's a PDF. 
    # If the environment supports it, we'd use a real PDF library.
    recipe_content = """
    CHEROKEE HERITAGE MENU - BRAINSTORMING
    
    Meal 1: ThreeSistersStew
    - Sweet_Corn: 3 handfuls per serving
    - Pinto_Beans: 2 scoops per serving
    - Winter_Squash: 1.0 units per serving

    Meal 2: BisonSliders
    - Ground_Bison: 4 handfuls per serving
    - Whole_Wheat_Buns: 1.0 units per serving
    - Secret_Zesty_Sauce: 1 scoop per serving
    
    Note: Refer to the Heritage Decoder for measurement conversions!
    """
    # Writing as .pdf but it's plain text for this mock - in a real high-end env we'd use fpdf
    with open("notes/recipe_ideas.pdf", "w", encoding="utf-8") as f:
        f.write(recipe_content)

if __name__ == "__main__":
    build()
