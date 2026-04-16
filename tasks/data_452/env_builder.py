import os

def build_env():
    base_dir = "assets/data_452"
    os.makedirs(base_dir, exist_ok=True)

    catalog = """[SYS LOG 08:00] Start export
ITEM_CODE: 001 | NAME: Organic Apples | PRICE: $1.50
[SYS LOG 08:01] Buffer overflow on node 4
ITEM_CODE: 002 | NAME: Whole Milk 1 Gal | PRICE: $3.20
ITEM_CODE: 003 | NAME: Canned Black Beans | PRICE: $0.80
[WARN] Skipping corrupted entry near line 45
ITEM_CODE: 004 | NAME: Ground Beef 80/20 | PRICE: $4.50
ITEM_CODE: 005 | NAME: Almonds Bulk | PRICE: $8.00
[SYS LOG 08:02] End export"""

    with open(os.path.join(base_dir, "catalog_export.dat"), "w", encoding="utf-8") as f:
        f.write(catalog)

    order = """Organic Apples, 120
Whole Milk 1 Gal, 50
Canned Black Beans, 200
Ground Beef 80/20, 30"""

    with open(os.path.join(base_dir, "smith_grocers_order.txt"), "w", encoding="utf-8") as f:
        f.write(order)

    setlist = """1. Sweet Home Alabama
2. Hotel California
3. Free Bird (if time permits)
4. Take It Easy"""

    with open(os.path.join(base_dir, "setlist.txt"), "w", encoding="utf-8") as f:
        f.write(setlist)

if __name__ == "__main__":
    build_env()
