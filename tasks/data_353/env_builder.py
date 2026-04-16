import os
import json

def build_env():
    base_dir = "assets/data_353"
    os.makedirs(base_dir, exist_ok=True)

    # 14 batches of Lavender Dream in total.
    # 14 * 150 = 2100 required.
    plan = """Monday:
- 3x Lavender Dream
- 2x Citrus Burst

Tuesday:
- 5x Lavender Dream
- 1x Ocean Breeze

Wednesday:
- 1x Oatmeal Soothe

Thursday:
- 4x Lavender Dream

Friday:
- 2x Lavender Dream
- 2x Citrus Burst
"""
    with open(os.path.join(base_dir, "production_plan.txt"), "w", encoding="utf-8") as f:
        f.write(plan)

    formulas = {
        "Lavender Dream": {
            "Lye": 500,
            "Olive Oil": 2000,
            "Lavender Essential Oil": 150
        },
        "Citrus Burst": {
            "Lye": 500,
            "Olive Oil": 2000,
            "Lemon Essential Oil": 200
        },
        "Ocean Breeze": {
            "Lye": 500,
            "Coconut Oil": 1500,
            "Sea Salt": 100
        },
        "Oatmeal Soothe": {
            "Lye": 500,
            "Olive Oil": 1800,
            "Oatmeal": 300
        }
    }
    with open(os.path.join(base_dir, "formulas.json"), "w", encoding="utf-8") as f:
        json.dump(formulas, f, indent=4)

    # Current inventory: 1250.
    # Shortage: 2100 - 1250 = 850.
    # Intentional OCR errors: '0' instead of 'O', 'l' instead of '1', 'O' instead of '0'
    inventory = """Item,Quantity
Lye,50000
0live 0il,l0000
Lemon Essential 0il,2000
Lavender Essential 0il,l25O
C0c0nut 0il,5000
Sea Sa1t,1000
0atmea1,2000
"""
    with open(os.path.join(base_dir, "inventory.csv"), "w", encoding="utf-8") as f:
        f.write(inventory)

if __name__ == "__main__":
    build_env()
