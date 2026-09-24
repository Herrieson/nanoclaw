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
try:
    client = OpenAI(
        api_key=MOCK_API_KEY,
        base_url=MOCK_API_BASE,
        http_client=http_client
    )
except Exception:
    pass

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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    score_details = []
    total_score = 0
    
    audit_dir = os.path.join(workspace, "audit_report")
    clean_csv_path = os.path.join(audit_dir, "clean_attendance.csv")
    unauth_txt_path = os.path.join(audit_dir, "unauthorized.txt")
    
    # 1. 检查目录 (10分)
    if os.path.isdir(audit_dir):
        score_details.append({"item": "检查结果目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "audit_report 目录存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查结果目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "audit_report 目录不存在"})
        
    # 2. 检查输出文件是否存在 (10分)
    files_exist = os.path.isfile(clean_csv_path) and os.path.isfile(unauth_txt_path)
    if files_exist:
        score_details.append({"item": "检查输出双文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "所需文件均存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查输出双文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "缺少一个或多个目标文件"})

    if files_exist:
        # 3. 解析并检查 clean_attendance.csv (40分)
        # 必须仅包含 PA-101, PA-202, PA-303, PA-505 及其正确部门
        expected_valid_employees = {
            "PA-101": "HR-Core",
            "PA-202": "IT-Support",
            "PA-303": "Exec-Admin",
            "PA-505": "HR-Core"
        }
        actual_valid_employees = {}
        csv_valid = True
        try:
            with open(clean_csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader, None)
                for row in reader:
                    if len(row) >= 2:
                        row_str = " ".join(row).upper()
                        # 尝试找出 ID
                        for eid in expected_valid_employees.keys():
                            if eid in row_str:
                                actual_valid_employees[eid] = row_str
        except Exception:
            csv_valid = False

        if csv_valid:
            matched_count = 0
            correct_dept_count = 0
            false_positive = False

            # 严查是否混入了未授权或不存在的人员
            with open(clean_csv_path, 'r', encoding='utf-8') as f:
                content = f.read().upper()
                if "PA-999" in content or "PA-888" in content:
                    false_positive = True

            for eid, expected_dept in expected_valid_employees.items():
                if eid in actual_valid_employees:
                    matched_count += 1
                    if expected_dept.upper() in actual_valid_employees[eid]:
                        correct_dept_count += 1

            if false_positive:
                score_details.append({"item": "核对合法人员名单(严格)", "score": 0, "max_score": 40, "passed": False, "reason": "严重错误：未授权人员被包含在合法名单中"})
            elif matched_count == 4 and correct_dept_count == 4:
                score_details.append({"item": "核对合法人员名单(严格)", "score": 40, "max_score": 40, "passed": True, "reason": "合法人员提取且部门匹配完全正确"})
                total_score += 40
            else:
                partial_score = (matched_count * 5) + (correct_dept_count * 5)
                score_details.append({"item": "核对合法人员名单(严格)", "score": partial_score, "max_score": 40, "passed": False, "reason": f"部分匹配：找到 {matched_count}/4 员工，{correct_dept_count}/4 部门正确"})
                total_score += partial_score
        else:
            score_details.append({"item": "核对合法人员名单(严格)", "score": 0, "max_score": 40, "passed": False, "reason": "无法解析 CSV 文件"})

        # 4. 解析并检查 unauthorized.txt (25分)
        # 必须包含 PA-999, PA-888
        try:
            with open(unauth_txt_path, 'r', encoding='utf-8') as f:
                unauth_text = f.read().upper()
            
            has_999 = "PA-999" in unauth_text and "HOUSE" in unauth_text
            has_888 = "PA-888" in unauth_text and "CHAD" in unauth_text
            has_valid = any(vid in unauth_text for vid in expected_valid_employees.keys())

            if has_valid:
                score_details.append({"item": "核对未授权人员名单", "score": 0, "max_score": 25, "passed": False, "reason": "严重错误：合法员工被列入黑名单"})
            elif has_999 and has_888:
                score_details.append({"item": "核对未授权人员名单", "score": 25, "max_score": 25, "passed": True, "reason": "成功提取所有未授权访客及姓名"})
                total_score += 25
            elif has_999 or has_888:
                score_details.append({"item": "核对未授权人员名单", "score": 10, "max_score": 25, "passed": False, "reason": "仅提取了部分未授权访客"})
                total_score += 10
            else:
                score_details.append({"item": "核对未授权人员名单", "score": 0, "max_score": 25, "passed": False, "reason": "未能提取未授权访客"})
        except Exception:
            score_details.append({"item": "核对未授权人员名单", "score": 0, "max_score": 25, "passed": False, "reason": "无法读取 txt 文件"})

        # 5. LLM 格式检查 (15分)
        try:
            with open(unauth_txt_path, 'r', encoding='utf-8') as f:
                unauth_content_for_llm = f.read()
            prompt = "Please evaluate if this unauthorized visitors file is cleanly and beautifully organized. It should clearly list the IDs and Names of unauthorized people, without being a messy copy-paste of raw logs. Respond YES if it looks well-organized and professional, NO otherwise."
            if llm_judge_content(prompt, unauth_content_for_llm):
                score_details.append({"item": "大模型检查排版美观度", "score": 15, "max_score": 15, "passed": True, "reason": "LLM 判定未授权人员名单排版整洁"})
                total_score += 15
            else:
                score_details.append({"item": "大模型检查排版美观度", "score": 0, "max_score": 15, "passed": False, "reason": "LLM 判定文件排版杂乱或仅为原始日志堆砌"})
        except Exception:
            score_details.append({"item": "大模型检查排版美观度", "score": 0, "max_score": 15, "passed": False, "reason": "读取文件供 LLM 检测时失败"})

    # 输出结果
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
