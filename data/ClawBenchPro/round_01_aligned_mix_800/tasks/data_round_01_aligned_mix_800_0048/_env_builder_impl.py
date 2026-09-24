import os
import argparse
import json
import csv

def build_turn_1():
    # 路径已在 assets/data_round_01_aligned_mix_800_0048/turn_1
    os.makedirs("proposals", exist_ok=True)
    os.makedirs("deliveries", exist_ok=True)
    
    # 供应商 A: 性能好，评分高，刚好在预算边缘
    with open("proposals/vendor_A_nexus.txt", "w") as f:
        f.write("Product: Nexus Tab 10\nSoftware Compatibility: 9.2\nUnit Price: 650\nMaintenance Fee: 50\nChips: Silicon-X1")
    
    # 供应商 B: 便宜，但软件兼容性不行
    with open("proposals/vendor_B_cheap.txt", "w") as f:
        f.write("Product: BudgetPad\nSoftware Compatibility: 7.5\nUnit Price: 400\nMaintenance Fee: 20\nChips: LowPower-Z")
        
    # 供应商 C: 完美方案，但实际上超支一点点 (如果算上维护费)
    # 计算：(680+30) * 120 = 85200 (超过 85000 预算)
    with open("proposals/vendor_C_edu.txt", "w") as f:
        f.write("Product: EduMax\nSoftware Compatibility: 8.8\nUnit Price: 680\nMaintenance Fee: 30\nChips: SecureCore-V2")

    # 供应商 D: 唯一真正的正确选项 (Turn 1)
    # 计算：(600+100) * 120 = 84000 (符合预算 85000)
    with open("proposals/vendor_D_alpha.txt", "w") as f:
        f.write("Product: AlphaStudy\nSoftware Compatibility: 8.6\nUnit Price: 600\nMaintenance Fee: 100\nChips: Legacy-M1")

def build_turn_2():
    # 模拟 Turn 2 的增量环境
    os.makedirs("compliance_updates", exist_ok=True)
    # 注入安全名单，故意把 Turn 1 表现最好的 Vendor D 排除（因为它用的是 Legacy 芯片）
    # 此时 Agent 必须重新寻找合规方案。
    # 观察：Vendor A 也不合规。只有 Vendor C 虽然原本超支，但如果现在有折扣或者... 哦不，此时必须引导 Agent 发现 Vendor E。
    security_data = {
        "approved_chipsets": ["Silicon-X1", "SecureCore-V2", "FutureChip-Alpha"],
        "policy_date": "2023-10-27",
        "audit_level": "Strict"
    }
    with open("compliance_updates/security_whitelist.json", "w") as f:
        json.dump(security_data, f)
    
    # 在 proposals 增加一个姗姗来迟的合规供应商 E
    with open("proposals/vendor_E_new.txt", "w") as f:
        # (620+80) * 120 = 84000. 符合 Turn 1 预算，且合规。
        f.write("Product: SafetyPad\nSoftware Compatibility: 8.7\nUnit Price: 620\nMaintenance Fee: 80\nChips: FutureChip-Alpha")

def build_turn_3():
    # 模拟 Turn 3 的增量环境
    os.makedirs("market_fluctuations", exist_ok=True)
    # 供应商 C 降价了！
    # 原价 680+30=710。现降价至 650+30=680。
    # 预算增加了 5000 -> 总 90000。
    # 120台 * 680 = 81600。
    # 这样就可以剩余 8400 美元来升级 8 年级的设备（30台）。
    with open("market_fluctuations/price_drops.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Vendor", "Product", "New_Unit_Price", "Note"])
        writer.writerow(["Vendor C", "EduMax", "650", "Seasonal Discount"])
        writer.writerow(["Vendor E", "SafetyPad", "610", "Bulk Discount"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
    elif args.turn == 3:
        build_turn_3()
