import os
import sys
import json
import csv
import re
from datetime import datetime
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
    volunteers = {}
    for i in range(5):
        path = os.path.join(workspace, f"auth_system/volunteers_db/db_shard_{i}.json")
        with open(path, "r") as f:
            data = json.load(f)
            for v in data["data"]:
                volunteers[v["id"]] = v
                
    approved_ids = set()
    roster_path = os.path.join(workspace, "event_management/approved_rosters/eco_cleanup_2023.txt")
    with open(roster_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                approved_ids.add(line)
                
    true_whitelist_ids = {vid for vid in approved_ids if volunteers[vid]["status"] == "Active"}
    
    suspect_names = set()
    details = {}
    
    field_dir = os.path.join(workspace, "field_data")
    for root, dirs, files in os.walk(field_dir):
        for file in files:
            if "draft" in file or "rejected" in file or "backup" in file:
                continue
            path = os.path.join(root, file)
            records = []
            if file.endswith(".csv"):
                with open(path, "r") as f:
                    reader = csv.reader(f)
                    next(reader)
                    records = list(reader)
            elif file.endswith(".tsv"):
                with open(path, "r") as f:
                    reader = csv.reader(f, delimiter='\t')
                    next(reader)
                    records = list(reader)
            elif file.endswith(".log"):
                with open(path, "r") as f:
                    for line in f:
                        if "=> Duration:" in line:
                            vid_match = re.search(r"ID:\s*(VOL_\d+)", line)
                            name_match = re.search(r"Name:\s*([^ ]+)\s*=>", line)
                            mins_match = re.search(r"Duration:\s*(\d+)", line)
                            if vid_match and name_match and mins_match:
                                records.append({
                                    "vid": vid_match.group(1),
                                    "name": name_match.group(1).strip(),
                                    "mins": int(mins_match.group(1))
                                })
                                
            for rec in records:
                if file.endswith(".csv") or file.endswith(".tsv"):
                    vid = rec[1]
                    name = rec[2].strip()
                    st = rec[3]
                    et = rec[4]
                    fmt = "%H:%M"
                    t1 = datetime.strptime(st, fmt)
                    t2 = datetime.strptime(et, fmt)
                    mins = (t2 - t1).total_seconds() / 60.0
                else:
                    vid = rec["vid"]
                    name = rec["name"]
                    mins = rec["mins"]
                    
                if vid not in true_whitelist_ids:
                    suspect_names.add(name)
                else:
                    if mins <= 720:
                        details[name] = details.get(name, 0) + (mins / 60.0)
                        
    total_hours = sum(details.values())
    sorted_details = {k: details[k] for k in sorted(details.keys())}
    return suspect_names, total_hours, sorted_details

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0

    suspects_path = os.path.join(workspace, "suspects.txt")
    report_path = os.path.join(workspace, "deliverables", "final_report.json")

    # 1. 检查目标文件是否存在 (10分)
    suspects_exist = os.path.exists(suspects_path)
    report_exist = os.path.exists(report_path)
    if suspects_exist and report_exist:
        score_details.append({"item": "文件结构检查", "score": 10, "max_score": 10, "passed": True, "reason": "所有要求的目标文件存在"})
        total_score += 10
    else:
        score_details.append({"item": "文件结构检查", "score": 0, "max_score": 10, "passed": False, "reason": "缺失目标文件"})
        
    if not (suspects_exist and report_exist):
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # 生成真实答案
    gt_suspect_names, gt_total_hours, gt_details = get_ground_truth(workspace)

    # 2. 解析 final_report.json (10分)
    try:
        with open(report_path, "r") as f:
            report_data = json.load(f)
        if "total_hours" in report_data and "details" in report_data and isinstance(report_data["details"], dict):
            score_details.append({"item": "JSON格式与模式验证", "score": 10, "max_score": 10, "passed": True, "reason": "final_report.json 格式正确"})
            total_score += 10
        else:
            score_details.append({"item": "JSON格式与模式验证", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 缺少关键字段或类型不符"})
            report_data = None
    except Exception as e:
        score_details.append({"item": "JSON格式与模式验证", "score": 0, "max_score": 10, "passed": False, "reason": f"无法解析 JSON: {e}"})
        report_data = None

    # 3. 对比 suspects.txt 准确度 (30分)
    try:
        with open(suspects_path, "r") as f:
            agent_suspects = {line.strip() for line in f if line.strip()}
        
        intersect = agent_suspects.intersection(gt_suspect_names)
        if agent_suspects == gt_suspect_names:
            score_details.append({"item": "嫌疑人名单精准验证", "score": 30, "max_score": 30, "passed": True, "reason": "嫌疑人名单完全一致"})
            total_score += 30
        else:
            precision = len(intersect) / len(agent_suspects) if agent_suspects else 0
            recall = len(intersect) / len(gt_suspect_names) if gt_suspect_names else 0
            score = int(30 * (precision * recall))
            score_details.append({"item": "嫌疑人名单精准验证", "score": score, "max_score": 30, "passed": False, "reason": f"名单有误，精准度:{precision:.2f}, 召回率:{recall:.2f}"})
            total_score += score
    except Exception as e:
        score_details.append({"item": "嫌疑人名单精准验证", "score": 0, "max_score": 30, "passed": False, "reason": f"读取 suspects.txt 失败: {e}"})

    # 4. 对比 final_report.json 的计算结果 (30分)
    if report_data:
        try:
            agent_total = float(report_data["total_hours"])
            agent_details = report_data["details"]
            
            # Total hours 验证 (15分)
            if abs(agent_total - gt_total_hours) < 0.1:
                score_details.append({"item": "总工时计算验证", "score": 15, "max_score": 15, "passed": True, "reason": "total_hours 误差极小，计算完全正确"})
                total_score += 15
            else:
                score_details.append({"item": "总工时计算验证", "score": 0, "max_score": 15, "passed": False, "reason": f"total_hours 计算错误。GT:{gt_total_hours}, Agent:{agent_total}"})
                
            # Details 字典验证 (15分)
            keys_sorted = list(agent_details.keys()) == sorted(agent_details.keys())
            if keys_sorted:
                diffs = []
                for k, v in gt_details.items():
                    if k not in agent_details:
                        diffs.append(k)
                    elif abs(float(agent_details[k]) - v) >= 0.1:
                        diffs.append(k)
                if not diffs and len(agent_details) == len(gt_details):
                    score_details.append({"item": "单人详细工时计算验证", "score": 15, "max_score": 15, "passed": True, "reason": "字典按字母序排列，且所有人员工时核对无误"})
                    total_score += 15
                else:
                    score_details.append({"item": "单人详细工时计算验证", "score": 0, "max_score": 15, "passed": False, "reason": "个别人员工时计算错误或缺失"})
            else:
                score_details.append({"item": "单人详细工时计算验证", "score": 0, "max_score": 15, "passed": False, "reason": "字典未按照名字字母顺序进行排序"})
        except Exception as e:
            score_details.append({"item": "计算结果提取异常", "score": 0, "max_score": 30, "passed": False, "reason": f"解析数值失败: {e}"})
    else:
        score_details.append({"item": "最终结果验证", "score": 0, "max_score": 30, "passed": False, "reason": "JSON未正确读取，跳过验证"})

    # 5. LLM 非结构化判定 (20分)
    try:
        with open(suspects_path, "r") as f:
            suspects_content = f.read()[:500] # 取前500字供模型判断即可
        prompt = "Does the following file content consist STRICTLY and ONLY of isolated names separated by newlines? It MUST NOT contain any conversational text, introductory sentences (e.g., 'Here are the suspects:'), bullet symbols (e.g., '-', '*'), or numbering (e.g., '1.'). Answer YES if it is pure names, NO if there is any other text or formatting."
        is_pure = llm_judge_content(prompt, suspects_content)
        if is_pure:
            score_details.append({"item": "LLM 语义内容校验", "score": 20, "max_score": 20, "passed": True, "reason": "suspects.txt 内容纯净，无多余寒暄及废话文本"})
            total_score += 20
        else:
            score_details.append({"item": "LLM 语义内容校验", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定 suspects.txt 包含无关引导语、符号或寒暄"})
    except Exception as e:
        score_details.append({"item": "LLM 语义内容校验", "score": 0, "max_score": 20, "passed": False, "reason": f"大模型验证出错: {e}"})

    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)

if __name__ == "__main__":
    verify()
