import os
import argparse
import csv
import json

def build_turn_1():
    os.makedirs("district_policies", exist_ok=True)
    os.makedirs("recipes/first_drafts", exist_ok=True)
    
    # Policy file
    policy_content = """
    OFFICIAL DISTRICT MEAL POLICY - OKLAHOMA STATE EDU
    --------------------------------------------------
    1. Financials: The absolute maximum budget for any single core meal serving is $2.80.
    2. Nutrition: 
       - Calories must be between 450 kcal and 750 kcal.
       - Sodium must strictly NOT exceed 850mg per serving.
       - Protein must be at least 15g.
    3. Allergens: Due to district-wide severe allergies, NO peanuts or tree nuts are allowed in any facility.
    """
    with open("district_policies/nutrition_standards.txt", "w", encoding="utf-8") as f:
        f.write(policy_content)
        
    # Recipes
    # Recipe 1: Fails allergen (peanuts)
    r1 = {
        "name": "Peanut Butter Power Bowl",
        "ingredients": ["Oats", "Peanut Butter", "Honey", "Milk"],
        "metrics": {"cost": 1.50, "calories": 600, "sodium": 300, "protein": 20}
    }
    # Recipe 2: Perfect, but uses Quinoa and Beef (Trap for T2)
    r2 = {
        "name": "Beef and Quinoa Skillet",
        "ingredients": ["Beef", "Quinoa", "Peppers", "Onions"],
        "metrics": {"cost": 2.40, "calories": 650, "sodium": 600, "protein": 30}
    }
    # Recipe 3: Fails sodium
    r3 = {
        "name": "Salty Ham Sandwich",
        "ingredients": ["Bread", "Ham", "Cheese", "Mustard"],
        "metrics": {"cost": 1.80, "calories": 500, "sodium": 1200, "protein": 18}
    }
    # Recipe 4: Good, safe
    r4 = {
        "name": "Three Sisters Stew",
        "ingredients": ["Corn", "Beans", "Squash", "Chicken Broth"],
        "metrics": {"cost": 1.90, "calories": 480, "sodium": 400, "protein": 16}
    }
    # Recipe 5: Good, safe
    r5 = {
        "name": "Turkey Wrap",
        "ingredients": ["Tortilla", "Turkey", "Lettuce", "Tomato"],
        "metrics": {"cost": 2.10, "calories": 550, "sodium": 700, "protein": 22}
    }
    # Recipe 6: Fails cost
    r6 = {
        "name": "Gourmet Salmon",
        "ingredients": ["Salmon", "Asparagus", "Rice"],
        "metrics": {"cost": 4.50, "calories": 600, "sodium": 500, "protein": 35}
    }
    
    recipes = {"r1": r1, "r2": r2, "r3": r3, "r4": r4, "r5": r5, "r6": r6}
    for k, v in recipes.items():
        with open(f"recipes/first_drafts/{v['name'].replace(' ', '_')}.json", "w", encoding="utf-8") as f:
            json.dump(v, f, indent=4)

def build_turn_2():
    os.makedirs("alerts", exist_ok=True)
    os.makedirs("recipes/emergency_backups", exist_ok=True)
    
    alert_content = """
    EMERGENCY MEMO: SUPPLY CHAIN DISRUPTION
    
    To all district food managers:
    Due to immediate transport strikes, the following rules apply until further notice:
    1. QUINOA is completely embargoed. Zero shipments available. Remove from all menus.
    2. BEEF prices have surged. Add $0.60 to the base cost per serving of any recipe containing Beef.
    """
    with open("alerts/supply_chain_memo.txt", "w", encoding="utf-8") as f:
        f.write(alert_content)
        
    # Backup recipes
    # Backup 1: Good, replaces r2
    b1 = {
        "name": "Chicken Bean Enchiladas",
        "ingredients": ["Chicken", "Beans", "Tortilla", "Cheese"],
        "metrics": {"cost": 2.30, "calories": 620, "sodium": 750, "protein": 25}
    }
    # Backup 2: Fails calories (too low)
    b2 = {
        "name": "Light Salad",
        "ingredients": ["Lettuce", "Tomato", "Cucumber"],
        "metrics": {"cost": 1.00, "calories": 200, "sodium": 100, "protein": 5}
    }
    # Backup 3: Fails cost limit (2.90 > 2.80)
    b3 = {
        "name": "Fancy Pork Roast",
        "ingredients": ["Pork", "Potatoes", "Carrots"],
        "metrics": {"cost": 2.90, "calories": 700, "sodium": 650, "protein": 28}
    }
    
    backups = [b1, b2, b3]
    for v in backups:
        with open(f"recipes/emergency_backups/{v['name'].replace(' ', '_')}.json", "w", encoding="utf-8") as f:
            json.dump(v, f, indent=4)

def build_turn_3():
    os.makedirs("catalogs", exist_ok=True)
    
    # For Turn 3, we expect the final recipes to be:
    # 1. Three Sisters Stew (Corn, Beans, Squash, Chicken Broth)
    # 2. Turkey Wrap (Tortilla, Turkey, Lettuce, Tomato)
    # 3. Chicken Bean Enchiladas (Chicken, Beans, Tortilla, Cheese)
    # The event requires 500 portions of EACH.
    # Total budget max = 3 meals * $2.80 * 500 = $4200.
    
    csv_data = [
        ["Ingredient", "Supplier", "Price_Per_500_Portions", "Is_Local", "Is_Indigenous"],
        ["Corn", "MegaFarm Corp", "100.00", "No", "No"],
        ["Corn", "Cherokee Heritage Farms", "150.00", "Yes", "Yes"],
        ["Beans", "National Foods", "80.00", "No", "No"],
        ["Beans", "Red Earth Co-op", "120.00", "Yes", "No"],
        ["Squash", "VeggieMart", "90.00", "No", "No"],
        ["Squash", "Oklahoma Growers", "200.00", "Yes", "No"], # Pricey trap
        ["Chicken Broth", "SoupBase Inc", "50.00", "No", "No"],
        ["Chicken Broth", "Local Bones", "70.00", "Yes", "No"],
        ["Tortilla", "BreadCorp", "100.00", "No", "No"],
        ["Tortilla", "Tulsa Millers", "130.00", "Yes", "No"],
        ["Turkey", "MeatGiant", "300.00", "No", "No"],
        ["Turkey", "Green Pastures", "450.00", "Yes", "No"], # Pricey trap
        ["Lettuce", "Leafy Co", "60.00", "No", "No"],
        ["Lettuce", "OKC Greens", "80.00", "Yes", "No"],
        ["Tomato", "Red Farms", "70.00", "No", "No"],
        ["Tomato", "Sunburst Local", "90.00", "Yes", "No"],
        ["Chicken", "MeatGiant", "250.00", "No", "No"],
        ["Chicken", "FreeRange OK", "400.00", "Yes", "No"],
        ["Cheese", "DairyKing", "150.00", "No", "No"],
        ["Cheese", "Okmulgee Dairy", "220.00", "Yes", "No"]
    ]
    
    with open("catalogs/bulk_suppliers.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
    elif args.turn == 3:
        build_turn_3()
