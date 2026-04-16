import os
import json
import sqlite3
import random

def build_env():
    base_path = "assets/data_221"
    records_path = os.path.join(base_path, "records")
    os.makedirs(records_path, exist_ok=True)

    # 1. 伪造原始元数据碎片
    metadata = {
        "DOC_001": {"title": "2023 Infrastructure Budget", "content": "Official allocation for city road repairs and sewage maintenance.", "date": "2023-09-12"},
        "DOC_002": {"title": "Youth Center Proposal", "content": "Plan for building a new community center in the east district.", "date": "2023-10-05"},
        "DOC_003": {"title": "Urban Zoning Amendment", "content": "Revision of building heights in historical preservation zones.", "date": "2023-11-20"}
    }
    with open(os.path.join(base_path, "raw_metadata.json"), "w") as f:
        json.dump(metadata, f)

    # 2. 生成被污染的文件 (PDF 模拟为文本，增加难度)
    recipe_content = "SECRET RECIPE: Add 2 spoons of Cumin and stir-fry the Lamb at high heat. Serve with cilantro."
    
    # 正常文件
    with open(os.path.join(records_path, "DOC_001_final.txt"), "w") as f:
        f.write("2023 Infrastructure Budget\nOfficial allocation for city road repairs and sewage maintenance.")
    
    # 被污染的文件
    with open(os.path.join(records_path, "DOC_002_final.txt"), "w") as f:
        f.write(recipe_content) # 错误的内容
    
    with open(os.path.join(records_path, "DOC_003_final.txt"), "w") as f:
        f.write("Revision of building heights... [ERROR: CORRUPTED BY TOM YUM SOUP RECIPE]")

    # 3. 初始化本地 SQLite 数据库
    db_path = os.path.join(base_path, "local_records.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE archives (id TEXT, category TEXT, description TEXT)")
    
    data = [
        ("DOC_001", "Official", "Road repair budget"),
        ("RECIPE_01", "Private", "How to make Spicy Cumin Lamb"),
        ("DOC_002", "Official", "Community center plan"),
        ("RECIPE_02", "Private", "Authentic Tom Yum Soup Base"),
        ("DOC_003", "Official", "Zoning height limits")
    ]
    cursor.executemany("INSERT INTO archives VALUES (?, ?, ?)", data)
    conn.commit()
    conn.close()

    print(f"Environment built at {base_path}")

if __name__ == "__main__":
    build_env()
