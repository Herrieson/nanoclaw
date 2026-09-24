import os
import sys
import json
import csv
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

def calculate_ground_truth(workspace):
    roster_id_to_name = {}
    roster_name_to_id = {}
    roster_path = os.path.join(workspace, "registry", "roster.csv")
    if not os.path.exists(roster_path):
        return set(), {}, {}
        
    with open(roster_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            vid = row.get("Volunteer_ID")
            name = row.get("Full_Name")
            if vid and name:
                roster_id_to_name[vid] = name
                roster_name_to_id[name] = vid

    latest_approvals = {}
    approvals_dir = os.path.join(workspace, "approvals")
    for root, _, files in os.walk(approvals_dir):
        for file in files:
            if file.endswith(".json"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    vid = data.get("volunteer_id")
                    ts = data.get("timestamp")
                    if vid and ts is not None:
                        if vid not in latest_approvals or ts > latest_approvals[vid]["timestamp"]:
                            latest_approvals[vid] = data
                except Exception:
                    pass
    
    authorized_vids = set()
    for vid, data in latest_approvals.items():
        if data.get("status") == "APPROVED" and data.get("assigned_program") in ["Bird-Watching", "Ecology"]:
            authorized_vids.add(vid)

    unauthorized_names = set()
    authorized_hours_strict = {}
    authorized_hours_loose = {}
    target_keywords = ["bird-watching", "ecology"]
    logs_dir = os.path.join(workspace, "field_logs")
    
    for root, _, files in os.walk(logs_dir):
        for file in files:
            path = os.path.join(root, file)
            records = []
            if file.endswith(".csv"):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            participant = row.get("Name") or row.get("V_ID")
                            hours = row.get("Duration") or row.get("Hours_Logged")
                            task = row.get("Task") or row.get("Activity_Type")
                            if participant is not None:
                                records.append({"participant": participant, "hours": hours, "event": task})
                except Exception:
                    pass
            elif file.endswith(".json"):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            records.extend(data)
                except Exception:
                    pass
            
            for rec in records:
                task = str(rec.get("event", "")).lower()
                if not any(kw in task for kw in target_keywords):
                    continue
                
                raw_participant = str(rec.get("participant", ""))
                raw_hours = rec.get("hours", "")
                
                h_strict = 0.0
                h_loose = 0.0
                try:
                    val = float(raw_hours)
                    h_loose = val
                    if val > 0:
                        h_strict = val
                except ValueError:
                    pass
                
                vid = None
                name = None
                if raw_participant in roster_id_to_name:
                    vid = raw_participant
                    name = roster_id_to_name[vid]
                elif raw_participant in roster_name_to_id:
                    name = raw_participant
                    vid = roster_name_to_id[name]
                else:
                    name = raw_participant
                
                is_authorized = (vid is not None) and (vid in authorized_vids)
                
                if not is_authorized:
                    unauthorized_names.add(name)
                else:
                    if h_strict > 0:
                        authorized_hours_strict[name] = authorized_hours_strict.get(name, 0.0) + h_strict
                    if h_loose != 0:
                        authorized_hours_loose[name] = authorized_hours_loose.get(name, 0.0) + h_loose

    return sorted(list(unauthorized_names)), authorized_hours_strict, authorized_hours_loose

def score_dict(agent_dict, gt_dict):
    if not gt_dict:
        return 0.0
    correct = 0
    wrong = 0
    for k, v in agent_dict.items():
        if k in gt_dict:
            if isinstance(v, (int, float)) and abs(v - gt_dict[k]) < 1e-3:
                correct += 1
            else:
                wrong += 1
        else:
            wrong += 1
            
    ratio = max(0, correct - wrong * 0.5) / len(gt_dict)
    return min(1.0, ratio)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    # Check deliverable file existence
    report_path = os.path.join(workspace, "deliverables", "reconciliation_report.json")
    if not os.path.exists(report_path):
        score_details.append({"item": "检查交付物是否存在", "score": 0, "max_score": 15, "passed": False, "reason": "未找到 deliverables/reconciliation_report.json 文件"})
        # Write failure and exit
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": score_details}, f, indent=2)
        return
        
    score_details.append({"item": "检查交付物是否存在", "score": 5, "max_score": 5, "passed": True, "reason": "交付文件存在"})
    total_score += 5

    # Check valid JSON and structure
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            report_data = json.load(f)
            
        if not isinstance(report_data, dict):
            raise ValueError("Root is not a dictionary.")
            
        score_details.append({"item": "检查文件是否为合法 JSON 对象", "score": 5, "max_score": 5, "passed": True, "reason": "文件是合法的 JSON 对象"})
        total_score += 5
        
        agent_keys = set(report_data.keys())
        expected_keys = {"unauthorized_participants", "authorized_hours"}
        if agent_keys == expected_keys:
            score_details.append({"item": "检查 JSON 顶层结构", "score": 5, "max_score": 5, "passed": True, "reason": "正确包含要求的两个键且无冗余"})
            total_score += 5
        else:
            score_details.append({"item": "检查 JSON 顶层结构", "score": 0, "max_score": 5, "passed": False, "reason": f"键结构不符合要求，存在: {agent_keys}"})
            
    except Exception as e:
        score_details.append({"item": "检查文件是否为合法 JSON 对象", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败或结构错误: {e}"})
        report_data = {}

    if not report_data:
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # Calculate Ground Truth
    gt_unauthorized, gt_hours_strict, gt_hours_loose = calculate_ground_truth(workspace)
    
    # Validate unauthorized_participants (Max 35)
    agent_unauth = report_data.get("unauthorized_participants", [])
    if isinstance(agent_unauth, list):
        gt_set = set(gt_unauthorized)
        ag_set = set(agent_unauth)
        if not gt_set and not ag_set:
            jaccard = 1.0
        elif not gt_set:
            jaccard = 0.0
        else:
            intersect = gt_set.intersection(ag_set)
            union = gt_set.union(ag_set)
            jaccard = len(intersect) / len(union) if union else 0.0
            
        jaccard_score = int(jaccard * 30)
        total_score += jaccard_score
        
        is_sorted = (agent_unauth == sorted(agent_unauth))
        sort_score = 5 if is_sorted and jaccard > 0.5 else 0
        total_score += sort_score
        
        score_details.append({
            "item": "验证未经授权的参与者名单及排序",
            "score": jaccard_score + sort_score,
            "max_score": 35,
            "passed": (jaccard_score + sort_score) == 35,
            "reason": f"名单准确率 Jaccard 相似度为 {jaccard:.2f}；排序验证得分 {sort_score}/5"
        })
    else:
        score_details.append({"item": "验证未经授权的参与者名单", "score": 0, "max_score": 35, "passed": False, "reason": "unauthorized_participants 并非数组"})

    # Validate authorized_hours (Max 50)
    agent_hours = report_data.get("authorized_hours", {})
    if isinstance(agent_hours, dict):
        ratio_strict = score_dict(agent_hours, gt_hours_strict)
        ratio_loose = score_dict(agent_hours, gt_hours_loose)
        best_ratio = max(ratio_strict, ratio_loose)
        
        hours_score = int(best_ratio * 50)
        total_score += hours_score
        score_details.append({
            "item": "验证合法志愿者工时计算",
            "score": hours_score,
            "max_score": 50,
            "passed": hours_score == 50,
            "reason": f"字典键值匹配准确率为 {best_ratio * 100:.1f}% (允许负数或过滤负数的两种规则取最优)"
        })
    else:
        score_details.append({"item": "验证合法志愿者工时计算", "score": 0, "max_score": 50, "passed": False, "reason": "authorized_hours 并非对象"})

    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)

if __name__ == "__main__":
    main()
