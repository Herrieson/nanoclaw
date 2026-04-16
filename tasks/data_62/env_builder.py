import os

def build_env():
    base_dir = "assets/data_62"
    os.makedirs(base_dir, exist_ok=True)

    log_content = """[2023-10-27 10:00:01] INFO system started.
[2023-10-27 10:02:11] WARN memory usage high.
[2023-10-27 10:05:22] DEBUG incoming payload: {"id": "B01", "name": "Reusable Cotton Bag", "supplier_code": "SUP-101", "price": 4.25}
[2023-10-27 10:06:00] ERROR failed to load image for B01
[2023-10-27 10:08:14] DEBUG incoming payload: {"id": "B02", "name": "Hemp Tote", "supplier_code": "SUP-102", "price": 6.50}
[2023-10-27 10:09:45] INFO user logged out.
[2023-10-27 10:10:00] DEBUG incoming payload: {"id": "B03", "name": "Recycled Plastic Bag", "supplier_code": "SUP-103", "price": 1.50}
[2023-10-27 10:11:11] WARN sync delayed.
[2023-10-27 10:15:22] DEBUG incoming payload: {"id": "B04", "name": "Beeswax Wrap", "supplier_code": "SUP-101", "price": 5.00}
[2023-10-27 10:18:30] DEBUG incoming payload: {"id": "B05", "name": "Bamboo Utensils", "supplier_code": "SUP-104", "price": 3.75}
[2023-10-27 10:20:01] INFO system shut down.
"""

    csv_content = """code,supplier_name,sustainability_score,contact
SUP-101,Tierra Viva,9,maria@tierraviva.mx
SUP-102,Green Alternatives,8,info@greenalt.com
SUP-103,CheapPack,4,sales@cheappack.com
SUP-104,EcoFake Co,6,boss@ecofake.com
"""

    with open(os.path.join(base_dir, "system_export.log"), "w", encoding="utf-8") as f:
        f.write(log_content)

    with open(os.path.join(base_dir, "suppliers.csv"), "w", encoding="utf-8") as f:
        f.write(csv_content)

if __name__ == "__main__":
    build_env()
