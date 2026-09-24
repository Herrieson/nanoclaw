import os
import sys
import json
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

def extract_all_strings(data):
    """递归提取 JSON 中的所有字符串内容用于后续精确匹配验证"""
    if isinstance(data, dict):
        res = []
        for v in data.values():
            res.extend(extract_all_strings(v))
        return res
    elif isinstance(data, list):
        res = []
        for v in data:
            res.extend(extract_all_strings(v))
        return res
    elif isinstance(data, str):
        return [data.strip().lower()]
    elif isinstance(data, (int, float)):
        return [str(data)]
    return []

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    score_details = []
    total_score = 0
    
    output_dir = os.path.join(workspace, "output")
    action_plan_path = os.path.join(output_dir, "action_plan.json")
    hazard_chart_path = os.path.join(output_dir, "hazard_chart.txt")
    
    # 1. 目录结构与文件存在性 (10分)
    score = 0
    reason = "缺少 output 目录或其下的关键文件。"
    if os.path.exists(output_dir):
        score += 4
        if os.path.exists(action_plan_path):
            score += 3
        if os.path.exists(hazard_chart_path):
            score += 3
        if score == 10:
            reason = "目录和关键文件全部存在。"
    score_details.append({"item": "检查结果目录与关键文件", "score": score, "max_score": 10, "passed": score == 10, "reason": reason})
    total_score += score

    # 2. action_plan.json 格式合法性与解析 (15分)
    plan_data = None
    if os.path.exists(action_plan_path):
        try:
            with open(action_plan_path, 'r', encoding='utf-8') as f:
                plan_data = json.load(f)
            score_details.append({"item": "检查 action_plan.json 格式", "score": 15, "max_score": 15, "passed": True, "reason": "JSON 格式合法且可解析。"})
            total_score += 15
        except Exception as e:
            score_details.append({"item": "检查 action_plan.json 格式", "score": 0, "max_score": 15, "passed": False, "reason": f"JSON 解析失败: {str(e)}"})
    else:
        score_details.append({"item": "检查 action_plan.json 格式", "score": 0, "max_score": 15, "passed": False, "reason": "文件不存在，无法验证。"})

    # 3. action_plan.json 内容精准验证 - Trails (30分)
    if plan_data is not None:
        strings = extract_all_strings(plan_data)
        
        target_trails = ["bear creek", "summit path", "canyon descent", "deadmans drop", "gravel pit"]
        decoy_trails = ["pine ridge", "lake loop", "meadow trail", "whispering pines"]
        
        found_targets = sum(1 for t in target_trails if any(t in s for s in strings))
        found_decoys = sum(1 for t in decoy_trails if any(t in s for s in strings))
        
        trails_score = 0
        trails_reason = ""
        
        if found_targets == len(target_trails) and found_decoys == 0:
            trails_score = 30
            trails_reason = "精确找出了所有 hazard > 3 的路径，且无干扰项。"
        else:
            trails_score = max(0, found_targets * 6 - found_decoys * 10)
            trails_reason = f"找到 {found_targets}/{len(target_trails)} 个目标路径，包含了 {found_decoys} 个错误路径。得分: {trails_score}"
            
        score_details.append({"item": "校验危险路径筛选结果", "score": trails_score, "max_score": 30, "passed": trails_score == 30, "reason": trails_reason})
        total_score += trails_score
    else:
        score_details.append({"item": "校验危险路径筛选结果", "score": 0, "max_score": 30, "passed": False, "reason": "缺少 JSON 数据"})

    # 4. action_plan.json 内容精准验证 - Volunteers (30分)
    if plan_data is not None:
        strings = extract_all_strings(plan_data)
        
        target_vols = ["samuel", "marie", "old_ben", "sarah"]
        traitor = "traitor_joe"
        
        found_targets = sum(1 for v in target_vols if any(v in s for s in strings))
        found_traitor = any(traitor in s for s in strings)
        
        vols_score = 0
        vols_reason = ""
        
        if found_targets == len(target_vols) and not found_traitor:
            vols_score = 30
            vols_reason = "精确找出了所有符合要求的活跃志愿者，无干扰项。"
        else:
            vols_score = max(0, found_targets * 7)
            if found_traitor:
                vols_score = max(0, vols_score - 15)
                vols_reason = f"找到 {found_targets}/{len(target_vols)} 个目标，但包含了非活跃的 Traitor_Joe，严重扣分。"
            else:
                vols_reason = f"找到 {found_targets}/{len(target_vols)} 个目标志愿者。得分: {vols_score}"
                
        score_details.append({"item": "校验志愿者筛选结果", "score": vols_score, "max_score": 30, "passed": vols_score == 30, "reason": vols_reason})
        total_score += vols_score
    else:
        score_details.append({"item": "校验志愿者筛选结果", "score": 0, "max_score": 30, "passed": False, "reason": "缺少 JSON 数据"})

    # 5. hazard_chart.txt 语义与图表检测 (15分)
    if os.path.exists(hazard_chart_path):
        try:
            with open(hazard_chart_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            prompt = (
                "Does the following file content successfully represent an ASCII bar chart "
                "showing hazard levels for the specific trails (Bear Creek, Summit Path, Canyon Descent, Deadmans Drop, Gravel Pit)? "
                "It must look like a bar chart (using symbols like *, #, -, etc.) and associate the names with varying lengths/numbers."
            )
            is_valid_chart = llm_judge_content(prompt, content)
            
            if is_valid_chart:
                score_details.append({"item": "LLM 判定 ASCII 图表合法性", "score": 15, "max_score": 15, "passed": True, "reason": "图表格式及包含的关键信息合法。"})
                total_score += 15
            else:
                score_details.append({"item": "LLM 判定 ASCII 图表合法性", "score": 0, "max_score": 15, "passed": False, "reason": "大模型判定图表不合规或未体现指定数据。"})
        except Exception as e:
            score_details.append({"item": "LLM 判定 ASCII 图表合法性", "score": 0, "max_score": 15, "passed": False, "reason": f"文件读取或 API 错误: {str(e)}"})
    else:
        score_details.append({"item": "LLM 判定 ASCII 图表合法性", "score": 0, "max_score": 15, "passed": False, "reason": "文件不存在"})

    # Output final score
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
