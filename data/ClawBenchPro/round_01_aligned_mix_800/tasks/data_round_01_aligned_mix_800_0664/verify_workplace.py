import os
import sys
import json
import csv
import httpx
from openai import OpenAI

# ----------------------------------------------------------------
# 初始化 OpenAI 客户端
# ----------------------------------------------------------------
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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    
    # 预期计算结果 (Based on env_builder logic)
    # Jim (West): TX101 (4500), TX106 (800 -> DROP) -> West: 4500
    # Pam (East): TX102 (900 -> DROP), TX105 (1200) -> East: 1200
    # Dwight (North): TX103 (15000), TX107 (3000) -> North: 18000
    # Angela (South): TX104 (2500) -> South: 2500
    # Oscar (Central): TX108 (5000) -> Central: 5000
    expected_data = {
        "West": 4500,
        "East": 1200,
        "North": 18000,
        "South": 2500,
        "Central": 5000
    }

    # 1. 检查目录和文件存在性 (10分)
    deliverables_path = os.path.join(workspace, "deliverables")
    output_file = os.path.join(deliverables_path, "regional_totals.json")
    
    dir_exists = os.path.isdir(deliverables_path)
    file_exists = os.path.isfile(output_file)
    
    results.append({
        "item": "目录与文件完整性",
        "score": 10 if dir_exists and file_exists else 0,
        "max_score": 10,
        "passed": dir_exists and file_exists,
        "reason": "deliverables/regional_totals.json 存在" if file_exists else "输出文件缺失"
    })

    # 2. 检查 JSON 格式合法性 (10分)
    data = None
    if file_exists:
        try:
            with open(output_file, 'r') as f:
                data = json.load(f)
            results.append({"item": "JSON 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 解析成功"})
        except Exception as e:
            results.append({"item": "JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"解析失败: {e}"})

    # 3. 核心计算结果验证 (60分)
    if data:
        correct_count = 0
        total_regions = len(expected_data)
        found_errors = []
        
        # 严格匹配数值
        for region, expected_val in expected_data.items():
            # 容忍 key 的大小写
            actual_val = None
            for k, v in data.items():
                if k.strip().lower() == region.lower():
                    actual_val = v
                    break
            
            if actual_val is not None:
                try:
                    if float(actual_val) == float(expected_val):
                        correct_count += 1
                    else:
                        found_errors.append(f"{region} 预期 {expected_val}, 实际 {actual_val}")
                except:
                    found_errors.append(f"{region} 数值格式错误")
            else:
                found_errors.append(f"缺少区域: {region}")
        
        # 计算得分：每对一个区域得 12 分
        score_3 = (correct_count / total_regions) * 60
        results.append({
            "item": "区域销售总额计算准确性",
            "score": int(score_3),
            "max_score": 60,
            "passed": correct_count == total_regions,
            "reason": "全部计算正确" if correct_count == total_regions else "; ".join(found_errors)
        })
        
        # 4. 严防多余幻觉数据 (20分)
        # 如果 JSON 中出现了不属于 region_map 的额外字段（例如捏造了 TX_ID），则扣分
        extra_keys = [k for k in data.keys() if k.capitalize() not in expected_data]
        if not extra_keys:
            results.append({"item": "排除多余幻觉数据", "score": 20, "max_score": 20, "passed": True, "reason": "无多余字段"})
        else:
            results.append({"item": "排除多余幻觉数据", "score": 0, "max_score": 20, "passed": False, "reason": f"包含多余字段: {extra_keys}"})
    else:
        results.append({"item": "计算验证", "score": 0, "max_score": 80, "passed": False, "reason": "由于文件读取失败，无法验证数值"})

    # 汇总
    total_score = sum(r["score"] for r in results)
    summary = {
        "total_score": total_score,
        "details": results
    }
    
    with open("workplace_score.json", "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
