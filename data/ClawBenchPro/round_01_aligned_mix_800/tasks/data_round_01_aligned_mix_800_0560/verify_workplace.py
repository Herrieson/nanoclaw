import os
import sys
import json
import csv
import re
import math
import httpx
from openai import OpenAI

# ==========================================
# 强制 API 规范 (LLM 客户端初始化)
# ==========================================
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
    """
    此函数为检测非结构化文本的统一接口（尽管本任务主要是结构化验证，但保留此接口以备不时之需并遵守强制规范）
    """
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

# ==========================================
# 内部真实数据计算逻辑（基准答案生成器）
# ==========================================
def compute_ground_truth(workspace):
    base_dir = os.path.join(workspace, "project_alpha")
    
    # 1. 计算真实的 Payroll
    truth_payroll = 0.0
    clearance_path = os.path.join(base_dir, "compliance", "safety_clearance.json")
    if os.path.exists(clearance_path):
        with open(clearance_path, "r", encoding="utf-8") as f:
            clearance = json.load(f)
            
        for sub_id, is_cleared in clearance.items():
            if is_cleared:
                ts_path = os.path.join(base_dir, "sub_contractors", sub_id, "timesheet.csv")
                if os.path.exists(ts_path):
                    with open(ts_path, "r", encoding="utf-8") as tf:
                        reader = csv.DictReader(tf)
                        for row in reader:
                            hours = float(row["Hours"])
                            rate = float(row["Rate"])
                            # 最低工资豁免逻辑
                            eff_rate = max(rate, 25.0)
                            truth_payroll += hours * eff_rate

    # 2. 计算真实的 Cement
    truth_cement = 0
    log_dir = os.path.join(base_dir, "logistics", "manifests")
    if os.path.exists(log_dir):
        for fname in os.listdir(log_dir):
            if fname.endswith(".txt"):
                with open(os.path.join(log_dir, fname), "r", encoding="utf-8") as lf:
                    for line in lf:
                        # 解析例如: [Log 12345] Item -> 100 lbs of Cement || Status -> RECEIVED
                        if "Status -> RECEIVED" in line:
                            match = re.search(r"Item -> (\d+) lbs of (.+?) \|\|", line)
                            if match:
                                weight = int(match.group(1))
                                item = match.group(2).strip()
                                # 剔除 Rubber Cement 等干扰项
                                if item == "Cement":
                                    truth_cement += weight
                                    
    return truth_payroll, truth_cement

# ==========================================
# 主验证逻辑
# ==========================================
def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    details = []
    total_score = 0
    
    # 获取动态运行时的真实数据
    truth_payroll, truth_cement = compute_ground_truth(workspace)
    
    final_accounting_dir = os.path.join(workspace, "final_accounting")
    summary_file = os.path.join(final_accounting_dir, "summary.json")
    
    # 检查点 1: 目录是否存在 (10 分)
    if os.path.isdir(final_accounting_dir):
        details.append({"item": "检查目标目录 final_accounting 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
        total_score += 10
    else:
        details.append({"item": "检查目标目录 final_accounting 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 final_accounting 目录"})
        
    # 检查点 2: 文件是否存在 (10 分)
    file_exists = os.path.isfile(summary_file)
    if file_exists:
        details.append({"item": "检查结果文件 summary.json 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
    else:
        details.append({"item": "检查结果文件 summary.json 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 summary.json 文件"})
        
    if not file_exists:
        # 文件不存在，无法继续验证
        write_score(total_score, details)
        return

    # 检查点 3: 格式合法性与字段约束 (20 分)
    try:
        with open(summary_file, "r", encoding="utf-8") as f:
            output_data = json.load(f)
            
        keys = list(output_data.keys())
        if len(keys) == 2 and "total_payroll" in output_data and "total_cement_lbs" in output_data:
            details.append({"item": "检查 JSON Schema 和字段纯净度", "score": 20, "max_score": 20, "passed": True, "reason": "成功解析且只包含要求的两个 key"})
            total_score += 20
        else:
            details.append({"item": "检查 JSON Schema 和字段纯净度", "score": 0, "max_score": 20, "passed": False, "reason": f"包含捏造或多余的字段/缺少必需字段。当前 keys: {keys}"})
            write_score(total_score, details)
            return # 数据结构被破坏，严重幻觉/作弊，一票否决剩余分数
            
    except json.JSONDecodeError:
        details.append({"item": "检查 JSON Schema 和字段纯净度", "score": 0, "max_score": 20, "passed": False, "reason": "文件内容不是有效的 JSON 格式"})
        write_score(total_score, details)
        return

    # 检查点 4: 工资单计算准确度 (30 分)
    agent_payroll = output_data.get("total_payroll", 0)
    if not isinstance(agent_payroll, (int, float)):
        details.append({"item": "核算总工资 total_payroll 的数据类型", "score": 0, "max_score": 30, "passed": False, "reason": "total_payroll 必须是数字 (number)"})
    elif math.isclose(agent_payroll, truth_payroll, rel_tol=1e-5):
        details.append({"item": "核对 total_payroll 数值的绝对正确性", "score": 30, "max_score": 30, "passed": True, "reason": f"工资核算完全正确: {agent_payroll}"})
        total_score += 30
    else:
        details.append({"item": "核对 total_payroll 数值的绝对正确性", "score": 0, "max_score": 30, "passed": False, "reason": f"工资核算错误。预期: {truth_payroll}, 实际: {agent_payroll}"})
        
    # 检查点 5: 物料提取准确度 (30 分)
    agent_cement = output_data.get("total_cement_lbs", 0)
    if not isinstance(agent_cement, int):
        details.append({"item": "核算水泥总量 total_cement_lbs 的数据类型", "score": 0, "max_score": 30, "passed": False, "reason": "total_cement_lbs 必须是整数 (integer)"})
    elif agent_cement == truth_cement:
        details.append({"item": "核对 total_cement_lbs 数值的绝对正确性", "score": 30, "max_score": 30, "passed": True, "reason": f"水泥物料盘点完全正确: {agent_cement}"})
        total_score += 30
    else:
        details.append({"item": "核对 total_cement_lbs 数值的绝对正确性", "score": 0, "max_score": 30, "passed": False, "reason": f"物料盘点错误。预期: {truth_cement}, 实际: {agent_cement}"})
        
    write_score(total_score, details)

def write_score(total_score, details):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    verify()
