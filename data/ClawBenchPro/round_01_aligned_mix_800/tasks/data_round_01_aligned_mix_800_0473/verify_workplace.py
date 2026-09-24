import os
import sys
import json
import csv
import re
from datetime import datetime
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

def get_ground_truth(workspace):
    """动态重跑正确的计算逻辑，获得当前随机种子下的确切结果作为基准。"""
    # 1. 计算支出 (Expenses)
    total_expenses = 0.0
    vendor_path = os.path.join(workspace, "reference", "vendor_catalog.json")
    outdoor_vendors = set()
    if os.path.exists(vendor_path):
        with open(vendor_path, "r", encoding="utf-8") as f:
            try:
                vendors = json.load(f)
                outdoor_vendors = {k for k, v in vendors.items() if v.get("category") in ["Hiking", "Camping"]}
            except Exception:
                pass

    receipts_dir = os.path.join(workspace, "receipts")
    if os.path.exists(receipts_dir):
        for file in os.listdir(receipts_dir):
            if file.endswith(".csv"):
                with open(os.path.join(receipts_dir, file), "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row.get("Status") == "CLEARED" and row.get("Vendor_Code") in outdoor_vendors:
                            try:
                                total_expenses += float(row["Amount"])
                            except Exception:
                                pass

    # 2. 计算木材 (Wood Inventory)
    latest_inventories = {}
    notes_dir = os.path.join(workspace, "workshop_notes")
    if os.path.exists(notes_dir):
        for root, _, files in os.walk(notes_dir):
            for file in files:
                if file.endswith(".md"):
                    with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                        content = f.read()
                        if content.startswith("---\n"):
                            parts = content.split("---\n", 2)
                            if len(parts) >= 3:
                                fm = parts[1]
                                body = parts[2]
                                
                                fm_dict = {}
                                for line in fm.split("\n"):
                                    if ":" in line:
                                        k, v = line.split(":", 1)
                                        fm_dict[k.strip()] = v.strip().strip('"')
                                
                                if fm_dict.get("type") == "inventory":
                                    loc = fm_dict.get("location")
                                    date_str = fm_dict.get("date")
                                    if date_str and loc:
                                        try:
                                            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                                            if loc not in latest_inventories or dt > latest_inventories[loc]["dt"]:
                                                latest_inventories[loc] = {"dt": dt, "body": body}
                                        except Exception:
                                            pass

    good_wood = {}
    for loc, data in latest_inventories.items():
        body = data["body"]
        for line in body.split("\n"):
            m = re.match(r"-\s+(.+)\s+board:\s+(\d+)\s+\[Condition:\s+(.+)\]", line.strip())
            if m:
                w_type = m.group(1).strip()
                count = int(m.group(2))
                cond = m.group(3).strip()
                if cond == "Good":
                    good_wood[w_type] = good_wood.get(w_type, 0) + count
                    
    return round(total_expenses, 2), good_wood

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    target_file = os.path.join(workspace, "plans", "budget_and_materials_summary.json")
    ground_truth_expenses, ground_truth_wood = get_ground_truth(workspace)
    
    # Check 1: 文件及目录存在性 (10 points)
    if os.path.exists(target_file):
        score_details.append({"item": "文件路径与存在性", "score": 10, "max_score": 10, "passed": True, "reason": "文件 plans/budget_and_materials_summary.json 存在"})
        total_score += 10
    else:
        score_details.append({"item": "文件路径与存在性", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 plans/budget_and_materials_summary.json"})
        
        # 写入直接失败的结果
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": score_details}, f, indent=2)
        return

    # Load JSON
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            user_data = json.load(f)
    except Exception as e:
        score_details.append({"item": "JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"无法解析为有效 JSON: {e}"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2)
        return

    # Check 2: JSON Schema 反幻觉验证 (10 points)
    expected_keys = {"total_outdoor_expenses", "good_wood_inventory"}
    user_keys = set(user_data.keys())
    extra_keys = user_keys - expected_keys
    if extra_keys:
        score_details.append({"item": "JSON 结构与防捏造字段", "score": 0, "max_score": 10, "passed": False, "reason": f"存在未要求的捏造字段或脏数据: {extra_keys}"})
    else:
        score_details.append({"item": "JSON 结构与防捏造字段", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 只包含要求的字段且无幻觉内容"})
        total_score += 10

    # Check 3 & 4: 支出数据的存在性与精准数值校验 (10 + 30 = 40 points)
    user_expenses = user_data.get("total_outdoor_expenses")
    if user_expenses is not None and isinstance(user_expenses, (int, float)):
        score_details.append({"item": "户外支出字段存在性与类型", "score": 10, "max_score": 10, "passed": True, "reason": "字段 total_outdoor_expenses 存在且为数值类型"})
        total_score += 10
        
        diff = abs(user_expenses - ground_truth_expenses)
        if diff < 0.02:
            score_details.append({"item": "户外支出计算精准度", "score": 30, "max_score": 30, "passed": True, "reason": f"支出数值准确。用户值: {user_expenses}, 真实值: {ground_truth_expenses}"})
            total_score += 30
        else:
            score_details.append({"item": "户外支出计算精准度", "score": 0, "max_score": 30, "passed": False, "reason": f"数值偏差过大。用户值: {user_expenses}, 真实值: {ground_truth_expenses}. 可能是未正确过滤 'CLEARED' 或未做连表匹配"})
    else:
        score_details.append({"item": "户外支出字段存在性与类型", "score": 0, "max_score": 10, "passed": False, "reason": "缺少 total_outdoor_expenses 或类型错误"})
        score_details.append({"item": "户外支出计算精准度", "score": 0, "max_score": 30, "passed": False, "reason": "缺少支出数据"})

    # Check 5 & 6: 木材数据的存在性与精准数值校验 (10 + 20 = 30 points)
    user_wood = user_data.get("good_wood_inventory")
    if user_wood is not None and isinstance(user_wood, dict):
        score_details.append({"item": "木材库存字段存在性与类型", "score": 10, "max_score": 10, "passed": True, "reason": "字段 good_wood_inventory 存在且为字典类型"})
        total_score += 10
        
        if user_wood == ground_truth_wood:
            score_details.append({"item": "木材库存去重与计算精准度", "score": 30, "max_score": 30, "passed": True, "reason": "所有木材种类及数量完全匹配(去重最新且只过滤了Good状态)"})
            total_score += 30
        else:
            # 部分匹配给部分分数
            correct_keys = set(ground_truth_wood.keys())
            matched = 0
            for k in correct_keys:
                if user_wood.get(k) == ground_truth_wood[k]:
                    matched += 1
            ratio = matched / max(len(correct_keys), 1)
            wood_score = int(30 * ratio)
            
            score_details.append({"item": "木材库存去重与计算精准度", "score": wood_score, "max_score": 30, "passed": wood_score == 30, "reason": f"部分匹配。得分: {wood_score}/30。用户值: {user_wood}, 真实值: {ground_truth_wood}。可能未能按时间戳获取每个location最新的库存，或混入了journal的数据。"})
            total_score += wood_score
    else:
        score_details.append({"item": "木材库存字段存在性与类型", "score": 0, "max_score": 10, "passed": False, "reason": "缺少 good_wood_inventory 字段或类型不为字典"})
        score_details.append({"item": "木材库存去重与计算精准度", "score": 0, "max_score": 30, "passed": False, "reason": "缺少库存字典"})

    # Optional LLC check: To strictly enforce usage in complex edge case (e.g. they provided a letter)
    # 此处虽然非必须，但作为防御机制应对 Agent 画蛇添足提供额外的 readme。
    plans_dir = os.path.join(workspace, "plans")
    extra_files = [f for f in os.listdir(plans_dir) if f != "budget_and_materials_summary.json"] if os.path.exists(plans_dir) else []
    for ef in extra_files:
        if ef.endswith((".md", ".txt")):
            ef_path = os.path.join(plans_dir, ef)
            with open(ef_path, "r", encoding="utf-8") as f:
                content = f.read()
            is_polite = llm_judge_content("Does the text contain a polite, reassuring tone to comfort an anxious widower?", content)
            if not is_polite:
                # 附加扣分：如果写了多余文件且态度不好
                score_details.append({"item": "LLM 语义分析: 额外留言语气", "score": -5, "max_score": 0, "passed": False, "reason": "产生的多余说明文件中，LLM 判定语气冰冷未能安抚用户 (扣减 5 分)"})
                total_score = max(0, total_score - 5)

    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2)

if __name__ == "__main__":
    verify()
