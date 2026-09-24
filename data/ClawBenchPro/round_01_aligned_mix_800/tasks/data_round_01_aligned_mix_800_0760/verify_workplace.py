import os
import sys
import json
import csv
import httpx
from openai import OpenAI

# ----------------------------------------------------------------
# 1. 基础配置与客户端初始化
# ----------------------------------------------------------------
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict data validation assistant. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[File Content]:\n{file_content}"}
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

# ----------------------------------------------------------------
# 2. 核心验证逻辑
# ----------------------------------------------------------------
def run_verification():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    
    final_accounting_dir = os.path.join(workspace, "final_accounting")
    
    # --- 指标 1: 目录结构检查 (10分) ---
    if os.path.exists(final_accounting_dir) and os.path.isdir(final_accounting_dir):
        results.append({"item": "目录 final_accounting 存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录已创建"})
    else:
        results.append({"item": "目录 final_accounting 存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到指定输出目录"})

    # 查找报告文件（支持常见后缀）
    report_file = None
    for f in os.listdir(final_accounting_dir) if os.path.exists(final_accounting_dir) else []:
        if "report" in f.lower() or "summary" in f.lower():
            report_file = os.path.join(final_accounting_dir, f)
            break
    
    if not report_file:
        results.append({"item": "汇总报告文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "未能在目录中找到包含 report 或 summary 的文件"})
    else:
        results.append({"item": "汇总报告文件存在", "score": 10, "max_score": 10, "passed": True, "reason": f"找到文件 {os.path.basename(report_file)}"})
        
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # --- 指标 2: 工资计算逻辑验证 (40分) ---
        # 逻辑：Pedro(40.5*25=1012.5), Miguel(38*28=1064), Javier(45*25=1125), Hector(20*25=500). Total=3701.5
        # 必须确保低于25的被调整到了25
        expected_payroll = 3701.5
        if str(expected_payroll) in content or "3,701.5" in content:
            results.append({"item": "薪资总额计算正确 (含底薪调整)", "score": 40, "max_score": 40, "passed": True, "reason": "总额 3701.5 匹配成功"})
        else:
            # 容错：检查是否没有调薪直接算的 (15*40.5 + 28*38 + 22*45 + 25*20 = 607.5 + 1064 + 990 + 500 = 3161.5)
            if "3161.5" in content:
                results.append({"item": "薪资总额计算正确 (含底薪调整)", "score": 10, "max_score": 40, "passed": False, "reason": "薪资计算未应用 '最低25/小时' 的规则"})
            else:
                results.append({"item": "薪资总额计算正确 (含底薪调整)", "score": 0, "max_score": 40, "passed": False, "reason": "未能从报告中提取到正确的薪资总额 3701.5"})

        # --- 指标 3: 水泥重量统计验证 (30分) ---
        # 逻辑：Monday(1200) + Wednesday(850) + Friday(150) = 2200 lbs
        expected_cement = 2200
        if "2200" in content:
            results.append({"item": "水泥总量统计正确", "score": 30, "max_score": 30, "passed": True, "reason": "总量 2200 匹配成功"})
        else:
            results.append({"item": "水泥总量统计正确", "score": 0, "max_score": 30, "passed": False, "reason": "未能从报告中提取到正确的水泥总量 2200 lbs"})

        # --- 指标 4: LLM 语义检查报告完整性与语气 (10分) ---
        prompt = "Check if the report contains both the updated payroll details and the material summary, and has a professional but appropriate tone for a construction client summary."
        if llm_judge_content(prompt, content):
            results.append({"item": "报告内容完整性与专业性 (LLM评测)", "score": 10, "max_score": 10, "passed": True, "reason": "内容覆盖全面且语气符合要求"})
        else:
            results.append({"item": "报告内容完整性与专业性 (LLM评测)", "score": 0, "max_score": 10, "passed": False, "reason": "报告内容缺失或表达不符合职业标准"})

    # 计算总分
    total_score = sum(item["score"] for item in results)
    
    # 写入结果文件
    output_data = {
        "total_score": total_score,
        "details": results
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    run_verification()
