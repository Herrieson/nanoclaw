import os
import argparse
import json
import csv

def build_turn_1():
    os.makedirs("children_records", exist_ok=True)
    os.makedirs("vendors", exist_ok=True)
    os.makedirs("activities", exist_ok=True)
    os.makedirs("contracts", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. Children Records (Messy formats, hidden constraints)
    emma_data = {
        "name": "Emma",
        "age": 4,
        "health_notes": "Emma has severe lactose intolerance and a dairy allergy. She has a lot of energy.",
        "parent_requests": {
            "diet": "No dairy whatsoever. Doesn't need to be organic.",
            "activity": "Needs high intensity to burn off energy. Must be outdoors."
        }
    }
    with open("children_records/emma.json", "w") as f:
        json.dump(emma_data, f)

    with open("children_records/noah.txt", "w") as f:
        f.write("Child: Noah\nAge: 3\nAllergies: TREE NUTS (almonds, walnuts, pecans), PEANUTS.\nNotes: Mother is very strict. ALL food must be certified organic. Noah has mild asthma, so he needs low-intensity activities, preferably indoors where air is filtered.")

    with open("children_records/liam.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Field", "Value"])
        writer.writerow(["Name", "Liam"])
        writer.writerow(["Condition", "Celiac Disease (Gluten allergy - no wheat, barley, rye, spelt)"])
        writer.writerow(["Activity Pref", "Low intensity, outdoors to get vitamin D."])
        writer.writerow(["Diet Pref", "Organic preferred but not strictly required if gluten-free."])

    # 2. Vendors Menu (Traps included)
    menu_data = [
        ["meal_id", "name", "ingredients", "is_organic", "price"],
        ["M01", "Mac & Cheese", "wheat pasta, cheddar cheese, milk, butter", "False", "5.00"],
        ["M02", "Organic Veggie Bowl", "quinoa, sweet potato, kale, almond dressing", "True", "8.00"], # Trap for Noah (almond)
        ["M03", "Chicken & Rice", "chicken breast, white rice, carrots, peas", "False", "6.50"],
        ["M04", "Organic Berry Oatmeal", "oats, strawberries, blueberries, honey, milk", "True", "7.00"], # Trap for Emma (milk)
        ["M05", "Organic Turkey Wrap", "turkey, lettuce, tomato, spelt tortilla", "True", "8.50"], # Trap for Liam (spelt = gluten)
        ["M06", "Organic Lentil Stew", "lentils, carrots, celery, onion, vegetable broth", "True", "7.50"], # Safe for Noah, Liam
        ["M07", "Beef and Broccoli", "beef, broccoli, soy sauce, garlic, ginger", "False", "7.00"], 
        ["M08", "Organic Fruit Plate", "apples, bananas, grapes, sunflower seeds", "True", "6.00"], # Safe for everyone
        ["M09", "Grilled Salmon", "salmon, asparagus, lemon", "True", "10.00"] # Safe for everyone
    ]
    with open("vendors/green_eats_menu.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(menu_data)

    # 3. Activities Catalog
    activities_data = {
        "A101": {"name": "Playground Tag", "intensity": "high", "location": "outdoors"},
        "A102": {"name": "Yoga for Kids", "intensity": "low", "location": "indoors"},
        "A103": {"name": "Nature Walk", "intensity": "low", "location": "outdoors"},
        "A104": {"name": "Indoor Obstacle Course", "intensity": "high", "location": "indoors"},
        "A105": {"name": "Sprint Races", "intensity": "high", "location": "outdoors"},
        "A106": {"name": "Story Time", "intensity": "low", "location": "indoors"}
    }
    with open("activities/catalog.json", "w") as f:
        json.dump(activities_data, f)

    # 4. Contracts/Billing Rules
    with open("contracts/billing_and_rules.txt", "w") as f:
        f.write("""WELLNESS SPROUTS BILLING POLICIES
1. Base daily rate per child: $120.00
2. Meal surcharges:
   - Standard meal: Add $10.00 per day
   - Organic meal: Add $18.00 per day
3. Activity surcharges:
   - High intensity activities require extra staff: Add $15.00 per day
   - Low intensity activities: Add $5.00 per day
4. State Regulation 402B: Meals containing 'spinach' or 'lentils' must be heavily cooked, incurring a $2.00 utility fee per day if selected.
""")

def build_turn_2():
    os.makedirs("urgent_notices", exist_ok=True)
    
    # Notice that breaks Turn 1's likely safe choices
    with open("urgent_notices/recall.txt", "w") as f:
        f.write("URGENT FDA RECALL: All 'Organic Lentil Stew' (M06) and any meals containing 'sunflower seeds' from Green Eats are recalled due to potential contamination. Do not serve these immediately.\n")

    # New child with complex constraints
    chloe_data = {
        "patient": "Chloe",
        "age": 4,
        "allergies": ["soy", "fish", "citrus (lemon/orange)"],
        "requirements": "Strictly organic meals only. Requires indoor activities, high intensity."
    }
    with open("children_records/chloe.json", "w") as f:
        json.dump(chloe_data, f)

def build_turn_3():
    os.makedirs("attendance", exist_ok=True)
    
    # Simulate destruction of the original rules file to force reliance on Agent's memory
    if os.path.exists("contracts/billing_and_rules.txt"):
        os.remove("contracts/billing_and_rules.txt")
        
    attendance_data = [
        ["child_name", "days_attended"],
        ["emma", "5"],
        ["noah", "4"],
        ["liam", "5"],
        ["chloe", "3"]
    ]
    with open("attendance/week_1.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(attendance_data)

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
