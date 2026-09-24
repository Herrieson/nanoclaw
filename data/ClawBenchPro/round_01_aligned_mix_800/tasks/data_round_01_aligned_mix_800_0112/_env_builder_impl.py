import os
import argparse
import pandas as pd
import json
import random

def build_turn_1():
    # 创建目录结构
    os.makedirs("proposals", exist_ok=True)
    os.makedirs("logistics", exist_ok=True)
    os.makedirs("analysis_report", exist_ok=True)

    # 1. 供应商报价单 (包含碳评分和价格)
    # 故意设计：有些价格极低但碳排不合格 (ID: V001)
    # 有些碳排合格但价格极高 (ID: V005)
    # 有些风险指数刚好在边缘 (ID: V003)
    vendor_data = {
        "vendor_id": ["V001", "V002", "V003", "V004", "V005", "V006", "V007", "V008"],
        "price_per_unit": [45.0, 52.0, 50.0, 58.0, 95.0, 54.0, 61.0, 48.0],
        "carbon_score": [40, 72, 68, 85, 90, 66, 78, 55], # 阈值 65
        "region": ["Asia", "Europe", "North America", "Asia", "Europe", "Asia", "Europe", "South America"]
    }
    pd.DataFrame(vendor_data).to_csv("proposals/vendor_quotes.csv", index=False)

    # 2. 物流数据 (xlsx 增加解析难度)
    # 风险计算: (base * 0.7) + (std * 0.3) <= 5.5
    # V002: (6 * 0.7) + (2 * 0.3) = 4.2 + 0.6 = 4.8 (OK)
    # V003: (7 * 0.7) + (1.5 * 0.3) = 4.9 + 0.45 = 5.35 (OK)
    # V004: (5 * 0.7) + (3 * 0.3) = 3.5 + 0.9 = 4.4 (OK)
    # V006: (8 * 0.7) + (2 * 0.3) = 5.6 + 0.6 = 6.2 (FAIL)
    logistics_data = {
        "vendor_id": ["V001", "V002", "V003", "V004", "V005", "V006", "V007", "V008"],
        "base_transit_days": [10, 6, 7, 5, 4, 8, 3, 12],
        "delay_std_dev": [2.5, 2.0, 1.5, 3.0, 1.2, 2.0, 1.0, 4.0]
    }
    pd.DataFrame(logistics_data).to_csv("logistics/transit_data.xlsx", index=False)

def build_turn_2():
    os.makedirs("updates", exist_ok=True)
    # 模拟物料变更需求
    # 陷阱：原本在 Turn 1 表现优秀的 V004 突然表示无法满足含镍量要求
    # V002 要求涨价 10% (符合 < 15% 规则)
    # V003 完美符合
    material_specs = {
        "nickel_content_requirement": "2.0%",
        "vendor_responses": {
            "V002": {"can_comply": True, "price_increase": 0.10},
            "V003": {"can_comply": True, "price_increase": 0.05},
            "V004": {"can_comply": False, "reason": "Technical limitations"},
            "V007": {"can_comply": True, "price_increase": 0.08},
            "V001": {"can_comply": True, "price_increase": 0.0}
        }
    }
    with open("updates/material_specs.json", "w") as f:
        json.dump(material_specs, f, indent=4)

def build_turn_3():
    # 第三轮主要是规则冲突，不需要额外生成大量文件
    # 但我们可以添加一个干扰用的额外供应商补充列表
    with open("updates/global_trade_alert.txt", "w") as f:
        f.write("URGENT: New Geodiversity Policy enacted. No more than one vendor from the same continent allowed if total vendors >= 3.")

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
