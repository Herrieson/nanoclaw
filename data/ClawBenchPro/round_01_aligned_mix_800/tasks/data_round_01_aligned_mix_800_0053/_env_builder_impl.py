import os
import argparse
import csv
import json

def build_turn_1():
    # 创建目录
    os.makedirs("vendors", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    
    # 1. 学校人口数据：预埋 Indian 占比超过 20% 的陷阱
    demographics = [
        ["Grade", "Total_Students", "Indian_Students", "Hispanic_Students", "Other"],
        ["Grade_3", 100, 25, 40, 35],  # 25% Indian
        ["Grade_4", 120, 10, 60, 50],  # < 10%
        ["Grade_5", 80, 22, 30, 28]    # 27.5% Indian
    ]
    with open("school_demographics.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(demographics)

    # 2. 供应商数据
    # Vendor A: 便宜但互动性低（需加 15% 损耗费），且内容配比不符合 Grade 3/5 的包容性要求
    vendor_a = {
        "name": "Global_Edu_Print",
        "total_cost": 7000,
        "engagement_score": 3.8,
        "content_diversity": {"South_Asian": 0.03, "Hispanic": 0.50},
        "packages": ["Grade_3", "Grade_4", "Grade_5"]
    }
    # Vendor B: 价格稍贵，正好在 8500 边缘，符合所有条件
    vendor_b = {
        "name": "Inclusive_Learning_Labs",
        "total_cost": 8200,
        "engagement_score": 4.5,
        "content_diversity": {"South_Asian": 0.12, "Hispanic": 0.30},
        "packages": ["Grade_3", "Grade_4", "Grade_5"]
    }
    # Vendor C: 极贵，超预算
    vendor_c = {
        "name": "Elite_Academy_Press",
        "total_cost": 9500,
        "engagement_score": 4.9,
        "content_diversity": {"South_Asian": 0.20, "Hispanic": 0.40},
        "packages": ["Grade_3", "Grade_4", "Grade_5"]
    }

    with open("vendors/vendor_A.json", "w") as f: json.dump(vendor_a, f)
    with open("vendors/vendor_B.json", "w") as f: json.dump(vendor_b, f)
    with open("vendors/vendor_C.json", "w") as f: json.dump(vendor_c, f)

def build_turn_2():
    os.makedirs("updates", exist_ok=True)
    
    # 1. 政策变动：将 Turn 1 中看似最完美的 Vendor B 的某个关键教材模块列入禁令
    with open("updates/policy_notice.txt", "w") as f:
        f.write("URGENT: Due to copyright infringement issues, all 'Inclusive_Learning_Labs' materials (Vendor B) related to 'Modern History' are BANNED from use. Please switch to alternate verified vendors immediately.")

    # 2. 学生反馈：Grade 4 反馈极差，Grade 5 反馈极好
    feedback = [
        {"grade": "Grade_3", "avg_satisfaction": 4.0},
        {"grade": "Grade_4", "avg_satisfaction": 1.2, "comment": "Too boring, even for a teaching assistant."},
        {"grade": "Grade_5", "avg_satisfaction": 4.8, "comment": "Love the South Asian stories!"}
    ]
    with open("updates/student_feedback.json", "w") as f:
        json.dump(feedback, f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
