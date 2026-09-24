import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，关闭 SSL 验证
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

def find_value_in_json(data, target_key_substring):
    """递归在JSON中寻找包含指定子串的键对应的值"""
    if isinstance(data, dict):
        for k, v in data.items():
            if target_key_substring.lower() in k.lower():
                return v
            result = find_value_in_json(v, target_key_substring)
            if result is not None:
                return result
    elif isinstance(data, list):
        for item in data:
            result = find_value_in_json(item, target_key_substring)
            if result is not None:
                return result
    return None

def find_carrier_in_json(data):
    """递归在JSON中寻找货运公司名称"""
    if isinstance(data, str):
        if "carrier d" in data.lower():
            return True
    elif isinstance(data, dict):
        for k, v in data.items():
            if "carrier" in k.lower() and isinstance(v, str) and "carrier d" in v.lower():
                return True
            if find_carrier_in_json(v):
                return True
    elif isinstance(data, list):
        for item in data:
            if find_carrier_in_json(item):
                return True
    return False

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    total_score = 0
    details = []
    
    target_dir = os.path.join(workspace, "expedite_action")
    target_file = os.path.join(target_dir, "summary.json")
    
    # 1. 检查目录 (10分)
    if os.path.isdir(target_dir):
        total_score += 10
        details.append({"item": "检查目标目录 expedite_action 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
    else:
        details.append({"item": "检查目标目录 expedite_action 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录不存在"})
        
    # 2. 检查文件 (10分)
    if os.path.isfile(target_file):
        total_score += 10
        details.append({"item": "检查目标文件 summary.json 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        
        # 3. 检查 JSON 格式 (10分)
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                content_str = f.read()
                data = json.loads(content_str)
            total_score += 10
            details.append({"item": "检查 summary.json 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "合法的 JSON 格式"})
            
            # 4. 检查缺件计算准确性 (40分，每个零件10分)
            parts_expected = {
                "EV-101": 500,
                "EV-102": 100,
                "EV-103": 30,
                "EV-104": 10
            }
            
            part_score = 0
            part_reason = []
            for part, expected_deficit in parts_expected.items():
                val = find_value_in_json(data, part)
                # 兼容数值提取与字符串转换
                if val is not None and str(expected_deficit) == str(val):
                    part_score += 10
                    part_reason.append(f"{part} 短缺量正确")
                else:
                    part_reason.append(f"{part} 短缺量错误 (期望: {expected_deficit}, 实际: {val})")
                    
            total_score += part_score
            details.append({
                "item": "检查零件短缺量计算结果的精准度", 
                "score": part_score, 
                "max_score": 40, 
                "passed": part_score == 40, 
                "reason": "; ".join(part_reason)
            })
            
            # 5. 检查运输公司筛选准确性 (30分)
            has_carrier_d = find_carrier_in_json(data)
            
            # 由于可能字段命名有偏差，再利用LLM对纯文本进行最终验证以防误判，但仍以严格的"Carrier D"提取为主要依据
            prompt_text = "Does the JSON data clearly identify 'Carrier D' as the chosen/selected carrier? Answer YES if it does, NO if it chooses another carrier or none."
            llm_confirm = llm_judge_content(prompt_text, content_str)
            
            if has_carrier_d or llm_confirm:
                total_score += 30
                details.append({"item": "检查最廉价可用同日达运输公司筛选结果", "score": 30, "max_score": 30, "passed": True, "reason": "成功筛选出 Carrier D"})
            else:
                details.append({"item": "检查最廉价可用同日达运输公司筛选结果", "score": 0, "max_score": 30, "passed": False, "reason": "未找到正确的运输公司 Carrier D"})
                
        except json.JSONDecodeError:
            details.append({"item": "检查 summary.json 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": "无法解析为 JSON"})
            details.append({"item": "检查零件短缺量计算结果的精准度", "score": 0, "max_score": 40, "passed": False, "reason": "JSON无法解析，跳过验证"})
            details.append({"item": "检查最廉价可用同日达运输公司筛选结果", "score": 0, "max_score": 30, "passed": False, "reason": "JSON无法解析，跳过验证"})
    else:
        details.append({"item": "检查目标文件 summary.json 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        details.append({"item": "检查 summary.json 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失，跳过"})
        details.append({"item": "检查零件短缺量计算结果的精准度", "score": 0, "max_score": 40, "passed": False, "reason": "文件缺失，跳过"})
        details.append({"item": "检查最廉价可用同日达运输公司筛选结果", "score": 0, "max_score": 30, "passed": False, "reason": "文件缺失，跳过"})

    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
