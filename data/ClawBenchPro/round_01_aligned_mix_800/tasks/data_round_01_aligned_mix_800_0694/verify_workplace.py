import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Initialize client, enforcing SSL bypass
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
    workspace_dir = os.path.join(workspace, "workspace")
    
    score_details = []
    total_score = 0

    # 1. Check workspace directory
    if os.path.isdir(workspace_dir):
        score_details.append({"item": "工作区目录 workspace 创建", "score": 5, "max_score": 5, "passed": True, "reason": "工作区目录已成功创建"})
        total_score += 5
    else:
        score_details.append({"item": "工作区目录 workspace 创建", "score": 0, "max_score": 5, "passed": False, "reason": "工作区目录未创建"})

    # 2. Check clean_catalog.json
    json_path = os.path.join(workspace_dir, "clean_catalog.json")
    json_valid = False
    records = []
    
    if os.path.isfile(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            json_valid = True
            
            # Recursive function to extract possible bead item dictionaries
            def traverse(node):
                if isinstance(node, list):
                    for i in node: traverse(i)
                elif isinstance(node, dict):
                    keys = [k.lower() for k in node.keys()]
                    # Identify item node based on typical fields
                    if any("bead" in k for k in keys) or any("price" in k for k in keys) or any("stock" in k for k in keys):
                        records.append(node)
                    else:
                        for v in node.values(): traverse(v)
            traverse(data)
            
            score_details.append({"item": "clean_catalog.json 存在且格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "JSON格式完全合法"})
            total_score += 10
        except Exception as e:
            score_details.append({"item": "clean_catalog.json 存在且格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"文件缺失或非合法JSON: {e}"})
    else:
        score_details.append({"item": "clean_catalog.json 存在且格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "clean_catalog.json 不存在"})

    if json_valid:
        # Check completeness
        if len(records) >= 8:
            score_details.append({"item": "JSON记录完整性", "score": 15, "max_score": 15, "passed": True, "reason": f"成功提取到 {len(records)} 条库存记录"})
            total_score += 15
        elif len(records) > 0:
            score_details.append({"item": "JSON记录完整性", "score": 5, "max_score": 15, "passed": False, "reason": f"提取到 {len(records)} 条记录，丢失了部分原始商品数据"})
            total_score += 5
        else:
            score_details.append({"item": "JSON记录完整性", "score": 0, "max_score": 15, "passed": False, "reason": "未能提取到有效的商品明细记录"})
            
        if len(records) > 0:
            norm_records = {}
            for r in records:
                item_id = None
                bead_type = None
                price = None
                for k, v in r.items():
                    k_low = k.lower()
                    if "id" in k_low or "item" in k_low:
                        item_id = str(v)
                    if "bead" in k_low or "type" in k_low or "name" in k_low:
                        bead_type = str(v)
                    if "price" in k_low or "cost" in k_low:
                        price = v
                if item_id: norm_records[item_id] = {"bead_type": bead_type, "price": price}
                elif bead_type: norm_records[bead_type] = {"bead_type": bead_type, "price": price}

            # Check Spacing inside BeadType strings
            spacing_clean = True
            for key, data in norm_records.items():
                bt = data["bead_type"]
                if bt is not None and isinstance(bt, str):
                    if bt != bt.strip():
                        spacing_clean = False
            
            if spacing_clean:
                score_details.append({"item": "BeadType名称前后空格清理", "score": 20, "max_score": 20, "passed": True, "reason": "有效去除了商品名称两端的杂乱空格"})
                total_score += 20
            else:
                score_details.append({"item": "BeadType名称前后空格清理", "score": 0, "max_score": 20, "passed": False, "reason": "商品名中仍包含未清洗的边缘空格（例如未 strip）"})
                
            # Check Price currency symbols and precise conversions
            price_clean = True
            price_accurate = True
            has_b002 = False
            has_b004 = False
            
            for key, data in norm_records.items():
                p = data["price"]
                if p is not None:
                    p_str = str(p).lower()
                    if "$" in p_str or "usd" in p_str:
                        price_clean = False
                    try:
                        p_val = float(p_str.replace("$","").replace("usd","").strip())
                        if "B002" in str(key):
                            has_b002 = True
                            if abs(p_val - 1.2) > 0.01:
                                price_accurate = False
                        if "B004" in str(key):
                            has_b004 = True
                            if abs(p_val - 15.0) > 0.01:
                                price_accurate = False
                    except:
                        price_clean = False
            
            if not has_b002 or not has_b004:
                price_accurate = False
            
            if price_clean:
                score_details.append({"item": "Price字段货币符号清理", "score": 15, "max_score": 15, "passed": True, "reason": "没有发现 $, USD 等冗余符号，被净化为纯数字格式"})
                total_score += 15
            else:
                score_details.append({"item": "Price字段货币符号清理", "score": 0, "max_score": 15, "passed": False, "reason": "Price 字段仍然包含字母/符号，或无法转换为浮点数"})

            if price_accurate and price_clean:
                 score_details.append({"item": "指定商品数值提取准确性", "score": 5, "max_score": 5, "passed": True, "reason": "B002 和 B004 的价格数值与预期完全匹配"})
                 total_score += 5
            else:
                 score_details.append({"item": "指定商品数值提取准确性", "score": 0, "max_score": 5, "passed": False, "reason": "特定商品价格数值提取错误或缺失"})

    else:
        score_details.append({"item": "JSON记录完整性", "score": 0, "max_score": 15, "passed": False, "reason": "JSON不存在或无法解析"})
        score_details.append({"item": "BeadType名称前后空格清理", "score": 0, "max_score": 20, "passed": False, "reason": "JSON不存在"})
        score_details.append({"item": "Price字段货币符号清理", "score": 0, "max_score": 15, "passed": False, "reason": "JSON不存在"})
        score_details.append({"item": "指定商品数值提取准确性", "score": 0, "max_score": 5, "passed": False, "reason": "JSON不存在"})

    # 3. Check amulet_cost.txt
    txt_path = os.path.join(workspace_dir, "amulet_cost.txt")
    if os.path.isfile(txt_path):
        score_details.append({"item": "amulet_cost.txt 文件创建", "score": 10, "max_score": 10, "passed": True, "reason": "文件已创建"})
        total_score += 10
        with open(txt_path, 'r', encoding='utf-8') as f:
            txt_content = f.read()
        
        if "47.4" in txt_content:
            prompt_text = "The user requested to calculate the total material cost for a specific recipe. The correct total is 47.40. Does the provided text clearly state that the total or final cost is exactly 47.4 or 47.40? (Minor formatting differences like $47.40 are acceptable). Please ensure it is presenting this number as the *total* or *final* result."
            is_correct = llm_judge_content(prompt_text, txt_content)
            if is_correct:
                score_details.append({"item": "总成本非结构化提取准确性", "score": 20, "max_score": 20, "passed": True, "reason": "LLM 鉴定确认正确得出了 $47.40 的最终材料花费"})
                total_score += 20
            else:
                score_details.append({"item": "总成本非结构化提取准确性", "score": 10, "max_score": 20, "passed": False, "reason": "文中包含 47.4，但大模型判定语义并未明确表示为总成本"})
                total_score += 10
        else:
             score_details.append({"item": "总成本非结构化提取准确性", "score": 0, "max_score": 20, "passed": False, "reason": "文本中没有包含正确的成本总计数字 47.4 或 47.40"})
    else:
        score_details.append({"item": "amulet_cost.txt 文件创建", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        score_details.append({"item": "总成本非结构化提取准确性", "score": 0, "max_score": 20, "passed": False, "reason": "文件不存在"})

    # Dump the result
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({
            "total_score": int(total_score),
            "details": score_details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
