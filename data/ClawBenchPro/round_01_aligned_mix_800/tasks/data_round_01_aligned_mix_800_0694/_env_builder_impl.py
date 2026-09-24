import os

def build_env():
    os.makedirs('supplier_drops', exist_ok=True)
    os.makedirs('notes', exist_ok=True)

    raw_inventory_content = """ItemID,BeadType,Color,Price,Stock
B001,  Kingman Turquoise ,Blue,$4.50,100
B002,Sterling Silver Spacer, Silver,1.20 USD, 500
B003,Red Coral,Red, 0.75 ,200
B004,Cedar Pendant, Brown ,$15.00 ,20
B005,Plastic Bead,Neon Green,0.10,1000
B006,  Obsidian  ,Black,  3.25, 40
B007,Glass Seed Bead, White, 0.05, 5000
B008, Gold Clasp, Gold, $4.00, 50
"""
    with open('supplier_drops/raw_inventory.csv', 'w', encoding='utf-8') as f:
        f.write(raw_inventory_content)

    recipe_content = """Salish Sea Amulet Recipe:
- 5x Kingman Turquoise
- 2x Sterling Silver Spacer
- 10x Red Coral
- 1x Cedar Pendant

Make sure to grab the exact names from the inventory!
"""
    with open('notes/amulet_recipe.txt', 'w', encoding='utf-8') as f:
        f.write(recipe_content)

if __name__ == '__main__':
    build_env()
