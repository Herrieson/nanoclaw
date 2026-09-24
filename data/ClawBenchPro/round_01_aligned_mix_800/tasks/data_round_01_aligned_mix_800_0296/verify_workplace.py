import os
import sys
import json
import csv
import httpx
from openai import OpenAI

# ----------------------------------------------------------------
# 1. 核心数据定义 (Ground Truth)
# ----------------------------------------------------------------
GROUND_TRUTH_DATA = {
    "SKU-1001": {"min_stock": 30, "qty": 45}, # OK
    "SKU-1002": {"min_stock": 20, "qty": 5},  # Need 15
    "SKU-1003": {"min_stock": 10, "qty": 2, "code": "99"}, # Damaged
    "SKU-1004": {"min_stock": 12, "qty": 12}, # OK
    "SKU-2001": {"min_stock": 15, "qty": 8},  # Need 7
    "SKU-2002": {"min_stock": 50, "qty": 0, "code": "99"}, # Damaged, Need 50
    "SKU-2003": {"min_stock": 10, "qty": 22}, # OK
    "SKU-2004": {"min_stock": 40, "qty": 10}, # Need 30
    "SKU-3001": {"min_stock": 5, "qty": 4, "code": "99"},  # Damaged, Need 1
    "SKU-3002": {"min_stock": 10, "qty": 15}, # OK
    "SKU-3003": {"min_stock": 20, "qty": 2},  # Need 18
}
DAMAGED_SKUS = ["SKU-1003", "SKU-2002", "SKU-3001"]
# Calculate expected restock: 
# 1002(15) + 2001(7) + 2002(50) + 2004(30) + 3001(1) + 3003(18) = 121
EXPECTED_RESTOCK_TOTAL = 121

# ----------------------------------------------------------------
# 2. 初始化环境与 LLM 客户端
# ----------------------------------------------------------------
workspace = sys.argv[1] if len(sys.argv) > 1 else "."
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)
client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)

def llm_judge_content(prompt_text, file_content):
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict logistics data auditor. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[File Content]:\n{file_content}"}
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception:
        return False

# ----------------------------------------------------------------
# 3. 评分逻辑
# ----------------------------------------------------------------
score = 0
details = []

# A. 检查 damaged_report.json (50分)
damaged_path = os.path.join(workspace, "damaged_report.json")
if os.path.exists(damaged_path):
    try:
        with open(damaged_path, 'r', encoding='utf-8') as f:
            damaged_data = json.load(f)
        
        # 结构合法性 (10分)
        score += 10
        details.append({"item": "damaged_report.json 格式合法", "score": 10, "max_score": 10, "passed": True})
        
        # 成员准确性 (20分)
        found_skus = [item.get("sku") for item in damaged_data if isinstance(item, dict)]
        if set(found_skus) == set(DAMAGED_SKUS):
            score += 20
            details.append({"item": "损坏商品列表 SKU 匹配", "score": 20, "max_score": 20, "passed": True})
        else:
            details.append({"item": "损坏商品列表 SKU 不匹配", "score": 0, "max_score": 20, "passed": False, "reason": f"预期 {DAMAGED_SKUS}, 实际 {found_skus}"})
            
        # 语义与内容深度 (20分 - 使用 LLM)
        content_str = json.dumps(damaged_data)
        prompt = "Does this JSON contain human-readable names for the SKUs (like 'Glass Cleaner' or 'USB-C Cable') and explicitly mention they are 'damaged' or 'code 99'?"
        if llm_judge_content(prompt, content_str):
            score += 20
            details.append({"item": "利用大模型检查损坏报告内容丰富度", "score": 20, "max_score": 20, "passed": True})
        else:
            details.append({"item": "利用大模型检查损坏报告内容丰富度", "score": 0, "max_score": 20, "passed": False, "reason": "报告缺失商品名称或未明确标注损坏状态"})
            
    except Exception as e:
        details.append({"item": "damaged_report.json 解析失败", "score": 0, "max_score": 50, "passed": False, "reason": str(e)})
else:
    details.append({"item": "damaged_report.json 缺失", "score": 0, "max_score": 50, "passed": False})

# B. 检查 restock_summary.txt (50分)
restock_path = os.path.join(workspace, "restock_summary.txt")
if os.path.exists(restock_path):
    try:
        with open(restock_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        # 精准数值匹配 (40分)
        # 提取第一个数字进行比较
        import re
        numbers = re.findall(r'\d+', content)
        if numbers and int(numbers[0]) == EXPECTED_RESTOCK_TOTAL:
            score += 40
            details.append({"item": "补货总数计算准确", "score": 40, "max_score": 40, "passed": True})
        else:
            actual = numbers[0] if numbers else "None"
            details.append({"item": "补货总数计算错误", "score": 0, "max_score": 40, "passed": False, "reason": f"预期 {EXPECTED_RESTOCK_TOTAL}, 实际 {actual}"})
            
        # 格式简洁度 (10分)
        if len(content) < 50: # 预期只是一个数字或简短说明
            score += 10
            details.append({"item": "补货总结格式规范", "score": 10, "max_score": 10, "passed": True})
        else:
            details.append({"item": "补货总结过于冗余", "score": 5, "max_score": 10, "passed": False, "reason": "文件内容包含过多无关描述"})

    except Exception as e:
        details.append({"item": "restock_summary.txt 读取失败", "score": 0, "max_score": 50, "passed": False, "reason": str(e)})
else:
    details.append({"item": "restock_summary.txt 缺失", "score": 0, "max_score": 50, "passed": False})

# ----------------------------------------------------------------
# 4. 输出最终结果
# ----------------------------------------------------------------
output = {
    "total_score": score,
    "details": details
}
with open("workplace_score.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(json.dumps(output, indent=2))
