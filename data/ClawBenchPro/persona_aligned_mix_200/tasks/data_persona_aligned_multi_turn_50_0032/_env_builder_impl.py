import os
import argparse
import random

def create_mock_vasp_log(filepath, num_iterations, energy_profile, force_profile, elements):
    """
    生成模拟的 VASP OUTCAR 格式的日志文件。
    energy_profile: 长度为 num_iterations 的能量列表
    force_profile: 长度为 num_iterations 的最大受力列表
    """
    with open(filepath, 'w') as f:
        f.write(" VASP 6.3.0 mock log\n")
        f.write(" POSCAR contains: " + " ".join(elements) + "\n\n")
        
        for i in range(num_iterations):
            f.write(f"-----------------------------------------\n")
            f.write(f" Iteration {i+1} / {num_iterations}\n")
            f.write(f"-----------------------------------------\n")
            
            # Mock Energy
            en = energy_profile[i]
            f.write(f"  free  energy   TOTEN  =      {en:.6f} eV\n\n")
            
            f.write(" POSITION                                       TOTAL-FORCE (eV/Angst)\n")
            f.write(" -----------------------------------------------------------------------------------\n")
            
            # Mock Atoms
            num_atoms = 5
            max_f = force_profile[i]
            for a in range(num_atoms):
                # Ensure the first atom has the max force for easy tracking, others are smaller
                if a == 0:
                    fx, fy, fz = max_f * 0.5, max_f * 0.5, max_f * 0.7071 # magnitude approx max_f
                else:
                    fx, fy, fz = random.uniform(0, max_f*0.5), random.uniform(0, max_f*0.5), 0.0
                f.write(f"  {random.uniform(0,10):.5f}  {random.uniform(0,10):.5f}  {random.uniform(0,10):.5f}      {fx:.5f}  {fy:.5f}  {fz:.5f}\n")
            f.write(" -----------------------------------------------------------------------------------\n\n")


def build_turn_1():
    os.makedirs("simulations/batch_1", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    # 结构A：完美收敛。能量下降，受力下降。
    en_A = [-150.0 - (i*0.1) for i in range(30)]
    f_A = [1.0 * (0.9 ** i) for i in range(30)] 
    f_A[-1] = 0.015 # 最终受力 < 0.02
    create_mock_vasp_log("simulations/batch_1/struct_A.log", 30, en_A, f_A, ["Li", "Co", "O"])
    
    # 结构B：掉入陷阱。能量在最后 5 步震荡超 0.05（极差），最终能量约 -100.5
    en_B = [-100.0 - (i*0.05) for i in range(25)]
    en_B.extend([-100.48, -100.55, -100.49, -100.56, -100.50]) # 震荡极差 = 0.08 > 0.05
    f_B = [0.8 * (0.95 ** i) for i in range(30)] # 受力最后降到了很低，但能量震荡
    create_mock_vasp_log("simulations/batch_1/struct_B.log", 30, en_B, f_B, ["Na", "Fe", "O"])
    
    # 结构C：掉入陷阱。受力降不下去（最后10步受力全大于 0.02）
    en_C = [-120.0 - (i*0.1) for i in range(25)]
    f_C = [1.0 * (0.95 ** i) for i in range(15)]
    f_C.extend([0.035] * 10) # 连续10步受力 0.035 > 0.02
    create_mock_vasp_log("simulations/batch_1/struct_C.log", 25, en_C, f_C, ["K", "Mn", "O"])

def build_turn_2():
    os.makedirs("simulations/batch_2", exist_ok=True)
    
    # 结构D：微调了陷阱B的结构。完美收敛，不震荡，受力小。
    # 毒药机制：它的最终能量是 -100.52。与 Turn 1 的 struct_B (-100.50) 差距 0.02 < 0.1 eV。
    # 应该被判断为 "伪收敛"。
    en_D = [-100.0 - (i*0.02) for i in range(26)] # 最终 -100.52
    f_D = [0.5 * (0.8 ** i) for i in range(26)]
    f_D[-1] = 0.01 # < 0.02
    create_mock_vasp_log("simulations/batch_2/struct_D.log", 26, en_D, f_D, ["Na", "Fe", "O"])
    
    # 结构E：完美收敛。没有任何毒药。
    en_E = [-200.0 - (i*0.5) for i in range(20)] # 最终 -209.5
    f_E = [0.6 * (0.8 ** i) for i in range(20)]
    f_E[-1] = 0.01
    create_mock_vasp_log("simulations/batch_2/struct_E.log", 20, en_E, f_E, ["Zn", "Ni", "O"])
    
    # 结构F：完美收敛。
    # 毒药机制：含有 Pd 元素。在 Turn 3 将被毙掉。
    en_F = [-180.0 - (i*0.2) for i in range(22)] # 最终 -184.2
    f_F = [0.7 * (0.85 ** i) for i in range(22)]
    f_F[-1] = 0.005
    create_mock_vasp_log("simulations/batch_2/struct_F.log", 22, en_F, f_F, ["Li", "Pd", "O"])

def build_turn_3():
    os.makedirs("emails", exist_ok=True)
    with open("emails/urgent_update.txt", "w") as f:
        f.write("发件人: 供应链采购部\n")
        f.write("主题: 紧急通知：贵金属原材料禁用\n")
        f.write("正文：\n")
        f.write("各位研发同事，由于近期国际市场波动，含有钯（Pd）元素的原材料成本上涨了300%。\n")
        f.write("为控制量产成本，所有新立项的候选材料体系中，一律不得包含 Pd 元素。\n")
        f.write("请检查你们的筛选池，剔除相关方案。\n")

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
