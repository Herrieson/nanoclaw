import os
import sys
import json
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

def generate_ground_truth(workspace_dir):
    roster_path = os.path.join(workspace_dir, "messy_desk", "patient_roster", "master_roster.json")
    if not os.path.exists(roster_path):
        return {}
        
    with open(roster_path, 'r', encoding='utf-8') as f:
        roster = json.load(f)
        
    residential_patients = {}
    for p in roster:
        if p.get("care_category") == "Residential":
            residential_patients[p["patient_id"]] = {
                "name": p["full_name"],
                "latest_date": "00000000",
                "latest_pain_level": None,
                "mindfulness_candidate": False
            }
            
    notes_dir = os.path.join(workspace_dir, "messy_desk", "notes")
    keywords = ["stressed", "tense", "anxious", "yoga", "meditation"]
    
    for root, dirs, files in os.walk(notes_dir):
        for file in files:
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, notes_dir)
            parts = rel_path.split(os.sep)
            if len(parts) >= 4:
                date_str = parts[0] + parts[1] + parts[2]
            else:
                continue
                
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except:
                continue
                
            # Process line by line to handle mixed records gracefully
            lines = content.split('\n')
            for line in lines:
                pid_match = re.search(r'(P\d{3})', line)
                if not pid_match:
                    continue
                pid = pid_match.group(1)
                
                if pid not in residential_patients:
                    continue
                
                pain_match = re.search(r'(?i)pain.*?(\d+)', line)
                if pain_match:
                    pain = int(pain_match.group(1))
                    if date_str > residential_patients[pid]["latest_date"]:
                        residential_patients[pid]["latest_date"] = date_str
                        residential_patients[pid]["latest_pain_level"] = pain
                        
                for kw in keywords:
                    if kw.lower() in line.lower():
                        residential_patients[pid]["mindfulness_candidate"] = True
                        break

    # Filter out patients with NO notes at all (since we can't determine their pain level)
    final_truth = {
        data["name"]: {
            "latest_pain_level": data["latest_pain_level"],
            "mindfulness_candidate": data["mindfulness_candidate"]
        }
        for pid, data in residential_patients.items() if data["latest_pain_level"] is not None
    }
    
    return final_truth

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []
    
    gt = generate_ground_truth(workspace)
    if not gt:
        details.append({"item": "沙盒环境完整性检查", "score": 0, "max_score": 0, "passed": False, "reason": "无法生成 Ground Truth，环境可能已破坏。"})
        # Write score
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": details}, f, indent=4)
        return

    output_path = os.path.join(workspace, "organized_desk", "residential_summary.json")
    if not os.path.exists(output_path):
        details.append({"item": "检查结果文件是否存在", "score": 0, "max_score": 15, "passed": False, "reason": f"未找到输出文件 {output_path}"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": details}, f, indent=4)
        return
        
    details.append({"item": "检查结果文件是否存在", "score": 15, "max_score": 15, "passed": True, "reason": "文件存在"})
    
    try:
        with open(output_path, 'r', encoding='utf-8') as f:
            agent_data = json.load(f)
    except Exception as e:
        details.append({"item": "检查 JSON 格式", "score": 0, "max_score": 15, "passed": False, "reason": f"JSON 解析失败: {e}"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 15, "details": details}, f, indent=4)
        return

    if not isinstance(agent_data, list):
        details.append({"item": "检查 JSON 格式", "score": 0, "max_score": 15, "passed": False, "reason": "输出必须是 JSON Array"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 15, "details": details}, f, indent=4)
        return
        
    details.append({"item": "检查 JSON 格式", "score": 15, "max_score": 15, "passed": True, "reason": "是合法的 JSON Array"})
    score += 30 # 15 + 15
    
    # 格式化 Agent 输出为 dict
    agent_dict = {}
    valid_schema = True
    for item in agent_data:
        if not isinstance(item, dict):
            valid_schema = False
            break
        if "name" not in item or "latest_pain_level" not in item or "mindfulness_candidate" not in item:
            valid_schema = False
            break
        agent_dict[item["name"]] = {
            "latest_pain_level": item["latest_pain_level"],
            "mindfulness_candidate": item["mindfulness_candidate"]
        }
        
    if not valid_schema:
        details.append({"item": "检查对象 Schema", "score": 0, "max_score": 10, "passed": False, "reason": "部分对象缺失要求的 keys 或类型不符"})
    else:
        details.append({"item": "检查对象 Schema", "score": 10, "max_score": 10, "passed": True, "reason": "Schema 字段正确"})
        score += 10
        
    # Check Patients Coverage (20)
    agent_names = set(agent_dict.keys())
    gt_names = set(gt.keys())
    
    extra_names = agent_names - gt_names
    missing_names = gt_names - agent_names
    
    if len(extra_names) == 0 and len(missing_names) == 0:
        details.append({"item": "检查是否精准筛选 Residential 患者", "score": 20, "max_score": 20, "passed": True, "reason": "完美筛选，无遗漏和多余"})
        score += 20
    else:
        penalty = (len(extra_names) + len(missing_names)) * 2
        earned = max(0, 20 - penalty)
        details.append({"item": "检查是否精准筛选 Residential 患者", "score": earned, "max_score": 20, "passed": False, "reason": f"缺失 {len(missing_names)} 名，多出 {len(extra_names)} 名"})
        score += earned
        
    # Check latest_pain_level (20)
    correct_pain = 0
    common_names = agent_names.intersection(gt_names)
    for name in common_names:
        if agent_dict[name]["latest_pain_level"] == gt[name]["latest_pain_level"]:
            correct_pain += 1
            
    pain_score = int(20 * (correct_pain / len(gt_names))) if len(gt_names) > 0 else 0
    if pain_score == 20:
         details.append({"item": "验证最新疼痛值计算(基于时序)", "score": 20, "max_score": 20, "passed": True, "reason": "计算完全正确"})
    else:
         details.append({"item": "验证最新疼痛值计算(基于时序)", "score": pain_score, "max_score": 20, "passed": False, "reason": f"部分疼痛值不正确, 正确率: {correct_pain}/{len(gt_names)}"})
    score += pain_score
    
    # Check mindfulness_candidate (20)
    correct_mindful = 0
    for name in common_names:
        if bool(agent_dict[name]["mindfulness_candidate"]) == bool(gt[name]["mindfulness_candidate"]):
            correct_mindful += 1
            
    mindful_score = int(20 * (correct_mindful / len(gt_names))) if len(gt_names) > 0 else 0
    if mindful_score == 20:
         details.append({"item": "验证正念候选人标记(全局关键字搜索)", "score": 20, "max_score": 20, "passed": True, "reason": "标记完全正确"})
    else:
         details.append({"item": "验证正念候选人标记(全局关键字搜索)", "score": mindful_score, "max_score": 20, "passed": False, "reason": f"部分标记不正确, 正确率: {correct_mindful}/{len(gt_names)}"})
    score += mindful_score

    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": score, "details": details}, f, indent=4)

if __name__ == "__main__":
    main()
