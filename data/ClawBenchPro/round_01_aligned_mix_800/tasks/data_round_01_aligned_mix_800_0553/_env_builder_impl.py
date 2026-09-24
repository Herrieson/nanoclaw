import os
import json
import random

def build_env():
    # Setup directories
    os.makedirs("church_funds", exist_ok=True)
    os.makedirs("church_documents", exist_ok=True)
    
    # Write Pastor's memo
    with open("church_documents/pastor_memo.txt", "w") as f:
        f.write("Memo from Pastor John\n")
        f.write("Date: Oct 1, 2023\n\n")
        f.write("Thank you to all volunteers for the upcoming Bake Sale! ")
        f.write("When sorting the funds, please remember that ONLY items categorized strictly as ")
        f.write("'Baked_Goods', 'Beverages_Homemade', or 'Preserves' will go to the Bake Sale fund.\n")
        f.write("Categories like 'Crafts', 'Donations', 'Fuel', 'Tobacco', or anything else must go to their respective separate accounts. ")
        f.write("God bless!\n")

    # Fixed seed for reproducibility of noise
    random.seed(1533)
    
    categories = ["Fuel", "Tobacco", "Snacks_Retail", "Personal", "Donations", "Crafts", 
                  "Baked_Goods", "Beverages_Homemade", "Preserves"]
    types = ["sale", "sale", "sale", "sale", "refund", "void", "expense"]
    
    # Generate 31 days of logs for October 2023
    for day in range(1, 32):
        day_dir = f"receipts/2023/10/{day:02d}"
        os.makedirs(day_dir, exist_ok=True)
        
        # Generate 10-25 junk files per day
        num_files = random.randint(10, 25)
        for i in range(num_files):
            file_data = {
                "batch_id": f"batch_{day:02d}_{i:03d}",
                "timestamp": f"2023-10-{day:02d}T10:00:00Z",
                "transactions": []
            }
            
            num_tx = random.randint(1, 5)
            for j in range(num_tx):
                cat = random.choice(categories)
                amt = round(random.uniform(1.0, 100.0), 2)
                use_cents = random.choice([True, False])
                tx = {
                    "item_name": f"Random Item {cat} {j}",
                    "category": cat,
                    "transaction_type": random.choice(types),
                }
                if use_cents:
                    tx["amount_cents"] = int(amt * 100)
                else:
                    tx["amount_usd"] = amt
                    
                file_data["transactions"].append(tx)
                
            with open(f"{day_dir}/pos_export_{i:03d}.json", "w") as f:
                json.dump(file_data, f, indent=2)

    # ---------------------------------------------------------
    # Inject Ground Truth Data precisely on October 15th, 2023
    # ---------------------------------------------------------
    target_dir = "receipts/2023/10/15"
    
    # 1. Valid JSON items mixed into specific files
    gt_file_1 = {
        "batch_id": "batch_15_901",
        "timestamp": "2023-10-15T09:15:00Z",
        "transactions": [
            {"item_name": "Pecan Pie", "category": "Baked_Goods", "transaction_type": "sale", "amount_usd": 15.50}, # Valid: 15.50
            {"item_name": "Pump 4 Unleaded", "category": "Fuel", "transaction_type": "sale", "amount_usd": 42.00}, # Invalid
            {"item_name": "Sweet Tea Jug", "category": "Beverages_Homemade", "transaction_type": "sale", "amount_cents": 850} # Valid: 8.50
        ]
    }
    with open(f"{target_dir}/pos_export_901.json", "w") as f:
        json.dump(gt_file_1, f, indent=2)

    gt_file_2 = {
        "batch_id": "batch_15_902",
        "timestamp": "2023-10-15T11:30:00Z",
        "transactions": [
            {"item_name": "Strawberry Jam", "category": "Preserves", "transaction_type": "sale", "amount_usd": 12.00}, # Valid: 12.00
            {"item_name": "Youth Choir Donation", "category": "Donations", "transaction_type": "sale", "amount_usd": 20.00}, # Invalid
            {"item_name": "Burnt Cookies", "category": "Baked_Goods", "transaction_type": "refund", "amount_usd": 5.00} # Invalid (refund)
        ]
    }
    with open(f"{target_dir}/pos_export_902.json", "w") as f:
        json.dump(gt_file_2, f, indent=2)

    gt_file_3 = {
        "batch_id": "batch_15_903",
        "timestamp": "2023-10-15T13:45:00Z",
        "transactions": [
            {"item_name": "Marlboro Lights", "category": "Tobacco", "transaction_type": "sale", "amount_cents": 850}, # Invalid
            {"item_name": "Giant Cinnamon Roll", "category": "Baked_Goods", "transaction_type": "sale", "amount_cents": 2200} # Valid: 22.00
        ]
    }
    with open(f"{target_dir}/pos_export_903.json", "w") as f:
        json.dump(gt_file_3, f, indent=2)

    # 2. Add the scribbles.txt for the manual cash transactions
    with open(f"{target_dir}/scribbles.txt", "w") as f:
        f.write("App crashed! Writing down cash sales temporarily:\n")
        f.write("- Sold a whole tray of Mary's brownies for 20.00 cash.\n")
        f.write("- Mrs. Higgins bought a Lemon Pound Cake: 18.00.\n")
        f.write("- Took 5.00 out of the till to buy a coffee next door (expense, do not count).\n")
        f.write("- Someone gave me 10.00 for the youth choir (donation).\n")
        
    # Final Math Check:
    # JSON Valid: 15.50 + 8.50 + 12.00 + 22.00 = 58.00
    # Scribble Valid: 20.00 + 18.00 = 38.00
    # Total Expected = 96.00

if __name__ == "__main__":
    build_env()
