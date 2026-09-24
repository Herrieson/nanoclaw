import os
import sys
import json
import csv
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

def compute_ground_truth(workspace):
    contracts_dir = os.path.join(workspace, "contracts")
    logs_dir = os.path.join(workspace, "collection_logs")
    revoked_file = os.path.join(workspace, "revoked_brands.txt")
    
    code_to_name = {}
    code_to_approved = {}
    
    # Parse revoked
    revoked_codes = set()
    if os.path.exists(revoked_file):
        with open(revoked_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    revoked_codes.add(line)
                    
    # Parse contracts
    if os.path.exists(contracts_dir):
        for root, _, files in os.walk(contracts_dir):
            for file in files:
                if file.endswith('.json'):
                    try:
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            code = data.get('brand_code')
                            name = data.get('brand_name')
                            status = data.get('status')
                            type_ = data.get('type')
                            
                            if code:
                                code_to_name[code] = name
                                is_approved = (status == 'ACTIVE') and (type_ == 'ECO_PARTNER') and (code not in revoked_codes)
                                code_to_approved[code] = is_approved
                    except:
                        pass
                        
    approved_partners = {}
    unapproved_junk = {}
    
    def add_to_counts(c, count):
        name = code_to_name.get(c, c)
        if code_to_approved.get(c, False):
            approved_partners[name] = approved_partners.get(name, 0) + count
        else:
            unapproved_junk[name] = unapproved_junk.get(name, 0) + count

    # Parse logs
    if os.path.exists(logs_dir):
        for root, _, files in os.walk(logs_dir):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    if file.endswith('.csv'):
                        with open(filepath, 'r', encoding='utf-8') as f:
                            reader = csv.DictReader(f)
                            for row in reader:
                                add_to_counts(row['brand_code'], int(row['frames_count']))
                    elif file.endswith('.tsv'):
                        with open(filepath, 'r', encoding='utf-8') as f:
                            reader = csv.DictReader(f, delimiter='\t')
                            for row in reader:
                                add_to_counts(row['brand_code'], int(row['frames_count']))
                    elif file.endswith('.json'):
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            for row in data.get('log_entries', []):
                                add_to_counts(row['brand_code'], int(row['frames_count']))
                except:
                    pass
                    
    return approved_partners, unapproved_junk

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_dir = os.path.join(workspace, "green_report")
    report_file = os.path.join(report_dir, "summary.json")
    
    score_details = []
    total_score = 0
    
    # 1. 检查目录 (10分)
    if os.path.isdir(report_dir):
        score_details.append({"item": "检查结果目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录 green_report 存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查结果目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录 green_report 不存在"})
        
    # 2. 检查文件与合法性 (15分)
    agent_data = None
    if os.path.isfile(report_file):
        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                agent_data = json.load(f)
            score_details.append({"item": "检查文件是否存在且为合法JSON", "score": 15, "max_score": 15, "passed": True, "reason": "文件 summary.json 存在且为合法 JSON"})
            total_score += 15
        except json.JSONDecodeError:
            score_details.append({"item": "检查文件是否存在且为合法JSON", "score": 5, "max_score": 15, "passed": False, "reason": "文件存在但无法解析为 JSON"})
            total_score += 5
    else:
        score_details.append({"item": "检查文件是否存在且为合法JSON", "score": 0, "max_score": 15, "passed": False, "reason": "文件 summary.json 不存在"})
        
    # 3. 检查 JSON Schema 结构 (15分)
    if agent_data is not None:
        if isinstance(agent_data, dict) and set(agent_data.keys()) == {"approved_partners", "unapproved_junk"}:
            score_details.append({"item": "检查 JSON Schema", "score": 15, "max_score": 15, "passed": True, "reason": "精确包含 required keys"})
            total_score += 15
        else:
            score_details.append({"item": "检查 JSON Schema", "score": 0, "max_score": 15, "passed": False, "reason": "顶级 Key 不对，捏造了多余字段或缺少要求字段"})
            
    # 4 & 5. 数据准确性校验 (60分)
    if agent_data is not None and isinstance(agent_data, dict):
        gt_approved, gt_unapproved = compute_ground_truth(workspace)
        ag_approved = agent_data.get("approved_partners", {})
        ag_unapproved = agent_data.get("unapproved_junk", {})
        
        # Approved Partners (30分)
        if ag_approved == gt_approved:
            score_details.append({"item": "校验 approved_partners 准确性", "score": 30, "max_score": 30, "passed": True, "reason": "数值完全一致"})
            total_score += 30
        else:
            # 计算重合度
            correct = sum(1 for k, v in gt_approved.items() if ag_approved.get(k) == v)
            total_keys = max(len(gt_approved), 1)
            partial = int((correct / total_keys) * 30)
            score_details.append({"item": "校验 approved_partners 准确性", "score": partial, "max_score": 30, "passed": False, "reason": f"部分匹配 ({correct}/{total_keys})，可能包含了违规品牌或者算错了总数。"})
            total_score += partial
            
        # Unapproved Junk (30分)
        if ag_unapproved == gt_unapproved:
            score_details.append({"item": "校验 unapproved_junk 准确性", "score": 30, "max_score": 30, "passed": True, "reason": "数值完全一致"})
            total_score += 30
        else:
            correct = sum(1 for k, v in gt_unapproved.items() if ag_unapproved.get(k) == v)
            total_keys = max(len(gt_unapproved), 1)
            partial = int((correct / total_keys) * 30)
            score_details.append({"item": "校验 unapproved_junk 准确性", "score": partial, "max_score": 30, "passed": False, "reason": f"部分匹配 ({correct}/{total_keys})，可能是对未知 brand_code 未做 fallback 处理。"})
            total_score += partial
    else:
        score_details.append({"item": "校验数据准确性", "score": 0, "max_score": 60, "passed": False, "reason": "无法读取有效的数据对象，数据得分为 0"})

    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": score_details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
