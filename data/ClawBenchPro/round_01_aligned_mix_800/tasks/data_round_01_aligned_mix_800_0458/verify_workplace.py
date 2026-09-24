import os
import sys
import json
import csv
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
    """大模型处理非结构化文本的统一接口，验证 ASCII 星号要求"""
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

def generate_expected_truth(workspace):
    """计算绝对的正确答案"""
    base_dir = os.path.join(workspace, 'supplier_dumps')
    config_dir = os.path.join(base_dir, 'system_config')
    
    # 解析字典
    cat_map = {}
    cat_path = os.path.join(config_dir, 'category_map.json')
    if os.path.exists(cat_path):
        with open(cat_path, 'r', encoding='utf-8') as f:
            cat_map = json.load(f)
            
    status_map = {}
    status_path = os.path.join(config_dir, 'status_codes.csv')
    if os.path.exists(status_path):
        with open(status_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                status_map[str(row['code'])] = row['meaning']
                
    expected_items = {}
    category_totals = {"Solar": 0.0, "Wind": 0.0, "Hydroponic": 0.0}
    
    # 遍历且严格按照年份进行剪枝
    for root, dirs, files in os.walk(base_dir):
        if 'system_config' in root:
            continue
            
        is_2024 = False
        path_parts = root.split(os.sep)
        for part in path_parts:
            if part.startswith('2024'):
                is_2024 = True
                break
        if not is_2024:
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            data = None
            if file.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                    except:
                        pass
            elif file.endswith('.csv'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        reader = csv.DictReader(f)
                        data = next(reader)
                    except:
                        pass
            if not data: continue
                
            cat_code = data.get('cat_code', '')
            status_code = str(data.get('status_code', ''))
            raw_cost = data.get('cost', '')
            
            trans_cat = cat_map.get(cat_code, 'Unknown')
            trans_status = status_map.get(status_code, 'Unknown')
            
            # 数据清洗：价格转换剔除非数字字符
            cost_str = str(raw_cost).strip()
            if not cost_str:
                price = -1.0
            else:
                cleaned_str = re.sub(r'[^\d\.-]', '', cost_str)
                try:
                    price = float(cleaned_str)
                except:
                    price = -1.0
                    
            # Non-negotiable rules
            if trans_cat not in ["Solar", "Wind", "Hydroponic"]: continue
            if trans_status == "Damaged": continue
            if price < 0: continue
                
            expected_items[data['id']] = {
                "id": data['id'],
                "category": trans_cat,
                "status": trans_status,
                "price": price
            }
            category_totals[trans_cat] += price
            
    return expected_items, category_totals

def extract_agent_items(data):
    """兼容提取 Agent 生成的 JSON 数据格式"""
    items = {}
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and 'id' in item:
                items[item['id']] = item
    elif isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, list):
                for item in v:
                    if isinstance(item, dict) and 'id' in item:
                        items[item['id']] = item
    return items

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    details = []
    total_score = 0
    
    project_brief = os.path.join(workspace, 'project_brief')
    usable_path = os.path.join(project_brief, 'usable_equipment.json')
    cost_path = os.path.join(project_brief, 'cost_chart.txt')
    
    brief_exists = os.path.isdir(project_brief)
    usable_exists = os.path.isfile(usable_path)
    cost_exists = os.path.isfile(cost_path)
    
    # Check 1: Files Existence (10)
    basic_score = (2 if brief_exists else 0) + (4 if usable_exists else 0) + (4 if cost_exists else 0)
    details.append({"item": "Base output directory & files existence", "score": basic_score, "max_score": 10, "passed": basic_score == 10, "reason": f"Dir: {brief_exists}, JSON: {usable_exists}, TXT: {cost_exists}"})
    total_score += basic_score
    
    if not brief_exists:
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return
        
    expected_items, expected_totals = generate_expected_truth(workspace)
    
    # Check 2: JSON Parsing (10)
    agent_data = None
    json_valid_score = 0
    if usable_exists:
        try:
            with open(usable_path, 'r', encoding='utf-8') as f:
                agent_data = json.load(f)
            json_valid_score = 10
            details.append({"item": "usable_equipment.json valid format", "score": 10, "max_score": 10, "passed": True, "reason": "Successfully parsed JSON"})
        except Exception as e:
            details.append({"item": "usable_equipment.json valid format", "score": 0, "max_score": 10, "passed": False, "reason": f"Parse failed: {e}"})
    else:
        details.append({"item": "usable_equipment.json format", "score": 0, "max_score": 10, "passed": False, "reason": "File missing"})
    total_score += json_valid_score
    
    # Check 3: Data Filtering Logic Precision/Recall - F1 Score (40)
    f1_score_val = 0
    common_ids = set()
    if agent_data is not None:
        agent_items = extract_agent_items(agent_data)
        exp_ids = set(expected_items.keys())
        agt_ids = set(agent_items.keys())
        
        tp = exp_ids.intersection(agt_ids)
        
        precision = len(tp) / len(agt_ids) if agt_ids else 0
        recall = len(tp) / len(exp_ids) if exp_ids else 0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        f1_score_val = int(40 * f1)
        common_ids = tp
        
        details.append({"item": "Filtering Accuracy (F1 Score) of items", "score": f1_score_val, "max_score": 40, "passed": f1_score_val == 40, "reason": f"Expected: {len(exp_ids)}, Agent: {len(agt_ids)}, Match: {len(tp)}. F1: {f1:.3f}"})
    else:
        details.append({"item": "Filtering Accuracy (F1 Score)", "score": 0, "max_score": 40, "passed": False, "reason": "No valid data"})
    total_score += f1_score_val
    
    # Check 4: Field Value Correctness (10)
    field_score = 0
    if common_ids:
        correct_count = 0
        sample_size = min(5, len(common_ids))
        for cid in list(common_ids)[:sample_size]:
            exp = expected_items[cid]
            agt = agent_items[cid]
            
            agt_values = [str(v).lower() for v in agt.values()]
            cat_match = any(exp['category'].lower() in v for v in agt_values)
            status_match = any(exp['status'].lower() in v for v in agt_values)
            price_match = False
            for v in agt.values():
                try:
                    if abs(float(v) - exp['price']) < 0.01:
                        price_match = True; break
                except: pass
            
            if cat_match and status_match and price_match:
                correct_count += 1
                
        field_score = int((correct_count / sample_size) * 10)
        details.append({"item": "Internal field translation & cleaning logic", "score": field_score, "max_score": 10, "passed": field_score == 10, "reason": f"{correct_count}/{sample_size} sample items fully verified"})
    else:
        details.append({"item": "Internal field correctly translated", "score": 0, "max_score": 10, "passed": False, "reason": "No matching elements to sample"})
    total_score += field_score
    
    # Check 5 & 6: Chart Generation & Format (20 + 10)
    if cost_exists:
        try:
            with open(cost_path, 'r', encoding='utf-8') as f:
                chart_text = f.read()
                
            def extract_cat_cost(text, category):
                for line in text.split('\n'):
                    if category.lower() in line.lower():
                        matches = re.findall(r'\d{1,3}(?:,\d{3})*(?:\.\d+)?', line)
                        if matches: return float(matches[-1].replace(',', ''))
                return None
                
            s_val = extract_cat_cost(chart_text, "Solar")
            w_val = extract_cat_cost(chart_text, "Wind")
            h_val = extract_cat_cost(chart_text, "Hydroponic")
            
            val_score = 0
            if s_val is not None and abs(s_val - expected_totals["Solar"]) <= 1.0: val_score += 6
            if w_val is not None and abs(w_val - expected_totals["Wind"]) <= 1.0: val_score += 7
            if h_val is not None and abs(h_val - expected_totals["Hydroponic"]) <= 1.0: val_score += 7
            
            details.append({"item": "cost_chart.txt totals exact accuracy", "score": val_score, "max_score": 20, "passed": val_score == 20, "reason": f"S:{s_val}(exp:{expected_totals['Solar']:.2f}) | W:{w_val} | H:{h_val}"})
            total_score += val_score
            
            prompt_text = "Does the text below represent an ASCII-style bar chart showing costs grouped by 'Solar', 'Wind', and 'Hydroponic'? Does it use asterisks '*' visually to represent every full 1,000 in the category total? (e.g. $4500 should have 4 asterisks)."
            is_valid_format = llm_judge_content(prompt_text, chart_text)
            llm_score = 10 if is_valid_format else 0
            details.append({"item": "cost_chart.txt ASCII format adherence (LLM Verification)", "score": llm_score, "max_score": 10, "passed": is_valid_format, "reason": f"LLM Judges: {'YES' if is_valid_format else 'NO'}"})
            total_score += llm_score
            
        except Exception as e:
            details.append({"item": "cost_chart.txt checks", "score": 0, "max_score": 30, "passed": False, "reason": f"Error: {e}"})
    else:
        details.append({"item": "cost_chart.txt checks", "score": 0, "max_score": 30, "passed": False, "reason": "Missing"})
        
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    main()
