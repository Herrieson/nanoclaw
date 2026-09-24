import os
import argparse
import json
import csv

def build_turn_1():
    os.makedirs("workspace", exist_ok=True)
    
    # 客户过敏史
    clients = {
        "Carmen": {"allergies": ["Ammonia", "PPD"]},
        "Lucia": {"allergies": []},
        "Rosa": {"allergies": ["Resorcinol"]},
        "Elena": {"allergies": []},
        "Maria": {"allergies": ["PPD"]}
    }
    with open("workspace/clients.json", "w") as f:
        json.dump(clients, f, indent=4)
        
    # 服务详情：定价，耗时(小时)，配方(商品编号及消耗ml)
    services = {
        "Full_Color": {
            "price": 140.0, 
            "duration": 2.0, 
            "products": {"Dye_A": 60, "Dev_20": 60}
        },
        "Highlights": {
            "price": 180.0,
            "duration": 3.0,
            "products": {"Bleach_Pdr": 40, "Dev_30": 80}
        },
        "Root_Touch_Up": {
            "price": 80.0,
            "duration": 1.5,
            "products": {"Dye_B": 40, "Dev_20": 40}
        },
        "Balayage": {
            "price": 220.0,
            "duration": 4.0,
            "products": {"Bleach_Pdr": 60, "Dev_30": 120, "Toner_X": 50}
        }
    }
    with open("workspace/services.json", "w") as f:
        json.dump(services, f, indent=4)
        
    # 库存：包含化学成分，剩余量，每ml成本价
    inventory_header = ["product_id", "remaining_ml", "cost_per_ml", "ingredients"]
    inventory_data = [
        ["Dye_A", 500, 0.20, "Water,Ammonia,Fragrance"], # Carmen 过敏
        ["Dye_B", 300, 0.15, "Water,PPD"],              # Maria 过敏
        ["Bleach_Pdr", 1000, 0.10, "Persulfates"],
        ["Dev_20", 2000, 0.05, "Hydrogen_Peroxide"],
        ["Dev_30", 1500, 0.08, "Hydrogen_Peroxide"],
        ["Toner_X", 100, 0.50, "Water,Resorcinol"]      # Rosa 过敏，且库存很低
    ]
    with open("workspace/inventory.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(inventory_header)
        writer.writerows(inventory_data)
        
    # 预约草稿：有些客户时间重叠，有些会引发过敏，有些利润很低
    schedule_header = ["client_name", "date", "start_time", "service_requested"]
    schedule_data = [
        ["Carmen", "2023-10-23", "09:00", "Full_Color"], # Ammonia过敏，应被踢出
        ["Lucia", "2023-10-23", "13:00", "Highlights"],  # 正常。总价180。成本:40*0.1+80*0.08=10.4。老板抽:54。净利:115.6
        ["Rosa", "2023-10-24", "10:00", "Balayage"],     # Resorcinol过敏，应被踢出
        ["Elena", "2023-10-24", "14:00", "Root_Touch_Up"],# 总价80。成本:40*0.15+40*0.05=8。老板抽:24。净利:48
        ["Maria", "2023-10-25", "10:00", "Highlights"],  # 正常。总价180。
        ["Elena", "2023-10-25", "10:00", "Full_Color"]   # 时间与Maria重叠。比较净利：Maria净利115.6；Elena总140,成本15,抽42,净利83。保留Maria。
    ]
    with open("workspace/schedule_draft.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(schedule_header)
        writer.writerows(schedule_data)

def build_turn_2():
    os.makedirs("updates", exist_ok=True)
    
    # 成本上涨，陷阱：让 Elena 的 Root_Touch_Up (原本净利48) 跌破 25 利润红线
    # Root_Touch_Up 用 Dye_B 40ml 和 Dev_20 40ml。原成本 8。
    # 如果 Dye_B 涨到 0.8，Dev_20 涨到 0.2。新成本 = 32 + 8 = 40。
    # 总价 80 - 抽成 24 - 新成本 40 = 16 < 25。必须被踢出！
    new_costs_header = ["product_id", "new_cost_per_ml"]
    new_costs_data = [
        ["Dye_B", 0.80],
        ["Dev_20", 0.20],
        ["Bleach_Pdr", 0.15]
    ]
    with open("updates/new_costs.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(new_costs_header)
        writer.writerows(new_costs_data)
        
    # 女儿日程，导致 Maria 的预约(10/25 10:00 Highlights，耗时3h -> 到13:00) 刚好卡在边缘或者冲突。
    # 要求是：周二(10/24) 下午 13:00 到 周三(10/25) 中午 12:00 冲突。
    # Maria 在 10/25 10:00，刚好在这个时间段内，必须取消。
    with open("updates/daughter_schedule.txt", "w") as f:
        f.write("Reminder: Church confirmation rehearsal for Sofia.\n")
        f.write("From: Tuesday (10/24) 13:00 PM\n")
        f.write("To: Wednesday (10/25) 12:00 PM\n")
        f.write("Do not miss this!\n")

def build_turn_3():
    os.makedirs("billing", exist_ok=True)
    # 老板的账单。此时真正的有效预约可能只剩 Lucia 了 (10/23 13:00)。
    # 假设老板恶意多算或者算了被取消的单子。
    # Lucia 的服务是 Highlights，总价 180，老板应抽 54。
    # 但老板不仅算了 Lucia 的 54，还把取消掉的 Elena 的 Root_Touch_Up (24) 和 Maria (54) 都算进去了。
    invoice = {
        "invoice_id": "INV-8890",
        "month": "October",
        "boss_cut_percentage": 30,
        "details": [
            {"client": "Lucia", "service": "Highlights", "charged_cut": 65.0}, # 多算了11刀
            {"client": "Elena", "service": "Root_Touch_Up", "charged_cut": 24.0}, # 被AI在turn2因利润取消
            {"client": "Maria", "service": "Highlights", "charged_cut": 54.0} # 被AI在turn2因日程取消
        ],
        "total_due": 143.0
    }
    with open("billing/boss_invoice.json", "w") as f:
        json.dump(invoice, f, indent=4)

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
