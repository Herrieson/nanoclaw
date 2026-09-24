import os
import sys
import json
import glob
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

def find_json_file(deliverables_dir):
    json_files = glob.glob(os.path.join(deliverables_dir, "*.json"))
    if not json_files:
        return None
    return json_files[0]

def extract_values_from_json(data):
    """Recursively extract all numeric values and lists of strings from the JSON."""
    numerics = []
    string_lists = []
    
    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if isinstance(v, (int, float)):
                    numerics.append(v)
                elif isinstance(v, list) and all(isinstance(i, str) for i in v):
                    string_lists.append(v)
                else:
                    walk(v)
        elif isinstance(node, list):
            if all(isinstance(i, str) for i in node):
                string_lists.append(node)
            else:
                for item in node:
                    walk(item)
    
    walk(data)
    return numerics, string_lists

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_dir = os.path.join(workspace, "deliverables")
    
    score_details = []
    total_score = 0
    
    # 1. 检查目录和 JSON 文件是否存在
    json_file = None
    if os.path.isdir(deliverables_dir):
        json_file = find_json_file(deliverables_dir)
        
    if json_file:
        score_details.append({"item": "Deliverables 目录下存在 JSON 文件", "score": 10, "max_score": 10, "passed": True, "reason": "找到了 JSON 文件"})
        total_score += 10
    else:
        score_details.append({"item": "Deliverables 目录下存在 JSON 文件", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 JSON 文件"})
        
    # 2. 验证 JSON 格式合法性
    json_data = None
    if json_file:
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            score_details.append({"item": "JSON 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "成功解析 JSON"})
            total_score += 10
        except json.JSONDecodeError:
            score_details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "文件不是合法的 JSON 格式"})
    else:
        score_details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在，无法解析"})

    # 如果可以解析，继续验证业务逻辑
    if json_data is not None:
        numerics, string_lists = extract_values_from_json(json_data)
        
        # 3. 验证未授权承包商名单 (40 分)
        # 预期的未授权列表：Shady Steve, Mike's Lawn Care, QuickFix LLC
        expected_rogues = {"shady steve", "mike's lawn care", "quickfix llc"}
        best_match_score = 0
        best_reason = "未找到包含正确的未授权承包商列表"
        
        for slist in string_lists:
            # Normalize list elements
            normalized_list = set(s.strip().lower() for s in slist)
            matched = len(expected_rogues.intersection(normalized_list))
            extra = len(normalized_list - expected_rogues)
            
            # 基础分：找到1个给10分，最多30分
            current_score = matched * 10
            # 惩罚：如果有合法供应商被当成了 rogue，或者有幻觉数据，每个扣 5 分
            current_score -= extra * 5
            
            # 如果全中且无额外错误，给满 40 分
            if matched == 3 and extra == 0:
                current_score = 40
                
            current_score = max(0, current_score)
            
            if current_score >= best_match_score:
                best_match_score = current_score
                if current_score == 40:
                    best_reason = "完美匹配未授权承包商列表"
                else:
                    best_reason = f"匹配了 {matched} 个未授权承包商，包含 {extra} 个错误项"

        score_details.append({"item": "正确识别未授权的承包商", "score": best_match_score, "max_score": 40, "passed": best_match_score == 40, "reason": best_reason})
        total_score += best_match_score

        # 4. 验证金额 (40 分)
        # 预期总金额: 2275.75
        expected_amount = 2275.75
        amount_found = False
        
        for num in numerics:
            if abs(num - expected_amount) < 0.001:
                amount_found = True
                break
                
        if amount_found:
            score_details.append({"item": "精确计算出合法工作总金额", "score": 40, "max_score": 40, "passed": True, "reason": "找到了正确的合法供应商总计开销 2275.75"})
            total_score += 40
        else:
            score_details.append({"item": "精确计算出合法工作总金额", "score": 0, "max_score": 40, "passed": False, "reason": "未能在 JSON 中找到数值 2275.75，这说明计算逻辑或数据清洗有误"})
            
    else:
        score_details.append({"item": "正确识别未授权的承包商", "score": 0, "max_score": 40, "passed": False, "reason": "无 JSON 数据可供提取"})
        score_details.append({"item": "精确计算出合法工作总金额", "score": 0, "max_score": 40, "passed": False, "reason": "无 JSON 数据可供提取"})

    score_dict = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(score_dict, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
