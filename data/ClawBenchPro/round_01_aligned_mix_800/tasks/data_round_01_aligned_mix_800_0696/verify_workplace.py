import os
import sys
import json
import re
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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    score_details = []
    total_score = 0
    
    damaged_report_path = os.path.join(workspace, "damaged_report.json")
    restock_summary_path = os.path.join(workspace, "restock_summary.txt")
    
    # Check 1: damaged_report.json 存在且为有效 JSON (10 points)
    damaged_exists_and_valid = False
    damaged_data = None
    if os.path.exists(damaged_report_path):
        try:
            with open(damaged_report_path, "r", encoding="utf-8") as f:
                damaged_data = json.load(f)
            damaged_exists_and_valid = True
            score_details.append({"item": "damaged_report.json 存在且格式正确", "score": 10, "max_score": 10, "passed": True, "reason": "成功读取并解析 JSON。"})
            total_score += 10
        except json.JSONDecodeError:
            score_details.append({"item": "damaged_report.json 存在且格式正确", "score": 0, "max_score": 10, "passed": False, "reason": "文件存在但不是合法的 JSON。"})
    else:
        score_details.append({"item": "damaged_report.json 存在且格式正确", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在。"})

    # Check 2 & 3: damaged_report.json 数据准确性 (总计 40 points)
    if damaged_exists_and_valid and isinstance(damaged_data, list):
        # We expect exactly 3 items: SKU-1003, SKU-2002, SKU-3001
        expected_skus = {"SKU-1003", "SKU-2002", "SKU-3001"}
        
        # 提取数据中的所有 SKU，兼容大小写和嵌套结构
        found_skus = set()
        for item in damaged_data:
            if isinstance(item, dict):
                # 尝试多种可能的键名
                sku_val = item.get("sku") or item.get("SKU") or item.get("id")
                if sku_val:
                    found_skus.add(str(sku_val).upper())

        # 检查数量是否刚好等于3 (10 points)
        if len(damaged_data) == 3:
            score_details.append({"item": "damaged_report.json 记录数量正确", "score": 10, "max_score": 10, "passed": True, "reason": "恰好包含 3 条记录。"})
            total_score += 10
        else:
            score_details.append({"item": "damaged_report.json 记录数量正确", "score": 0, "max_score": 10, "passed": False, "reason": f"包含 {len(damaged_data)} 条记录，期望 3 条。"})

        # 检查 SKU 集合是否完全匹配 (30 points)
        if found_skus == expected_skus:
            score_details.append({"item": "damaged_report.json 包含准确的破损物品", "score": 30, "max_score": 30, "passed": True, "reason": "精准提取了所有的 damaged SKU，无遗漏无幻觉。"})
            total_score += 30
        else:
            missing = expected_skus - found_skus
            extra = found_skus - expected_skus
            reason_str = f"SKU 匹配失败。缺失: {missing}, 多余: {extra}"
            score_details.append({"item": "damaged_report.json 包含准确的破损物品", "score": 0, "max_score": 30, "passed": False, "reason": reason_str})
    elif damaged_exists_and_valid:
        score_details.append({"item": "damaged_report.json 根节点应为列表", "score": 0, "max_score": 40, "passed": False, "reason": "JSON 格式非预期列表形态，无法提取正确信息。"})
    else:
        score_details.append({"item": "damaged_report.json 数据准确性", "score": 0, "max_score": 40, "passed": False, "reason": "未找到有效的 JSON 文件。"})

    # Check 4: restock_summary.txt 存在 (10 points)
    restock_exists = False
    restock_content = ""
    if os.path.exists(restock_summary_path):
        restock_exists = True
        with open(restock_summary_path, "r", encoding="utf-8") as f:
            restock_content = f.read().strip()
        score_details.append({"item": "restock_summary.txt 存在", "score": 10, "max_score": 10, "passed": True, "reason": "找到了 restock_summary.txt 文件。"})
        total_score += 10
    else:
        score_details.append({"item": "restock_summary.txt 存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 restock_summary.txt 文件。"})

    # Check 5: restock_summary.txt 的计算数值准确度 (40 points)
    # The expected total quantity is:
    # 1002: 20-5=15
    # 1003: 10-2=8
    # 2001: 15-8=7
    # 2002: 50-0=50
    # 2004: 40-10=30
    # 3001: 5-4=1
    # 3003: 20-2=18
    # Sum = 15+8+7+50+30+1+18 = 129
    if restock_exists:
        # Extract all numbers
        numbers = re.findall(r'\d+', restock_content)
        if "129" in numbers:
            # 严格模式：如果只包含 129（即用户听从了 'just put that single total number'）
            if len(numbers) == 1 and restock_content == "129":
                score_details.append({"item": "restock_summary.txt 数值计算正确且格式完美", "score": 40, "max_score": 40, "passed": True, "reason": "精确输出了 '129' 且无冗余字符。"})
                total_score += 40
            else:
                score_details.append({"item": "restock_summary.txt 数值计算正确", "score": 30, "max_score": 40, "passed": True, "reason": "包含了正确的数值 129，但包含多余文本或数字（未遵守 single total number 约束）。"})
                total_score += 30
        else:
            score_details.append({"item": "restock_summary.txt 数值计算正确", "score": 0, "max_score": 40, "passed": False, "reason": f"计算错误，预期 129，实际找到的数字为: {numbers}"})
    else:
         score_details.append({"item": "restock_summary.txt 数值计算正确", "score": 0, "max_score": 40, "passed": False, "reason": "未找到文件。"})

    # Save to result
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    verify()
