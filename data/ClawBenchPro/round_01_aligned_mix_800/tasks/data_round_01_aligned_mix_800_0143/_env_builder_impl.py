import os
import argparse
import random

def build_turn_1():
    # 路径已由框架设定为 assets/data_round_01_aligned_mix_800_0143/turn_1
    os.makedirs("raw_data/trial_logs", exist_ok=True)
    os.makedirs("protocol", exist_ok=True)
    
    # 编写原始指南
    with open("protocol/guidelines.txt", "w") as f:
        f.write("Standard Deviation Limit: 15.0\nMax Flux: 25%\n")
        
    # 编写修正备忘录 (模拟PDF内容)
    with open("protocol/latest_memo.txt", "w") as f:
        f.write("CORRECTION: The Max Flux threshold mentioned in guidelines.txt is too loose. "
                "For high-risk groups, use 20%. High-risk is defined as Baseline Systolic > 140.")

    # 生成实验数据：包含陷阱
    data = [
        "PatientID,Baseline_BP,Current_BP,HeartRate",
        "P001,120,165,60", # 偏离率 (165-120)/120 = 37.5% > 20%? NO, Baseline<=140, limit is 40% according to prompt (or is it?)
        "P002,150,185,60", # Baseline > 140, 偏离 (185-150)/150 = 23.3% > 20%? YES. (High risk)
        "P003,110,110,60", # Normal
        "P004,145,210,60", # (210-145)/145 = 44.8% > 40%. (Toxic outlier)
        "P005,130,150,72", # Normal
    ]
    with open("raw_data/trial_logs/batch_01.csv", "w") as f:
        f.write("\n".join(data))

def build_turn_2():
    # 路径为 assets/data_round_01_aligned_mix_800_0143/turn_2，已继承 turn_1 的文件
    os.makedirs("updates/new_batches", exist_ok=True)
    
    # 新的政策变动：引入年龄因素，且不直接给公式
    with open("updates/policy_change.txt", "w") as f:
        f.write("URGENT: New ethics rule - Patients over 65 have a 5% tighter tolerance on all flux metrics. "
                "Also, cross-reference data_round_01_aligned_mix_800_0143_demographics.csv for age data.")
    
    # 增加人口普查数据
    with open("updates/data_round_01_aligned_mix_800_0143_demographics.csv", "w") as f:
        f.write("PatientID,Age\nP001,70\nP002,45\nP003,68\nP004,30\nP005,50\nP006,72")
        
    # 新批次数据
    new_data = [
        "PatientID,Baseline_BP,Current_BP,HeartRate",
        "P006,120,140,60", # (140-120)/120 = 16.6%. If age > 65, limit might be 15% (20% - 5%). 
    ]
    with open("updates/new_batches/batch_02.csv", "w") as f:
        f.write("\n".join(new_data))

def build_turn_3():
    # 路径为 assets/data_round_01_aligned_mix_800_0143/turn_3
    os.makedirs("lab_results/chemical_logs", exist_ok=True)
    
    # 系统性偏差检查：血药浓度。要求二阶导数为0（即线性变化）
    # P003 是 Phase I 看起来最正常的，现在给它埋雷
    with open("lab_results/chemical_logs/P003_lab.csv", "w") as f:
        f.write("Time,Concentration\n0,0.1\n1,0.2\n2,0.3\n3,0.4") # 线性，二阶导为0
        
    with open("lab_results/chemical_logs/P001_lab.csv", "w") as f:
        f.write("Time,Concentration\n0,0.1\n1,0.4\n2,0.9\n3,1.6") # 二阶导不为0 (t^2)
        
    # 注入干扰项 batch_03
    with open("raw_data/trial_logs/batch_03.csv", "w") as f:
        f.write("PatientID,Baseline_BP,Current_BP,HeartRate\nP099,120,125,70")

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
