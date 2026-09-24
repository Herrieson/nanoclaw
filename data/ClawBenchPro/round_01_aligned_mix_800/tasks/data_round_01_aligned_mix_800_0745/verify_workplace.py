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
    deliverables_dir = os.path.join(workspace, "deliverables")
    
    total_score = 0
    details = []

    # 1. 检查 deliverables 目录是否存在 (10 分)
    if os.path.isdir(deliverables_dir):
        score = 10
        total_score += score
        details.append({"item": "Deliverables 目录存在", "score": score, "max_score": 10, "passed": True, "reason": "`deliverables` 目录已创建"})
    else:
        details.append({"item": "Deliverables 目录存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 `deliverables` 目录"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 2. 检查目录下是否有非空报告文件 (10 分)
    report_files = [f for f in os.listdir(deliverables_dir) if os.path.isfile(os.path.join(deliverables_dir, f))]
    if len(report_files) > 0:
        score = 10
        total_score += score
        details.append({"item": "报告文件生成", "score": score, "max_score": 10, "passed": True, "reason": "找到了报告文件"})
    else:
        details.append({"item": "报告文件生成", "score": 0, "max_score": 10, "passed": False, "reason": "`deliverables` 目录下没有任何文件"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 读取生成的报告内容（可能包含多个文件，将它们拼接读取以防拆分报告）
    report_content = ""
    for file_name in report_files:
        file_path = os.path.join(deliverables_dir, file_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                report_content += f.read() + "\n"
        except Exception:
            pass

    if not report_content.strip():
        details.append({"item": "文件内容不为空", "score": 0, "max_score": 80, "passed": False, "reason": "报告文件内容为空无法验证"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 3. 大模型验证：MegaCorp Oil 赞助商状态检查 (20 分)
    prompt_1 = "Does the report explicitly and correctly identify 'MegaCorp Oil' as a business/sponsor that is still 'Pending' (hasn't paid up)?"
    if llm_judge_content(prompt_1, report_content):
        score = 20
        total_score += score
        details.append({"item": "准确标识 MegaCorp Oil", "score": score, "max_score": 20, "passed": True, "reason": "大模型判定报告准确指出了 MegaCorp Oil 为 Pending 状态"})
    else:
        details.append({"item": "准确标识 MegaCorp Oil", "score": 0, "max_score": 20, "passed": False, "reason": "未能准确指出 MegaCorp Oil"})

    # 4. 大模型验证：Global Retailers LLC 赞助商状态检查 (20 分)
    prompt_2 = "Does the report explicitly and correctly identify 'Global Retailers LLC' as a business/sponsor that is still 'Pending' (hasn't paid up)?"
    if llm_judge_content(prompt_2, report_content):
        score = 20
        total_score += score
        details.append({"item": "准确标识 Global Retailers LLC", "score": score, "max_score": 20, "passed": True, "reason": "大模型判定报告准确指出了 Global Retailers LLC 为 Pending 状态"})
    else:
        details.append({"item": "准确标识 Global Retailers LLC", "score": 0, "max_score": 20, "passed": False, "reason": "未能准确指出 Global Retailers LLC"})

    # 5. 大模型验证：Park Cleanup 志愿时间统计 (20 分)
    prompt_3 = "Does the report explicitly and accurately state that the TOTAL volunteer hours for the 'Park Cleanup' initiative is EXACTLY 48 (or 48.0)?"
    if llm_judge_content(prompt_3, report_content):
        score = 20
        total_score += score
        details.append({"item": "准确统计 Park Cleanup 时间", "score": score, "max_score": 20, "passed": True, "reason": "大模型判定正确得出了 48 小时的总志愿时间"})
    else:
        details.append({"item": "准确统计 Park Cleanup 时间", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定未能给出正确的 48 小时总时长，或未过滤掉其他项目的时长"})

    # 6. 大模型验证：报告格式是否得体 (20 分)
    prompt_4 = "Is this document formatted as a nice, neat, and organized summary report (rather than just raw unstructured data dumps or irrelevant conversational text)?"
    if llm_judge_content(prompt_4, report_content):
        score = 20
        total_score += score
        details.append({"item": "报告排版得体", "score": score, "max_score": 20, "passed": True, "reason": "大模型判定报告结构清晰整洁"})
    else:
        details.append({"item": "报告排版得体", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定排版杂乱或不符合总结报告特征"})

    # 写入最终分数
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    main()
