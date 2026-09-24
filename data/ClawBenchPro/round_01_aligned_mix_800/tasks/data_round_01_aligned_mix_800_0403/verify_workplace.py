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

def extract_weight(raw_str):
    m = re.match(r'^([\d\.]+)\s*(kg|lbs)?$', str(raw_str).strip(), re.IGNORECASE)
    if not m:
        return 0.0
    val = float(m.group(1))
    unit = m.group(2).lower() if m.group(2) else 'lbs'
    if unit == 'kg':
        val *= 2.2
    return val

def compute_ground_truth(workspace):
    roster_path = os.path.join(workspace, "roster_sys_export_latest.jsonl")
    enrolled_students = set()
    if os.path.exists(roster_path):
        with open(roster_path, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip(): continue
                record = json.loads(line)
                if record.get("course_code") == "AP_ENV_SCI" and record.get("status") == "ENROLLED":
                    enrolled_students.add(record.get("student_name"))
    
    total_recycling = 0.0
    total_compost = 0.0
    total_landfill = 0.0
    intruders = set()
    
    submissions_dir = os.path.join(workspace, "submissions")
    if os.path.exists(submissions_dir):
        for root, dirs, files in os.walk(submissions_dir):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                except:
                    continue
                
                if "ZWW-2023-FALL" not in content:
                    continue
                
                student = None
                rec = comp = land = 0.0
                
                if file.endswith('.json'):
                    try:
                        data = json.loads(content)
                        student = data.get("metadata", {}).get("student_name")
                        rec = extract_weight(data.get("log", {}).get("recycling", ""))
                        comp = extract_weight(data.get("log", {}).get("compost", ""))
                        land = extract_weight(data.get("log", {}).get("landfill", ""))
                    except: pass
                elif file.endswith('.csv'):
                    try:
                        lines = content.strip().split('\n')
                        reader = list(csv.reader(lines))
                        for row in reader:
                            if len(row) >= 2:
                                if row[0] == "Student": student = row[1]
                                elif row[0] == "Recycling": rec = extract_weight(row[1])
                                elif row[0] == "Compost": comp = extract_weight(row[1])
                                elif row[0] == "Landfill": land = extract_weight(row[1])
                    except: pass
                elif file.endswith('.txt'):
                    try:
                        lines = content.strip().split('\n')
                        for line in lines:
                            if line.startswith("Name:"):
                                student = line.replace("Name:", "").strip()
                            elif line.startswith("- recycling:"):
                                rec = extract_weight(line.replace("- recycling:", "").strip())
                            elif line.startswith("- compost:"):
                                comp = extract_weight(line.replace("- compost:", "").strip())
                            elif line.startswith("- landfill:"):
                                land = extract_weight(line.replace("- landfill:", "").strip())
                    except: pass
                
                if not student:
                    continue
                
                if student in enrolled_students:
                    total_recycling += rec
                    total_compost += comp
                    total_landfill += land
                else:
                    intruders.add(student)
                    
    return {
        "total_recycling_lbs": round(total_recycling, 2),
        "total_compost_lbs": round(total_compost, 2),
        "total_landfill_lbs": round(total_landfill, 2),
        "intruders": sorted(list(intruders))
    }

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    score_details = []
    total_score = 0
    
    # 1. 检查目录结构
    deliv_dir = os.path.join(workspace, "deliverables")
    if os.path.isdir(deliv_dir):
        total_score += 10
        score_details.append({"item": "检查 deliverables 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
    else:
        score_details.append({"item": "检查 deliverables 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录不存在"})
    
    # 2. 检查输出文件及格式
    board_summary_path = os.path.join(deliv_dir, "board_summary.json")
    agent_data = None
    if os.path.exists(board_summary_path):
        try:
            with open(board_summary_path, 'r', encoding='utf-8') as f:
                agent_data = json.load(f)
            total_score += 10
            score_details.append({"item": "检查 board_summary.json 是否存在且格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在且为合法 JSON"})
        except Exception as e:
            score_details.append({"item": "检查 board_summary.json 是否存在且格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"文件解析失败: {e}"})
    else:
        score_details.append({"item": "检查 board_summary.json 是否存在且格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
    
    # 若存在合法数据，进行结果比对
    if agent_data is not None:
        truth = compute_ground_truth(workspace)
        
        # 3. 检查没有多余字段
        expected_keys = {"total_recycling_lbs", "total_compost_lbs", "total_landfill_lbs", "intruders"}
        agent_keys = set(agent_data.keys())
        if agent_keys == expected_keys:
            total_score += 5
            score_details.append({"item": "检查无捏造字段", "score": 5, "max_score": 5, "passed": True, "reason": "字段与要求完全匹配"})
        else:
            score_details.append({"item": "检查无捏造字段", "score": 0, "max_score": 5, "passed": False, "reason": f"存在多余或缺失字段: {agent_keys ^ expected_keys}"})
        
        # 4. 精准比对三个重量 (每个 15 分)
        for key in ["total_recycling_lbs", "total_compost_lbs", "total_landfill_lbs"]:
            agent_val = agent_data.get(key)
            truth_val = truth[key]
            
            if type(agent_val) in (int, float) and abs(agent_val - truth_val) <= 0.01:
                total_score += 15
                score_details.append({"item": f"精准计算 {key}", "score": 15, "max_score": 15, "passed": True, "reason": f"计算结果 {agent_val} 与答案 {truth_val} 一致"})
            else:
                score_details.append({"item": f"精准计算 {key}", "score": 0, "max_score": 15, "passed": False, "reason": f"计算错误或格式不对，期望: {truth_val}, 实际: {agent_val}"})
        
        # 5. 精准比对 intruders 名单 (30 分)
        agent_intruders = agent_data.get("intruders")
        truth_intruders = truth["intruders"]
        
        if isinstance(agent_intruders, list) and agent_intruders == truth_intruders:
            total_score += 30
            score_details.append({"item": "精准提取并排序 intruders", "score": 30, "max_score": 30, "passed": True, "reason": "名单完全正确且按字母序排列"})
        else:
            if isinstance(agent_intruders, list) and set(agent_intruders) == set(truth_intruders):
                total_score += 15
                score_details.append({"item": "精准提取并排序 intruders", "score": 15, "max_score": 30, "passed": False, "reason": "名单集合正确，但未按字母序排列"})
            else:
                score_details.append({"item": "精准提取并排序 intruders", "score": 0, "max_score": 30, "passed": False, "reason": "名单不正确"})
    else:
        # 分数清零逻辑由之前未加分处理
        score_details.append({"item": "跳过数据比对", "score": 0, "max_score": 80, "passed": False, "reason": "JSON无法解析"})

    # 写入得分报告
    report = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
