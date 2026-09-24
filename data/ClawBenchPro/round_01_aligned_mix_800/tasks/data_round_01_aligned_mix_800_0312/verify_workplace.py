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

def get_part_deficit(data, part_name):
    """递归遍历 JSON，精确查找该零件对应的短缺数值"""
    if isinstance(data, dict):
        for k, v in data.items():
            # 有时 Agent 可能将零件号作为 key
            if part_name.lower() in k.lower():
                if isinstance(v, (int, float)):
                    return v
                # 如果值是字符串的数字，尝试转换
                if isinstance(v, str) and v.isdigit():
                    return int(v)
            # 或者值里包含一个字典结构
            elif isinstance(v, (dict, list)):
                res = get_part_deficit(v, part_name)
                if res is not None:
                    return res
    elif isinstance(data, list):
        for item in data:
            # 有时 Agent 会创建 [{'part': 'EV-101', 'deficit': 500}] 这样的结构
            if isinstance(item, dict):
                has_part = any(isinstance(v, str) and part_name.lower() in v.lower() for v in item.values())
                if has_part:
                    # 找到该字典中的数字作为 deficit
                    for v in item.values():
                        if isinstance(v, (int, float)):
                            return v
                        if isinstance(v, str) and v.isdigit():
                            return int(v)
            res = get_part_deficit(item, part_name)
            if res is not None:
                return res
    return None

def find_carrier(data, target_carrier):
    """递归遍历 JSON，精确匹配目标承运商"""
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, str) and target_carrier.lower() in v.lower():
                return True
            if isinstance(v, (dict, list)):
                if find_carrier(v, target_carrier):
                    return True
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, str) and target_carrier.lower() in item.lower():
                return True
            if find_carrier(item, target_carrier):
                return True
    return False

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    score_details = []
    total_score = 0
    
    folder_path = os.path.join(workspace, "expedite_action")
    file_path = os.path.join(folder_path, "summary.json")
    
    # 1. Check Directory
    if os.path.isdir(folder_path):
        score_details.append({"item": "目录创建检查", "score": 10, "max_score": 10, "passed": True, "reason": "成功创建 expedite_action 目录"})
        total_score += 10
    else:
        score_details.append({"item": "目录创建检查", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 expedite_action 目录"})

    # 2. Check File
    file_exists = os.path.exists(file_path)
    if file_exists:
        score_details.append({"item": "摘要文件创建检查", "score": 10, "max_score": 10, "passed": True, "reason": "成功创建 summary.json 文件"})
        total_score += 10
    else:
        score_details.append({"item": "摘要文件创建检查", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 summary.json 文件"})
    
    json_data = None
    if file_exists:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content_str = f.read()
                json_data = json.loads(content_str)
            score_details.append({"item": "文件格式校验", "score": 10, "max_score": 10, "passed": True, "reason": "文件是合法的 JSON 格式"})
            total_score += 10
        except Exception as e:
            score_details.append({"item": "文件格式校验", "score": 0, "max_score": 10, "passed": False, "reason": f"文件不是合法的 JSON，解析报错: {e}"})

    # 3. Check Deficits Calculation & 4. Carrier Selection
    if json_data is not None:
        expected_deficits = {
            "EV-101": 500,
            "EV-102": 100,
            "EV-103": 30,
            "EV-104": 10
        }
        
        for part, expected_val in expected_deficits.items():
            actual_val = get_part_deficit(json_data, part)
            if actual_val == expected_val:
                score_details.append({"item": f"精准提取计算：{part} 短缺量", "score": 10, "max_score": 10, "passed": True, "reason": f"精确匹配短缺量 {expected_val}"})
                total_score += 10
            else:
                score_details.append({"item": f"精准提取计算：{part} 短缺量", "score": 0, "max_score": 10, "passed": False, "reason": f"未提取到 {expected_val} 或计算错误 (解析到 {actual_val})"})
        
        has_carrier_d = find_carrier(json_data, "Carrier D")
        if has_carrier_d:
            score_details.append({"item": "最优承运商选择", "score": 20, "max_score": 20, "passed": True, "reason": "正确剔除无效及非Same-Day承运商，锁定 Carrier D"})
            total_score += 20
        else:
            score_details.append({"item": "最优承运商选择", "score": 0, "max_score": 20, "passed": False, "reason": "未能在结构化数据中精确匹配到最优承运商 Carrier D"})
        
        # 5. LLM Tone/Redundancy check
        llm_prompt = "Does this JSON content look completely professional and clean? It should ONLY contain essential data (part deficits and carrier info) and absolutely NO lengthy conversational text, step-by-step reasoning, or apologies. Respond with YES if it is clean and terse, or NO if it contains conversational bloat."
        is_clean = llm_judge_content(llm_prompt, content_str)
        if is_clean:
            score_details.append({"item": "LLM语义检测：JSON纯净度", "score": 10, "max_score": 10, "passed": True, "reason": "文件内容精简，不包含啰嗦对话和多余解释"})
            total_score += 10
        else:
            score_details.append({"item": "LLM语义检测：JSON纯净度", "score": 0, "max_score": 10, "passed": False, "reason": "包含大段非必要的自然语言解释，违背调度员不要啰嗦的指令"})
    else:
        # 兜底：如果没有合法的 JSON，后续所有项均 0 分
        score_details.append({"item": "精准提取计算与承运商选择", "score": 0, "max_score": 60, "passed": False, "reason": "无法读取有效的 JSON 数据"})
        score_details.append({"item": "LLM语义检测：JSON纯净度", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在或不可读"})

    # Write output
    output_data = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
