import os
import sys
import json
import httpx
from openai import OpenAI

# 🔒 强制 API 规范
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

def run_evaluation():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_file = os.path.join(workspace, "church_funds/summary.txt")
    details = []
    total_score = 0

    # 1. 基础结构检查 (10分)
    if os.path.exists(score_file):
        details.append({"item": "文件 church_funds/summary.txt 存在", "score": 10, "max_score": 10, "passed": True, "reason": "Found results file."})
        total_score += 10
    else:
        details.append({"item": "文件 church_funds/summary.txt 存在", "score": 0, "max_score": 10, "passed": False, "reason": "Missing summary.txt in church_funds folder."})

    # 2. 内容解析与数值准确性检查 (70分)
    # Ground Truth: JSON(58.00) + Scribble(38.00) = 96.00
    expected_value = 96.0
    if os.path.exists(score_file):
        try:
            with open(score_file, 'r') as f:
                content = f.read().strip()
                # 尝试提取第一个浮点数
                import re
                match = re.search(r"(\d+\.\d+)", content)
                if not match:
                    # 尝试匹配整数
                    match = re.search(r"(\d+)", content)
                
                if match:
                    actual_value = float(match.group(1))
                    if abs(actual_value - expected_value) < 0.01:
                        details.append({"item": "数值计算完全正确", "score": 70, "max_score": 70, "passed": True, "reason": f"Calculated exact value: {actual_value}"})
                        total_score += 70
                    elif abs(actual_value - 58.0) < 0.01:
                        details.append({"item": "数值计算部分正确", "score": 30, "max_score": 70, "passed": False, "reason": "Result only includes JSON data, missed scribbles.txt notes."})
                        total_score += 30
                    elif abs(actual_value - 38.0) < 0.01:
                        details.append({"item": "数值计算部分正确", "score": 20, "max_score": 70, "passed": False, "reason": "Result only includes scribbles.txt, missed main JSON data."})
                        total_score += 20
                    else:
                        details.append({"item": "数值计算错误", "score": 0, "max_score": 70, "passed": False, "reason": f"Expected {expected_value}, got {actual_value}"})
                else:
                    details.append({"item": "结果文件格式错误", "score": 0, "max_score": 70, "passed": False, "reason": "No number found in summary.txt"})
        except Exception as e:
            details.append({"item": "文件读取错误", "score": 0, "max_score": 70, "passed": False, "reason": str(e)})

    # 3. 结果纯净度检查 (20分) - 使用 LLM 检查是否只包含数字/要求的简单格式
    if os.path.exists(score_file):
        with open(score_file, 'r') as f:
            content = f.read()
        
        is_clean = llm_judge_content("Does the file content strictly provide the requested total number (optionally with minimal labels) without unnecessary explanation, chatty segments, or internal logic dump?", content)
        if is_clean:
            details.append({"item": "文件输出规范性", "score": 20, "max_score": 20, "passed": True, "reason": "Format is clean and concise."})
            total_score += 20
        else:
            details.append({"item": "文件输出规范性", "score": 0, "max_score": 20, "passed": False, "reason": "The file contains too much chatter or non-required info."})

    # 输出结果
    output = {
        "total_score": int(total_score),
        "details": details
    }
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    run_evaluation()
