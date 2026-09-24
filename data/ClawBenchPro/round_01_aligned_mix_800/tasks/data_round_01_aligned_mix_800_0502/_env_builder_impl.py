import os
import csv
import json
import random

def build_env():
    # 🚨 执行此脚本时，当前工作目录 (cwd) 已经被设定为了 `assets/data_round_01_aligned_mix_800_0502/`。
    root_dir = "legacy_storage_v4"
    accounting_dir = "accounting"
    os.makedirs(root_dir, exist_ok=True)
    os.makedirs(accounting_dir, exist_ok=True)

    minerals = ["Copper", "Zinc", "Nickel", "Aluminum"]
    # 核心价格表（隐藏在某个日志文件中）
    market_prices = {
        "Copper": 9.2,
        "Zinc": 2.8,
        "Nickel": 17.5,
        "Aluminum": 2.4
    }

    # 1. 散布价格锚点 (隐藏在几百个无用日志中的一个)
    for i in range(50):
        log_name = f"sys_log_{i:03d}.txt"
        with open(os.path.join(root_dir, log_name), "w") as f:
            if i == 27: # 选一个固定的日志写入价格
                f.write("SYSTEM_INIT_SUCCESS\n")
                f.write(f"[MARKET_SNAPSHOT] {json.dumps(market_prices)}\n")
                f.write("BUFFER_CLEARED\n")
            else:
                f.write(f"NOISE_DATA_{random.getrandbits(32)}\n")

    # 2. 生成极其碎片化的数据 (CSV, JSON, TXT 混合)
    batch_counter = 1000
    
    # 制造重复数据与噪音
    all_batches = []
    for _ in range(300):
        m = random.choice(minerals)
        bid = f"B{batch_counter}"
        weight = random.uniform(100, 5000)
        purity = random.uniform(70, 98)
        unit = random.choice(["kg", "g", ""])
        if unit == "g": weight = weight * 1000
        
        all_batches.append({"id": bid, "m": m, "w": weight, "p": purity, "u": unit})
        batch_counter += 1

    # 将这些数据打碎存放在不同深度的子目录
    sub_dirs = ["shards_alpha", "shards_beta", "temp_archives/old_system"]
    for sd in sub_dirs:
        os.makedirs(os.path.join(root_dir, sd), exist_ok=True)

    # 分发数据
    for idx, batch in enumerate(all_batches):
        target_dir = os.path.join(root_dir, random.choice(sub_dirs))
        file_ext = random.choice(["csv", "json", "log"])
        
        # 故意制造一些 deprecated 诱饵文件
        if idx % 10 == 0:
            bad_file = os.path.join(target_dir, f"backup_v0_deprecated_{idx}.csv")
            with open(bad_file, "w") as f: f.write("TRASH_DATA,0,0,0")

        file_path = os.path.join(target_dir, f"data_chunk_{idx}.{file_ext}")
        
        if file_ext == "csv":
            with open(file_path, "w") as f:
                f.write("batch_id,mineral,weight,purity\n")
                f.write(f"{batch['id']},{batch['m']},{batch['w']}{batch['u']},{batch['p']}%\n")
        elif file_ext == "json":
            with open(file_path, "w") as f:
                json.dump({"meta": {"id": batch['id']}, "spec": {"type": batch['m'], "mass": f"{batch['w']}{batch['u']}", "purity_level": batch['p']}}, f)
        else:
            with open(file_path, "w") as f:
                f.write(f"REF: {batch['id']} | TYPE: {batch['m']} | QTY: {batch['w']}{batch['u']} | QUAL: {batch['p']}\n")

    # 3. 故意制造少量重复批次 (用于测试去重逻辑)
    with open(os.path.join(root_dir, "reconcile_final.log"), "w") as f:
        # 重复 B1000 的数据，但纯度不同，应以 ID 去重（或提示逻辑处理）
        f.write("REF: B1000 | TYPE: Copper | QTY: 1200kg | QUAL: 88.5\n")

if __name__ == "__main__":
    build_env()
