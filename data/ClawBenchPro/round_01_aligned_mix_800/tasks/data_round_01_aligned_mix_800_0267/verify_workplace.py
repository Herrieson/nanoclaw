import os
import sys
import json
import httpx
from openai import OpenAI

# 配置常量
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化 LLM 客户端
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
    report_path = os.path.join(workspace, "cookout_plan/party_summary.json")
    score = 0
    details = []

    # 1. 基础文件存在性检查 (10分)
    if os.path.exists(report_path):
        score += 10
        details.append({"item": "检查结果文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 party_summary.json 已生成"})
        
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 2. 结构合法性检查 (10分)
            required_keys = ["ingredients", "party_budget", "total_cost", "under_budget"]
            missing_keys = [k for k in required_keys if k not in data]
            if not missing_keys:
                score += 10
                details.append({"item": "JSON 结构合法性", "score": 10, "max_score": 10, "passed": True, "reason": "包含所有必需字段"})
            else:
                details.append({"item": "JSON 结构合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"缺失字段: {missing_keys}"})

            # 3. 财务计算逻辑校验 (30分)
            # Take-home: 4000, Bills: 1200+450+200+300 = 2150. Disposable: 1850. Budget (10%): 185.
            expected_budget = 185.0
            actual_budget = data.get("party_budget", 0)
            if abs(float(actual_budget) - expected_budget) < 1.0:
                score += 30
                details.append({"item": "派对预算计算(10%可支配收入)", "score": 30, "max_score": 30, "passed": True, "reason": f"预算计算正确: ${actual_budget}"})
            else:
                details.append({"item": "派对预算计算(10%可支配收入)", "score": 0, "max_score": 30, "passed": False, "reason": f"预算计算错误。期望: {expected_budget}, 实际: {actual_budget}"})

            # 4. 配方扩增与成本校验 (40分)
            # 原配方(5人): beef(3), chiles(6), garlic(4), onion(1), tortilla(1)
            # 25人份 (5倍): beef(15), chiles(30), garlic(20), onion(5), tortilla(5)
            # 成本: 15*6.50 + 30*0.20 + 20*0.10 + 5*0.80 + 5*3.00 = 97.5 + 6.0 + 2.0 + 4.0 + 15.0 = 124.5
            expected_cost = 124.5
            actual_cost = data.get("total_cost", 0)
            if abs(float(actual_cost) - expected_cost) < 2.0:
                score += 40
                details.append({"item": "配方扩增与超市调价计算", "score": 40, "max_score": 40, "passed": True, "reason": f"成本计算准确: ${actual_cost}"})
            else:
                details.append({"item": "配方扩增与超市调价计算", "score": 0, "max_score": 40, "passed": False, "reason": f"成本计算不准确。期望约 {expected_cost}, 实际 {actual_cost}"})

            # 5. 逻辑一致性检查 (10分)
            # 124.5 < 185, under_budget should be true
            expected_under_budget = expected_cost < expected_budget
            actual_under_budget = data.get("under_budget")
            if actual_under_budget == expected_under_budget:
                score += 10
                details.append({"item": "超支逻辑判断一致性", "score": 10, "max_score": 10, "passed": True, "reason": "逻辑判断正确"})
            else:
                details.append({"item": "超支逻辑判断一致性", "score": 0, "max_score": 10, "passed": False, "reason": "逻辑判断与数值不符"})

        except Exception as e:
            details.append({"item": "文件解析错误", "score": 0, "max_score": 80, "passed": False, "reason": str(e)})
    else:
        details.append({"item": "检查结果文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失"})

    # 最终分值归一化处理
    total_score = max(0, min(100, score))
    
    result = {
        "total_score": int(total_score),
        "details": details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
