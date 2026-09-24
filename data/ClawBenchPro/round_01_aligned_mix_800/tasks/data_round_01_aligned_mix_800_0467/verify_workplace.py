import os
import sys
import json
import math
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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_file = os.path.join(workspace, "cookout_plan", "party_summary.json")
    
    total_score = 0
    details = []

    # 1. 检查文件是否存在 (10分)
    if not os.path.exists(target_file):
        details.append({"item": "检查结果文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "party_summary.json 文件不存在"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": 0, "details": details}, f, indent=2)
        return
    else:
        details.append({"item": "检查结果文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "party_summary.json 文件存在"})
        total_score += 10
        
    # 2. 检查 JSON 格式合法性 (15分)
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            content_str = f.read()
            data = json.loads(content_str)
        details.append({"item": "验证 JSON 格式合法性", "score": 15, "max_score": 15, "passed": True, "reason": "文件为有效 JSON 结构"})
        total_score += 15
    except Exception as e:
        details.append({"item": "验证 JSON 格式合法性", "score": 0, "max_score": 15, "passed": False, "reason": f"JSON 解析失败: {str(e)}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return
        
    # 3. 检查必要字段 Schema (10分)
    required_keys = ["ingredients", "party_budget", "total_cost", "under_budget"]
    missing_keys = [k for k in required_keys if k not in data]
    if missing_keys:
        details.append({"item": "检查必要字段是否存在", "score": 0, "max_score": 10, "passed": False, "reason": f"缺失字段: {missing_keys}"})
    else:
        details.append({"item": "检查必要字段是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "所有要求的数据字段均存在"})
        total_score += 10
        
    # 若结构损坏，中断后续取值校验
    if missing_keys:
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 4. Ingredients 严格校验与防幻觉测试 (20分)
    expected_ingredients = {
        "beef_chuck_lbs": 15,
        "dried_guajillo_chiles": 30,
        "garlic_cloves": 20,
        "onion": 5,
        "corn_tortillas_pack": 5
    }
    actual_ingredients = data.get("ingredients", {})
    if not isinstance(actual_ingredients, dict):
        details.append({"item": "食材及扩增比例准确性", "score": 0, "max_score": 20, "passed": False, "reason": "ingredients 字段非有效字典类型"})
    else:
        is_match = True
        reason_ing = ""
        actual_keys = set(actual_ingredients.keys())
        expected_keys = set(expected_ingredients.keys())
        
        if actual_keys != expected_keys:
            is_match = False
            reason_ing = "食材种类不匹配。可能未找到正确食谱或大模型发生了幻觉捏造额外节点。"
        else:
            for k, v in expected_ingredients.items():
                try:
                    actual_v = float(actual_ingredients[k])
                    if abs(actual_v - v) > 1e-3:
                        is_match = False
                        reason_ing = f"食材 {k} 的数量错误，预期 {v}，实际 {actual_v}。未能按 5 倍正确扩增。"
                        break
                except (ValueError, TypeError):
                    is_match = False
                    reason_ing = f"食材 {k} 的值类型非数值型。"
                    break
        
        if is_match:
            details.append({"item": "食材及扩增比例准确性", "score": 20, "max_score": 20, "passed": True, "reason": "食材清单提取及其 5 倍扩增数量完全正确"})
            total_score += 20
        else:
            details.append({"item": "食材及扩增比例准确性", "score": 0, "max_score": 20, "passed": False, "reason": reason_ing})
            
    # 5. Budget 计算的精密校验 (15分)
    actual_budget = data.get("party_budget")
    if type(actual_budget) in (int, float) and abs(actual_budget - 120.0) < 1e-3:
        details.append({"item": "预算计算准确性", "score": 15, "max_score": 15, "passed": True, "reason": "party_budget 计算正确 (严格匹配 120.0)"})
        total_score += 15
    else:
        details.append({"item": "预算计算准确性", "score": 0, "max_score": 15, "passed": False, "reason": f"party_budget 计算错误，预期 120.0，实际为 {actual_budget}"})
        
    # 6. Total Cost 跨表检索的精密校验 (15分)
    actual_cost = data.get("total_cost")
    if type(actual_cost) in (int, float) and abs(actual_cost - 124.5) < 1e-3:
        details.append({"item": "总花费跨表计算准确性", "score": 15, "max_score": 15, "passed": True, "reason": "total_cost 跨表计算正确 (严格匹配 124.5)"})
        total_score += 15
    else:
        details.append({"item": "总花费跨表计算准确性", "score": 0, "max_score": 15, "passed": False, "reason": f"total_cost 跨表计算错误，预期 124.5，实际为 {actual_cost}"})

    # 7. 布尔决策判定 (5分)
    actual_under = data.get("under_budget")
    if actual_under is False:
        details.append({"item": "预算布尔逻辑准确性", "score": 5, "max_score": 5, "passed": True, "reason": "under_budget 正确判定为 False"})
        total_score += 5
    else:
        details.append({"item": "预算布尔逻辑准确性", "score": 0, "max_score": 5, "passed": False, "reason": "under_budget 逻辑比较出错，124.5 不应 <= 120.0，应为 False"})

    # 8. LLM 纯净度与幻觉探测 (10分)
    # 此步骤专门对抗大模型常见弊端：随意往输出文件添加总结陈词或无关字符串
    llm_prompt = "Examine the following JSON content. Does it ONLY contain professional machine-readable data structures? Check if there are ANY conversational fillers (e.g. 'Here is your data', 'I hope this helps'), arbitrary comments, or highly emotional subjective text added by AI. Reply 'YES' if it is STRICTLY professional data with NO conversational/emotional noise. Reply 'NO' if there is AI conversational chatter."
    is_clean = llm_judge_content(llm_prompt, content_str)
    
    if is_clean:
        details.append({"item": "利用大模型验证内容纯净度", "score": 10, "max_score": 10, "passed": True, "reason": "大模型判定文件为纯净的专业数据载荷，无闲聊及捏造内容"})
        total_score += 10
    else:
        details.append({"item": "利用大模型验证内容纯净度", "score": 0, "max_score": 10, "passed": False, "reason": "大模型检测出 JSON 文件内部掺杂了闲聊或不专业的自然语言"})

    # 输出评测结果
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2)

if __name__ == "__main__":
    main()
