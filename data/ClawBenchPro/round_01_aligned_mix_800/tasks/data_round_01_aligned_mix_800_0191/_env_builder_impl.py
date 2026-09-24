import os
import argparse
import json
import csv

def build_turn_1():
    # 供应商投标数据
    os.makedirs("vendor_proposals", exist_ok=True)
    
    vendors = [
        {"name": "OldMan_Seafood", "theme": "The Old Man and the Sea", "price": 17.5, "credit": 82, "veg_cal": 550, "carbon": 5.2}, # 价格合规，信用高，素食合规，但碳排高(T2陷阱)
        {"name": "Gatsby_Feast", "theme": "The Great Gatsby", "price": 22.0, "credit": 90, "veg_cal": 450, "carbon": 3.1}, # 价格超标 (T1淘汰)
        {"name": "Orwell_Kitchen", "theme": "1984", "price": 15.0, "credit": 78, "veg_cal": 700, "carbon": 2.5}, # 素食热量超标 (T1淘汰)
        {"name": "Dublin_Bites", "theme": "Ulysses", "price": 16.0, "credit": 85, "veg_cal": 480, "carbon": 3.8}, # 完美选手 (T1入围)
        {"name": "Kafka_Cafe", "theme": "The Metamorphosis", "price": 14.5, "credit": 60, "veg_cal": 400, "carbon": 1.2}, # 信用过低 (T1淘汰)
        {"name": "Austen_Tea", "theme": "Pride and Prejudice", "price": 18.0, "credit": 88, "veg_cal": 520, "carbon": 2.0}, # 完美选手 (T1入围)
        {"name": "Moby_Grill", "theme": "Moby Dick", "price": 18.2, "credit": 76, "veg_cal": 590, "carbon": 4.5}, # T1符合，T2碳排陷阱
        {"name": "Dickens_Dining", "theme": "Great Expectations", "price": 12.0, "credit": 80, "veg_cal": 550, "carbon": 3.5} # 替补选手
    ]
    
    for v in vendors:
        with open(f"vendor_proposals/{v['name']}.json", "w") as f:
            json.dump({
                "vendor_info": {"name": v['name'], "credit_score": v['credit']},
                "proposal": {
                    "literary_theme": v['theme'],
                    "package_price": v['price'],
                    "menu": [
                        {"item": "Signature Meat", "carbon_index": v['carbon']},
                        {"item": "Literature Veggie", "calories": v['veg_cal'], "carbon_index": v['carbon'] * 0.6}
                    ]
                }
            }, f, indent=4)

def build_turn_2():
    os.makedirs("updates", exist_ok=True)
    # 增加黑名单和新的碳排规则
    with open("updates/compliance_memo.txt", "w") as f:
        f.write("URGENT MEMO - STATE DINING OFFICE\n")
        f.write("1. Blacklisted: OldMan_Seafood (Environmental violation in local river).\n")
        f.write("2. New Carbon Policy: Any single item's carbon_index must be below 4.0.\n")
        f.write("3. All vendors must provide a 'Net-Zero' statement by tomorrow.")

def build_turn_3():
    os.makedirs("feedback", exist_ok=True)
    os.makedirs("logistics", exist_ok=True)
    
    # 针对 Austen_Tea 的投诉（其菜品名字可能具有阶级嘲讽性，纯属虚构剧情）
    with open("feedback/petitions.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["source", "target_vendor", "target_item", "issue"])
        writer.writerow(["Literature Society", "Austen_Tea", "Signature Meat", "The name 'Poor-Relief Porridge' is offensive to the historical context of the work."])

    # 预订数据
    orders = {
        "Dublin_Bites": 150,
        "Austen_Tea": 120,
        "Dickens_Dining": 200,
        "Moby_Grill": 100
    }
    with open("logistics/actual_orders.json", "w") as f:
        json.dump(orders, f)

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
