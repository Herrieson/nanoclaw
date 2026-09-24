import os
import sys
import json
import httpx
import glob
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

def extract_all_values(obj):
    """Recursively extract all values from a JSON object to handle arbitrary keys"""
    values = []
    if isinstance(obj, dict):
        for v in obj.values():
            values.extend(extract_all_values(v))
    elif isinstance(obj, list):
        for item in obj:
            values.extend(extract_all_values(item))
    else:
        values.append(obj)
    return values

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    score_details = []
    total_score = 0
    
    # 1. Check Output Directory (15 points)
    output_dir = os.path.join(workspace, "dashboard_api")
    dir_exists = os.path.isdir(output_dir)
    if dir_exists:
        score_details.append({"item": "检查目标目录 dashboard_api 是否存在", "score": 15, "max_score": 15, "passed": True, "reason": "目录已创建"})
        total_score += 15
    else:
        score_details.append({"item": "检查目标目录 dashboard_api 是否存在", "score": 0, "max_score": 15, "passed": False, "reason": "未找到 dashboard_api 目录"})
    
    # 2. Check Valid JSON File (15 points)
    json_files = glob.glob(os.path.join(output_dir, "*.json")) if dir_exists else []
    valid_json_content = None
    json_file_path = None
    
    if json_files:
        for jf in json_files:
            try:
                with open(jf, "r", encoding="utf-8") as f:
                    valid_json_content = json.load(f)
                    json_file_path = jf
                    break
            except Exception:
                continue
    
    if valid_json_content is not None:
        score_details.append({"item": "检查是否生成了合法的 JSON 产物", "score": 15, "max_score": 15, "passed": True, "reason": f"成功解析 {os.path.basename(json_file_path)}"})
        total_score += 15
    else:
        score_details.append({"item": "检查是否生成了合法的 JSON 产物", "score": 0, "max_score": 15, "passed": False, "reason": "未能找到或解析有效的 JSON 文件"})
    
    # Value Checks
    fuel_passed = False
    miles_passed = False
    city_passed = False
    semantic_passed = False
    
    if valid_json_content is not None:
        all_values = extract_all_values(valid_json_content)
        
        # 3. Fuel Calculation (20 points) - Expected 475.85
        for v in all_values:
            if isinstance(v, (int, float)) and abs(v - 475.85) < 0.01:
                fuel_passed = True
                break
            elif isinstance(v, str) and "475.85" in v:
                fuel_passed = True
                break
        
        if fuel_passed:
            score_details.append({"item": "准确计算燃油总成本", "score": 20, "max_score": 20, "passed": True, "reason": "找到正确的燃油总额 475.85"})
            total_score += 20
        else:
            score_details.append({"item": "准确计算燃油总成本", "score": 0, "max_score": 20, "passed": False, "reason": "未找到预期的燃油总额（需处理脏数据计算）"})
            
        # 4. Mileage Calculation (20 points) - Expected 1755.5
        for v in all_values:
            if isinstance(v, (int, float)) and abs(v - 1755.5) < 0.01:
                miles_passed = True
                break
            elif isinstance(v, str) and "1755.5" in v:
                miles_passed = True
                break
                
        if miles_passed:
            score_details.append({"item": "准确提取并恢复总里程", "score": 20, "max_score": 20, "passed": True, "reason": "找到正确的总里程 1755.5 (包含故障恢复里程)"})
            total_score += 20
        else:
            score_details.append({"item": "准确提取并恢复总里程", "score": 0, "max_score": 20, "passed": False, "reason": "未找到正确的总里程，可能未能成功恢复 Day 4 故障数据"})
            
        # 5. Longest Idle City (20 points) - Expected "Gary, IN" or "Gary"
        for v in all_values:
            if isinstance(v, str) and ("gary, in" in v.lower() or "gary" in v.lower()):
                city_passed = True
                break
                
        if city_passed:
            score_details.append({"item": "准确识别最长闲置城市", "score": 20, "max_score": 20, "passed": True, "reason": "找到正确的城市 Gary, IN"})
            total_score += 20
        else:
            score_details.append({"item": "准确识别最长闲置城市", "score": 0, "max_score": 20, "passed": False, "reason": "未找到目标城市，可能未能解密行车记录仪 .dat 文件"})
            
        # 6. Semantic Schema Verification via LLM (10 points)
        json_str = json.dumps(valid_json_content, indent=2)
        prompt = "Does this JSON structurally contain keys/values representing three distinct concepts: total fuel spend, total miles driven, and a city name? (Ignore exact numeric accuracy, focus on semantic structure)"
        semantic_passed = llm_judge_content(prompt, json_str)
        
        if semantic_passed:
            score_details.append({"item": "利用大模型检查 JSON 语义结构", "score": 10, "max_score": 10, "passed": True, "reason": "大模型判定产物包含了对应的三大字段维度"})
            total_score += 10
        else:
            score_details.append({"item": "利用大模型检查 JSON 语义结构", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定 JSON 格式/语义不符合输出要求"})
            
    else:
        score_details.append({"item": "准确计算燃油总成本", "score": 0, "max_score": 20, "passed": False, "reason": "无合法的 JSON 产物"})
        score_details.append({"item": "准确提取并恢复总里程", "score": 0, "max_score": 20, "passed": False, "reason": "无合法的 JSON 产物"})
        score_details.append({"item": "准确识别最长闲置城市", "score": 0, "max_score": 20, "passed": False, "reason": "无合法的 JSON 产物"})
        score_details.append({"item": "利用大模型检查 JSON 语义结构", "score": 0, "max_score": 10, "passed": False, "reason": "无合法的 JSON 产物"})
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({
            "total_score": total_score,
            "details": score_details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
