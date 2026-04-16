import os
import json
import re

def verify():
    results = {
        "claim_report_exists": False,
        "correct_total_claim": False,
        "explanation_in_spanish": False,
        "calculation_logic": False
    }
    
    base_path = "."
    workspace_files = os.listdir(".")
    
    # 1. 检查索赔报告是否生成 (通常 Agent 会在当前目录生成)
    report_file = None
    for f in workspace_files:
        if "claim" in f.lower() and f.endswith(".txt") or f.endswith(".pdf") or f.endswith(".md"):
            report_file = f
            results["claim_report_exists"] = True
            break
            
    # 2. 校验计算逻辑
    # 停工时间: 10-24 09:15 到 10-25 07:00，但当日剩余工时计算通常按 8 小时标准减去已做工时。
    # 从 09:15 停工到 17:00 下班，损失工时为 7.75 小时。
    # 8 人 * 7.75 小时 * $45 = $2790
    # 物资损失: 5*120 + 2*25 + 10*85 = 600 + 50 + 850 = $1500
    # 总额理论应为 $4290 (或基于 8 小时整天计算的 $4680)
    if report_file:
        with open(report_file, 'r') as f:
            content = f.read()
            if "4290" in content or "4680" in content or "4500" in content: # 允许一定的计算偏差
                results["correct_total_claim"] = True

    # 3. 检查是否有西班牙语解释
    # 在 trace 或生成的最终回复中寻找西班牙语关键词
    # 注意：这里逻辑上通常需要检查 Agent 的最后一次输出，此处通过生成一个 summary.txt 来模拟
    if os.path.exists("summary_mateo.txt"):
        with open("summary_mateo.txt", 'r') as f:
            content = f.read().lower()
            if "total" in content and ("dólares" in content or "calculado" in content):
                results["explanation_in_spanish"] = True

    with open("state.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
