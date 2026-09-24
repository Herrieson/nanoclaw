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

def calculate_golden(workspace):
    hazards = set()
    safety_matrix = {}
    with open(os.path.join(workspace, "compliance/safety_matrix.json"), "r", encoding="utf-8") as f:
        safety_matrix = json.load(f)
    
    site_records_dir = os.path.join(workspace, "sync_dump/site_records")
    for root, _, files in os.walk(site_records_dir):
        for file in files:
            if file.endswith(".txt"):
                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    lines = f.read().split('\n')
                    inspector = ""
                    status = ""
                    code = ""
                    desc = ""
                    for line in lines:
                        if line.startswith("Inspector:"): inspector = line.split(":", 1)[1].strip()
                        elif line.startswith("Status:"): status = line.split(":", 1)[1].strip()
                        elif line.startswith("Incident_Code:"): code = line.split(":", 1)[1].strip()
                        elif line.startswith("Incident_Desc:"): desc = line.split(":", 1)[1].strip()
                    
                    if inspector == "Marcus" and status == "Finalized":
                        if safety_matrix.get(code, 0) >= 4:
                            if desc:
                                hazards.add(desc)

    vendor_cat = {}
    with open(os.path.join(workspace, "accounting/vendor_categories.csv"), "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            vendor_cat[row["Vendor_ID"]] = row["Category"]
            
    construction_total = 0.0
    art_total = 0.0
    financials_dir = os.path.join(workspace, "sync_dump/financials")
    for root, _, files in os.walk(financials_dir):
        for file in files:
            if file.endswith(".json"):
                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        if str(data.get("card_last4")) == "4921" and data.get("status") == "POSTED":
                            vid = data.get("vendor_id")
                            cat = vendor_cat.get(vid)
                            amt = float(data.get("amount", 0))
                            if cat == "Construction":
                                construction_total += amt
                            elif cat == "Art":
                                art_total += amt
                    except json.JSONDecodeError:
                        pass
                        
    return hazards, construction_total, art_total

def extract_amounts(text, keyword):
    pattern = re.compile(rf"(?i){keyword}[^\d]*(\d+(?:\.\d+)?)")
    match = pattern.search(text)
    if match:
        return float(match.group(1))
    return None

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    golden_hazards, golden_const, golden_art = calculate_golden(workspace)

    # 1. Check directory existence (10 points)
    ready_dir = os.path.join(workspace, "ready_for_monday")
    if os.path.isdir(ready_dir):
        score_details.append({"item": "检查结果目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录 ready_for_monday 存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查结果目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 ready_for_monday 目录"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 2. Check safety hazards file (45 points)
    hazards_file = os.path.join(ready_dir, "critical_hazards.txt")
    if os.path.isfile(hazards_file):
        score_details.append({"item": "安全隐患文件存在", "score": 5, "max_score": 5, "passed": True, "reason": "critical_hazards.txt 文件存在"})
        total_score += 5
        
        with open(hazards_file, "r", encoding="utf-8") as f:
            agent_hazards_content = f.read()
            agent_hazards_lines = [line.strip() for line in agent_hazards_content.split('\n') if line.strip()]
        
        agent_hazards_set = set(agent_hazards_lines)
        missing = golden_hazards - agent_hazards_set
        extra = agent_hazards_set - golden_hazards
        
        if len(missing) == 0 and len(extra) == 0 and len(golden_hazards) > 0:
            score_details.append({"item": "安全隐患描述精准提取", "score": 40, "max_score": 40, "passed": True, "reason": "完全精准提取了所有满足条件的隐患描述，没有遗漏和幻觉"})
            total_score += 40
        else:
            penalty = 40
            reason = []
            if len(missing) > 0:
                penalty -= min(20, len(missing) * 2)
                reason.append(f"漏掉 {len(missing)} 个描述")
            if len(extra) > 0:
                penalty -= min(20, len(extra) * 2)
                reason.append(f"捏造或错误提取 {len(extra)} 个描述")
            
            final_h_score = max(0, penalty)
            score_details.append({"item": "安全隐患描述精准提取", "score": final_h_score, "max_score": 40, "passed": final_h_score==40, "reason": "; ".join(reason)})
            total_score += final_h_score
    else:
        score_details.append({"item": "安全隐患文件存在", "score": 0, "max_score": 5, "passed": False, "reason": "未找到 critical_hazards.txt"})
        score_details.append({"item": "安全隐患描述精准提取", "score": 0, "max_score": 40, "passed": False, "reason": "文件不存在，无法验证"})

    # 3. Check financial expense file (45 points)
    expense_file = os.path.join(ready_dir, "expense_totals.txt")
    if os.path.isfile(expense_file):
        score_details.append({"item": "财务支出文件存在", "score": 5, "max_score": 5, "passed": True, "reason": "expense_totals.txt 文件存在"})
        total_score += 5
        
        with open(expense_file, "r", encoding="utf-8") as f:
            expense_content = f.read()
            
        agent_const = extract_amounts(expense_content, "Construction")
        agent_art = extract_amounts(expense_content, "Art")
        
        fin_score = 0
        fin_reasons = []
        
        # fallback to LLM if regex fails
        if agent_const is None or agent_art is None:
            llm_prompt = f"The exact total for Construction is {golden_const:.2f} or {golden_const}. The exact total for Art is {golden_art:.2f} or {golden_art}. Does the file content state THESE EXACT AMOUNTS for their respective categories?"
            llm_result = llm_judge_content(llm_prompt, expense_content)
            if llm_result:
                fin_score = 40
                fin_reasons.append("LLM 验证大意与数值完全吻合")
            else:
                fin_reasons.append("正则未匹配到有效数字且 LLM 判定数值不准确或缺失")
        else:
            if abs(agent_const - golden_const) < 0.01:
                fin_score += 20
                fin_reasons.append("Construction 总金额精准无误")
            else:
                fin_reasons.append(f"Construction 金额错误 (期望 {golden_const}, 实际提取 {agent_const})")
                
            if abs(agent_art - golden_art) < 0.01:
                fin_score += 20
                fin_reasons.append("Art 总金额精准无误")
            else:
                fin_reasons.append(f"Art 金额错误 (期望 {golden_art}, 实际提取 {agent_art})")
                
        score_details.append({"item": "金额统计严格比对", "score": fin_score, "max_score": 40, "passed": fin_score == 40, "reason": "; ".join(fin_reasons)})
        total_score += fin_score
    else:
        score_details.append({"item": "财务支出文件存在", "score": 0, "max_score": 5, "passed": False, "reason": "未找到 expense_totals.txt"})
        score_details.append({"item": "金额统计严格比对", "score": 0, "max_score": 40, "passed": False, "reason": "文件不存在，无法验证"})

    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)

if __name__ == "__main__":
    verify()
