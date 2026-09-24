import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

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

def verify_workplace():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    total_score = 0
    details = []

    report_path = os.path.join(workspace, "deliverables", "audit_report.json")
    
    # 1. 检查物理结果产物目录与文件是否存在 (10分)
    if os.path.exists(report_path):
        total_score += 10
        details.append({"item": "检查 audit_report.json 文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "交付文件存在"})
    else:
        details.append({"item": "检查 audit_report.json 文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 deliverables/audit_report.json"})
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)
        return

    # 2. 检查 JSON 解析合法性 (原生代码负责结构性检查) (10分)
    file_content = ""
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            file_content = f.read()
            json_data = json.loads(file_content) # 严格解析，不使用正则模糊匹配
        total_score += 10
        details.append({"item": "检查文件结构化合法性", "score": 10, "max_score": 10, "passed": True, "reason": "是合法的 JSON 结构"})
    except Exception as e:
        details.append({"item": "检查文件结构化合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"无法被解析为合法 JSON: {e}"})
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)
        return

    # 辅助函数，将对不确定 Schema 的 JSON 语义验证交给 LLM Judge
    def evaluate_dimension(name, prompt, max_pts):
        nonlocal total_score
        passed = llm_judge_content(prompt, file_content)
        if passed:
            total_score += max_pts
            details.append({"item": name, "score": max_pts, "max_score": max_pts, "passed": True, "reason": "大模型语义验证通过"})
        else:
            details.append({"item": name, "score": 0, "max_score": max_pts, "passed": False, "reason": "大模型语义验证未通过"})

    # 3. 语义验证：是否找出了 3 个 Missing Transcripts (安排了但没录音) (每项 10 分，共 30 分)
    evaluate_dimension(
        "识别 Missing 差异1 (Doe v. City, 10-01)",
        "Check if the JSON report identifies the scheduled deposition for 'Doe v. City' on '2023-10-01' as a missing transcript or not occurred.",
        10
    )
    evaluate_dimension(
        "识别 Missing 差异2 (Roe v. Inc, 10-02)",
        "Check if the JSON report identifies the scheduled deposition for 'Roe v. Inc' on '2023-10-02' as a missing transcript or not occurred.",
        10
    )
    evaluate_dimension(
        "识别 Missing 差异3 (Smith v. State, 10-03)",
        "Check if the JSON report identifies the scheduled deposition for 'Smith v. State' on '2023-10-03' as a missing transcript or not occurred.",
        10
    )

    # 4. 语义验证：是否找出了 2 个 Unscheduled Depositions (录音了但没在日程里) (每项 10 分，共 20 分)
    evaluate_dimension(
        "识别 Unscheduled 差异1 (Smith v. State, 10-02)",
        "Check if the JSON report identifies that a deposition happened for 'Smith v. State' on '2023-10-02' but it was unscheduled or not in the master schedule.",
        10
    )
    evaluate_dimension(
        "识别 Unscheduled 差异2 (Doe v. City, 10-02)",
        "Check if the JSON report identifies that a deposition happened for 'Doe v. City' on '2023-10-02' but it was unscheduled.",
        10
    )

    # 5. 语义验证：是否找出了 1 个 Unauthorized Personnel 异常事件 (20 分)
    evaluate_dimension(
        "识别 Unauthorized Personnel (Paralegal Miller)",
        "Check if the JSON report explicitly names 'Paralegal Miller' as unauthorized to conduct the deposition for 'Smith v. State'.",
        20
    )

    # 6. 幻觉与捏造惩罚：不能冤枉合规的律师 (10 分)
    evaluate_dimension(
        "无捏造幻觉惩罚检查 (合法律师保护)",
        "Check if the JSON report correctly AVOIDS classifying 'Siobhan O'Malley' as unauthorized. Answer 'YES' if Siobhan O'Malley is NOT listed as unauthorized, and 'NO' if she is falsely accused or penalized.",
        10
    )

    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify_workplace()
