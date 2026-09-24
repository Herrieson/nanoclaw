import os
import sys
import json
import httpx
import glob
import re
from openai import OpenAI

# ==========================================
# 强制 API 规范 (LLM 验证探针初始化)
# ==========================================
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
    """用于检测非结构化文本的统一接口"""
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

# ==========================================
# 核心验证逻辑
# ==========================================

def calculate_ground_truth(workspace):
    """
    现场动态计算真值，确保绝对的准确性。
    重走一遍正确的业务逻辑：授权鉴定 -> 穿越日志 -> 时长与违规者统计 -> 映射真实姓名。
    """
    # 1. 寻找真正的授权名单
    true_auth_emp_ids = set()
    policy_dir = os.path.join(workspace, "case_files/auth_policies")
    for p_file in glob.glob(f"{policy_dir}/*.json"):
        try:
            with open(p_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                # 严格条件：case_id 匹配且 approved 严格等于布尔值 True
                if data.get("case_id") == "2024-CV-882" and data.get("approved") is True:
                    true_auth_emp_ids.update(data.get("authorized_emp_ids", []))
        except Exception:
            continue

    # 2. 解析碎片的服务器日志
    billable_mins = 0
    unauth_emp_ids = set()
    log_dir = os.path.join(workspace, "server_logs")
    log_pattern = re.compile(r"CASE:\s*(\S+)\s*\|\s*USER:\s*(\S+)\s*\|\s*DURATION:\s*(\d+)m\s*\|\s*STATUS:\s*(\S+)")
    
    for log_file in glob.glob(f"{log_dir}/**/*.log", recursive=True):
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    match = log_pattern.search(line)
                    if match:
                        case_id, user_id, duration, status = match.groups()
                        if case_id == "2024-CV-882":
                            if user_id in true_auth_emp_ids:
                                if status == "SUCCESS":
                                    billable_mins += int(duration)
                            else:
                                unauth_emp_ids.add(user_id)
        except Exception:
            continue

    # 3. 映射违规者真实姓名
    unauth_names = set()
    hr_dir = os.path.join(workspace, "hr_records/employees")
    for emp_id in unauth_emp_ids:
        emp_file = os.path.join(hr_dir, f"{emp_id}.json")
        try:
            with open(emp_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "full_name" in data:
                    unauth_names.add(data["full_name"])
        except Exception:
            continue

    return billable_mins, unauth_names

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    total_score = 0
    details = []
    
    report_path = os.path.join(workspace, "audit_reports/final_report.json")
    
    # 验证项 1: 文件是否存在及 JSON 格式合法性 (15分)
    if not os.path.exists(report_path):
        details.append({"item": "检查最终报告文件是否存在", "score": 0, "max_score": 15, "passed": False, "reason": "未找到 audit_reports/final_report.json 文件"})
        # 严重错误，直接输出
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": 0, "details": details}, f, indent=2)
        return

    try:
        with open(report_path, "r", encoding="utf-8") as f:
            report_data = json.load(f)
        details.append({"item": "检查最终报告文件是否存在", "score": 15, "max_score": 15, "passed": True, "reason": "文件存在且是合法的 JSON"})
    except json.JSONDecodeError:
        details.append({"item": "检查最终报告文件是否存在", "score": 0, "max_score": 15, "passed": False, "reason": "文件存在但不是合法的 JSON 格式"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": 15, "details": details}, f, indent=2)
        return

    # 验证项 2: Schema 结构验证 (15分)
    has_unauth = "unauthorized_users" in report_data
    has_billable = "total_billable_minutes" in report_data
    is_list = isinstance(report_data.get("unauthorized_users"), list)
    is_int = isinstance(report_data.get("total_billable_minutes"), int)
    extra_keys = set(report_data.keys()) - {"unauthorized_users", "total_billable_minutes"}
    
    schema_score = 0
    schema_reason = []
    if has_unauth and is_list:
        schema_score += 5
    else:
        schema_reason.append("缺少 unauthorized_users 字段或非列表格式")
        
    if has_billable and is_int:
        schema_score += 5
    else:
        schema_reason.append("缺少 total_billable_minutes 字段或非整数格式")
        
    if len(extra_keys) == 0:
        schema_score += 5
    else:
        schema_reason.append(f"存在多余的非法字段(幻觉): {extra_keys}")
        
    details.append({"item": "JSON Schema及字段完整性验证", "score": schema_score, "max_score": 15, "passed": schema_score == 15, "reason": "; ".join(schema_reason) if schema_reason else "Schema 完全符合要求"})
    
    # 获取真值
    true_billable, true_unauth_names = calculate_ground_truth(workspace)
    
    # 验证项 3: 计费时长计算准确度 (35分)
    agent_billable = report_data.get("total_billable_minutes", -1)
    if agent_billable == true_billable:
        details.append({"item": "核对总计费时长计算是否精准", "score": 35, "max_score": 35, "passed": True, "reason": f"精确匹配，值为 {true_billable} 分钟"})
    else:
        details.append({"item": "核对总计费时长计算是否精准", "score": 0, "max_score": 35, "passed": False, "reason": f"计算错误，预期为 {true_billable}，实际提交为 {agent_billable}。可能是未过滤 SUCCESS 或未过滤真实授权名单。"})

    # 验证项 4: 违规人员名单准确度 (35分)
    agent_unauth_raw = report_data.get("unauthorized_users", [])
    if not isinstance(agent_unauth_raw, list):
        agent_unauth_raw = []
        
    agent_unauth_names = set(agent_unauth_raw)
    
    # 梯度计分：全对35分。漏报/误报按比例扣分。未去重扣除5分。
    list_score = 35
    list_reason = []
    
    missing_names = true_unauth_names - agent_unauth_names
    extra_names = agent_unauth_names - true_unauth_names
    
    if len(agent_unauth_raw) != len(agent_unauth_names):
        list_score -= 5
        list_reason.append("名单未去重")
        
    if missing_names:
        penalty = len(missing_names) * 2  # 每个漏报扣2分
        list_score -= penalty
        list_reason.append(f"漏报了 {len(missing_names)} 名违规者")
        
    if extra_names:
        penalty = len(extra_names) * 3  # 每个误报/捏造扣3分
        list_score -= penalty
        list_reason.append(f"误报或捏造了 {len(extra_names)} 个无辜人员/错误工号")
        
    # 如果列表完全偏离或为空，兜底不能低于 0 分
    list_score = max(0, list_score)
    if list_score == 35:
        list_reason = ["违规者名单完全精准，真实姓名映射正确且已去重"]
        
    # [调用大模型探针]：检查 agent 是否在 unauthorized_users 中混入了废话或非人名的解释性语句。
    # 即使代码验证集合通过，也要防范如 "Name: John Doe", "I found Alice" 这种格式。
    if list_score > 0 and agent_unauth_raw:
        sample_str = json.dumps(agent_unauth_raw[:5]) # 抽样前5个
        llm_prompt = "Examine this JSON list. Does it contain ONLY pure human names (like 'John Smith_1', 'Alice Doe_5') without ANY conversational filler, keys like 'Name:', or explanatory text?"
        is_clean = llm_judge_content(llm_prompt, sample_str)
        if not is_clean:
            list_score -= 10
            list_score = max(0, list_score)
            list_reason.append("大模型判定：名单列表中混入了非规范的自然语言解释或多余前缀，格式不够严谨。")

    details.append({"item": "违规人员名单及姓名映射准确度", "score": list_score, "max_score": 35, "passed": list_score == 35, "reason": "; ".join(list_reason)})

    # 计算总分
    total_score = sum(d["score"] for d in details)
    
    # 写入结果
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
