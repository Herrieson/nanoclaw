import os
import sqlite3
import json

def setup_environment():
    base_path = "assets/data_75"
    os.makedirs(base_path, exist_ok=True)
    os.makedirs(f"{base_path}/legacy_scripts", exist_ok=True)

    # 1. 创建合规性规则说明 (模糊指示)
    compliance_rules = """
    CALIFORNIA SB-258 EXTENSION (MOCK)
    ----------------------------------
    Regulation for Natural Skincare:
    1. Every product containing allergens (Lavender Oil, Citric Acid) must be flagged.
    2. Environmental Score Calculation:
       - Base Score: 100
       - If contains 'Synthetic Fragrance': -50
       - If contains 'Parabens': -40
       - If contains 'Lavender Oil': +10 (Natural antioxidant)
       - If contains 'Citric Acid': +5 (Natural preservative)
    3. Output must be a JSON array with product name, flag, and final_score.
    """
    with open(f"{base_path}/compliance_rules.txt", "w") as f:
        f.write(compliance_rules)

    # 2. 创建加密的数据库
    db_path = f"{base_path}/inventory.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE products (id INTEGER, name TEXT, ingredients_encrypted BLOB)")
    
    # 异或加密函数 (Key: Rosemary)
    def xor_encrypt(data, key="Rosemary"):
        key = (key * (len(data) // len(key) + 1))[:len(data)]
        return bytes([b1 ^ b2 for b1, b2 in zip(data.encode(), key.encode())])

    products = [
        (1, "Lavender Calm Serum", "Lavender Oil, Water, Glycerin, Synthetic Fragrance"),
        (2, "Eco-Bright Face Wash", "Citric Acid, Aloe Vera, Water"),
        (3, "Pure Rose Moisturizer", "Rose Oil, Water, Parabens"),
        (4, "Morning Dew Mist", "Water, Citric Acid, Lavender Oil")
    ]

    for p in products:
        encrypted_ing = xor_encrypt(p[2])
        cursor.execute("INSERT INTO products VALUES (?, ?, ?)", (p[0], p[1], encrypted_ing))
    
    conn.commit()
    conn.close()

    # 3. 创建损坏的旧脚本
    broken_script = """
import sqlite3
import json

# I think the key was 'Rosemary'? 
# I failed to implement the XOR part correctly - Mike
def get_report():
    conn = sqlite3.connect('../inventory.db')
    # BUG: Wrong table name or column?
    data = conn.execute("SELECT * FROM items").fetchall()
    # TODO: Decrypt ingredients using XOR with 'Rosemary'
    # TODO: Calculate scores
    print("This script is unfinished and broken.")

if __name__ == "__main__":
    get_report()
    """
    with open(f"{base_path}/legacy_scripts/report_gen.py", "w") as f:
        f.write(broken_script)

    # 4. 额外迷惑文件
    with open(f"{base_path}/notes.txt", "w") as f:
        f.write("Need to remember: Rosemary is the secret to everything. Organic is better.")

if __name__ == "__main__":
    setup_environment()
