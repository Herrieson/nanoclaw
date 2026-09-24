import os
import sys
import json
import httpx
import re
import csv
import yaml
from openai import OpenAI

# ----------------------------------------------------------------
# 1. 核心环境与常量定义
# ----------------------------------------------------------------
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """检测非结构化文本的统一接口"""
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
# 2. 真实数据计算逻辑 (Ground Truth Calculation)
# ----------------------------------------------------------------
def get_ground_truth(workspace):
    # 1. Date
    cal_path = os.path.join(workspace, "calendar.yaml")
    with open(cal_path, 'r') as f:
        cal = yaml.safe_load(f)
    event_date = next(e['date'] for e in cal['events'] if e['name'] == "Midnight Art")

    # 2. Expenses
    total_expenses = 0
    receipts_dir = os.path.join(workspace, "receipts")
    for fn in os.listdir(receipts_dir):
        if fn.endswith(".json"):
            with open(os.path.join(receipts_dir, fn), 'r') as f:
                data = json.load(f)
                if data['date'] == event_date:
                    total_expenses += sum(item['cost'] for item in data['items'])

    # 3. VIP List
    vips = []
    emails_dir = os.path.join(workspace, "emails")
    for fn in os.listdir(emails_dir):
        with open(os.path.join(emails_dir, fn), 'r') as f:
            content = f.read()
            if "Subject: CONFIRMED VIPs" in content:
                # Extract names - simple split based on the known format in env_builder
                vips = content.split("event:\n")[1].split("\n\n")[0].split("\n")
                vips = [v.strip() for v in vips if v.strip()]
                break

    # 4. Tips & Profit
    total_tips = 0
    valid_vips_above_500 = []
    tips_dir = os.path.join(workspace, "tips_logs")
    
    def clean_amt(s):
        s = s.replace('$', '').replace('USD', '').strip()
        return int(float(s))

    for fn in os.listdir(tips_dir):
        if fn.endswith(".csv"):
            with open(os.path.join(tips_dir, fn), 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['Status'] == 'CLEARED':
                        amt = clean_amt(row['Amount'])
                        total_tips += amt
                        if row['Guest_Name'] in vips and amt > 500:
                            if row['Guest_Name'] not in valid_vips_above_500:
                                valid_vips_above_500.append(row['Guest_Name'])

    net_profit = total_tips - total_expenses
    return net_profit, sorted(valid_vips_above_500)

# ----------------------------------------------------------------
# 3. 评测执行
# ----------------------------------------------------------------
def run_evaluation():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    
    report_path = os.path.join(workspace, "for_mateo/final_report.txt")
    
    # Check 1: File Existence (10 points)
    if not os.path.exists(report_path):
        score_details.append({"item": "检查结果文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 for_mateo/final_report.txt"})
        # Write 0 and exit if file is missing
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": score_details}, f)
        return

    score_details.append({"item": "检查结果文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件已生成"})

    # Read content
    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Get Ground Truth
    gt_profit, gt_vips = get_ground_truth(workspace)

    # Check 2: Net Profit Extraction and Verification (40 points)
    # Using regex to find the number in the report
    profit_match = re.search(r"(-?\d[\d,]*\.?\d*)", content)
    if profit_match:
        try:
            reported_profit = float(profit_match.group(1).replace(',', ''))
            if abs(reported_profit - gt_profit) < 1.0: # allow float diff but data is int
                score_details.append({"item": "Net Profit 计算准确度", "score": 40, "max_score": 40, "passed": True, "reason": f"利润计算正确: {gt_profit}"})
            else:
                score_details.append({"item": "Net Profit 计算准确度", "score": 0, "max_score": 40, "passed": False, "reason": f"利润计算错误。期望: {gt_profit}, 实际检测到: {reported_profit}"})
        except:
            score_details.append({"item": "Net Profit 数据解析", "score": 0, "max_score": 40, "passed": False, "reason": "无法从文件中解析出有效的利润数值"})
    else:
        score_details.append({"item": "Net Profit 数据解析", "score": 0, "max_score": 40, "passed": False, "reason": "报告中未提及利润数值"})

    # Check 3: VIP List Precision (40 points)
    # Use LLM to extract VIP names from the file to avoid brittle regex on unstructured text
    vips_extraction_prompt = "From the provided file, list the names of VIPs who tipped more than $500. Provide the names separated by commas. Only provide names, no other text."
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[{"role": "user", "content": f"{vips_extraction_prompt}\n\n[File Content]:\n{content}"}],
            temperature=0
        )
        reported_vips_raw = response.choices[0].message.content.strip().split(',')
        reported_vips = sorted([n.strip() for n in reported_vips_raw if n.strip()])
        
        # Exact match of lists
        if reported_vips == gt_vips:
            score_details.append({"item": "VIP 筛选列表准确度 (严格条件: Status=CLEARED, Amount > 500)", "score": 40, "max_score": 40, "passed": True, "reason": "VIP 名单完全正确"})
        else:
            missing = set(gt_vips) - set(reported_vips)
            extra = set(reported_vips) - set(gt_vips)
            reason = ""
            if missing: reason += f"缺失: {missing}. "
            if extra: reason += f"多余或错误(可能包含<=500或未CLEARED的人): {extra}."
            score_details.append({"item": "VIP 筛选列表准确度", "score": max(0, 40 - 10 * (len(missing) + len(extra))), "max_score": 40, "passed": False, "reason": reason})
    except Exception as e:
        score_details.append({"item": "VIP 名单解析失败", "score": 0, "max_score": 40, "passed": False, "reason": f"LLM 解析 VIP 出错: {e}"})

    # Check 4: Tone and Format (10 points) - Mateo requested a "clean file" for his manager
    tone_ok = llm_judge_content("Does the following content look like a professional or organized summary for a manager? It should clearly state the net profit and the VIP list without containing raw code or messy logs.", content)
    if tone_ok:
        score_details.append({"item": "报告格式与易读性", "score": 10, "max_score": 10, "passed": True, "reason": "报告格式整洁，符合业务需求"})
    else:
        score_details.append({"item": "报告格式与易读性", "score": 0, "max_score": 10, "passed": False, "reason": "报告显得杂乱或包含无关信息"})

    # Final Score Calculation
    total_score = sum(d['score'] for d in score_details)
    
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": int(total_score), "details": score_details}, f)

if __name__ == "__main__":
    run_evaluation()
