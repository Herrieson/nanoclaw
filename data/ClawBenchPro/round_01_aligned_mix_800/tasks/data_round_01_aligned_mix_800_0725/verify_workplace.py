import os
import sys
import json
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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    total_score = 0
    details = []

    deliverables_dir = os.path.join(workspace, "deliverables")
    unauth_file = os.path.join(deliverables_dir, "unauthorized_report.txt")
    audit_file = os.path.join(deliverables_dir, "final_audit.json")

    # 1. 检查基础目录结构 (10分)
    if os.path.isdir(deliverables_dir):
        total_score += 10
        details.append({"item": "检查 deliverables 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "deliverables 目录已创建"})
    else:
        details.append({"item": "检查 deliverables 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "deliverables 目录未创建"})

    # 2. 检查黑名单文本格式并调用 LLM 分析语义与名单 (30分)
    if os.path.isfile(unauth_file):
        with open(unauth_file, "r", encoding="utf-8") as f:
            unauth_content = f.read()
        
        prompt = """Please verify if this unauthorized volunteers report meets the following strict criteria:
1. It clearly identifies exactly TWO intruders: "Intruder Dave" and "Evil Steve".
2. It NEVER mentions the authorized volunteers (Mary Sobieski, John Kowalski, Agnieszka Novak, Robert Miller, Theresa Wisniewski) as intruders.
Does the report strictly satisfy these criteria? Answer YES or NO."""

        if llm_judge_content(prompt, unauth_content):
            total_score += 30
            details.append({"item": "违规者名单内容检查(LLM)", "score": 30, "max_score": 30, "passed": True, "reason": "准确识别出了所有的违规者且没有误伤"})
        else:
            details.append({"item": "违规者名单内容检查(LLM)", "score": 0, "max_score": 30, "passed": False, "reason": "未能准确指出所有违规者，或误将白名单人员加入其中"})
    else:
        details.append({"item": "违规者名单内容检查(LLM)", "score": 0, "max_score": 30, "passed": False, "reason": "文件 unauthorized_report.txt 不存在"})

    # 3. 检查最终工时 JSON 数据合法性 (10分)
    audit_data = None
    if os.path.isfile(audit_file):
        try:
            with open(audit_file, "r", encoding="utf-8") as f:
                audit_data = json.load(f)
            total_score += 10
            details.append({"item": "检查 JSON 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "final_audit.json 格式正确"})
        except json.JSONDecodeError:
            details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": "final_audit.json JSON 解析失败"})
    else:
        details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": "文件 final_audit.json 不存在"})

    # 4. 精准验证每个授权志愿者的工时 (共50分，每人10分)
    # Expected hours:
    # Mary Sobieski: 3.5 + 2.5 + 1.0 = 7.0
    # John Kowalski: 120min = 2.0
    # Agnieszka Novak: 4.0
    # Robert Miller: 5.2
    # Theresa Wisniewski: 13:00 to 14:15 = 1.25 -> round to 1.2 or 1.3
    
    expected_hours = {
        "Mary Sobieski": [7.0],
        "John Kowalski": [2.0],
        "Agnieszka Novak": [4.0],
        "Robert Miller": [5.2],
        "Theresa Wisniewski": [1.2, 1.3] # 允许浮点四舍五入的差异
    }

    if audit_data and isinstance(audit_data, dict):
        for person, expected_vals in expected_hours.items():
            actual = audit_data.get(person)
            if actual is not None:
                try:
                    actual_val = float(actual)
                    if any(abs(actual_val - ev) < 0.05 for ev in expected_vals):
                        total_score += 10
                        details.append({"item": f"工时验证: {person}", "score": 10, "max_score": 10, "passed": True, "reason": f"成功计算出正确工时 {actual_val}"})
                    else:
                        details.append({"item": f"工时验证: {person}", "score": 0, "max_score": 10, "passed": False, "reason": f"工时错误，期望在 {expected_vals} 附近，实际为 {actual_val}"})
                except ValueError:
                    details.append({"item": f"工时验证: {person}", "score": 0, "max_score": 10, "passed": False, "reason": f"工时数值非法: {actual}"})
            else:
                details.append({"item": f"工时验证: {person}", "score": 0, "max_score": 10, "passed": False, "reason": f"未能在字典中找到该志愿者记录"})
    else:
        details.append({"item": "详细工时验证", "score": 0, "max_score": 50, "passed": False, "reason": "缺少合法 JSON 数据或数据不是字典类型以进行进一步评估"})

    # 输出结果
    result = {
        "total_score": total_score,
        "details": details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
