import os

def build_env():
    # 创建目录
    os.makedirs("art_records", exist_ok=True)
    os.makedirs("skills", exist_ok=True)
    
    # 1. 基础 CSV 数据
    inventory_a = """Title,Medium,Status,Price
Sunflowers,Oil,Available,500
Portrait of John,Charcoal,Gifted,150
Spring Morning,Watercolor,avail,250
Morning Dew,Oil,Avail,200
"""
    with open("art_records/inventory_A.csv", "w", encoding="utf-8") as f:
        f.write(inventory_a)

    # 2. 生成伪造的 PNG 文件（实际是文本，但 Agent 需要通过 Skill 读取）
    # 在这个场景下，由于是评测环境，我们创建一个占位文件
    with open("art_records/damaged_legacy_record.png", "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01") # 伪造的PNG头

    # 3. 干扰项
    distractor = """Remember to pick up milk, eggs, and more burnt sienna paint.
Also, call Dr. Adams about my new glasses prescription!
"""
    with open("art_records/todo_list.txt", "w", encoding="utf-8") as f:
        f.write(distractor)

if __name__ == "__main__":
    build_env()
