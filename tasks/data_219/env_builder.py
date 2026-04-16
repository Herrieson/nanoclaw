import os
import json
import binascii

def setup_environment():
    base_path = "assets/data_219/recovery_vault"
    os.makedirs(base_path, exist_ok=True)

    # 1. 模拟原始数据 (隐藏在 Hex Dump 中)
    # 这里的书籍是 "Rare Organic Living & Vegan Smoothies" 系列
    books = [
        {"title": "The Green Alchemist", "author": "Sage Miller", "price": 45.00, "nutri_code": "NC-9921"},
        {"title": "Sprouts & Spirits", "author": "Luna Green", "price": 29.95, "nutri_code": "NC-4432"},
        {"title": "Fermentation Secrets", "author": "Dr. Gutman", "price": 55.50, "nutri_code": "NC-1029"},
        {"title": "Raw Vitality", "author": "Marcus Thorne", "price": 32.00, "nutri_code": "NC-8876"}
    ]

    # 生成一个伪造的 hex dump 文件，混杂在一些垃圾数据中
    hex_dump_path = os.path.join(base_path, "sector_0xFB2.bin")
    with open(hex_dump_path, "wb") as f:
        f.write(os.urandom(1024)) # 随机头部
        for book in books:
            book_str = f"BOOK_START|{book['title']}|{book['author']}|{book['price']}|{book['nutri_code']}|BOOK_END\n"
            f.write(book_str.encode('utf-8'))
        f.write(os.urandom(512)) # 随机尾部

    # 2. 生成一个误导性的/有线索的日志文件
    log_path = os.path.join(base_path, "cleanup_error.log")
    log_content = """
    [INFO] Starting disk optimization...
    [WARN] Unexpected file format in /db/inventory.db. Skipping backup.
    [ERROR] CRITICAL: Sector 0xFB2 contains unindexed stream data.
    [INFO] Moving raw sector data to /assets/data_219/recovery_vault/sector_0xFB2.bin for manual review.
    [INFO] Deleted /db/inventory.db. 
    [SUCCESS] 420MB freed. Environment sustained.
    """
    with open(log_path, "w") as f:
        f.write(log_content)

    # 3. 创建一个破碎的系统配置文件，确认折扣逻辑
    config_path = os.path.join(base_path, "store_policy.cfg")
    with open(config_path, "w") as f:
        f.write("DISCOUNT_TYPE: STUDENT\n")
        f.write("DISCOUNT_VALUE: 0.15\n")
        f.write("TARGET_COLLECTION: Rare Organic Living & Vegan Smoothies\n")

if __name__ == "__main__":
    setup_environment()
