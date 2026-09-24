import os
import json
import random
import string

def build_env():
    # 设定随机种子以保证环境生成的确定性和可解性
    random.seed(42)

    os.makedirs("data_lake/invoices", exist_ok=True)
    os.makedirs("procurement_policies", exist_ok=True)
    os.makedirs("syslogs", exist_ok=True)
    os.makedirs("final_audit", exist_ok=True)

    # ==========================
    # 1. 制造白名单与噪音政策文件
    # ==========================
    legit_suppliers = ["NeonWoods Corp", "Titanium Timber", "CyberOak Ltd", "SynthPine Systems"]
    fake_suppliers_1 = ["Shadow Lumber", "Scrap King", "Corpo Wood"]
    fake_suppliers_2 = ["Null Materials", "Rust Belt Wood", "Glitch Timber"]

    policies = [
        ("v1.0_draft.json", {"status": "draft", "suppliers": fake_suppliers_1}, False),
        ("v1.5_revised.txt", f"Suppliers considered: {', '.join(fake_suppliers_2)}\nStatus: Pending", False),
        ("v2.0_final_v2_real.json", {"active_suppliers": legit_suppliers, "metadata": {"seal": "[APPROVED_BY_DIRECTOR]"}}, True),
        ("v2.1_proposal.md", "# Proposed Suppliers\n- Shadow Lumber\n- Neo Wood\n\n[REJECTED_BY_DIRECTOR]", False),
    ]

    for i in range(20):
        # 增加纯噪音文件
        policies.append((f"trash_policy_{i}.log", f"Some random policy data {random.randint(1000, 9999)}", False))

    for filename, content, is_valid in policies:
        with open(os.path.join("procurement_policies", filename), "w") as f:
            if isinstance(content, dict) or isinstance(content, list):
                json.dump(content, f)
            else:
                f.write(content)

    # ==========================
    # 2. 制造海量发票迷宫
    # ==========================
    illegal_in_use = ["Scrap King", "Rust Belt Wood", "Underground Timber"]
    all_categories = ["Lumber", "Timber", "Food", "Oil", "Droid Parts", "Concrete"]
    
    invoices_data = []
    
    # 生成 1000 个发票
    for i in range(1000):
        inv_id = f"INV-2077-{str(i).zfill(4)}"
        
        # 决定发票类型
        is_target_material = random.random() < 0.4
        category = random.choice(["Lumber", "Timber"]) if is_target_material else random.choice(["Food", "Oil", "Droid Parts", "Concrete"])
        
        # 决定供应商
        if is_target_material:
            is_legal = random.random() < 0.6
            supplier = random.choice(legit_suppliers) if is_legal else random.choice(illegal_in_use)
        else:
            supplier = random.choice(["BurgerTech", "SludgeOil Corp", "Fix-It Drones", "MegaBlock"])
            
        amount = random.randint(100, 10000)
        
        inv = {
            "invoice_id": inv_id,
            "category": category,
            "supplier": supplier,
            "amount": amount,
            "notes": "".join(random.choices(string.ascii_letters, k=20))
        }
        invoices_data.append(inv)
        
        # 存入深度嵌套目录结构
        year = random.choice(["2076", "2077"])
        month = str(random.randint(1, 12)).zfill(2)
        zone = random.choice(["zone_alpha", "zone_beta", "zone_gamma", "zone_delta", "zone_omega"])
        dir_path = os.path.join("data_lake/invoices", year, month, zone)
        os.makedirs(dir_path, exist_ok=True)
        
        # 混杂不同的文件扩展名
        ext = random.choice([".json", ".inv", ".dat"])
        with open(os.path.join(dir_path, f"{inv_id}{ext}"), "w") as f:
            json.dump(inv, f)

    # ==========================
    # 3. 制造地狱级系统日志与签收记录
    # ==========================
    # 收集需要被标记为“已签收”的合法及非法材料发票ID（制造干扰，外卖也可能被签收）
    received_ids = []
    for inv in invoices_data:
        # 无论是不是木材，都有50%概率被入库
        if random.random() < 0.5:
            received_ids.append(inv["invoice_id"])

    # 生成 5 个庞大的日志文件
    for log_idx in range(5):
        log_lines = []
        for _ in range(10000):
            # 制造极多噪音
            msg_type = random.choice(["ERROR", "WARNING", "INFO", "DEBUG"])
            module = random.choice(["[SYS_KERN]", "[NET_AUTH]", "[DRIVE_MEM]", "[SCANNER_V3]", "[SCANNER_V2]"])
            junk = "".join(random.choices(string.ascii_letters + string.digits, k=15))
            
            if module == "[SCANNER_V3]" and random.random() < 0.05 and received_ids:
                # 注入真实的签收记录
                popped_id = received_ids.pop(random.randint(0, len(received_ids)-1))
                log_lines.append(f"2077-11-{random.randint(10,30)}T12:00:00 {msg_type} {module} RECV_OK: {popped_id} - STATUS: LOGGED")
            elif module == "[SCANNER_V3]" and random.random() < 0.1:
                # 注入失败的扫描或别的状态
                fake_id = f"INV-2077-{random.randint(9000, 9999)}"
                log_lines.append(f"2077-11-{random.randint(10,30)}T12:00:00 ERROR {module} RECV_FAIL: {fake_id} - CHECKSUM_ERR")
            else:
                # 纯粹的废话日志
                log_lines.append(f"2077-11-{random.randint(10,30)}T12:00:00 {msg_type} {module} Memory dump: {junk} operation timeout.")
                
        with open(os.path.join("syslogs", f"system_run_{log_idx}.log"), "w") as f:
            f.write("\n".join(log_lines))

if __name__ == "__main__":
    build_env()
