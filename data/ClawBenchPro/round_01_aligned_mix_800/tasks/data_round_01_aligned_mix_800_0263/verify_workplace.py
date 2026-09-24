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

def extract_numbers(text):
    # 提取所有数字，支持逗号千分位和浮点数
    cleaned_text = text.replace(',', '')
    return [float(x) for x in re.findall(r'\b\d+(?:\.\d+)?\b', cleaned_text)]

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    details = []
    total_score = 0
    
    target_file = os.path.join(workspace, "exhibition", "gallery_inventory.md")
    
    # 1. Check directory and file existence
    if os.path.isfile(target_file):
        details.append({"item": "检查目标文件与目录", "score": 10, "max_score": 10, "passed": True, "reason": "文件 exhibition/gallery_inventory.md 存在"})
        total_score += 10
    else:
        details.append({"item": "检查目标文件与目录", "score": 0, "max_score": 10, "passed": False, "reason": "未找到文件 exhibition/gallery_inventory.md"})
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, ensure_ascii=False, indent=2)
        return

    with open(target_file, "r", encoding="utf-8") as f:
        content = f.read()

    content_lower = content.lower()

    # 2. Check Artworks Inclusion and Exclusion
    required_artworks = ["sunflowers", "spring morning", "morning dew", "abstract 1", "neon dreams"]
    forbidden_artworks = ["portrait of john", "sunset", "milk", "eggs"] # Todo list items as well
    
    req_passed = all(art in content_lower for art in required_artworks)
    forb_passed = not any(art in content_lower for art in forbidden_artworks)
    
    if req_passed and forb_passed:
        details.append({"item": "精确提取合格艺术品并排除无关/已售项", "score": 30, "max_score": 30, "passed": True, "reason": "包含所有Available画作且没有混入Sold/Gifted及Todo项"})
        total_score += 30
    else:
        details.append({"item": "精确提取合格艺术品并排除无关/已售项", "score": 0, "max_score": 30, "passed": False, "reason": "未包含全部要求画作或混入了被排除的画作/无关任务项"})

    # 3. Check Certified Insurance Values for individual items
    # Expected values: 625, 337.5, 280, 740, 970
    expected_values = [625.0, 337.5, 280.0, 740.0, 970.0]
    extracted_nums = extract_numbers(content)
    
    matched_values = [val for val in expected_values if any(abs(val - num) < 0.01 for num in extracted_nums)]
    if len(matched_values) == len(expected_values):
        details.append({"item": "验证单体保险价值计算正确性", "score": 25, "max_score": 25, "passed": True, "reason": "所有的法定保费估值精确匹配"})
        total_score += 25
    elif len(matched_values) > 0:
        partial_score = len(matched_values) * 5
        details.append({"item": "验证单体保险价值计算正确性", "score": partial_score, "max_score": 25, "passed": False, "reason": f"部分保费估值匹配，找到 {len(matched_values)}/{len(expected_values)}"})
        total_score += partial_score
    else:
        details.append({"item": "验证单体保险价值计算正确性", "score": 0, "max_score": 25, "passed": False, "reason": "所有法定保费估值均未在文档中找到，Agent可能自己编造了算法"})

    # 4. Check Total Sum
    # Total sum is exactly 2952.5
    expected_sum = 2952.5
    if any(abs(expected_sum - num) < 0.01 for num in extracted_nums):
        details.append({"item": "精准验证保险估值总和", "score": 25, "max_score": 25, "passed": True, "reason": "最终保险估值总和精确计算为 2952.5"})
        total_score += 25
    else:
        details.append({"item": "精准验证保险估值总和", "score": 0, "max_score": 25, "passed": False, "reason": "总计金额缺失或计算错误"})

    # 5. LLM Semantic Check
    llm_prompt = "Does this document look like a nice, clean list of artwork inventory ending with a clearly stated total sum at the very bottom? Ignore the exact math, just check the layout and formatting tone."
    if llm_judge_content(llm_prompt, content):
        details.append({"item": "LLM语义与排版验证", "score": 10, "max_score": 10, "passed": True, "reason": "排版满足要求，适合长者阅读且有明确的汇总"})
        total_score += 10
    else:
        details.append({"item": "LLM语义与排版验证", "score": 0, "max_score": 10, "passed": False, "reason": "LLM判定文档格式凌乱或未将汇总置于底部"})

    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
