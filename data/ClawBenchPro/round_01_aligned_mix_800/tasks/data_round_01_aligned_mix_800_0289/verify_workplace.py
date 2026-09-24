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

def check_ingredient_quantity(text, keywords, expected_numbers):
    """
    严禁简单的模糊匹配。
    提取文中所有数字，并验证其是否与指定的食材关键词在一定字符距离（上下文窗口）内成对出现。
    且数字的浮点值必须完全精确匹配 expected_numbers。
    """
    text_lower = text.lower()
    number_matches = list(re.finditer(r'\b\d+(?:\.\d+)?\b', text_lower))
    
    for kw in keywords:
        kw_lower = kw.lower()
        # 查找关键词所有出现的位置
        kw_starts = [m.start() for m in re.finditer(re.escape(kw_lower), text_lower)]
        
        for start_idx in kw_starts:
            for nm in number_matches:
                # 检查数字与关键词的距离是否在 80 个字符以内（同一行或相邻上下文中）
                if abs(nm.start() - start_idx) <= 80:
                    try:
                        num_val = float(nm.group())
                        for exp in expected_numbers:
                            if abs(num_val - exp) < 0.001:
                                return True
                    except ValueError:
                        continue
    return False

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_path = os.path.join(workspace, "deliverables")
    
    details = []
    total_score = 0
    
    # Check 1: Deliverables Directory (5 pts)
    dir_exists = os.path.exists(deliverables_path) and os.path.isdir(deliverables_path)
    if dir_exists:
        details.append({"item": "检查结果目录是否存在", "score": 5, "max_score": 5, "passed": True, "reason": "`deliverables` 目录存在"})
        total_score += 5
    else:
        details.append({"item": "检查结果目录是否存在", "score": 0, "max_score": 5, "passed": False, "reason": "`deliverables` 目录不存在"})
    
    # Check 2: Report File (5 pts)
    report_content = ""
    file_exists = False
    if dir_exists:
        files = os.listdir(deliverables_path)
        if len(files) > 0:
            file_exists = True
            try:
                with open(os.path.join(deliverables_path, files[0]), "r", encoding="utf-8") as f:
                    report_content = f.read()
                details.append({"item": "检查报告文件是否存在", "score": 5, "max_score": 5, "passed": True, "reason": f"找到报告文件: {files[0]}"})
                total_score += 5
            except Exception as e:
                details.append({"item": "检查报告文件是否存在", "score": 0, "max_score": 5, "passed": False, "reason": f"无法读取报告文件: {e}"})
        else:
            details.append({"item": "检查报告文件是否存在", "score": 0, "max_score": 5, "passed": False, "reason": "`deliverables` 目录为空"})
    else:
        details.append({"item": "检查报告文件是否存在", "score": 0, "max_score": 5, "passed": False, "reason": "缺少父级目录"})

    if file_exists and report_content.strip():
        # Check 3: LLM Semantic - Tone and Formatting (10 pts)
        prompt_tone = "Does this text represent a clear, formal shopping and prep list appropriate for a sous-chef reporting to a busy cook? It should NOT be a raw JSON dump or informal messy notes."
        if llm_judge_content(prompt_tone, report_content):
            details.append({"item": "大模型检查语义语气", "score": 10, "max_score": 10, "passed": True, "reason": "语气得体且格式清晰正式"})
            total_score += 10
        else:
            details.append({"item": "大模型检查语义语气", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定内容不符合正式报告清单的要求"})

        # Check 4: LLM Semantic - Guest Logic (20 pts)
        prompt_guest = "Does this text explicitly mention or confirm that exactly 19 regular guests (or 19 portions) are being accounted for? (Excluding vegans/gluten-free)."
        if llm_judge_content(prompt_guest, report_content):
            details.append({"item": "大模型检查就餐人数逻辑", "score": 20, "max_score": 20, "passed": True, "reason": "正确指出了 19 名普通食客"})
            total_score += 20
        else:
            details.append({"item": "大模型检查就餐人数逻辑", "score": 0, "max_score": 20, "passed": False, "reason": "未正确指出或未提及 19 名普通食客，过滤逻辑失败"})

        # Check 5: Strict Math - Tortillas (15 pts) (Needs 37)
        if check_ingredient_quantity(report_content, ["tortilla", "tortillas"], [37, 37.0]):
            details.append({"item": "精准数值提取: 需购买的玉米饼数量", "score": 15, "max_score": 15, "passed": True, "reason": "成功提取并匹配准确数值 (37)"})
            total_score += 15
        else:
            details.append({"item": "精准数值提取: 需购买的玉米饼数量", "score": 0, "max_score": 15, "passed": False, "reason": "未能从上下文中提取到正确的玉米饼购买数量 (应为 37)"})

        # Check 6: Strict Math - Chicken (15 pts) (Needs 8.0 lbs)
        if check_ingredient_quantity(report_content, ["chicken", "pollo", "lbs", "pound"], [8, 8.0]):
            details.append({"item": "精准数值提取: 需购买的鸡肉重量", "score": 15, "max_score": 15, "passed": True, "reason": "成功提取并匹配准确数值 (8.0)"})
            total_score += 15
        else:
            details.append({"item": "精准数值提取: 需购买的鸡肉重量", "score": 0, "max_score": 15, "passed": False, "reason": "未能从上下文中提取到正确的鸡肉购买数量 (应为 8.0)"})

        # Check 7: Strict Math - Cheese (15 pts) (Needs 66.0 oz)
        if check_ingredient_quantity(report_content, ["cheese", "queso", "oz", "ounce"], [66, 66.0]):
            details.append({"item": "精准数值提取: 需购买的奶酪重量", "score": 15, "max_score": 15, "passed": True, "reason": "成功提取并匹配准确数值 (66.0)"})
            total_score += 15
        else:
            details.append({"item": "精准数值提取: 需购买的奶酪重量", "score": 0, "max_score": 15, "passed": False, "reason": "未能从上下文中提取到正确的奶酪购买数量 (应为 66.0)"})

        # Check 8: Strict Math - Sauce (15 pts) (Needs 2.75 cans)
        if check_ingredient_quantity(report_content, ["sauce", "salsa", "can", "cans"], [2.75]):
            details.append({"item": "精准数值提取: 需购买的酱汁罐数", "score": 15, "max_score": 15, "passed": True, "reason": "成功提取并匹配准确数值 (2.75)"})
            total_score += 15
        else:
            details.append({"item": "精准数值提取: 需购买的酱汁罐数", "score": 0, "max_score": 15, "passed": False, "reason": "未能从上下文中提取到正确的酱汁购买数量 (应为 2.75)"})
    else:
        # If no file exists, auto-fail semantic and math checks
        for item_name, max_val in [("大模型检查语义语气", 10), ("大模型检查就餐人数逻辑", 20), 
                                   ("精准数值提取: 需购买的玉米饼数量", 15), ("精准数值提取: 需购买的鸡肉重量", 15), 
                                   ("精准数值提取: 需购买的奶酪重量", 15), ("精准数值提取: 需购买的酱汁罐数", 15)]:
            details.append({"item": item_name, "score": 0, "max_score": max_val, "passed": False, "reason": "由于报告文件不存在或为空，跳过此项检查"})

    result_json = {
        "total_score": total_score,
        "details": details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result_json, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    verify()
