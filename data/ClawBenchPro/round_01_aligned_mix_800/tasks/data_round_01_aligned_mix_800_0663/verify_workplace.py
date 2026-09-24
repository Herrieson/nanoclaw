import os
import sys
import json
import httpx
import re
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
    """检测非结构化文本的统一接口"""
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
    exhibition_dir = os.path.join(workspace, "exhibition")
    inventory_path = os.path.join(exhibition_dir, "gallery_inventory.md")

    total_score = 0
    details = []

    # 1. 目录存在检测 (10分)
    if os.path.isdir(exhibition_dir):
        total_score += 10
        details.append({"item": "检查 exhibition 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录已成功创建"})
    else:
        details.append({"item": "检查 exhibition 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录未创建"})

    # 2. 文件存在检测 (10分)
    if not os.path.isfile(inventory_path):
        details.append({"item": "检查 gallery_inventory.md 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件未创建"})
        details.append({"item": "检查有效画作的数据提取", "score": 0, "max_score": 12, "passed": False, "reason": "文件不存在"})
        details.append({"item": "检查无效数据的剔除", "score": 0, "max_score": 8, "passed": False, "reason": "文件不存在"})
        details.append({"item": "检查底层总价值计算及位置", "score": 0, "max_score": 30, "passed": False, "reason": "文件不存在"})
        details.append({"item": "排版风格与杂项LLM检测", "score": 0, "max_score": 30, "passed": False, "reason": "文件不存在"})
        
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)
        return

    total_score += 10
    details.append({"item": "检查 gallery_inventory.md 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件已创建"})
    
    with open(inventory_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    content_lower = content.lower()

    # 3. 检查必须提取出的可用画作 (12分)
    required_paintings = ["sunflowers", "spring morning", "morning dew", "abstract 1"]
    req_score = 0
    missing = []
    for p in required_paintings:
        if p in content_lower:
            req_score += 3
        else:
            missing.append(p)
    if req_score == 12:
        details.append({"item": "检查有效画作的数据提取", "score": 12, "max_score": 12, "passed": True, "reason": "成功提取了所有状态为 available 的画作"})
    else:
        details.append({"item": "检查有效画作的数据提取", "score": req_score, "max_score": 12, "passed": False, "reason": f"缺失了应包含的画作: {missing}"})
    total_score += req_score

    # 4. 检查是否严格过滤了错误的数据 (8分)
    excluded_paintings = ["portrait of john", "sunset"]
    exc_score = 8
    included_wrong = []
    for p in excluded_paintings:
        if p in content_lower:
            exc_score -= 4
            included_wrong.append(p)
    if exc_score == 8:
        details.append({"item": "检查无效数据的剔除", "score": 8, "max_score": 8, "passed": True, "reason": "成功过滤了已出售和赠送的画作"})
    else:
        details.append({"item": "检查无效数据的剔除", "score": exc_score, "max_score": 8, "passed": False, "reason": f"错误地包含了无需列出的画作: {included_wrong}"})
    total_score += exc_score

    # 5. 计算结果检查 (精确提取)及其位置验证 (30分)
    # 计算公式应为: 500 + 250 + 200 + 600 = 1550
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    if not lines:
        details.append({"item": "检查底层总价值计算及位置", "score": 0, "max_score": 30, "passed": False, "reason": "文件内容为空"})
    else:
        # 获取最底部的几行（最多3行有效文本），满足用户要求“write the total sum very clearly at the very bottom”
        last_few_lines = " ".join(lines[-3:])
        # 允许形式： 1550, 1,550, 1550.00 等
        if re.search(r'1,?550(?:\.00)?', last_few_lines):
            details.append({"item": "检查底层总价值计算及位置", "score": 30, "max_score": 30, "passed": True, "reason": "文件底端准确呈现了正确计算的总预估价值 1550"})
            total_score += 30
        else:
            # 退而求其次，检查全文是否包含 1550，但放错位置
            if re.search(r'1,?550(?:\.00)?', content):
                details.append({"item": "检查底层总价值计算及位置", "score": 15, "max_score": 30, "passed": False, "reason": "计算正确得到 1550，但未遵循指令将其放置在文档的绝对底部"})
                total_score += 15
            else:
                details.append({"item": "检查底层总价值计算及位置", "score": 0, "max_score": 30, "passed": False, "reason": "未能正确计算出总价值 1550，或未使用数字体现结果"})

    # 6. 利用 LLM 检查软性需求（视觉排版清晰 + 隔离污染） (30分)
    prompt = """Please check if the Markdown document satisfies BOTH of the following requirements:
1. Formatting: It is clearly formatted to be easily readable for an elderly person with poor vision. It MUST use large Markdown headers (like # or ##) and/or well-spaced, clear bulleted/bold lists.
2. Contamination: It does NOT contain any irrelevant grocery or to-do list items (e.g., milk, eggs, burnt sienna paint, Dr. Adams, glasses prescription, etc.).
Answer 'YES' if BOTH requirements are met, otherwise answer 'NO'."""
    llm_passed = llm_judge_content(prompt, content)
    if llm_passed:
        details.append({"item": "排版风格与杂项LLM检测", "score": 30, "max_score": 30, "passed": True, "reason": "排版清晰适合视力不佳者，且无任务杂项污染"})
        total_score += 30
    else:
        details.append({"item": "排版风格与杂项LLM检测", "score": 0, "max_score": 30, "passed": False, "reason": "排版过于密集不符合 Persona 设定，或错误混入了 Todo list 的干扰项"})

    # 输出结果
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
