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

# 初始化客户端，必须关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    # 此函数为检测非结构化文本的统一接口
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
    """动态在沙盒内计算绝对正确的标准答案"""
    active_staff = set()
    registry_path = os.path.join(workspace, "state_registry")
    if os.path.exists(registry_path):
        for root, _, files in os.walk(registry_path):
            for f in files:
                if f.endswith(".json"):
                    with open(os.path.join(root, f), "r", encoding="utf-8") as fp:
                        data = json.load(fp)
                        for item in data:
                            if item.get("status") == "Active":
                                active_staff.add(item.get("staff_id"))
                                
    revoked_staff = set()
    disc_path = os.path.join(workspace, "disciplinary_actions")
    if os.path.exists(disc_path):
        for root, _, files in os.walk(disc_path):
            for f in files:
                if f.endswith(".txt"):
                    with open(os.path.join(root, f), "r", encoding="utf-8") as fp:
                        content = fp.read()
                        if "FINALIZED_OCT_2023" in content:
                            matches = re.findall(r"REVOKED:\s*(S-[A-Z0-9]+)", content)
                            for m in matches:
                                revoked_staff.add(m)
                                
    real_active = active_staff - revoked_staff
    
    unique_sessions = {}
    sub_path = os.path.join(workspace, "school_submissions")
    if os.path.exists(sub_path):
        for root, _, files in os.walk(sub_path):
            for f in files:
                filepath = os.path.join(root, f)
                if f.endswith(".json"):
                    with open(filepath, "r", encoding="utf-8") as fp:
                        data = json.load(fp)
                        for item in data:
                            unique_sessions[str(item["session_id"])] = item
                elif f.endswith(".csv"):
                    with open(filepath, "r", encoding="utf-8", newline='') as fp:
                        reader = csv.DictReader(fp)
                        for row in reader:
                            unique_sessions[str(row["session_id"])] = row
                            
    total_valid_duration = 0
    unauthorized = set()
    
    for sess_id, record in unique_sessions.items():
        dur_str = str(record.get("duration", "0"))
        match = re.search(r"([\d.]+)", dur_str)
        if not match: 
            continue
        val = float(match.group(1))
        
        if "h" in dur_str.lower():
            mins = int(val * 60)
        else:
            mins = int(val)
            
        staff_id = record.get("staff_id")
        if staff_id in real_active:
            total_valid_duration += mins
        else:
            unauthorized.add(staff_id)
            
    return total_valid_duration, sorted(list(unauthorized))

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    total_score = 0
    details = []
    
    # 动态获取标准答案
    try:
        gt_duration, gt_unauth = compute_ground_truth(workspace)
    except Exception as e:
        print(f"Error computing ground truth: {e}")
        gt_duration, gt_unauth = 0, []

    target_file = os.path.join(workspace, "audit_results", "final_audit.json")
    
    # 检查 1: 文件是否存在 (10分)
    if os.path.exists(target_file):
        total_score += 10
        details.append({"item": "检查目标结果文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "final_audit.json 存在"})
    else:
        details.append({"item": "检查目标结果文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "final_audit.json 不存在"})
        # 无法继续
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 读取并解析文件内容
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            agent_data = json.load(f)
    except Exception as e:
        details.append({"item": "检查文件是否为合法JSON格式", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    total_score += 10
    details.append({"item": "检查文件是否为合法JSON格式", "score": 10, "max_score": 10, "passed": True, "reason": "格式合法"})

    # 检查 2: 验证合规总时长 (40分)
    agent_duration = agent_data.get("total_valid_duration_minutes", None)
    if agent_duration is not None and agent_duration == gt_duration:
        total_score += 40
        details.append({"item": "精准验证合规记录总时长", "score": 40, "max_score": 40, "passed": True, "reason": f"时长计算精准: {agent_duration}"})
    else:
        details.append({"item": "精准验证合规记录总时长", "score": 0, "max_score": 40, "passed": False, "reason": f"计算错误，预期 {gt_duration}，实际为 {agent_duration}"})

    # 检查 3: 验证未授权人员名单 (40分)
    agent_unauth = agent_data.get("unauthorized_practitioners", [])
    if isinstance(agent_unauth, list) and agent_unauth == gt_unauth:
        total_score += 40
        details.append({"item": "精准验证未授权人员名单(排序与去重)", "score": 40, "max_score": 40, "passed": True, "reason": "名单匹配，完全正确"})
    else:
        # 部分给分机制，如果只是没有排序，但在集合中
        if set(agent_unauth) == set(gt_unauth):
            total_score += 20
            details.append({"item": "精准验证未授权人员名单(排序与去重)", "score": 20, "max_score": 40, "passed": False, "reason": "名单内容正确，但未进行去重或排序"})
        else:
            missing = set(gt_unauth) - set(agent_unauth)
            extra = set(agent_unauth) - set(gt_unauth)
            details.append({"item": "精准验证未授权人员名单(排序与去重)", "score": 0, "max_score": 40, "passed": False, "reason": f"名单错误。缺失: {len(missing)}项，多出: {len(extra)}项"})

    # 输出结果
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    main()
