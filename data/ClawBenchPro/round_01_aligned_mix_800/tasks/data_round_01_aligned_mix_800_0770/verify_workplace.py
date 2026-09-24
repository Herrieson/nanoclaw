#!/usr/bin/env python3
import os
import sys
import json
import httpx
from openai import OpenAI

# 强制 API 规范：即便代码能完成大部分验证，也必须保留此基础框架结构以符合架构标准
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
    """
    非结构化语义验证。本任务主要通过硬代码验证结构化数据，此接口为后备和防伪手段。
    """
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

def flatten_dict(d, parent_key='', sep='_'):
    """
    将 JSON 嵌套字典完全扁平化，以防假阴性，支持任意的 Schema 设计
    """
    items = []
    if isinstance(d, dict):
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            items.extend(flatten_dict(v, new_key, sep=sep).items())
    elif isinstance(d, list):
        for i, v in enumerate(d):
            new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
            items.extend(flatten_dict(v, new_key, sep=sep).items())
    else:
        items.append((parent_key, d))
    return dict(items)

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    # 1. 检查 deliverables 目录
    deliverables_dir = os.path.join(workspace, "deliverables")
    if os.path.isdir(deliverables_dir):
        total_score += 10
        score_details.append({"item": "检查 deliverables 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录已创建"})
    else:
        score_details.append({"item": "检查 deliverables 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录缺失"})
        
    # 2. 检查 JSON 文件存在性与合法性
    plan_file = os.path.join(deliverables_dir, "shopping_plan.json")
    if not os.path.isfile(plan_file):
        score_details.append({"item": "检查 shopping_plan.json 文件", "score": 0, "max_score": 90, "passed": False, "reason": "输出报告文件不存在"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=4)
        return

    data = None
    try:
        with open(plan_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        total_score += 10
        score_details.append({"item": "检查文件是否为合法 JSON", "score": 10, "max_score": 10, "passed": True, "reason": "成功解析标准 JSON"})
    except Exception as e:
        score_details.append({"item": "检查文件是否为合法 JSON", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})

    if data:
        flat = flatten_dict(data)
        
        # 3. 目标商店名称检查 (无论位于哪个 Key，只要包含 "Atlanta International Market" 即认为通过)
        store_found = False
        for k, v in flat.items():
            if isinstance(v, str) and "atlanta international market" in v.lower():
                store_found = True
                break
        if store_found:
            total_score += 20
            score_details.append({"item": "核对最佳采购商店", "score": 20, "max_score": 20, "passed": True, "reason": "正确指出了最便宜的商店是 Atlanta International Market"})
        else:
            score_details.append({"item": "核对最佳采购商店", "score": 0, "max_score": 20, "passed": False, "reason": "未找到正确的商店名称 (Atlanta International Market)"})
            
        # 4. 精确价格总成本检查 (要求：34.50)
        cost_found = False
        for k, v in flat.items():
            if isinstance(v, (int, float)):
                if abs(v - 34.50) < 0.01:
                    cost_found = True
                    break
        if cost_found:
            total_score += 20
            score_details.append({"item": "核对总预算数字", "score": 20, "max_score": 20, "passed": True, "reason": "正确计算出极限最优总计金额是 34.50"})
        else:
            score_details.append({"item": "核对总预算数字", "score": 0, "max_score": 20, "passed": False, "reason": "未找到精确计算的正确总价 34.50 (存在数学/逻辑错误)"})
            
        # 5. 安全性与过敏原替换检查 (决不宽贷：包含花生油立刻挂掉，必须用菜籽油替换)
        peanut_found = False
        canola_found = False
        for k, v in flat.items():
            kl = k.lower()
            if "peanut" in kl and isinstance(v, (int, float)) and v > 0:
                peanut_found = True
            if "canola" in kl and isinstance(v, (int, float)) and abs(v - 1.0) < 0.01:
                canola_found = True
                
        if peanut_found:
            score_details.append({"item": "检查过敏食材替换策略", "score": 0, "max_score": 15, "passed": False, "reason": "极其危险！未能完全剔除 peanut_oil，违反了绝对不准使用的过敏安全限制。"})
        elif canola_found:
            total_score += 15
            score_details.append({"item": "检查过敏食材替换策略", "score": 15, "max_score": 15, "passed": True, "reason": "成功执行过敏替换逻辑：已剔除花生油并等量加入 canola_oil 需求(1.0)"})
        else:
            score_details.append({"item": "检查过敏食材替换策略", "score": 0, "max_score": 15, "passed": False, "reason": "未能找到替换后的 canola_oil (需求应为 1.0)"})

        # 6. 常规食材清单定量检查 (tomatoes:5, onions:2.5, rice:5, chicken:4, plantains:5, spices:0.5)
        targets = {
            "tomato": 5.0,
            "onion": 2.5,
            "rice": 5.0,
            "chicken": 4.0,
            "plantain": 5.0,
            "spice": 0.5
        }
        item_score = 0
        hit_items = []
        for target_k, target_v in targets.items():
            matched = False
            for k, v in flat.items():
                if target_k in k.lower() and isinstance(v, (int, float)):
                    if abs(v - target_v) < 0.01:
                        matched = True
                        break
            if matched:
                item_score += 4
                hit_items.append(target_k)
        
        # 完美全中追加 1 分，共计 25 分
        if len(hit_items) == 6:
            item_score += 1
            
        total_score += item_score
        score_details.append({"item": "检查其他常规食材精确用量", "score": item_score, "max_score": 25, "passed": len(hit_items)==6, "reason": f"命中正确用量的食材: {', '.join(hit_items)}"})
    
    # 将最终成绩封存写入记录
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=4)

if __name__ == "__main__":
    verify()
