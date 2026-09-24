import os
import argparse
import json
import random

def build_turn_1():
    # 创建目录结构
    os.makedirs("submissions", exist_ok=True)
    os.makedirs("guidelines", exist_ok=True)
    
    # 策展初始规则文件 (存在矛盾和模糊性)
    curation_brief = {
        "theme": "Urban Echoes",
        "budget_limit": 50000,
        "constraints": [
            "No more than 3 digital pieces",
            "At least 2 pieces from local Florida artists",
            "Must include at least one sculpture but shipping for heavy items must not exceed 10% of total budget"
        ],
        "artist_blacklist": ["Marcus Vane"], # 以前合作过有纠纷的
        "preferred_mediums": ["Oil", "Digital", "Mixed Media", "Sculpture"]
    }
    with open("guidelines/curation_brief.json", "w") as f:
        json.dump(curation_brief, f, indent=4)

    # 生成 10 个候选方案，故意制造临界值
    proposals = [
        {"id": "A01", "artist": "Elena Rossi", "location": "Miami, FL", "medium": "Oil", "price": 12000, "weight_kg": 5, "shipping_cost": 200},
        {"id": "A02", "artist": "Marcus Vane", "location": "New York, NY", "medium": "Digital", "price": 8000, "weight_kg": 0, "shipping_cost": 0}, # 黑名单陷阱
        {"id": "A03", "artist": "Sarah Jenkins", "location": "Orlando, FL", "medium": "Sculpture", "price": 15000, "weight_kg": 250, "shipping_cost": 4800}, # 运费超支陷阱 (4800 > 10% of total or per item? 设定为total的10%)
        {"id": "A04", "artist": "Xavier Chen", "location": "Seattle, WA", "medium": "Digital", "price": 5000, "weight_kg": 0, "shipping_cost": 0},
        {"id": "A05", "artist": "Lila Thorne", "location": "Tampa, FL", "medium": "Mixed Media", "price": 9500, "weight_kg": 15, "shipping_cost": 400},
        {"id": "A06", "artist": "Kobe Bryant (Art Studio)", "location": "Los Angeles, CA", "medium": "Digital", "price": 7000, "weight_kg": 0, "shipping_cost": 0},
        {"id": "A07", "artist": "Maria Garcia", "location": "Miami, FL", "medium": "Sculpture", "price": 11000, "weight_kg": 80, "shipping_cost": 800}, # 另一个雕塑，符合运费
        {"id": "A08", "artist": "Aiden Smith", "location": "Austin, TX", "medium": "Oil", "price": 6000, "weight_kg": 8, "shipping_cost": 300},
        {"id": "A09", "artist": "Jordan Lee", "location": "Jacksonville, FL", "medium": "Digital", "price": 5500, "weight_kg": 0, "shipping_cost": 0},
        {"id": "A10", "artist": "Sam Rivers", "location": "Chicago, IL", "medium": "Oil", "price": 13000, "weight_kg": 10, "shipping_cost": 500}
    ]
    
    for p in proposals:
        with open(f"submissions/proposal_{p['id']}.json", "w") as f:
            json.dump(p, f, indent=4)

def build_turn_2():
    # 增加新的冲突：版权纠纷文件
    os.makedirs("legal_notices", exist_ok=True)
    legal_issue = {
        "alert": "Copyright Infringement",
        "detail": "Artist Maria Garcia's sculpture 'Fluidity' (A07) is currently under legal dispute for conceptual plagiarism.",
        "action_required": "Immediate suspension of A07 from all curation lists."
    }
    with open("legal_notices/dispute_A07.json", "w") as f:
        json.dump(legal_issue, f, indent=4)
    
    # 增加一名新艺术家的紧急投稿，作为 A07 的替代，但其预算非常接近临界点
    emergency_proposal = {
        "id": "B01", 
        "artist": "Zoe West", 
        "location": "Tallahassee, FL", 
        "medium": "Sculpture", 
        "price": 14500, 
        "weight_kg": 100, 
        "shipping_cost": 1200
    }
    with open("submissions/proposal_B01.json", "w") as f:
        json.dump(emergency_proposal, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
