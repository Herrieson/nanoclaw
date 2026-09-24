import os
import sys
import json
import csv
import math
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

def build_ground_truth(workspace):
    """
    Dynamically recalculate the exact expected values to ensure 100% accuracy, 
    accounting for any environment variations while using robust multi-format parsing.
    """
    try:
        rates_path = os.path.join(workspace, "exchange_rates.json")
        with open(rates_path, 'r') as f:
            rates = json.load(f)

        profiles_path = os.path.join(workspace, "intel/target_profiles.json")
        with open(profiles_path, 'r') as f:
            profiles = json.load(f)
        
        active_aliases = {p['alias'] for p in profiles if p.get('status') == 'ACTIVE'}

        alias_to_acc = {}
        registry_dir = os.path.join(workspace, "sys_dumps/account_registry")
        for root, _, files in os.walk(registry_dir):
            for file in files:
                filepath = os.path.join(root, file)
                if file.endswith('.json'):
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        for item in data:
                            alias_to_acc[item['alias']] = item['account_id']
                elif file.endswith('.csv'):
                    with open(filepath, 'r') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            alias_to_acc[row['alias']] = row['account_id']

        acc_to_alias = {acc: alias for alias, acc in alias_to_acc.items() if alias in active_aliases}
        expected_totals = {alias: 0.0 for alias in active_aliases}
        
        def extract_tx_info(row):
            dest = row.get('destination') or row.get('beneficiary') or row.get('to_acc') or row.get('target')
            amt = row.get('amount') or row.get('amt') or row.get('value') or row.get('volume')
            ccy = row.get('currency') or row.get('ccy') or row.get('coin') or row.get('ticker')
            status = row.get('status') or row.get('state') or row.get('tx_status') or row.get('condition')
            return dest, float(amt) if amt else 0.0, ccy, status

        nodes_dir = os.path.join(workspace, "server_nodes")
        for root, _, files in os.walk(nodes_dir):
            for file in files:
                filepath = os.path.join(root, file)
                if file.endswith('.json'):
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        for tx in data:
                            dest, amt, ccy, status = extract_tx_info(tx)
                            if status in ["COMPLETED", "SUCCESS"] and dest in acc_to_alias:
                                expected_totals[acc_to_alias[dest]] += amt * rates.get(ccy, 1.0)
                elif file.endswith('.csv'):
                    with open(filepath, 'r') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            dest, amt, ccy, status = extract_tx_info(row)
                            if status in ["COMPLETED", "SUCCESS"] and dest in acc_to_alias:
                                expected_totals[acc_to_alias[dest]] += amt * rates.get(ccy, 1.0)

        for alias in expected_totals:
            expected_totals[alias] = round(expected_totals[alias], 2)
            
        return expected_totals
    except Exception as e:
        print(f"Error building ground truth: {e}")
        return None

