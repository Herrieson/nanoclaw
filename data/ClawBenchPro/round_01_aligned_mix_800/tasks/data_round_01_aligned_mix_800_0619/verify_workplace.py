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

def extract_all_numbers(text):
    # 提取文本中所有的数字以供严谨对比
    pattern = r'\b\d+(?:\.\d+)?\b'
    matches = re.findall(pattern, text)
    return set([float(m) for m in matches])

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0

    target_dir = os.path.join(workspace, "ready_for_monday")
    
    # 1. 检查目录是否存在 (10 points)
    dir_exists = os.path.isdir(target_dir)
    if dir_exists:
        results.append({"item": "检查目标目录 ready_for_monday 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录已创建"})
        total_score += 10
    else:
        results.append({"item": "检查目标目录 ready_for_monday 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录未找到"})
        # 目录不存在直接结束
        output_result(total_score, results)
        return

    # 2. 检查文件数量 (10 points)
    files = [f for f in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, f))]
    if len(files) >= 2:
        results.append({"item": "检查目录内是否至少包含2个文件", "score": 10, "max_score": 10, "passed": True, "reason": f"找到了 {len(files)} 个文件"})
        total_score += 10
    else:
        results.append({"item": "检查目录内是否至少包含2个文件", "score": 0, "max_score": 10, "passed": False, "reason": f"只找到了 {len(files)} 个文件，不符合题目要求的两个独立文件"})

    # 读取所有文件内容进行统一核对
    combined_content = ""
    for f in files:
        with open(os.path.join(target_dir, f), "r", encoding="utf-8") as file:
            combined_content += file.read() + "\n"

    # 3. 严格代码检测：计算结果是否精准 (40 points)
    # 正确的业务逻辑：
    # 建筑支出: 450 + 120 + 15 + 300 = 885
    # 艺术支出: 35.5 + 85 + 150 = 270.5
    numbers_found = extract_all_numbers(combined_content)
    
    if 885.0 in numbers_found:
        results.append({"item": "代码检测: 建筑材料总支出计算正确 (885)", "score": 20, "max_score": 20, "passed": True, "reason": "成功提取到正确的建筑支出总计 885"})
        total_score += 20
    else:
        results.append({"item": "代码检测: 建筑材料总支出计算正确 (885)", "score": 0, "max_score": 20, "passed": False, "reason": "未能在输出文件中找到正确的建筑总计 885"})

    if 270.5 in numbers_found:
        results.append({"item": "代码检测: 艺术材料总支出计算正确 (270.5)", "score": 20, "max_score": 20, "passed": True, "reason": "成功提取到正确的艺术支出总计 270.5"})
        total_score += 20
    else:
        results.append({"item": "代码检测: 艺术材料总支出计算正确 (270.5)", "score": 0, "max_score": 20, "passed": False, "reason": "未能在输出文件中找到正确的艺术总计 270.5"})

    # 4. LLM 语义检测：安全总结的质量与过滤规则 (40 points)
    prompt_scaffolding = "Does the text explicitly mention the 'missing guardrails on the scaffolding' or 'scaffolding hazard'?"
    prompt_wire = "Does the text explicitly mention the 'exposed live wire'?"
    prompt_minor = "Does the text mention minor issues like 'dust masks' or 'hard hats'? Answer YES if it includes them, NO if it cleanly excluded them."
    prompt_tone = "Is the text professional and suitable for a city inspector, without Marcus's personal ramblings?"

    # 检查重度危险 1
    if llm_judge_content(prompt_scaffolding, combined_content):
        results.append({"item": "LLM语义检测: 包含脚手架缺失护栏的致命隐患", "score": 10, "max_score": 10, "passed": True, "reason": "成功提取脚手架隐患"})
        total_score += 10
    else:
        results.append({"item": "LLM语义检测: 包含脚手架缺失护栏的致命隐患", "score": 0, "max_score": 10, "passed": False, "reason": "缺失脚手架隐患"})

    # 检查重度危险 2
    if llm_judge_content(prompt_wire, combined_content):
        results.append({"item": "LLM语义检测: 包含裸露带电电线的即时危险", "score": 10, "max_score": 10, "passed": True, "reason": "成功提取电线隐患"})
        total_score += 10
    else:
        results.append({"item": "LLM语义检测: 包含裸露带电电线的即时危险", "score": 0, "max_score": 10, "passed": False, "reason": "缺失电线隐患"})

    # 检查是否过滤轻微隐患 (反向检测)
    if not llm_judge_content(prompt_minor, combined_content):
        results.append({"item": "LLM语义检测: 成功剔除微小隐患(口罩、安全帽等)", "score": 10, "max_score": 10, "passed": True, "reason": "未包含非致命的安全警告，遵循了指令"})
        total_score += 10
    else:
        results.append({"item": "LLM语义检测: 成功剔除微小隐患(口罩、安全帽等)", "score": 0, "max_score": 10, "passed": False, "reason": "错误地包含了次要隐患，未遵循 only explicit critical hazards 的要求"})

    # 检查语气
    if llm_judge_content(prompt_tone, combined_content):
        results.append({"item": "LLM语义检测: 总结内容专业，没有个人无关抱怨", "score": 10, "max_score": 10, "passed": True, "reason": "语气专业"})
        total_score += 10
    else:
        results.append({"item": "LLM语义检测: 总结内容专业，没有个人无关抱怨", "score": 0, "max_score": 10, "passed": False, "reason": "包含了与安全无关的个人抱怨或语境不当"})

    output_result(total_score, results)

def output_result(total_score, results):
    output = {
        "total_score": total_score,
        "details": results
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(json.dumps(output, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
