import os
import sys
import json
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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    total_score = 0
    details = []

    deliverables_dir = os.path.join(workspace, "deliverables")
    report_file = os.path.join(deliverables_dir, "client_report.txt")

    # 1. Check Directory (10 points)
    if os.path.isdir(deliverables_dir):
        total_score += 10
        details.append({"item": "检查 deliverables 目录", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
    else:
        details.append({"item": "检查 deliverables 目录", "score": 0, "max_score": 10, "passed": False, "reason": "目录不存在"})

    # 2. Check File Existence (10 points)
    if os.path.isfile(report_file):
        total_score += 10
        details.append({"item": "检查 client_report.txt 文件", "score": 10, "max_score": 10, "passed": True, "reason": "报告文件存在"})
        
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()
            content_lower = content.lower()

        # 3. Check Exact Machine Matches (30 points, 10 each)
        # Stark -> Atlas-Pro
        if "stark" in content_lower and ("atlas-pro" in content_lower or "m-102" in content_lower):
            total_score += 10
            details.append({"item": "Stark 匹配验证", "score": 10, "max_score": 10, "passed": True, "reason": "正确匹配 Atlas-Pro"})
        else:
            details.append({"item": "Stark 匹配验证", "score": 0, "max_score": 10, "passed": False, "reason": "未正确匹配 Stark 和 Atlas-Pro"})

        # Wayne -> Hermes-Lite
        if "wayne" in content_lower and ("hermes-lite" in content_lower or "m-103" in content_lower):
            total_score += 10
            details.append({"item": "Wayne 匹配验证", "score": 10, "max_score": 10, "passed": True, "reason": "正确匹配 Hermes-Lite"})
        else:
            details.append({"item": "Wayne 匹配验证", "score": 0, "max_score": 10, "passed": False, "reason": "未正确匹配 Wayne 和 Hermes-Lite"})

        # Acme -> Vulcan-Heavy
        if "acme" in content_lower and ("vulcan-heavy" in content_lower or "m-104" in content_lower):
            total_score += 10
            details.append({"item": "Acme 匹配验证", "score": 10, "max_score": 10, "passed": True, "reason": "正确匹配 Vulcan-Heavy"})
        else:
            details.append({"item": "Acme 匹配验证", "score": 0, "max_score": 10, "passed": False, "reason": "未正确匹配 Acme 和 Vulcan-Heavy"})

        # 4. Check Exact Commission Calculation (20 points)
        # 5% of (220000 + 85000 + 350000) = 5% of 655000 = 32750
        if "32750" in content.replace(",", "") or "32,750" in content:
            total_score += 20
            details.append({"item": "总佣金计算验证", "score": 20, "max_score": 20, "passed": True, "reason": "佣金计算准确 (32750)"})
        else:
            details.append({"item": "总佣金计算验证", "score": 0, "max_score": 20, "passed": False, "reason": "佣金数值 32750 未找到，计算错误或遗漏"})

        # 5. LLM Check: Formal Tone and Context Formatting (20 points)
        prompt = "Does this text represent a formal business report listing client-machine matching results and calculating a final commission? It should NOT look like a casual dump, but an organized formal report."
        is_formal = llm_judge_content(prompt, content)
        if is_formal:
            total_score += 20
            details.append({"item": "报告正式性语义验证", "score": 20, "max_score": 20, "passed": True, "reason": "LLM 判定报告格式规范且语调正式"})
        else:
            details.append({"item": "报告正式性语义验证", "score": 0, "max_score": 20, "passed": False, "reason": "LLM 判定报告不符合正式商业报告的标准"})

    else:
        details.append({"item": "检查 client_report.txt 文件", "score": 0, "max_score": 10, "passed": False, "reason": "报告文件不存在"})
        details.append({"item": "Stark 匹配验证", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        details.append({"item": "Wayne 匹配验证", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        details.append({"item": "Acme 匹配验证", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        details.append({"item": "总佣金计算验证", "score": 0, "max_score": 20, "passed": False, "reason": "文件不存在"})
        details.append({"item": "报告正式性语义验证", "score": 0, "max_score": 20, "passed": False, "reason": "文件不存在"})

    result = {
        "total_score": total_score,
        "details": details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    verify()
