import os
import base64

def build_env():
    # 注意：不再建立明文的 supplier_invoices 目录，强制要求 Agent 使用 API 查询工具
    
    # 建立夜班收货记录目录
    os.makedirs("shift_logs", exist_ok=True)
    
    # 真实情况 (与原逻辑一致保证计算结果不变):
    # Organic Avocados: 收了 8 个 (少了 2 个) -> 2 * 2.50 = 5.00
    # Artisan Sourdough: 收了 5 个 (正常)
    # Manchego Cheese (lbs): 收了 20 个 (正常)
    # Truffle Oil: 收了 10 个 (少了 2 个) -> 2 * 25.00 = 50.00
    # Heirloom Tomatoes: 收了 55 个 (多了 5 个，User只关心少了的被坑的钱，多的不用算)
    # Saffron (oz): 收了 0 个 (少了 1 个) -> 1 * 80.00 = 80.00
    # 丢失总金额 = 5.00 + 50.00 + 80.00 = 135.00
    
    raw_csv_content = """Item Scanned,Qty
  organic Avocados,8
artisan sourdough ,5
 Manchego Cheese (LBS),20
truffle oil,10
Heirloom Tomatoes  ,55
"""
    
    # 将原始脏数据 CSV 进行 Base64 编码，模拟专有格式，迫使 Agent 必须调用解码 Skill
    encoded_content = base64.b64encode(raw_csv_content.encode("utf-8"))
    
    with open("shift_logs/receiving_night_shift.bin", "wb") as f:
        f.write(encoded_content)

if __name__ == "__main__":
    build_env()
