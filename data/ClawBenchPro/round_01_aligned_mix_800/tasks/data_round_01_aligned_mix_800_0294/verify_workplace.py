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

def verify_workplace(workspace):
    details = []
    total_score = 0
    workspace_dir = os.path.join(workspace, "workspace")
    catalog_path = os.path.join(workspace_dir, "clean_catalog.json")
    summary_path = os.path.join(workspace_dir, "amulet_cost.txt")

    # 1. Check Directory Existence (10 points)
    if os.path.exists(workspace_dir) and os.path.isdir(workspace_dir):
        details.append({"item": "检查 workspace 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "workspace 目录存在"})
        total_score += 10
    else:
        details.append({"item": "检查 workspace 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "workspace 目录不存在"})
    
    # 2. Check JSON File Existence & Validity (15 points)
    catalog_data = None
    if os.path.exists(catalog_path):
        try:
            with open(catalog_path, 'r', encoding='utf-8') as f:
                catalog_data = json.load(f)
            details.append({"item": "检查 clean_catalog.json 是否为合法JSON", "score": 15, "max_score": 15, "passed": True, "reason": "成功解析JSON格式"})
            total_score += 15
        except Exception as e:
            details.append({"item": "检查 clean_catalog.json 是否为合法JSON", "score": 0, "max_score": 15, "passed": False, "reason": f"JSON解析失败: {e}"})
    else:
        details.append({"item": "检查 clean_catalog.json 是否为合法JSON", "score": 0, "max_score": 15, "passed": False, "reason": "文件不存在"})

    # 3. Check JSON Structure & Strict Normalized Pricing (25 points)
    if catalog_data:
        try:
            items = catalog_data if isinstance(catalog_data, list) else catalog_data.get('items', catalog_data.get('inventory', []))
            if not items and isinstance(catalog_data, dict):
                items = list(catalog_data.values())
            
            price_map = {}
            for item in items:
                if not isinstance(item, dict): continue
                # Extract bead type name loosely but check prices strictly
                name = item.get('BeadType') or item.get('name') or item.get('ItemID') or str(item)
                price_val = item.get('Price') or item.get('price') or item.get('Price (USD)') or item.get('USD_Price')
                
                if isinstance(price_val, str):
                    clean_price = re.sub(r'[^\d.]', '', price_val)
                    price_val = float(clean_price) if clean_price else 0.0
                
                name_clean = re.sub(r'\s+', '', str(name).lower())
                price_map[name_clean] = float(price_val)

            # Expected normalized USD prices
            # Kingman Turquoise: 6.00 CAD * 0.75 = 4.5
            # Red Coral: 15.00 MXN * 0.05 = 0.75
            # Cedar Pendant: 15.00 USD = 15.0
            
            passed = True
            reason = "关键商品 USD 价格换算和提取全部正确"
            
            if not any("kingmanturquoise" in k for k in price_map):
                passed, reason = False, "缺少 Kingman Turquoise 记录"
            elif not any("kingmanturquoise" in k and price_map[k] == 4.5 for k in price_map):
                passed, reason = False, "Kingman Turquoise 的价格换算错误 (应为 4.50 USD)"

            elif not any("redcoral" in k for k in price_map):
                passed, reason = False, "缺少 Red Coral 记录"
            elif not any("redcoral" in k and price_map[k] == 0.75 for k in price_map):
                passed, reason = False, "Red Coral 的价格换算错误 (应为 0.75 USD)"
                
            elif not any("cedarpendant" in k and price_map[k] == 15.0 for k in price_map):
                passed, reason = False, "Cedar Pendant 的价格错误 (应为 15.0 USD)"

            if passed:
                details.append({"item": "检查 JSON 数据的价格单位归一化和换算精准度", "score": 25, "max_score": 25, "passed": True, "reason": reason})
                total_score += 25
            else:
                details.append({"item": "检查 JSON 数据的价格单位归一化和换算精准度", "score": 0, "max_score": 25, "passed": False, "reason": reason})
        except Exception as e:
            details.append({"item": "检查 JSON 数据的价格单位归一化和换算精准度", "score": 0, "max_score": 25, "passed": False, "reason": f"解析异常: {e}"})
    else:
         details.append({"item": "检查 JSON 数据的价格单位归一化和换算精准度", "score": 0, "max_score": 25, "passed": False, "reason": "缺少 JSON 数据支持解析"})

    # 4. Check TXT File Existence (10 points)
    summary_text = ""
    if os.path.exists(summary_path):
        with open(summary_path, 'r', encoding='utf-8') as f:
            summary_text = f.read()
        details.append({"item": "检查 amulet_cost.txt 文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
    else:
        details.append({"item": "检查 amulet_cost.txt 文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})

    # 5. Check Exact Math Result in TXT (25 points)
    if summary_text:
        # Expected: 5*4.5 + 2*1.20 + 10*0.75 + 1*15.00 = 22.50 + 2.40 + 7.50 + 15.00 = 47.40
        numbers = re.findall(r'\d+\.\d+', summary_text)
        if any(abs(float(n) - 47.40) < 0.001 for n in numbers):
            details.append({"item": "检查最终材料 BOM 成本计算结果", "score": 25, "max_score": 25, "passed": True, "reason": "准确提取且计算出了总成本 47.40"})
            total_score += 25
        else:
            details.append({"item": "检查最终材料 BOM 成本计算结果", "score": 0, "max_score": 25, "passed": False, "reason": "计算结果错误或未找到浮点数 47.40"})
    else:
        details.append({"item": "检查最终材料 BOM 成本计算结果", "score": 0, "max_score": 25, "passed": False, "reason": "内容为空"})

    # 6. LLM Check for Unstructured Natural Language Completeness (15 points)
    if summary_text:
        prompt = "Does the text below clearly state that it is a summary or cost calculation for the 'Salish Sea Amulet' (or similar context) and mention that the currency is USD?"
        if llm_judge_content(prompt, summary_text):
            details.append({"item": "利用大模型检查文本语义完整性", "score": 15, "max_score": 15, "passed": True, "reason": "文本提到了 Amulet 并标注了 USD 单位"})
            total_score += 15
        else:
            details.append({"item": "利用大模型检查文本语义完整性", "score": 0, "max_score": 15, "passed": False, "reason": "文本缺失必要的上下文（未提及 Amulet 或 USD）"})
    else:
        details.append({"item": "利用大模型检查文本语义完整性", "score": 0, "max_score": 15, "passed": False, "reason": "无内容可供大模型评估"})

    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    work_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    verify_workplace(work_dir)
