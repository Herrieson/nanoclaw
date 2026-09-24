import os
import argparse
import csv
import json

def build_turn_1():
    # 创建目录
    os.makedirs("archive", exist_ok=True)
    os.makedirs("blueprints", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 供应商报价 - 故意制造数据脏乱和逻辑陷阱
    vendors = [
        ["ID", "Name", "Category", "Price", "Tags", "Notes"],
        ["V01", "GreenEarth Co.", "Soil", "1200", "Certified Organic, Low Carbon", "Highly recommended"],
        ["V02", "QuickGrow Corp", "Soil", "800", "Chemical, High Yield", "Avoid for eco-projects"],
        ["V03", "BioLife Solutions", "Soil", "1500", "Certified Organic", "Slightly expensive but premium"],
        ["V04", "EcoDrop Systems", "Irrigation", "2200", "Low Carbon, Recycled Plastic", "Standard system"],
        ["V05", "WaterMaster", "Irrigation", "1800", "High Efficiency", "Unknown carbon footprint"],
        ["V06", "Gaia Seeds", "Seeds", "600", "Heirloom, Organic", "Complete set"],
        ["V07", "PurePlant", "Seeds", "400", "Certified Organic", "Basic set"],
        ["V08", "Titan Garden", "Irrigation", "2500", "Solar Powered, Low Carbon", "Top tier eco-friendly"]
    ]
    with open("archive/vendor_quotes.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(vendors)

    # 场地勘测 - 包含非结构化描述
    survey = """
    SITE SURVEY - SECTION 42-B
    Total Area: 5000 sq ft.
    Soil Quality: Moderate.
    CRITICAL WARNINGS:
    - Point (23, 45): Lead Contamination Risk detected. Do not plant edibles here.
    - Point (10, 12): High salinity area.
    - Northern Perimeter: High shade, suitable for teaching area later.
    Legacy Infrastructure: Old pipes at (15, 15) must be bypassed.
    """
    with open("blueprints/site_survey.txt", "w") as f:
        f.write(survey)

def build_turn_2():
    os.makedirs("council_updates", exist_ok=True)
    # 政策文件 - 引入新规则
    new_regs = """
    CITY COUNCIL REGULATION #2024-09
    All new community garden irrigation systems MUST include a 'Rainwater Capture Feedback Loop'.
    Systems without this feature will NOT be permitted after next month.
    Current approved systems on market: Titan Garden (Model S), AquaSave Pro.
    Note: EcoDrop Systems (V04) has recently filed for bankruptcy and is no longer fulfilling orders.
    """
    with open("council_updates/new_regs.pdf.txt", "w") as f:
        f.write(new_regs)

def build_turn_3():
    # 种子目录 - 复杂计算
    seeds = [
        {"name": "Heritage Tomato", "type": "Vegetable", "price": 50, "diversity_score": 0.15},
        {"name": "Wild Lavender", "type": "Flower", "price": 30, "diversity_score": 0.25},
        {"name": "Native Grass Mix", "type": "Grass", "price": 80, "diversity_score": 0.45},
        {"name": "Rare Orchid", "type": "Flower", "price": 200, "diversity_score": 0.60},
        {"name": "Standard Carrot", "type": "Vegetable", "price": 20, "diversity_score": 0.05}
    ]
    with open("archive/seed_catalog.json", "w") as f:
        json.dump(seeds, f)

    # 泄露报告 - 信用危机
    leaks = """
    INTERNAL LOG - CONFIDENTIAL
    INVESTIGATION ON GREENEARTH CO. (V01):
    Recent audit shows V01 sourced 40% of their 'Organic' soil from non-certified industrial sites.
    Status: Fraudulent Green Claims.
    Action: Revoke Eco-Certification immediately.
    """
    with open("archive/leaked_reports.log", "w") as f:
        f.write(leaks)

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
