import os
import argparse
import json
import csv

def build_turn_1():
    # 建立目录结构
    os.makedirs("applications", exist_ok=True)
    os.makedirs("standards", exist_ok=True)
    os.makedirs("current_inventory", exist_ok=True)

    # 1. 州标准文件
    with open("standards/eco_criteria.txt", "w") as f:
        f.write("State Regulation 2024-X:\n")
        f.write("Minimum Recycled Content: 35%\n")
        f.write("Maximum Carbon Footprint: 2.5kg CO2e/unit\n")

    # 2. 初始基准价格
    baseline = {
        "standard_widget": {"unit_price": 45.0, "current_supplier": "OldCorp"}
    }
    with open("current_inventory/baseline.json", "w") as f:
        json.dump(baseline, f)

    # 3. 供应商申请书 (埋点：EcoFlow 看起来最美，但碳足迹压线)
    apps = [
        {"name": "GreenLife_Inc", "recycled": "40%", "carbon": 2.1, "price": 52.0, "quality": 4.5},
        {"name": "EcoFlow_Systems", "recycled": "38%", "carbon": 2.49, "price": 48.0, "quality": 4.8}, # 踩线通过
        {"name": "BioGoods_Ltd", "recycled": "30%", "carbon": 1.8, "price": 55.0, "quality": 4.2},   # 比例不合规
        {"name": "PureSource", "recycled": "50%", "carbon": 3.0, "price": 42.0, "quality": 3.8}     # 碳足迹不合规
    ]
    for i, app in enumerate(apps):
        with open(f"applications/app_{i}.json", "w") as f:
            json.dump(app, f)

def build_turn_2():
    os.makedirs("updates", exist_ok=True)
    # 1. 新的禁用成分 (埋点：EcoFlow 使用了 PFAS，将被剔除)
    with open("standards/prohibited_v2.csv", "w") as f:
        f.write("chemical_id,restriction_level\n")
        f.write("PFAS,Banned\n")
        f.write("BPA,Limited\n")

    # 更新供应商细节：EcoFlow 的化学成分
    # 这是一个隐藏逻辑，需要 Agent 去之前的 application 或者是这一轮的补充说明中发现
    with open("updates/supplier_chemical_disclosure.json", "w") as f:
        json.dump({
            "EcoFlow_Systems": ["PFAS", "Silicon"],
            "GreenLife_Inc": ["Water", "Recycled_PET"],
            "BioGoods_Ltd": ["Cotton"],
            "PureSource": ["Steel"]
        }, f)

    # 2. 物流运费波动 (GreenLife 运费上涨最少)
    logistics = {
        "GreenLife_Inc": 2.0,
        "EcoFlow_Systems": 8.5,
        "BioGoods_Ltd": 5.0,
        "PureSource": 1.5
    }
    with open("updates/logistics_delta.json", "w") as f:
        json.dump(logistics, f)

def build_turn_3():
    # 1. 质量审计报告 (XML格式增加解析复杂度)
    xml_content = """<audit>
    <supplier name="GreenLife_Inc">
        <rating>4.6</rating>
        <last_inspection>2023-12-01</last_inspection>
    </supplier>
    <supplier name="BioGoods_Ltd">
        <rating>3.5</rating>
        <last_inspection>2023-11-15</last_inspection>
    </supplier>
</audit>"""
    with open("updates/quality_audit.xml", "w") as f:
        f.write(xml_content)
    
    os.makedirs("deliverables", exist_ok=True)

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
