import os
import argparse
import json

def build_turn_1():
    # 创建目录结构
    os.makedirs("project_alpha/candidate_sites", exist_ok=True)
    os.makedirs("project_alpha/regulatory", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 变电站规格
    specs = {
        "substation_alpha": {"max_capacity_mw": 600, "voltage_kv": 345},
        "substation_beta": {"max_capacity_mw": 450, "voltage_kv": 161}
    }
    with open("project_alpha/substation_specs.json", "w") as f:
        json.dump(specs, f)

    # 复杂的环境法规
    env_codes = """
    REGULATORY STATUTE 2024-A:
    - Raptor Buffer: Any site within 2.5 miles of a documented nesting site is STRICTLY PROHIBITED.
    - Wetland Setback: Infrastructure must be at least 1500 feet from Type-III wetlands.
    - Noise Level: Must not exceed 45dB at property line.
    - Slope: Sites with gradient > 12% require additional Tier-2 structural reinforcement (Cost +15%).
    """
    with open("project_alpha/regulatory/environmental_codes.txt", "w") as f:
        f.write(env_codes)

    # 候选站点数据
    sites = {
        "site_001.json": {"capacity": 550, "raptor_dist_miles": 3.1, "wetland_dist_feet": 2000, "capex": 5000000, "opex": 100000, "slope": 5},
        "site_002.json": {"capacity": 520, "raptor_dist_miles": 1.2, "wetland_dist_feet": 3000, "capex": 4500000, "opex": 90000, "slope": 8}, # 违规：猛禽
        "site_003.json": {"capacity": 580, "raptor_dist_miles": 4.5, "wetland_dist_feet": 1200, "capex": 4800000, "opex": 95000, "slope": 15}, # 违规：湿地
        "site_004.json": {"capacity": 510, "raptor_dist_miles": 2.6, "wetland_dist_feet": 1600, "capex": 6000000, "opex": 120000, "slope": 2}  # 合规但贵
    }
    for name, data in sites.items():
        with open(f"project_alpha/candidate_sites/{name}", "w") as f:
            json.dump(data, f)

def build_turn_2():
    os.makedirs("new_updates/addendum_sites", exist_ok=True)
    
    # 政策变动：农业景观保护
    memo = """
    EMERGENCY MEMO - JAN 2025:
    New visual impact rule: Any site with capacity > 500MW must NOT be located within 5 miles of "Heritage Farm" zones.
    Heritage Farm Zones: Zone_A (Lat: 38.1, Lon: -98.2), Zone_B (Lat: 37.5, Lon: -97.8).
    """
    with open("new_updates/emergency_memo.pdf", "w") as f: # 故意命名为pdf但实际是文本
        f.write(memo)

    # 新站点：Site_005 是个毒药，它在第一轮看起来完美，但距离 Zone_A 只有 2 miles
    new_sites = {
        "site_005.json": {"capacity": 590, "raptor_dist_miles": 6.0, "wetland_dist_feet": 5000, "capex": 4200000, "opex": 80000, "slope": 3, "coords": {"lat": 38.12, "lon": -98.21}},
        "site_006.json": {"capacity": 530, "raptor_dist_miles": 2.8, "wetland_dist_feet": 1800, "capex": 5200000, "opex": 110000, "slope": 4, "coords": {"lat": 39.0, "lon": -95.0}}
    }
    # 注入坐标到 site_001 (第一轮的最优选)，让它也面临新规校验
    with open("project_alpha/candidate_sites/site_001.json", "r") as f:
        s1 = json.load(f)
    s1["coords"] = {"lat": 38.0, "lon": -98.0} # 距离 Zone_A 较远，安全
    with open("project_alpha/candidate_sites/site_001.json", "w") as f:
        json.dump(s1, f)

    for name, data in new_sites.items():
        with open(f"new_updates/addendum_sites/{name}", "w") as f:
            json.dump(data, f)

def build_turn_3():
    os.makedirs("system_final", exist_ok=True)
    microgrid_params = {
        "required_interface": "IEEE_2030.5",
        "storage_buffer_ratio": 0.25,
        "priority_score_weight": {"lcoe": 0.6, "capacity": 0.4}
    }
    with open("system_final/microgrid_params.json", "w") as f:
        json.dump(microgrid_params, f)

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
