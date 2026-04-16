import os
import csv
import json

def build_env():
    workspace = "assets/data_223/workspace"
    os.makedirs(workspace, exist_ok=True)
    
    data = [
        {
            "item_id": "ITM001", "product_name": "Whey Protein Isolate", "category": "Supplements", 
            "nutrition": {"sugar": 2, "protein": 24, "organic": False, "ingredients": ["Whey", "Stevia", "Natural Flavors"]}
        },
        {
            "item_id": "ITM002", "product_name": "Organic Kale Chips", "category": "Snacks", 
            "nutrition": {"sugar": 1, "protein": 3, "organic": True, "ingredients": ["Kale", "Olive Oil", "Sea Salt"]}
        },
        {
            "item_id": "ITM003", "product_name": "Neon Gummy Bears", "category": "Candy", 
            "nutrition": {"sugar": 25, "protein": 0, "organic": False, "ingredients": ["Sugar", "Corn Syrup", "Artificial Colors", "Gelatin"]}
        },
        {
            "item_id": "ITM004", "product_name": "Muscle Max Bar", "category": "Supplements", 
            "nutrition": {"sugar": 12, "protein": 22, "organic": False, "ingredients": ["Soy Protein", "Chocolate", "Artificial Colors"]}
        },
        {
            "item_id": "ITM005", "product_name": "Cola Classic", "category": "Beverages", 
            "nutrition": {"sugar": 39, "protein": 0, "organic": False, "ingredients": ["Carbonated Water", "High Fructose Corn Syrup", "Caramel Color"]}
        },
        {
            "item_id": "ITM006", "product_name": "Raw Almonds", "category": "Snacks", 
            "nutrition": {"sugar": 3, "protein": 6, "organic": False, "ingredients": ["Almonds"]}
        },
        {
            "item_id": "ITM007", "product_name": "Organic Fruit Lollipops", "category": "Candy", 
            "nutrition": {"sugar": 16, "protein": 0, "organic": True, "ingredients": ["Organic Cane Sugar", "Organic Fruit Juice"]}
        },
        {
            "item_id": "ITM008", "product_name": "Zero Sugar Energy Drink", "category": "Beverages", 
            "nutrition": {"sugar": 0, "protein": 0, "organic": False, "ingredients": ["Water", "Caffeine", "Artificial Colors", "Sucralose"]}
        }
    ]
    
    csv_path = os.path.join(workspace, "incoming_truck.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["item_id", "product_name", "category", "nutrition_info"])
        for row in data:
            writer.writerow([row["item_id"], row["product_name"], row["category"], json.dumps(row["nutrition"])])

if __name__ == "__main__":
    build_env()
