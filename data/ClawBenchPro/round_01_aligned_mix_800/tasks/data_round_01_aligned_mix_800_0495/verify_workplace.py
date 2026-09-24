import os
import sys
import json
import csv
import glob
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

def calculate_ground_truth(workspace):
    # 1. Active Roster
    active_emps = {}
    roster_path = os.path.join(workspace, "schedules/roster/active_employees.csv")
    if not os.path.exists(roster_path):
        return None
    with open(roster_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            active_emps[row["emp_id"]] = float(row["base_weekly_hours"])

    # 2. Adjustments
    scheduled = active_emps.copy()
    adj_files = glob.glob(os.path.join(workspace, "schedules/adjustments/*.json"))
    for adj_file in adj_files:
        if "rejected" in os.path.basename(adj_file).lower():
            continue
        with open(adj_file, "r", encoding="utf-8") as f:
            try:
                adj_data = json.load(f)
                for emp, val in adj_data.items():
                    if emp in scheduled:
                        scheduled[emp] += float(val)
            except:
                pass

    # 3. Raw Logs Week 42
    actual_mins = {}
    week_42_dir = os.path.join(workspace, "raw_logs/week_42")
    for root, dirs, files in os.walk(week_42_dir):
        for file in files:
            if file.endswith(".jsonl"):
                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            data = json.loads(line)
                            if "emp_id" in data and "logged_minutes" in data:
                                emp = data["emp_id"]
                                actual_mins[emp] = actual_mins.get(emp, 0) + float(data["logged_minutes"])
                        except:
                            pass

    actual_hours = {emp: mins / 60.0 for emp, mins in actual_mins.items()}

    # 4. Rules
    expected_ghosts = set([emp for emp in actual_hours if emp not in active_emps])
    
    expected_violators = set()
    for emp in active_emps:
        act = actual_hours.get(emp, 0.0)
        sch = scheduled.get(emp, 0.0)
        if act > sch * 1.1:
            expected_violators.add(emp)

    expected_valid = {}
    for emp in active_emps:
        expected_valid[emp] = {
            "scheduled_hours": scheduled.get(emp, 0.0),
            "actual_hours": actual_hours.get(emp, 0.0)
        }

    return {
        "valid_payroll": expected_valid,
        "ghost_employees": expected_ghosts,
        "overtime_violators": expected_violators
    }

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    details = []
    total_score = 0

    # Check file existence
    json_path = os.path.join(workspace, "deliverables", "payroll_final.json")
    txt_path = os.path.join(workspace, "deliverables", "audit_summary.txt")

    if not os.path.exists(json_path):
        details.append({"item": "Deliverable JSON存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 deliverables/payroll_final.json"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": details}, f)
        return
        
    details.append({"item": "Deliverable JSON存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件结构正确"})
    total_score += 10

    # Parse Agent JSON
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            agent_data = json.load(f)
    except Exception as e:
        details.append({"item": "JSON 格式有效性", "score": 0, "max_score": 70, "passed": False, "reason": f"解析失败: {e}"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f)
        return

    gt = calculate_ground_truth(workspace)
    if not gt:
        details.append({"item": "Ground Truth 计算", "score": 0, "max_score": 0, "passed": False, "reason": "无法读取沙盒原始数据生成答案对比"})
        return

    # Check Ghosts
    agent_ghosts = set(agent_data.get("ghost_employees", []))
    if agent_ghosts == gt["ghost_employees"]:
        details.append({"item": "Ghost Employees 识别准确", "score": 20, "max_score": 20, "passed": True, "reason": "成功识别所有幽灵打卡并过滤week_41"})
        total_score += 20
    else:
        details.append({"item": "Ghost Employees 识别准确", "score": 0, "max_score": 20, "passed": False, "reason": f"差异. Agent: {agent_ghosts}, GT: {gt['ghost_employees']}"})

    # Check Violators
    agent_violators = set(agent_data.get("overtime_violators", []))
    if agent_violators == gt["overtime_violators"]:
        details.append({"item": "Overtime Violators 计算准确", "score": 20, "max_score": 20, "passed": True, "reason": "精确拦截被驳回的调休记录并计算10%溢出阈值"})
        total_score += 20
    else:
        details.append({"item": "Overtime Violators 计算准确", "score": 0, "max_score": 20, "passed": False, "reason": f"差异. Agent: {agent_violators}, GT: {gt['overtime_violators']}"})

    # Check Valid Payroll (Precision)
    agent_valid = agent_data.get("valid_payroll", {})
    correct_valid = 0
    total_valid = len(gt["valid_payroll"])
    
    if total_valid > 0 and isinstance(agent_valid, dict):
        for emp, vals in gt["valid_payroll"].items():
            a_vals = agent_valid.get(emp, {})
            try:
                if math.isclose(a_vals.get("scheduled_hours", -1), vals["scheduled_hours"], abs_tol=0.01) and \
                   math.isclose(a_vals.get("actual_hours", -1), vals["actual_hours"], abs_tol=0.01):
                    correct_valid += 1
            except:
                pass
        
        valid_score = int(30 * (correct_valid / total_valid))
        if valid_score == 30:
            details.append({"item": "合规工时基础池精确度", "score": 30, "max_score": 30, "passed": True, "reason": "所有活跃员工的排班与实际计算全部正确"})
        else:
            details.append({"item": "合规工时基础池精确度", "score": valid_score, "max_score": 30, "passed": False, "reason": f"部分员工数值计算错误，正确率: {correct_valid}/{total_valid}"})
        total_score += valid_score
    else:
        details.append({"item": "合规工时基础池精确度", "score": 0, "max_score": 30, "passed": False, "reason": "valid_payroll 格式错误或为空"})

    # Check Audit Summary LLM
    if os.path.exists(txt_path):
        with open(txt_path, "r", encoding="utf-8") as f:
            summary_content = f.read()
        
        prompt = (
            "Evaluate if the summary adopts the persona of a stressed, high-blood-pressure 54-year-old female bookkeeper "
            "scolding interns, AND clearly summarizes the count or lists the ghost employees and overtime violators."
        )
        passed = llm_judge_content(prompt, summary_content)
        if passed:
            details.append({"item": "审计总结报告要求与语气", "score": 20, "max_score": 20, "passed": True, "reason": "符合角色扮演且包含关键数量信息"})
            total_score += 20
        else:
            details.append({"item": "审计总结报告要求与语气", "score": 0, "max_score": 20, "passed": False, "reason": "未达标（缺失数据或缺少暴躁语气）"})
    else:
        details.append({"item": "审计总结报告要求与语气", "score": 0, "max_score": 20, "passed": False, "reason": "文件未生成"})

    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    verify()
