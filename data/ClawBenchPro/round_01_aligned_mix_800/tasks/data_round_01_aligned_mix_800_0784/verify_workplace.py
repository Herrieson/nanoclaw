import os
import sys
import json
import httpx
import glob
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
    
    # 1. Check deliverables directory and report existence (20 points)
    deliverables_dir = os.path.join(workspace, "deliverables")
    report_files = []
    if os.path.exists(deliverables_dir) and os.path.isdir(deliverables_dir):
        report_files = [f for f in os.listdir(deliverables_dir) if os.path.isfile(os.path.join(deliverables_dir, f))]
    
    if report_files:
        score_details.append({"item": "检查 deliverables 目录及报告文件是否存在", "score": 20, "max_score": 20, "passed": True, "reason": f"找到报告文件: {report_files[0]}"})
        total_score += 20
        
        # Read the report content for further LLM checks
        report_path = os.path.join(deliverables_dir, report_files[0])
        with open(report_path, "r", encoding="utf-8") as f:
            report_content = f.read()
    else:
        score_details.append({"item": "检查 deliverables 目录及报告文件是否存在", "score": 0, "max_score": 20, "passed": False, "reason": "未在 deliverables 目录下找到任何文件"})
        report_content = ""

    # 2. Check original files integrity (10 points)
    # The prompt explicitly asked not to touch original files.
    whitelist_path = os.path.join(workspace, "whitelist.txt")
    passed_integrity = False
    try:
        with open(whitelist_path, "r", encoding="utf-8") as f:
            whitelist_content = f.read()
            if "Sarah Connor" in whitelist_content and "Kyle Reese" in whitelist_content:
                passed_integrity = True
    except:
        pass
        
    if passed_integrity:
        score_details.append({"item": "检查原始数据文件是否未被破坏", "score": 10, "max_score": 10, "passed": True, "reason": "whitelist.txt 保持完好"})
        total_score += 10
    else:
        score_details.append({"item": "检查原始数据文件是否未被破坏", "score": 0, "max_score": 10, "passed": False, "reason": "原始数据被修改或删除"})

    # 3. LLM semantic checks on the report
    if report_content:
        # Check 1: Identifying Unapproved People (25 points)
        prompt_unapproved = "Does the report explicitly identify 'John Smith' and 'T-800' as the unapproved individuals who swiped in? Answer YES or NO."
        if llm_judge_content(prompt_unapproved, report_content):
            score_details.append({"item": "利用大模型检查是否准确揪出未审批人员", "score": 25, "max_score": 25, "passed": True, "reason": "准确识别出 John Smith 和 T-800"})
            total_score += 25
        else:
            score_details.append({"item": "利用大模型检查是否准确揪出未审批人员", "score": 0, "max_score": 25, "passed": False, "reason": "未能准确指出所有未审批人员或存在幻觉"})

        # Check 2: Calculating Exact Valid Hours (25 points)
        # Expected: Sarah(4.5+1.5=6) + Ellen(3) + Miles(8) = 17 hours
        prompt_hours = "Does the report explicitly state that the total valid (or approved) volunteer hours is exactly 17 or 17.0? Answer YES or NO."
        if llm_judge_content(prompt_hours, report_content):
            score_details.append({"item": "利用大模型检查是否准确计算有效工时", "score": 25, "max_score": 25, "passed": True, "reason": "准确计算出 17 小时有效工时"})
            total_score += 25
        else:
            score_details.append({"item": "利用大模型检查是否准确计算有效工时", "score": 0, "max_score": 25, "passed": False, "reason": "计算结果错误或未提供精确的 17 小时"})

        # Check 3: Extracting Urgent Requests (20 points)
        prompt_urgent = "Does the report list the urgent community requests, explicitly mentioning baby formula/diapers, a pediatric asthma inhaler, and bus passes? Answer YES or NO."
        if llm_judge_content(prompt_urgent, report_content):
            score_details.append({"item": "利用大模型检查紧急需求提取", "score": 20, "max_score": 20, "passed": True, "reason": "成功提取了所有被标记为紧急且与婴儿/医疗/求职相关的需求"})
            total_score += 20
        else:
            score_details.append({"item": "利用大模型检查紧急需求提取", "score": 0, "max_score": 20, "passed": False, "reason": "遗漏了部分紧急需求或混入了非紧急需求"})
    else:
        score_details.append({"item": "利用大模型检查是否准确揪出未审批人员", "score": 0, "max_score": 25, "passed": False, "reason": "无报告文件"})
        score_details.append({"item": "利用大模型检查是否准确计算有效工时", "score": 0, "max_score": 25, "passed": False, "reason": "无报告文件"})
        score_details.append({"item": "利用大模型检查紧急需求提取", "score": 0, "max_score": 20, "passed": False, "reason": "无报告文件"})

    # Write output score
    score_data = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(score_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
