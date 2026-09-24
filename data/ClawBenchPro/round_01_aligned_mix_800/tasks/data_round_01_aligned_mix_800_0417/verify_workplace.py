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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_file = os.path.join(workspace, "final_order.json")
    
    score_details = []
    total_score = 0
    
    # 1. 检查文件是否存在
    file_exists = os.path.exists(target_file)
    if file_exists:
        score_details.append({"item": "文件存在性", "score": 10, "max_score": 10, "passed": True, "reason": "final_order.json 存在"})
        total_score += 10
    else:
        score_details.append({"item": "文件存在性", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 final_order.json"})
        
        # 文件不存在直接输出 0 分退出
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": 0, "details": score_details}, f, indent=2, ensure_ascii=False)
        return

    # 2. 检查 JSON 格式合法性
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        score_details.append({"item": "JSON 格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "成功解析 JSON"})
        total_score += 10
    except Exception as e:
        score_details.append({"item": "JSON 格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON 解析失败: {e}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)
        return

    # 3. 检查 Schema (必要键是否存在)
    has_keys = "missing_parts" in data and "longest_part_inch" in data
    if has_keys:
        score_details.append({"item": "Schema 完整性", "score": 10, "max_score": 10, "passed": True, "reason": "包含所有必要字段"})
        total_score += 10
    else:
        score_details.append({"item": "Schema 完整性", "score": 0, "max_score": 10, "passed": False, "reason": "缺失 missing_parts 或 longest_part_inch 字段"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)
        return

    # 4. 检查 missing_parts 的内容准确性
    expected_parts = ["chassis_rail", "diesel_tank", "front_grille", "led_headlights", "mud_flaps"]
    missing_parts = data.get("missing_parts", [])
    
    if not isinstance(missing_parts, list):
        score_details.append({"item": "missing_parts 数据类型", "score": 0, "max_score": 5, "passed": False, "reason": "missing_parts 不是列表"})
    else:
        score_details.append({"item": "missing_parts 数据类型", "score": 5, "max_score": 5, "passed": True, "reason": "missing_parts 是列表"})
        total_score += 5
        
        # 检查元素是否完全正确（去重并对比）
        missing_parts_set = set(missing_parts)
        expected_parts_set = set(expected_parts)
        
        if missing_parts_set == expected_parts_set:
            score_details.append({"item": "缺失零件提取准确度", "score": 25, "max_score": 25, "passed": True, "reason": "成功提取所有正确的缺失零件，无幻觉数据"})
            total_score += 25
        else:
            correct_count = len(missing_parts_set.intersection(expected_parts_set))
            wrong_count = len(missing_parts_set - expected_parts_set)
            pts = max(0, correct_count * 5 - wrong_count * 5)
            score_details.append({"item": "缺失零件提取准确度", "score": pts, "max_score": 25, "passed": pts > 0, "reason": f"提取命中 {correct_count} 个，错误/幻觉 {wrong_count} 个"})
            total_score += pts
            
        # 检查是否排序
        if sorted(expected_parts) == missing_parts:
            score_details.append({"item": "缺失零件排序", "score": 10, "max_score": 10, "passed": True, "reason": "列表按字典序正确排序"})
            total_score += 10
        else:
            score_details.append({"item": "缺失零件排序", "score": 0, "max_score": 10, "passed": False, "reason": "列表未按要求排序"})

    # 5. 检查 longest_part_inch 的计算结果
    longest = data.get("longest_part_inch")
    if isinstance(longest, (int, float)):
        # 允许极小的浮点误差
        if math.isclose(longest, 25.0, abs_tol=0.1):
            score_details.append({"item": "最长部件尺寸计算", "score": 30, "max_score": 30, "passed": True, "reason": "成功排除诱饵并正确完成单位转换"})
            total_score += 30
        elif math.isclose(longest, 1000.0, abs_tol=0.1):
            score_details.append({"item": "最长部件尺寸计算", "score": 0, "max_score": 30, "passed": False, "reason": "使用了废弃的 decoy blueprint 数据"})
        else:
            score_details.append({"item": "最长部件尺寸计算", "score": 0, "max_score": 30, "passed": False, "reason": f"数值计算错误，预期 25.0，实际为 {longest}"})
    else:
        score_details.append({"item": "最长部件尺寸计算", "score": 0, "max_score": 30, "passed": False, "reason": "longest_part_inch 不是有效的数值类型"})

    # 汇总写入
    with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
