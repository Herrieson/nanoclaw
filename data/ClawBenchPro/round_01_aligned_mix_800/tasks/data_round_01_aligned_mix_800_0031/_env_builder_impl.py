import os
import argparse
import csv
import json

def build_turn_1():
    # 创建内部规格目录
    os.makedirs("internal_specs", exist_ok=True)
    with open("internal_specs/recycling_standards.md", "w") as f:
        f.write("# 再生材料利用指南\n- 必须包含至少35%的再生塑料或20%的再生金属。\n- 优先考虑可二次切削的材料。")
    
    with open("internal_specs/safety_redline.json", "w", encoding="utf-8") as f:
        # 预埋红线：稳定性必须 > 0.85
        json.dump({"min_stability_index": 0.85, "max_lead_content": "50ppm"}, f)

    # 财务计算逻辑
    os.makedirs("finance_rules", exist_ok=True)
    with open("finance_rules/logic.txt", "w") as f:
        f.write("最终成本 = (基础单价 * (1 + 增值税率13%)) + (运输里程 * 费率0.55/km) + 处理附加费200")

    # 供应商原始数据
    os.makedirs("procurement_options", exist_ok=True)
    # 供应商A: 完美但稳定性刚过线
    # 供应商B: 便宜但再生比例低
    # 供应商C: 贵但各方面优秀
    # 供应商D: 稳定性不达标（陷阱）
    options = [
        ["vendor_id", "base_price", "distance_km", "recycle_content_pct"],
        ["V-001", "1200", "150", "40"], # A
        ["V-002", "950", "300", "15"],  # B (不合规-再生低)
        ["V-003", "1500", "50", "50"],  # C
        ["V-004", "1100", "200", "38"]  # D
    ]
    with open("procurement_options/quotes.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(options)

    # 稳定性指标 (独立文件，模拟多文件依赖)
    with open("chemical_stability_indices.csv", "w") as f:
        f.write("vendor_id,stability\nV-001,0.87\nV-002,0.92\nV-003,0.98\nV-004,0.72\n")

    # 详细规格书（包含后续轮次需要的艺术参数）
    os.makedirs("material_properties", exist_ok=True)
    properties = {
        "V-001": {"plasticity_index": 0.65, "tensile_strength": "400MPa"},
        "V-003": {"plasticity_index": 0.88, "tensile_strength": "450MPa"},
        "V-004": {"plasticity_index": 0.92, "tensile_strength": "380MPa"}
    }
    for vid, p in properties.items():
        with open(f"material_properties/{vid}_specs.json", "w") as f:
            json.dump(p, f)

def build_turn_2():
    # 注入增量更新
    os.makedirs("incoming_updates", exist_ok=True)
    # 费率上调，将影响成本排名
    with open("incoming_updates/logistics_v2.txt", "w") as f:
        f.write("自本月起，运输费率由0.55/km上调至1.25/km。")
    
    # 信誉风险：V-001 被爆再生比例虚假，实际只有 25% (低于第一轮 35% 的标准)
    with open("incoming_updates/audit_vulnerability.csv", "w") as f:
        f.write("target_vendor,finding,actual_recycle_pct\nV-001,Mismatched reporting,25\n")

def build_turn_3():
    # 这一轮主要靠 Prompt 驱动，不增加新物理文件，但现有文件中的 plasticity_index 成为关键
    pass

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
