import os
import csv
import json

def build_env():
    # 创建目录
    os.makedirs("records", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. 创建白名单
    authorized = ["Alice Miller", "Bob Chen", "Sarah Jenkins", "David Strauss", "Linda Goldstein"]
    with open("authorized_volunteers.txt", "w", encoding='utf-8') as f:
        f.write("\n".join(authorized))

    # 2. 创建脏数据记录
    # 记录1：CSV格式，含混合数据
    records_1 = [
        ["Name", "Item", "Category", "Amount"],
        ["Alice Miller", "Saffron from Spain", "Ingredients", "150.50"],
        ["Bob Chen", "Wok Rental", "Equipment", "45.00"],
        ["Stranger Danger", "Gasoline", "Travel", "30.00"], # 不在名单，类别不对
        ["Sarah Jenkins", "Organic Chicken", "Ingredients", "88.20"],
    ]
    with open("records/batch_alpha.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(records_1)

    # 记录2：文本杂乱格式
    raw_text = """
    ENTRY ID: 002
    VOLUNTEER: Linda Goldstein
    PURCHASE: Industrial Blender
    DEPT: Equipment
    COST: 320.00
    ---
    ENTRY ID: 003
    VOLUNTEER: David Strauss
    PURCHASE: Parking Fee
    DEPT: Misc
    COST: 15.00
    ---
    ENTRY ID: 004
    VOLUNTEER: Malicious User
    PURCHASE: Caviar
    DEPT: Ingredients
    COST: 500.00
    """
    with open("records/notes_july.txt", "w", encoding='utf-8') as f:
        f.write(raw_text)

    # 记录3：带噪点的CSV
    records_2 = [
        ["Name", "Item", "Category", "Amount"],
        ["Bob Chen", "Extra Spices", "Ingredients", "12.30"],
        ["Alice Miller", "Apron", "Uniform", "25.00"], # 类别不对
    ]
    with open("records/final_claims.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(records_2)

if __name__ == "__main__":
    build_env()
