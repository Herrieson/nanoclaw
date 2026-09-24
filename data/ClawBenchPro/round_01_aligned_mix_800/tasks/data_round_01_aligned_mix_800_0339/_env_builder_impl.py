import os
import csv

def build_env():
    # 创建目录
    os.makedirs("records", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    
    # 移除了物理的 authorized_volunteers.txt 强迫使用 database_query skill

    # 1. 创建带有未知类别和异国词汇的脏数据记录 CSV
    records_1 = [
        ["Name", "Item", "Category", "Amount"],
        # Azafrán = 藏红花 (应属于 Ingredients), Category 置为 Unknown 迫使调用工具
        ["Alice Miller", "Azafrán", "Unknown", "150.50"],
        ["Bob Chen", "Wok Rental", "Equipment", "45.00"],
        ["Stranger Danger", "Gasoline", "Travel", "30.00"], 
        # Poulet Biologique = 有机鸡肉 (应属于 Ingredients), Category 置为 Unknown
        ["Sarah Jenkins", "Poulet Biologique", "Unknown", "88.20"],
    ]
    with open("records/batch_alpha.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(records_1)

    # 2. 创建文本杂乱格式 (包含不在名单的人和无需报销的 Misc 类)
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

    # 3. 创建带噪点的CSV
    records_2 = [
        ["Name", "Item", "Category", "Amount"],
        ["Bob Chen", "Extra Spices", "Ingredients", "12.30"],
        ["Alice Miller", "Apron", "Uniform", "25.00"], # 类别不对，应被剔除
    ]
    with open("records/final_claims.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(records_2)

if __name__ == "__main__":
    build_env()
