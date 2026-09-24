import os
import sys
import json
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

def verify(workspace):
    score_details = []
    total_score = 0

    # 1. 检查目录和文件
    json_path = os.path.join(workspace, "summary", "clothing_expenses.json")
    if not os.path.exists(json_path):
        score_details.append({"item": "检查目标JSON文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": f"未找到文件: {json_path}"})
        return 0, score_details
    else:
        score_details.append({"item": "检查目标JSON文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10

    # 2. 解析 JSON 文件合法性
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        score_details.append({"item": "检查JSON格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "成功解析JSON文件"})
        total_score += 10
    except Exception as e:
        score_details.append({"item": "检查JSON格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败: {e}"})
        return total_score, score_details

    # 3. 提取结果
    items_found = []
    total_sum_found = None

    def traverse(node):
        nonlocal total_sum_found
        if isinstance(node, dict):
            for k, v in node.items():
                if k.lower() in ["total_sum", "total", "totalsum", "sum"]:
                    if isinstance(v, (int, float)):
                        total_sum_found = float(v)
                    elif isinstance(v, str):
                        try:
                            total_sum_found = float(v.replace("$", "").replace(",", ""))
                        except:
                            pass
            
            item_name = None
            item_cost = None
            for k, v in node.items():
                if k.lower() in ["item", "name", "description", "product"]:
                    item_name = str(v)
                if k.lower() in ["cost", "price", "amount", "value"]:
                    if isinstance(v, (int, float)):
                        item_cost = float(v)
                    elif isinstance(v, str):
                        try:
                            item_cost = float(v.replace("$", "").replace(",", ""))
                        except:
                            pass
            if item_name and item_cost is not None:
                items_found.append({"item": item_name, "cost": item_cost})
            
            for v in node.values():
                traverse(v)
        elif isinstance(node, list):
            for v in node:
                traverse(v)

    traverse(data)

    # 真实数据源
    truth_items = [
        {"keys": ["trench", "1940"], "cost": 125.50},
        {"keys": ["chore", "1950", "workwear"], "cost": 55.00},
        {"keys": ["corduroy", "1970", "pants"], "cost": 22.75},
        {"keys": ["cravat", "antique", "v-s"], "cost": 45.00},
        {"keys": ["fedora", "1960", "hat"], "cost": 40.00},
        {"keys": ["cufflinks", "victorian", "v-s"], "cost": 88.20},
        {"keys": ["denim", "jacket", "vintage"], "cost": 65.00}
    ]
    truth_total = 441.45

    # 4. 正确识别复古服装记录验证
    matched_count = 0
    matched_indices = set()
    
    for extracted in items_found:
        c = extracted["cost"]
        n = extracted["item"].lower()
        
        for idx, ti in enumerate(truth_items):
            if idx in matched_indices:
                continue
            # 价格匹配（容差 0.01）
            if abs(c - ti["cost"]) < 0.01:
                # 首先使用代码检查关键词
                if any(k in n for k in ti["keys"]):
                    matched_count += 1
                    matched_indices.add(idx)
                    break
                else:
                    # 如果代码无法匹配，使用 LLM 作为柔性兜底防御假阴性
                    prompt = "Does this text clearly describe a vintage clothing item, antique accessory, or contain the tag [V-S]? Note: If it says fishing gear, groceries, or machine sensor, it is NOT."
                    if llm_judge_content(prompt, extracted["item"]):
                        matched_count += 1
                        matched_indices.add(idx)
                        break

    item_score = matched_count * 5
    item_passed = matched_count == 7
    score_details.append({
        "item": "正确识别目标记录",
        "score": item_score,
        "max_score": 35,
        "passed": item_passed,
        "reason": f"成功识别 {matched_count}/7 条服装支出记录。"
    })
    total_score += item_score

    # 5. 过滤噪音数据
    noise_count = len(items_found) - matched_count
    if noise_count == 0 and len(items_found) > 0:
        noise_score = 20
        noise_passed = True
        noise_reason = "数据纯净，未混入机器日志、钓鱼、杂货等噪音数据。"
    else:
        deduct = min(noise_count * 5, 20)
        noise_score = 20 - deduct
        noise_passed = False
        noise_reason = f"混入 {noise_count} 条多余/错误数据，扣除 {deduct} 分。"
    
    score_details.append({
        "item": "过滤噪音与防幻觉",
        "score": noise_score,
        "max_score": 20,
        "passed": noise_passed,
        "reason": noise_reason
    })
    total_score += noise_score

    # 6. 验证总金额计算
    if total_sum_found is not None:
        if abs(total_sum_found - truth_total) < 0.01:
            sum_score = 25
            sum_passed = True
            sum_reason = f"正确计算出总额 total_sum: {total_sum_found}"
        else:
            sum_score = 0
            sum_passed = False
            sum_reason = f"提取的总额 {total_sum_found} 不正确，应为 {truth_total}。"
    else:
        sum_score = 0
        sum_passed = False
        sum_reason = "未能找到或提取 total_sum 字段。"
    
    score_details.append({
        "item": "验证总金额精确度",
        "score": sum_score,
        "max_score": 25,
        "passed": sum_passed,
        "reason": sum_reason
    })
    total_score += sum_score

    return total_score, score_details

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score, details = verify(workspace)
    
    output = {
        "total_score": score,
        "details": details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
