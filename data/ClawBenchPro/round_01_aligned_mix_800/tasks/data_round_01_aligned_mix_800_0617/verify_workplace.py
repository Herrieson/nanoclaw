import os
import sys
import json
import httpx
from openai import OpenAI

# 强制要求的 LLM 验证初始化逻辑
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

def write_score(total_score, details):
    res = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    target_file = os.path.join(workspace, "final_order.json")
    
    # 1. 检查文件是否存在 (10分)
    if os.path.exists(target_file):
        total_score += 10
        score_details.append({"item": "检查 final_order.json 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
    else:
        score_details.append({"item": "检查 final_order.json 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        write_score(total_score, score_details)
        return

    # 2. 检查 JSON 格式是否合法 (10分)
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        total_score += 10
        score_details.append({"item": "检查 JSON 格式是否合法", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 格式合法且可解析"})
    except Exception as e:
        score_details.append({"item": "检查 JSON 格式是否合法", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        write_score(total_score, score_details)
        return

    # 3. 检查必备字段是否存在 (20分)
    if isinstance(data, dict):
        has_missing = "missing_parts" in data
        has_longest = "longest_part_inch" in data
        
        if has_missing:
            total_score += 10
            score_details.append({"item": "包含 missing_parts 字段", "score": 10, "max_score": 10, "passed": True, "reason": "包含 missing_parts 数组"})
        else:
            score_details.append({"item": "包含 missing_parts 字段", "score": 0, "max_score": 10, "passed": False, "reason": "缺失 missing_parts 字段"})
            
        if has_longest:
            total_score += 10
            score_details.append({"item": "包含 longest_part_inch 字段", "score": 10, "max_score": 10, "passed": True, "reason": "包含 longest_part_inch 数值"})
        else:
            score_details.append({"item": "包含 longest_part_inch 字段", "score": 0, "max_score": 10, "passed": False, "reason": "缺失 longest_part_inch 字段"})
    else:
        score_details.append({"item": "JSON 根节点结构", "score": 0, "max_score": 20, "passed": False, "reason": "JSON 根节点必须是 Object / 字典"})
        has_missing, has_longest = False, False

    # 4. 精准比对缺失库存部件 (30分)
    if has_missing:
        # 正确答案：chassis_frame(0), exhaust_pipe(-2), mud_flaps(0), front_grille("none")
        expected_parts = {"chassis_frame", "exhaust_pipe", "mud_flaps", "front_grille"}
        actual_parts = data["missing_parts"]
        if isinstance(actual_parts, list):
            actual_set = set(actual_parts)
            if actual_set == expected_parts and len(actual_parts) == len(expected_parts):
                total_score += 30
                score_details.append({"item": "精准提取零库存和负库存部件", "score": 30, "max_score": 30, "passed": True, "reason": "完全匹配所有耗尽部件，无幻觉数据"})
            else:
                score_details.append({"item": "精准提取零库存和负库存部件", "score": 0, "max_score": 30, "passed": False, "reason": f"提取错误或存在幻觉数据。期待: {expected_parts}, 实际: {actual_parts}"})
        else:
            score_details.append({"item": "精准提取零库存和负库存部件", "score": 0, "max_score": 30, "passed": False, "reason": "missing_parts 并非数组类型"})

    # 5. 精准比对最大长度计算 (30分)
    if has_longest:
        actual_val = data["longest_part_inch"]
        if isinstance(actual_val, (int, float)):
            # 50.8 cm / 2.54 = 20.0 inch。允许一定浮点数精度误差。
            if abs(actual_val - 20.0) < 0.05:
                total_score += 30
                score_details.append({"item": "正确计算并转换最大尺寸", "score": 30, "max_score": 30, "passed": True, "reason": "正确找出最大长度并转换为 20.0 英寸"})
            else:
                score_details.append({"item": "正确计算并转换最大尺寸", "score": 0, "max_score": 30, "passed": False, "reason": f"数值错误，实际输出: {actual_val}，期待: 20.0"})
        else:
            score_details.append({"item": "正确计算并转换最大尺寸", "score": 0, "max_score": 30, "passed": False, "reason": "longest_part_inch 不是数字类型"})

    write_score(total_score, score_details)

if __name__ == "__main__":
    main()
