import os
import argparse
import random
import json

def build_turn_1():
    # 模拟极度混乱的文件结构
    os.makedirs("clutter/inbox", exist_ok=True)
    os.makedirs("clutter/notes/scraps", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. 财务流水：包含干扰项和脏数据
    with open("clutter/bank_statement_raw.txt", "w") as f:
        f.write("Date,Desc,Amt\n")
        f.write("2023-10-01,eBay-Payout-Ref#882,450.00\n")
        f.write("2023-10-05,Coffee, -5.50\n")
        f.write("2023-10-06,Mercari-Deposit,120.00\n")
        f.write("2023-10-10,System-Error-Correction, +0.00\n")
        f.write("2023-10-15,YardSale_Cash,200.00\n")
        f.write("2023-10-20,eBay-Payout-Ref#991,315.50\n")

    # 2. 销售记录：结构不一
    sales_data = [
        {"item": "Solar-Power-Bank-X1", "platform": "eBay", "price": 450.0, "status": "shipped", "ref": "882"},
        {"item": "Retro-E-Ink-Tablet", "platform": "Mercari", "price": 120.0, "status": "completed", "ref": "M11"},
        {"item": "Smart-Garden-Sensor-V3", "platform": "eBay", "price": 350.0, "status": "pending", "ref": "991"} # 银行显示315.50，这里预埋差额陷阱（手续费）
    ]
    with open("clutter/inbox/online_sales.json", "w") as f:
        json.dump(sales_data, f)

    # 3. 乱七八糟的笔记
    with open("clutter/notes/scraps/scratchpad.txt", "w") as f:
        f.write("Don't forget: Every sale on eBay has a 10% platform fee + $3.5 fixed fee. \n")
        f.write("If the math doesn't add up on #991, check if the sensor was actually $350 or if I misremembered. \n")
        f.write("I need to keep track of my total income for the disability benefit review. Limit is $1000/month from sales.\n")

def build_turn_2():
    # 注入新的物流争议文件
    os.makedirs("clutter/disputes", exist_ok=True)
    with open("clutter/disputes/email_thread.txt", "w") as f:
        f.write("From: CustomerSupport@eBay.com\nRe: Ref#882\n")
        f.write("The buyer claims the Solar-Power-Bank-X1 was damaged. We might need to refund $150.\n")
    
    # 修改原本的规则：突然发现去年的审计文件
    with open("clutter/notes/archive_tax.txt", "w") as f:
        f.write("Correction for 2023: Any 'YardSale' cash over $150 must be reported as 100% profit. \n")

def build_turn_3():
    # 最终的混乱：硬件回收计划
    with open("clutter/recycling_list.csv", "w") as f:
        f.write("Device,Category,Value_Estimate\n")
        f.write("Old-Macbook-2012,Laptop,50\n")
        f.write("Broken-Drone,Toy,20\n")
        f.write("Kindle-G3,Reader,30\n")

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
