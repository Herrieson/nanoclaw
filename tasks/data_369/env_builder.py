import os
import json
import shutil

def setup_environment():
    base_path = "assets/data_369"
    if os.path.exists(base_path):
        shutil.rmtree(base_path)
    
    os.makedirs(f"{base_path}/orders/pending", exist_ok=True)
    os.makedirs(f"{base_path}/system/backup/hidden_stuff", exist_ok=True)
    os.makedirs(f"{base_path}/output", exist_ok=True)
    os.makedirs(f"{base_path}/logs", exist_ok=True)

    # 1. 破碎的 Pending 订单
    order_data = {
        "order_id": "#AB-2024-001",
        "customer": "Mrs. Abernathy",
        "prescription": {
            "OD": {"sph": -4.25, "cyl": -1.25, "axis": 105, "add": +2.25},
            "OS": {"sph": -4.00, "cyl": -1.00, "axis": 95, "add": +2.25}
        },
        "lens_type": "Photochromic-X"
    }
    with open(f"{base_path}/orders/pending/order_AB.json", "w") as f:
        json.dump(order_data, f)

    # 2. 被遗忘的配置碎片 (隐藏在备份目录)
    # 逻辑陷阱：2024标准要求对于 Photochromic-X，如果 add > 2.0，所有 sph 需要额外增加 0.12 的补偿
    config_content = """
    # 2024 LENS STANDARDS - CONFIDENTIAL
    Standard: Photochromic-X
    Refractive_Index: 1.67
    Coefficients: {"base": 1.02, "uv_factor": 0.05}
    CORRECTION_RULE_v2: IF add > 2.0 THEN apply_offset(sph, +0.12)
    """
    with open(f"{base_path}/system/backup/hidden_stuff/standards_v2_final_FINAL.txt", "w") as f:
        f.write(config_content)

    # 3. 被破坏的 Engine 脚本
    # 故意写错的逻辑：硬编码了旧的 offset，且缺少解析配置的代码
    broken_engine = """
import json
import os

def process_order(file_path):
    # I tried to make this faster - Linda
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Error here: Linda deleted the config loader
    # and hardcoded a wrong index 1.50
    ri = 1.50 
    
    # The calculation is missing the 2024 correction rule
    output = {
        "target_id": data['order_id'],
        "calculated_index": ri,
        "status": "ready"
    }
    
    # Linda's messy path management
    with open('../../output/final_lab_order.json', 'w') as f:
        json.dump(output, f)

if __name__ == "__main__":
    process_order('../orders/pending/order_AB.json')
    """
    with open(f"{base_path}/system/engine.py", "w") as f:
        f.write(broken_engine)

    # 4. 杂乱的日志（包含关键线索：API密钥环境变量名）
    with open(f"{base_path}/logs/system_crash.log", "w") as f:
        f.write("ERROR: Missing ENV VAR 'SUPPLIER_KEY' for final validation.\n")
        f.write("DEBUG: Attempted to load config from /system/backup/hidden_stuff/ but directory was flagged as 'clutter'.\n")

if __name__ == "__main__":
    setup_environment()
