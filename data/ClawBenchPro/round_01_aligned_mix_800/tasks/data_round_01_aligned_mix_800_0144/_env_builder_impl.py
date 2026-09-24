import os
import argparse
import json
import csv

def build_turn_1():
    # 模拟进入 assets/data_round_01_aligned_mix_800_0144/turn_1
    os.makedirs("client_assets/proj_alpha", exist_ok=True)
    os.makedirs("client_assets/proj_beta", exist_ok=True)
    os.makedirs("build_plan", exist_ok=True)
    
    # 规则文件：定义版本红线
    with open("requirements.csv", "w", encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["library", "min_version", "max_version", "license_required"])
        writer.writerow(["jquery", "3.0.0", "3.6.0", "MIT"])
        writer.writerow(["lodash", "4.0.0", "4.17.21", "MIT"])
        writer.writerow(["bootstrap", "4.5.0", "5.1.0", "MIT"])
        writer.writerow(["moment", "2.20.0", "2.29.1", "MIT"])

    # 项目 Alpha 的依赖（包含干扰项：版本过低）
    alpha_manifest = {
        "project": "Alpha",
        "dependencies": {
            "jquery": "2.2.4", # 冲突：低于 min_version
            "lodash": "4.17.20",
            "moment": "2.24.0"
        }
    }
    with open("client_assets/proj_alpha/manifest.json", "w") as f:
        json.dump(alpha_manifest, f, indent=4)

    # 项目 Beta 的依赖（包含干扰项：许可证缺失或版本边缘）
    beta_manifest = {
        "project": "Beta",
        "dependencies": {
            "jquery": "3.5.1",
            "bootstrap": "5.2.0", # 冲突：高于 max_version
            "lodash": "4.17.21"
        }
    }
    with open("client_assets/proj_beta/manifest.json", "w") as f:
        json.dump(beta_manifest, f, indent=4)

    # 复杂性：增加一个隐藏的共享组件库，它依赖于一个特定的 jquery 版本
    os.makedirs("client_assets/shared", exist_ok=True)
    with open("client_assets/shared/common_utils.js", "w") as f:
        f.write("// Requires jquery >= 3.4.0 and < 3.6.0\nfunction common_init() { console.log('Init'); }")

def build_turn_2():
    # 模拟进入 assets/data_round_01_aligned_mix_800_0144/turn_2
    os.makedirs("new_assets", exist_ok=True)
    
    # 增加新框架的描述文件
    shakti_info = {
        "name": "Shakti-UI",
        "version": "1.0.0",
        "conflicts_with": {
            "jquery": "< 3.5.0" # 强制要求更高版本的 jquery，可能与 Turn 1 的某些选择冲突
        },
        "requires": {
            "lodash": ">= 4.17.21"
        }
    }
    with open("new_assets/shakti_config.json", "w") as f:
        json.dump(shakti_info, f, indent=4)

def build_turn_3():
    # 模拟进入 assets/data_round_01_aligned_mix_800_0144/turn_3
    # 安全报告：指向 Turn 1/2 中大家最倾向于选用的 lodash 4.17.21
    with open("vulnerability_report.txt", "w") as f:
        f.write("SECURITY ALERT\n")
        f.write("CVE-2024-XXXXX: lodash versions <= 4.17.21 contain high severity prototype pollution.\n")
        f.write("Recommended fix: Upgrade to 4.17.22 or use 'underscore' as fallback.\n")
        f.write("Note: 'underscore' is NOT currently in our approved requirements.csv list.\n")

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
