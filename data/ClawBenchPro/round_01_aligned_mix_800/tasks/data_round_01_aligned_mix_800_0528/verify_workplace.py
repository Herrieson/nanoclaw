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

def compute_gold(workspace):
    apps_dir = os.path.join(workspace, "data_lake", "applications")
    profiles_dir = os.path.join(workspace, "data_lake", "profiles")
    matrix_path = os.path.join(workspace, "reference", "activity_matrix.csv")

    risk_map = {}
    if os.path.exists(matrix_path):
        with open(matrix_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                risk_map[row["Activity_Code"]] = row["Risk_Class"]

    standard_ids = []
    high_risk_ids = []
    total_children = 0

    if not os.path.exists(apps_dir): 
        return standard_ids, high_risk_ids, total_children

    for fname in os.listdir(apps_dir):
        if not fname.endswith('.json'):
            continue
        app_path = os.path.join(apps_dir, fname)
        try:
            with open(app_path, 'r', encoding='utf-8') as f:
                app_data = json.load(f)
        except Exception:
            continue
        
        if app_data.get("approval_status") == "PENDING":
            client_id = app_data.get("client_id")
            prof_ref = app_data.get("profile_ref")
            prof_path = os.path.join(profiles_dir, f"{prof_ref}.json")
            if not os.path.exists(prof_path):
                continue
            try:
                with open(prof_path, 'r', encoding='utf-8') as f:
                    prof_data = json.load(f)
            except Exception:
                continue
            
            children = prof_data.get("personal_info", {}).get("children", 0)
            total_children += children
            
            activity_codes = prof_data.get("activity_codes", [])
            is_high = False
            for code in activity_codes:
                if risk_map.get(code) in ["C", "D"]:
                    is_high = True
                    break
            
            if is_high:
                high_risk_ids.append(client_id)
            else:
                standard_ids.append(client_id)
                
    return set(standard_ids), set(high_risk_ids), total_children

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    score_details = []
    total_score = 0
    
    # 1. 检查目标目录 (10分)
    target_dir = os.path.join(workspace, "policy_sorting")
    if os.path.isdir(target_dir):
        score_details.append({"item": "检查 policy_sorting 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查 policy_sorting 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 policy_sorting 目录"})
        with open(os.path.join(workspace, "workplace_score.json"), 'w') as f:
            json.dump({"total_score": 0, "details": score_details}, f, indent=2)
        return

    # 金标准计算
    gold_standard_ids, gold_high_risk_ids, gold_total_children = compute_gold(workspace)
    
    files_in_dir = [f for f in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, f))]
    json_files = [f for f in files_in_dir if f.endswith('.json')]
    text_files = [f for f in files_in_dir if not f.endswith('.json')]
    
    # 2. 检查输出 JSON 文件结构 (10分)
    if len(json_files) == 2:
        score_details.append({"item": "检查 JSON 分类文件数量", "score": 10, "max_score": 10, "passed": True, "reason": "正确创建了两个 JSON 文件"})
        total_score += 10
    else:
        score_details.append({"item": "检查 JSON 分类文件数量", "score": 0, "max_score": 10, "passed": False, "reason": f"找到了 {len(json_files)} 个 JSON 文件，期望 2 个"})

    # 3 & 4. 交叉验证两个 JSON 文件内容 (各 30分)
    score_standard = 0
    score_high = 0
    if len(json_files) >= 2:
        try:
            with open(os.path.join(target_dir, json_files[0]), 'r') as f:
                list_a = set(json.load(f))
            with open(os.path.join(target_dir, json_files[1]), 'r') as f:
                list_b = set(json.load(f))
                
            # 区分哪个是 standard，哪个是 high_risk
            # 基于与金标准的交集大小
            inter_a_std = len(list_a.intersection(gold_standard_ids))
            inter_b_std = len(list_b.intersection(gold_standard_ids))
            
            if inter_a_std > inter_b_std:
                agent_standard, agent_high = list_a, list_b
            else:
                agent_standard, agent_high = list_b, list_a
                
            if agent_standard == gold_standard_ids:
                score_standard = 30
                score_details.append({"item": "验证 Standard 风险分类结果", "score": 30, "max_score": 30, "passed": True, "reason": "Standard 客户完全一致"})
            else:
                score_details.append({"item": "验证 Standard 风险分类结果", "score": 0, "max_score": 30, "passed": False, "reason": "Standard 客户数据有误（存在错漏或未过滤损坏数据）"})

            if agent_high == gold_high_risk_ids:
                score_high = 30
                score_details.append({"item": "验证 High Risk 风险分类结果", "score": 30, "max_score": 30, "passed": True, "reason": "High Risk 客户完全一致"})
            else:
                score_details.append({"item": "验证 High Risk 风险分类结果", "score": 0, "max_score": 30, "passed": False, "reason": "High Risk 客户数据有误（是否误用了过期矩阵？）"})
        except Exception as e:
            score_details.append({"item": "解析 JSON 结果文件", "score": 0, "max_score": 60, "passed": False, "reason": "文件不是合法的 JSON 数组结构"})
            
    total_score += (score_standard + score_high)

    # 5. 验证儿童统计数字与大模型评估 (20分)
    score_demographic = 0
    if len(text_files) > 0:
        target_txt = text_files[0]
        with open(os.path.join(target_dir, target_txt), 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 精确代码验证数字
        numbers = re.findall(r'\d+', content)
        if str(gold_total_children) in numbers:
            score_demographic += 10
            # LLM 语义验证：是否合理传达了统计结果而没有产生不必要的幻觉
            llm_prompt = "Does the following text simply and clearly convey the total number of children/dependents for the pending applicants without adding unnecessary, hallucinatory narratives or extra unrequested fields?"
            if llm_judge_content(llm_prompt, content):
                score_demographic += 10
                score_details.append({"item": "验证 Demographic Report", "score": 20, "max_score": 20, "passed": True, "reason": "统计数值完全正确，且表达清晰无幻觉"})
            else:
                score_details.append({"item": "验证 Demographic Report", "score": 10, "max_score": 20, "passed": False, "reason": "统计数值正确，但文本包含过度幻觉或不必要信息"})
        else:
            score_details.append({"item": "验证 Demographic Report", "score": 0, "max_score": 20, "passed": False, "reason": f"未能在文本中找到正确的结果数字 {gold_total_children}"})
    else:
        score_details.append({"item": "验证 Demographic Report", "score": 0, "max_score": 20, "passed": False, "reason": "未找到包含统计结果的纯文本文件"})

    total_score += score_demographic

    with open(os.path.join(workspace, "workplace_score.json"), 'w') as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)

if __name__ == "__main__":
    verify()