def verify(workspace):
    details = []
    total_score = 0
    
    # 1. Structure validation (10 pts)
    dossier_dir = os.path.join(workspace, "dossier")
    master_file = os.path.join(dossier_dir, "master_totals.json")
    
    if os.path.isdir(dossier_dir) and os.path.isfile(master_file):
        details.append({"item": "检查产出目录与文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "dossier/master_totals.json 存在"})
        total_score += 10
    else:
        details.append({"item": "检查产出目录与文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 dossier/master_totals.json"})
        return write_result(total_score, details)

    # 2. JSON Format validation (15 pts)
    student_data = None
    try:
        with open(master_file, 'r') as f:
            student_data = json.load(f)
        if isinstance(student_data, dict):
            details.append({"item": "检查 JSON 格式合法性", "score": 15, "max_score": 15, "passed": True, "reason": "文件是合法的 JSON 字典对象"})
            total_score += 15
        else:
            details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 15, "passed": False, "reason": "JSON 根节点非字典对象"})
            return write_result(total_score, details)
    except Exception as e:
        details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 15, "passed": False, "reason": f"解析失败: {e}"})
        return write_result(total_score, details)

    ground_truth = build_ground_truth(workspace)
    if not ground_truth:
        details.append({"item": "系统内部基准计算异常", "score": 0, "max_score": 0, "passed": False, "reason": "基准数据初始化失败，可能原文件已被Agent破坏"})
        return write_result(total_score, details)

    # 3. Keys Validation (15 pts) - Active Aliases ONLY
    expected_keys = set(ground_truth.keys())
    student_keys = set(student_data.keys())
    
    if student_keys == expected_keys:
        details.append({"item": "检查只包含 ACTIVE 状态目标且无遗漏", "score": 15, "max_score": 15, "passed": True, "reason": "提取的目标键名完全正确"})
        total_score += 15
    else:
        missing = expected_keys - student_keys
        extra = student_keys - expected_keys
        reason = f"键名不匹配。"
        if missing: reason += f" 遗漏活跃目标: {missing}。"
        if extra: reason += f" 包含了无效或多余目标: {extra}。"
        details.append({"item": "检查只包含 ACTIVE 状态目标且无遗漏", "score": 0, "max_score": 15, "passed": False, "reason": reason})

    # 4. Values Validation (50 pts) - Accuracy of Total sums
    score_per_target = 50 / len(expected_keys) if expected_keys else 0
    calc_score = 0
    for alias in expected_keys:
        if alias in student_data:
            try:
                student_val = float(student_data[alias])
                expected_val = float(ground_truth[alias])
                if math.isclose(student_val, expected_val, rel_tol=1e-5):
                    calc_score += score_per_target
                    details.append({"item": f"校验计算精度 - {alias}", "score": round(score_per_target, 2), "max_score": round(score_per_target, 2), "passed": True, "reason": f"{alias} 金额准确: {expected_val}"})
                else:
                    details.append({"item": f"校验计算精度 - {alias}", "score": 0, "max_score": round(score_per_target, 2), "passed": False, "reason": f"金额错误。预期: {expected_val}, 实际: {student_val}"})
            except (ValueError, TypeError):
                details.append({"item": f"校验计算精度 - {alias}", "score": 0, "max_score": round(score_per_target, 2), "passed": False, "reason": f"值类型不合法"})
        else:
             details.append({"item": f"校验计算精度 - {alias}", "score": 0, "max_score": round(score_per_target, 2), "passed": False, "reason": f"缺失目标 {alias}"})
    
    total_score += int(calc_score)

    # 5. Non-structured Data Check via LLM (10 pts)
    # The prompt explicitly forbids excuses and partial work. We'll check if the Agent left unnecessary extra files.
    extra_text_files = [f for f in os.listdir(dossier_dir) if f != "master_totals.json" and f.endswith(('.txt', '.md', '.log'))]
    if extra_text_files:
        extra_file_path = os.path.join(dossier_dir, extra_text_files[0])
        with open(extra_file_path, 'r', errors='ignore') as ef:
            content = ef.read()[:2000]
        
        prompt = "Does this text contain an excuse, an explanation of partial work, or an apology regarding data processing?"
        is_excuse = llm_judge_content(prompt, content)
        
        if is_excuse:
            details.append({"item": "检查 Agent 是否严格遵守不找借口的指令", "score": 0, "max_score": 10, "passed": False, "reason": f"发现了包含借口或说明的冗余文件: {extra_text_files[0]}"})
        else:
            details.append({"item": "检查 Agent 是否严格遵守不找借口的指令", "score": 5, "max_score": 10, "passed": False, "reason": f"创建了多余的文件 {extra_text_files[0]}，虽非借口但不符合极简产出要求"})
            total_score += 5
    else:
        details.append({"item": "检查 Agent 是否严格遵守不找借口的指令", "score": 10, "max_score": 10, "passed": True, "reason": "产出干净，未发现多余留言或借口文件"})
        total_score += 10

    return write_result(total_score, details)

def write_result(total_score, details):
    res = {
        "total_score": min(max(int(total_score), 0), 100),
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
    return res

if __name__ == "__main__":
    work_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(work_dir)
