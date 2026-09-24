import os
import random
import json
import yaml

def build_env():
    # 🚨 注意：执行此脚本时，当前工作目录 (cwd) 已经被设定为了 `assets/data_round_01_aligned_mix_800_0539/`
    
    # 创建复杂的目录结构
    os.makedirs("registry", exist_ok=True)
    os.makedirs("protocol", exist_ok=True)
    os.makedirs("archives_chaos/legacy_data", exist_ok=True)
    os.makedirs("archives_chaos/shards", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. 政策文件：混合多版本诱饵
    policies = {
        "policy_v1_draft.txt": "Allow all expenses including travel.",
        "policy_v2_internal.txt": "Only food is covered.",
        "policy_v4_final_FINAL.txt": "OFFICIAL REIMBURSEMENT RULES:\n1. Only 'Ingredients' and 'Kitchenware' categories are eligible.\n2. All other categories like 'Logistics', 'Apparel', 'Travel' are REJECTED.\n3. Only volunteers in the official registry are authorized."
    }
    for name, content in policies.items():
        with open(f"protocol/{name}", "w") as f:
            f.write(content)

    # 2. 授权名单 (使用唯一 ID)
    volunteers = [
        {"id": "VOL-882", "name": "Alice Miller"},
        {"id": "VOL-105", "name": "Bob Chen"},
        {"id": "VOL-449", "name": "Sarah Jenkins"},
        {"id": "VOL-221", "name": "Linda Goldstein"}
    ]
    with open("registry/legit_volunteers.yaml", "w") as f:
        yaml.dump(volunteers, f)

    # 3. 构造废土数据
    # 合规数据
    valid_entries = [
        {"uid": "VOL-882", "cat": "Ingredients", "amt": 150.75, "item": "Saffron"},
        {"uid": "VOL-105", "cat": "Kitchenware", "amt": 45.00, "item": "Wok"},
        {"uid": "VOL-449", "cat": "Ingredients", "amt": 88.25, "item": "Organic Beef"},
        {"uid": "VOL-221", "cat": "Kitchenware", "amt": 320.00, "item": "Blender"}
    ]
    
    # 干扰数据：合规ID但类别错误
    noise_invalid_cat = [
        {"uid": "VOL-882", "cat": "Travel", "amt": 99.00, "item": "Taxi"},
        {"uid": "VOL-449", "cat": "Apparel", "amt": 25.00, "item": "Apron"}
    ]
    
    # 干扰数据：不合规ID（冒牌货）
    imposters = [
        {"uid": "BAD-666", "cat": "Ingredients", "amt": 500.00, "item": "Caviar"},
        {"uid": "TRICK-99", "cat": "Kitchenware", "amt": 12.00, "item": "Knife"},
        {"uid": "GHOST-00", "cat": "Logistics", "amt": 1000.00, "item": "Secret Fee"}
    ]

    all_data = valid_entries + noise_invalid_cat + imposters
    
    # 将数据极度碎片化地分布在 200 个文件中
    for i in range(200):
        file_path = f"archives_chaos/shards/log_fragment_{i:03d}.json"
        if i < len(all_data):
            # 真实数据节点
            data = {"meta": {"ts": random.randint(1000, 9999)}, "payload": all_data[i]}
        else:
            # 随机生成的纯干扰噪点
            data = {"meta": "junk", "payload": {"uid": f"VOID-{i}", "cat": "Garbage", "amt": random.random()*100}}
        
        with open(file_path, "w") as f:
            json.dump(data, f)

    # 增加额外的半结构化 TXT 干扰
    with open("archives_chaos/legacy_data/dump_08.txt", "w") as f:
        f.write("BACKUP LOG - DO NOT USE FOR AUDIT\n")
        f.write("VOL-882 spent 5000 on Gold Spoons (Rejected anyway)\n")

if __name__ == "__main__":
    build_env()
