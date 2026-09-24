import os
import argparse
import json

def build_turn_1():
    # 初始环境构建
    os.makedirs("incoming_requests/equipment", exist_ok=True)
    os.makedirs("incoming_requests/venues", exist_ok=True)
    os.makedirs("incoming_requests/volunteers", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 供应商数据：陷阱在于最便宜的没有降噪，最贵的超支
    vendors = [
        {"name": "SonicBlast Pro", "price": 4200, "features": ["Standard", "High Volume"], "desc": "Great for rock concerts."},
        {"name": "Inclusive Sound Systems", "price": 4800, "features": ["Noise-Reduction Optimized", "Braille Labels"], "desc": "Designed for special education environments."},
        {"name": "Budget Audio", "price": 3000, "features": ["Standard"], "desc": "Cheapest option on the market."},
        {"name": "Premium Harmonics", "price": 6500, "features": ["Noise-Reduction Optimized", "Wireless"], "desc": "Top-tier quality but expensive."}
    ]
    for i, v in enumerate(vendors):
        with open(f"incoming_requests/equipment/quote_{i}.json", "w") as f:
            json.dump(v, f)

    # 场地数据：只有一个完全符合要求
    venues = [
        {"name": "Main Gym", "accessible": True, "quiet_room": False, "capacity": 500},
        {"name": "Community Hall", "accessible": True, "quiet_room": True, "capacity": 200},
        {"name": "School Garden", "accessible": False, "quiet_room": False, "capacity": 300}
    ]
    with open("incoming_requests/venues/evaluation_reports.csv", "w") as f:
        f.write("name,accessible,quiet_room,capacity\n")
        for v in venues:
            f.write(f"{v['name']},{v['accessible']},{v['quiet_room']},{v['capacity']}\n")

    # 志愿者与学生：需要 1-on-1 逻辑匹配
    students = [
        {"name": "Leo", "needs": "Autism Support"},
        {"name": "Sam", "needs": "Visual Impairment"},
        {"name": "Maya", "needs": "Mobility Support"}
    ]
    volunteers = [
        {"name": "Alice", "exp": "Special Ed Certified"},
        {"name": "Bob", "exp": "Music Background"},
        {"name": "Charlie", "exp": "Braille Expert"},
        {"name": "Diana", "exp": "Physical Therapist Assistant"}
    ]
    with open("incoming_requests/volunteers/profiles.json", "w") as f:
        json.dump({"students": students, "volunteers": volunteers}, f)

def build_turn_2():
    # 增量与冲突
    os.makedirs("updates_turn2", exist_ok=True)
    
    # 预算变动通知
    with open("updates_turn2/budget_cut.txt", "w") as f:
        f.write("URGENT: Total budget reduced by 15% due to new international instrument segment.\n")
        f.write("New international segment equipment cost: $800 (Fixed).")

    # 场地故障
    with open("updates_turn2/venue_incident.txt", "w") as f:
        f.write("Maintenance Alert: Community Hall Quiet Room is flooded. Not available for the festival.\n")
        f.write("New venue option available: Arts Center, accessible: Yes, Quiet Room: Yes, cost: $500.")

def build_turn_3():
    # 最终细节补充
    os.makedirs("final_roster", exist_ok=True)
    os.makedirs("final_delivery", exist_ok=True)
    
    with open("final_roster/schedule_conflicts.json", "w") as f:
        json.dump({
            "delivery_time": "09:00 AM",
            "setup_duration": "3 hours",
            "volunteer_arrivals": [
                {"name": "Alice", "time": "09:30 AM"},
                {"name": "Charlie", "time": "10:00 AM"}
            ],
            "notes": "Small space in Arts Center; no more than 3 people during setup."
        }, f)

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
