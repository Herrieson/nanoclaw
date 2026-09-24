import os
import argparse
import csv
import json

def build_turn_1():
    # 部门配额
    os.makedirs("departments", exist_ok=True)
    with open("departments/quota.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Department", "Total_Quota"])
        writer.writerow(["Transport", "1500.0"])
        writer.writerow(["Health", "1200.0"])
        writer.writerow(["Education", "800.0"])
        writer.writerow(["Housing", "500.0"])

    # 历史已用额度
    os.makedirs("history_records", exist_ok=True)
    history = {
        "John_Doe": 450.0,    # 濒临500限额
        "Jane_Smith": 100.0,
        "Mike_Johnson": 0.0,
        "Emily_Davis": 300.0,
        "Sarah_Connor": 480.0 # 极容易超限
    }
    with open("history_records/2023_expenses.json", "w") as f:
        json.dump(history, f, indent=4)

    # 申请文件预埋陷阱
    os.makedirs("applications", exist_ok=True)
    
    # 陷阱1：John Doe 申请合规项目 60 美元，但总额 450+60=510 超出 500 限额，应当被拒。
    # 因为合规，所以他不进黑名单，只是不批。
    with open("applications/John_Doe_app.txt", "w") as f:
        f.write("Name: John_Doe\nDepartment: Transport\nItem: 认证健身房年费\nAmount: 60.0")

    # 陷阱2：Mike Johnson 申请了炸鸡，违规项目，不仅拒，还要进黑名单！
    with open("applications/Mike_Johnson_app.txt", "w") as f:
        f.write("Name: Mike_Johnson\nDepartment: Housing\nItem: 德州炸鸡派对套餐\nAmount: 120.0")

    # 正常通过：Jane Smith 申请冥想课 200，Health 部门剩余充足。
    with open("applications/Jane_Smith_app.txt", "w") as f:
        f.write("Name: Jane_Smith\nDepartment: Health\nItem: 冥想课程\nAmount: 200.0")

    # 陷阱3：Emily Davis 申请合规，但是 Transport 部门被前序扣除后可能不够？
    # Transport 初始 1500，John 失败(不扣)，Emily 申请 1400。
    # Emily历史300，申请1400超出个人500红线，拒。
    with open("applications/Emily_Davis_app.txt", "w") as f:
        f.write("Name: Emily_Davis\nDepartment: Transport\nItem: 有机蔬菜\nAmount: 1400.0")

    # 正常通过：Sarah Connor 申请有机蔬菜 15，480+15=495，合规通过，Education 扣除 15。
    with open("applications/Sarah_Connor_app.txt", "w") as f:
        f.write("Name: Sarah_Connor\nDepartment: Education\nItem: 有机蔬菜\nAmount: 15.0")
        
    os.makedirs("approved_output", exist_ok=True)


def build_turn_2():
    # 注意：运行在 turn 2 目录下，这里应该只创建增量文件
    os.makedirs("memos", exist_ok=True)
    with open("memos/merger_notice.txt", "w") as f:
        f.write("OFFICIAL MEMO\n\n")
        f.write("Effective immediately, the 'Housing' and 'Transport' departments are merged into a new department called 'Urban_Development'.\n")
        f.write("Please consolidate their resources accordingly.\n")

    os.makedirs("new_applications", exist_ok=True)
    
    # 新申请：Mike Johnson，昨天因为炸鸡进了黑名单。今天申请合规的冥想课 100。
    # 按照规则：扣减50%，即只批 50。由于他之前历史是0，当前是50，未超个人限制。
    # 部门变更为新合并的 Urban_Development。
    with open("new_applications/Mike_Johnson_day2.txt", "w") as f:
        f.write("Name: Mike_Johnson\nDepartment: Urban_Development\nItem: 冥想课程\nAmount: 100.0")

    # 新申请：Alice Cooper (新人，历史记录里没有，默认为0)。申请有机蔬菜 300。
    # 部门：Urban_Development。
    with open("new_applications/Alice_Cooper_day2.txt", "w") as f:
        f.write("Name: Alice_Cooper\nDepartment: Urban_Development\nItem: 有机蔬菜\nAmount: 300.0")

    # 新申请：Jane Smith 昨天批了200（历史100+200=300），今天申请250。300+250=550超标，拒。
    with open("new_applications/Jane_Smith_day2.txt", "w") as f:
        f.write("Name: Jane_Smith\nDepartment: Health\nItem: 认证健身房年费\nAmount: 250.0")

    os.makedirs("final_approved_today", exist_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
