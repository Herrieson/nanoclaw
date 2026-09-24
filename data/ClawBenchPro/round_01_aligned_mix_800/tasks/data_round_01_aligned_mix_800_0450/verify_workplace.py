import os
import sys
import json
import csv
import re
import httpx
from openai import OpenAI

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

def calculate_golden_truth(workspace):
    """
    Directly parse the generated environment to calculate the exact true integers 
    for revenue and expenses to avoid dependency on random seed stability alone.
    """
    registry_path = os.path.join(workspace, "desk_drawer_dump", "system_backups", "master_registry_2023.csv")
    valid_jobs = set()
    
    if os.path.exists(registry_path):
        with open(registry_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("Status") == "Completed":
                    valid_jobs.add(row.get("Job_ID"))
                    
    dump_dir = os.path.join(workspace, "desk_drawer_dump")
    total_rev = 0
    total_exp = 0
    
    if not os.path.exists(dump_dir):
        return 0, 0

    for root, dirs, files in os.walk(dump_dir):
        for file in files:
            filepath = os.path.join(root, file)
            if file.endswith(".txt") and file.startswith("scratchpad"):
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        job_match = re.search(r"Job Ref:\s*(J-\d+)", content)
                        if job_match:
                            job_id = job_match.group(1)
                            if job_id in valid_jobs:
                                rev_match = re.search(r"Amount Billed:\s*\$(\d+)", content)
                                exp_match = re.search(r"Parts Cost:\s*\$(\d+)", content)
                                if rev_match: total_rev += int(rev_match.group(1))
                                if exp_match: total_exp += int(exp_match.group(1))
                except Exception: pass
                            
            elif file.endswith(".json") and file.startswith("mob_export"):
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        job_id = data.get("jobRef")
                        if job_id in valid_jobs:
                            total_rev += int(data.get("financials", {}).get("revenue", 0))
                            total_exp += int(data.get("financials", {}).get("expenses", 0))
                except Exception: pass
                    
            elif file == "transactions.csv":
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            job_id = row.get("RefID")
                            if job_id in valid_jobs:
                                cat = row.get("Category")
                                amt = int(row.get("Amount", 0))
                                if cat == "Revenue": total_rev += amt
                                elif cat == "Expense": total_exp += amt
                except Exception: pass
                    
    return total_rev, total_exp

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    # 1. Check Directory
    target_dir = os.path.join(workspace, "accountant_ready")
    if os.path.isdir(target_dir):
        score_details.append({"item": "检查目标文件夹 accountant_ready 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件夹存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查目标文件夹 accountant_ready 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件夹缺失"})
        
    # 2. Check File
    target_file = os.path.join(target_dir, "tax_headache_summary.json")
    agent_rev, agent_exp = None, None
    if os.path.exists(target_file):
        score_details.append({"item": "检查结果文件 tax_headache_summary.json 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
        
        # 3. Check JSON Format and Keys
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if "total_revenue" in data and "total_expenses" in data:
                score_details.append({"item": "检查 JSON 格式与必需字段", "score": 20, "max_score": 20, "passed": True, "reason": "字段 total_revenue 和 total_expenses 存在"})
                total_score += 20
                agent_rev = data["total_revenue"]
                agent_exp = data["total_expenses"]
            else:
                score_details.append({"item": "检查 JSON 格式与必需字段", "score": 0, "max_score": 20, "passed": False, "reason": "缺少必需的键名或捏造了多余的键名"})
        except Exception as e:
            score_details.append({"item": "检查 JSON 格式与必需字段", "score": 0, "max_score": 20, "passed": False, "reason": f"解析 JSON 失败: {e}"})
    else:
        score_details.append({"item": "检查结果文件 tax_headache_summary.json 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失"})
        score_details.append({"item": "检查 JSON 格式与必需字段", "score": 0, "max_score": 20, "passed": False, "reason": "文件缺失，无法检查"})

    # 4 & 5. Precision Calculations
    golden_rev, golden_exp = calculate_golden_truth(workspace)
    
    if agent_rev is not None and int(agent_rev) == golden_rev:
        score_details.append({"item": "核对总收入(total_revenue)绝对准确性", "score": 30, "max_score": 30, "passed": True, "reason": f"匹配成功：{golden_rev}"})
        total_score += 30
    else:
        score_details.append({"item": "核对总收入(total_revenue)绝对准确性", "score": 0, "max_score": 30, "passed": False, "reason": f"匹配失败。期望 {golden_rev}，实际为 {agent_rev}"})

    if agent_exp is not None and int(agent_exp) == golden_exp:
        score_details.append({"item": "核对总支出(total_expenses)绝对准确性", "score": 30, "max_score": 30, "passed": True, "reason": f"匹配成功：{golden_exp}"})
        total_score += 30
    else:
        score_details.append({"item": "核对总支出(total_expenses)绝对准确性", "score": 0, "max_score": 30, "passed": False, "reason": f"匹配失败。期望 {golden_exp}，实际为 {agent_exp}"})

    # Write output
    result = {
        "total_score": total_score,
        "details": score_details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
