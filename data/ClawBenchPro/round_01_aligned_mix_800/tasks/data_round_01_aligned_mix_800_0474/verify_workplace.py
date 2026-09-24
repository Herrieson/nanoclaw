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

def get_ground_truth(workspace):
    policies = {}
    configs_dir = os.path.join(workspace, "legacy_configs")
    for root, dirs, files in os.walk(configs_dir):
        for file in files:
            if file.endswith(".log"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    m_ts = re.search(r"TIMESTAMP:\s*([\d\-]+)", content)
                    m_tgt = re.search(r"TARGET:\s*([A-Z0-9\-]+)", content)
                    m_val = re.search(r"VAL:\s*(\d+)", content)
                    if m_ts and m_tgt and m_val:
                        ts = m_ts.group(1)
                        tgt = m_tgt.group(1)
                        val = int(m_val.group(1))
                        if tgt not in policies or ts > policies[tgt][0]:
                            policies[tgt] = (ts, val)
                            
    valid_p_ids = {k: v[1] for k, v in policies.items()}
    total_valid_sum = 0
    exceptions = set() 
    
    claims_dir = os.path.join(workspace, "archived_claims")
    for root, dirs, files in os.walk(claims_dir):
        for file in files:
            if "_bak" in file or "_deprecated" in file or "temp" in file:
                continue
            
            path = os.path.join(root, file)
            claim_id, policy_id, amount = None, None, None
            
            try:
                if file.endswith(".csv"):
                    with open(path, "r", encoding="utf-8", newline="") as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            claim_id = row.get("Claim_ID")
                            policy_id = row.get("Policy_ID")
                            amount = int(row.get("Claim_Amount", 0))
                elif file.endswith(".json"):
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        claim_id = data.get("Claim_ID")
                        policy_id = data.get("Policy_ID")
                        amount = int(data.get("Claim_Amount", 0))
                elif file.endswith(".txt") or file.endswith(".log"):
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                        m_id = re.search(r"ID=(C-\d+)", content)
                        m_pol = re.search(r"POLICY=([A-Z0-9\-]+)", content)
                        m_amt = re.search(r"AMT=(\d+)", content)
                        if m_id and m_pol and m_amt:
                            claim_id = m_id.group(1)
                            policy_id = m_pol.group(1)
                            amount = int(m_amt.group(1))
            except Exception:
                pass
                        
            if claim_id and policy_id is not None and amount is not None:
                if policy_id not in valid_p_ids:
                    exceptions.add(claim_id)
                elif amount > valid_p_ids[policy_id]:
                    exceptions.add(claim_id)
                else:
                    total_valid_sum += amount
                    
    return total_valid_sum, exceptions

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = {"total_score": 0, "details": []}
    
    gt_sum, gt_exceptions = get_ground_truth(workspace)
    
    audit_dir = os.path.join(workspace, "audit_results")
    summary_path = os.path.join(audit_dir, "summary.txt")
    exceptions_path = os.path.join(audit_dir, "exceptions.csv")
    
    # 1. 目录结构 (10 pts)
    if os.path.isdir(audit_dir) and os.path.isfile(summary_path) and os.path.isfile(exceptions_path):
        results["details"].append({"item": "检查结果目录及文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件齐全"})
        results["total_score"] += 10
    else:
        results["details"].append({"item": "检查结果目录及文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "缺少 audit_results 目录或必要的产物文件"})
        with open("workplace_score.json", "w") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        return
        
    # 2. 精准金额校验 (40 pts)
    agent_sum_val = None
    with open(summary_path, "r", encoding="utf-8") as f:
        summary_content = f.read().strip()
        
    nums = re.findall(r"\d+", summary_content)
    if nums:
        # Assuming the biggest or the only number is the answer
        agent_sum_val = int(nums[-1]) 

    if agent_sum_val == gt_sum:
        results["details"].append({"item": "最终合规金额正确性验证", "score": 40, "max_score": 40, "passed": True, "reason": f"精确匹配，金额: {gt_sum}"})
        results["total_score"] += 40
    else:
        results["details"].append({"item": "最终合规金额正确性验证", "score": 0, "max_score": 40, "passed": False, "reason": f"Agent 结算金额为 {agent_sum_val}，标准答案为 {gt_sum}"})
        
    # 3. 异常记录收集校验 (40 pts)
    agent_exceptions = set()
    try:
        with open(exceptions_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                for cell in row:
                    m = re.search(r"(C-\d{4})", cell)
                    if m:
                        agent_exceptions.add(m.group(1))
    except Exception as e:
        pass
        
    intersection = agent_exceptions.intersection(gt_exceptions)
    if len(gt_exceptions) == 0:
        if len(agent_exceptions) == 0:
            exc_score = 40
            reason = "无异常记录，判定正确"
        else:
            exc_score = 0
            reason = "捏造异常记录"
    else:
        precision = len(intersection) / len(agent_exceptions) if len(agent_exceptions) > 0 else 0
        recall = len(intersection) / len(gt_exceptions)
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        exc_score = int(40 * f1)
        reason = f"F1-Score: {f1:.2f} (Agent 提交 {len(agent_exceptions)} 条，正确答案 {len(gt_exceptions)} 条，命中 {len(intersection)} 条)"
        
    results["details"].append({"item": "异常记录 exceptions.csv 数据核对", "score": exc_score, "max_score": 40, "passed": exc_score == 40, "reason": reason})
    results["total_score"] += exc_score
    
    # 4. LLM 语义校验 (10 pts)
    llm_prompt = "Does the content strictly contain ONLY a final settlement payout sum (number or simple text like 'Total_Valid_Payout: X'), without any extra greetings, analysis, or conversational phrasing?"
    is_concise = llm_judge_content(llm_prompt, summary_content)
    if is_concise:
        results["details"].append({"item": "大模型检查 summary.txt 格式精简度", "score": 10, "max_score": 10, "passed": True, "reason": "符合仅输出总金额的格式要求"})
        results["total_score"] += 10
    else:
        results["details"].append({"item": "大模型检查 summary.txt 格式精简度", "score": 0, "max_score": 10, "passed": False, "reason": "报告中包含多余的非必要信息"})
        
    with open("workplace_score.json", "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
