import os
import sys
import json
import csv
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

def calculate_f1(expected_set, agent_set):
    """Calculate F1 score to assign partial credits for sets of items/tuples."""
    if not expected_set and not agent_set:
        return 1.0
    if not expected_set or not agent_set:
        return 0.0
    intersect = expected_set.intersection(agent_set)
    precision = len(intersect) / len(agent_set)
    recall = len(intersect) / len(expected_set)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    score_details = []
    total_score = 0
    
    # 1. Check Directory
    reports_dir = os.path.join(workspace, "reports")
    if os.path.isdir(reports_dir):
        score_details.append({"item": "检查 reports 目录是否存在", "score": 5, "max_score": 5, "passed": True, "reason": "reports 目录已成功创建"})
        total_score += 5
    else:
        score_details.append({"item": "检查 reports 目录是否存在", "score": 0, "max_score": 5, "passed": False, "reason": "reports 目录未创建"})
        
    # =====================================================================
    # GROUND TRUTH CALCULATION (Robust parsing to tolerate Agent fragmentation)
    # =====================================================================
    ref_schools = os.path.join(workspace, "reference/school_registry.json")
    ref_skus = os.path.join(workspace, "reference/sku_master.csv")
    req_dir = os.path.join(workspace, "requests")
    logs_dir = os.path.join(workspace, "warehouse_logs")
    
    school_map = {}
    try:
        with open(ref_schools, 'r', encoding='utf-8') as f:
            for s in json.load(f):
                school_map[s["school_code"]] = s["school_name"]
    except:
        pass
        
    item_to_sku = {}
    try:
        with open(ref_skus, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                item_to_sku[row["Item_Name"]] = row["SKU"]
    except:
        pass

    # Extract valid requests regardless of file extensions (to test Agent's robustness)
    approved_reqs = []
    try:
        for root, dirs, files in os.walk(req_dir):
            for file in files:
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, dict) and data.get("status") == "APPROVED":
                            approved_reqs.append(data)
                except:
                    pass
    except:
        pass

    # Process warehouse logs traversing deep nested structure
    net_shipped = {}
    try:
        for root, dirs, files in os.walk(logs_dir):
            for file in files:
                if file.endswith(".csv"):
                    path = os.path.join(root, file)
                    with open(path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            st = row.get("Status")
                            sc = row.get("School_Code")
                            sk = row.get("SKU")
                            try:
                                qt = int(row.get("Qty", 0))
                            except:
                                qt = 0
                            
                            # Net value calculation
                            if st == "SHIPPED":
                                net_shipped[(sc, sk)] = net_shipped.get((sc, sk), 0) + qt
                            elif st == "RETURNED":
                                net_shipped[(sc, sk)] = net_shipped.get((sc, sk), 0) - qt
    except:
        pass

    # Reconcile missing items & art schools
    expected_missing_items = {}
    expected_art_schools = set()
    
    for req in approved_reqs:
        s_code = req.get("school_code")
        s_name = school_map.get(s_code)
        if not s_name:
            continue
            
        has_art = False
        missing_for_school = {}
        for item, req_qty in req.get("requested_items", {}).items():
            if item in ["Acrylic Paint", "Blank Canvas"]:
                has_art = True
            
            sku = item_to_sku.get(item)
            if not sku:
                continue
                
            shipped = net_shipped.get((s_code, sku), 0)
            missing = req_qty - shipped
            if missing > 0:
                missing_for_school[item] = missing
                
        if missing_for_school:
            expected_missing_items[s_name] = missing_for_school
            
        if has_art:
            expected_art_schools.add(s_name)

    expected_schools_set = set(expected_missing_items.keys())
    expected_tuples = set()
    for s_name, items in expected_missing_items.items():
        for i_name, qty in items.items():
            expected_tuples.add((s_name, i_name, qty))

    # =====================================================================
    # AGENT EVALUATION - missing_items.json
    # =====================================================================
    missing_json_path = os.path.join(reports_dir, "missing_items.json")
    agent_missing = None
    if os.path.isfile(missing_json_path):
        try:
            with open(missing_json_path, 'r', encoding='utf-8') as f:
                agent_missing = json.load(f)
            score_details.append({"item": "检查 missing_items.json", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在且为合法 JSON"})
            total_score += 10
        except Exception as e:
            score_details.append({"item": "检查 missing_items.json", "score": 0, "max_score": 10, "passed": False, "reason": f"解析 JSON 失败: {e}"})
    else:
        score_details.append({"item": "检查 missing_items.json", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失"})

    if agent_missing is not None and isinstance(agent_missing, dict):
        agent_schools_set = set(agent_missing.keys())
        agent_tuples = set()
        for s_name, items in agent_missing.items():
            if isinstance(items, dict):
                for k, v in items.items():
                    try:
                        agent_tuples.add((str(s_name), str(k), int(v)))
                    except:
                        pass
        
        # Exact School Matching via F1 Score
        school_f1 = calculate_f1(expected_schools_set, agent_schools_set)
        s_score = int(round(school_f1 * 20))
        total_score += s_score
        score_details.append({"item": "校验缺失学校名单匹配度", "score": s_score, "max_score": 20, "passed": s_score == 20, "reason": f"学校集合精准匹配度 F1 Score: {school_f1:.2f}"})
        
        # Granular Items Matching via F1 Score
        item_f1 = calculate_f1(expected_tuples, agent_tuples)
        i_score = int(round(item_f1 * 30))
        total_score += i_score
        score_details.append({"item": "校验缺失物品级明细匹配度", "score": i_score, "max_score": 30, "passed": i_score == 30, "reason": f"明细元组精准匹配度 F1 Score: {item_f1:.2f}"})
    else:
        score_details.append({"item": "校验缺失学校名单匹配度", "score": 0, "max_score": 20, "passed": False, "reason": "未获取到有效目标 JSON 数据"})
        score_details.append({"item": "校验缺失物品级明细匹配度", "score": 0, "max_score": 30, "passed": False, "reason": "未获取到有效目标 JSON 数据"})

    # =====================================================================
    # AGENT EVALUATION - art_schools.txt
    # =====================================================================
    art_txt_path = os.path.join(reports_dir, "art_schools.txt")
    agent_art_schools = set()
    txt_content = ""
    if os.path.isfile(art_txt_path):
        score_details.append({"item": "检查 art_schools.txt", "score": 5, "max_score": 5, "passed": True, "reason": "文件存在"})
        total_score += 5
        try:
            with open(art_txt_path, 'r', encoding='utf-8') as f:
                txt_content = f.read()
                for line in txt_content.splitlines():
                    val = line.strip()
                    # Strip possible markdown list bullets to be lenient
                    if val.startswith("- "): val = val[2:]
                    if val.startswith("* "): val = val[2:]
                    if val:
                        agent_art_schools.add(val)
        except:
            pass
    else:
        score_details.append({"item": "检查 art_schools.txt", "score": 0, "max_score": 5, "passed": False, "reason": "文件缺失"})
        
    if os.path.isfile(art_txt_path):
        art_f1 = calculate_f1(expected_art_schools, agent_art_schools)
        a_score = int(round(art_f1 * 20))
        total_score += a_score
        score_details.append({"item": "美术学校黑名单匹配度", "score": a_score, "max_score": 20, "passed": a_score == 20, "reason": f"名单精准匹配度 F1 Score: {art_f1:.2f}"})
        
        # Strict semantic validation for conversational fillers via LLM
        prompt = "Check if the provided text is strictly a clean list of school names without ANY conversational filler, extra paragraphs, or markdown headers (e.g. 'Here are the schools:'). It should just be the pure names separated by newlines."
        is_clean = llm_judge_content(prompt, txt_content)
        l_score = 10 if is_clean else 0
        total_score += l_score
        score_details.append({"item": "利用大模型验证文本纯度 (无幻觉/废话)", "score": l_score, "max_score": 10, "passed": is_clean, "reason": "纯净文本" if is_clean else "包含寒暄、无关文本或严重格式冗余"})
    else:
        score_details.append({"item": "美术学校黑名单匹配度", "score": 0, "max_score": 20, "passed": False, "reason": "文件缺失"})
        score_details.append({"item": "利用大模型验证文本纯度 (无幻觉/废话)", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失"})

    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding='utf-8') as f:
        json.dump({
            "total_score": total_score,
            "details": score_details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
