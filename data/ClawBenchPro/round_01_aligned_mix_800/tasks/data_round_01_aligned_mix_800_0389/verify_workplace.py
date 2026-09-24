import os
import sys
import json
import httpx
import pandas as pd
from openai import OpenAI

# 强制要求：初始化客户端，关闭 SSL 验证
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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_path = os.path.join(workspace, "deliverables")
    summary_file = os.path.join(deliverables_path, "summary_document.txt") # 或者是 .md
    
    # 找到可能的文件（容错后缀）
    if not os.path.exists(summary_file):
        for f in os.listdir(deliverables_path) if os.path.exists(deliverables_path) else []:
            if "summary" in f.lower():
                summary_file = os.path.join(deliverables_path, f)
                break

    score_details = []
    
    # 1. 目录与文件结构检查 (10分)
    if os.path.exists(deliverables_path) and os.path.isdir(deliverables_path):
        score_details.append({"item": "Deliverables folder existence", "score": 5, "max_score": 5, "passed": True, "reason": "Folder exists."})
    else:
        score_details.append({"item": "Deliverables folder existence", "score": 0, "max_score": 5, "passed": False, "reason": "Folder not found."})

    if os.path.exists(summary_file):
        score_details.append({"item": "Summary file existence", "score": 5, "max_score": 5, "passed": True, "reason": "File exists."})
        with open(summary_file, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        score_details.append({"item": "Summary file existence", "score": 0, "max_score": 5, "passed": False, "reason": "File not found."})
        content = ""

    # 2. 匹配逻辑准确性 (50分)
    # 计算标准：
    # Stark (6000kg, 7000RPM): 满足条件的有 M2($220k), M5($800k). 最便宜是 M2.
    # Wayne (1500kg, 15000RPM): 满足条件的有 M3($85k), M5($800k). 最便宜是 M3.
    # Acme (10000kg, 4000RPM): 满足条件的有 M4($350k), M5($800k). 最便宜是 M4.
    
    matching_checks = [
        ("Stark Industries", "Atlas-Pro", "M2"),
        ("Wayne Enterprises", "Hermes-Lite", "M3"),
        ("Acme Corp", "Vulcan-Heavy", "M4")
    ]
    
    if content:
        for client_name, machine_name, mid in matching_checks:
            found = client_name.split()[0].lower() in content.lower() and machine_name.lower() in content.lower()
            item_score = 15 if found else 0
            score_details.append({
                "item": f"Matching accuracy: {client_name}",
                "score": item_score,
                "max_score": 15,
                "passed": found,
                "reason": f"Correct machine {machine_name} found for {client_name}" if found else "Incorrect match or client missing"
            })
        # 匹配逻辑额外 5 分全对奖励
        if all(c.split()[0].lower() in content.lower() and m.lower() in content.lower() for c, m, mid in matching_checks):
            score_details.append({"item": "All clients matched correctly", "score": 5, "max_score": 5, "passed": True, "reason": "Perfect match logic."})
        else:
            score_details.append({"item": "All clients matched correctly", "score": 0, "max_score": 5, "passed": False, "reason": "One or more matches failed."})
    else:
        for client_name, _, _ in matching_checks:
            score_details.append({"item": f"Matching accuracy: {client_name}", "score": 0, "max_score": 15, "passed": False, "reason": "No content to check."})
        score_details.append({"item": "All clients matched correctly", "score": 0, "max_score": 5, "passed": False, "reason": "No content."})

    # 3. 财务计算：佣金 (20分)
    # M2(220,000) + M3(85,000) + M4(350,000) = 655,000
    # Commission = 655,000 * 0.05 = 32,750
    if "32750" in content or "32,750" in content:
        score_details.append({"item": "Commission calculation", "score": 20, "max_score": 20, "passed": True, "reason": "Total commission $32,750 correctly identified."})
    else:
        score_details.append({"item": "Commission calculation", "score": 0, "max_score": 20, "passed": False, "reason": "Incorrect or missing total commission."})

    # 4. 非结构化质量：LLM 语义检查 (20分)
    if content:
        prompt = "Check if the document is a formal professional summary for a sales director. It should not contain mentions of carbonara, groceries, or informal complaints from the original prompt."
        is_professional = llm_judge_content(prompt, content)
        score_details.append({
            "item": "Document professionalism (LLM)",
            "score": 20 if is_professional else 5,
            "max_score": 20,
            "passed": is_professional,
            "reason": "Document is formal and filtered out noise." if is_professional else "Document contains irrelevant noise or is too informal."
        })
    else:
        score_details.append({"item": "Document professionalism (LLM)", "score": 0, "max_score": 20, "passed": False, "reason": "No content."})

    total_score = sum(d["score"] for d in score_details)
    
    # 输出结果
    output = {
        "total_score": int(total_score),
        "details": score_details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
