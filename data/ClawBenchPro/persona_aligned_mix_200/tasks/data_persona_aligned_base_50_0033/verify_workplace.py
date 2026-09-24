import os
import sys
import json
import math
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

def extract_quaternions(json_obj):
    """
    通过结构遍历，严格从任意层级的嵌套 JSON 中提取出类似 [float, float, float, float] 的记录，
    规避纯正则表达式可能引发的假阳性匹配。
    """
    extracted = []
    
    def traverse(obj):
        if isinstance(obj, dict):
            nums = [v for v in obj.values() if isinstance(v, (int, float))]
            if len(nums) == 4:
                # 优先尝试根据 w, x, y, z 键名提取
                keys = list(obj.keys())
                w_v = next((obj[k] for k in keys if 'w' in k.lower()), None)
                x_v = next((obj[k] for k in keys if 'x' in k.lower()), None)
                y_v = next((obj[k] for k in keys if 'y' in k.lower()), None)
                z_v = next((obj[k] for k in keys if 'z' in k.lower()), None)
                if all(v is not None for v in [w_v, x_v, y_v, z_v]):
                    extracted.append((float(w_v), float(x_v), float(y_v), float(z_v)))
                else:
                    # 降级：按数值顺序提取
                    extracted.append(tuple(float(n) for n in nums[:4]))
            else:
                for v in obj.values():
                    traverse(v)
        elif isinstance(obj, list):
            # 检查当前列表是否恰好为一组四元数
            nums = [x for x in obj if isinstance(x, (int, float))]
            if len(nums) == 4 and len(obj) == 4:
                extracted.append(tuple(float(n) for n in nums))
            else:
                for v in obj:
                    traverse(v)

    traverse(json_obj)
    return extracted

def match_quaternions(extracted, expected):
    matched_flags = [False] * len(expected)
    score = 0
    for ex in extracted:
        best_match_idx = -1
        for i, exp in enumerate(expected):
            if not matched_flags[i]:
                # 允许极小的浮点数误差
                if all(math.isclose(a, b, abs_tol=1e-3) for a, b in zip(ex, exp)):
                    best_match_idx = i
                    break
        if best_match_idx != -1:
            matched_flags[best_match_idx] = True
            score += 10
            
    return score, matched_flags

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_file = os.path.join(workspace, "flight_dynamics", "quaternions.json")
    
    score_details = []
    total_score = 0
    
    # 1. 物理探针：检查文件是否存在
    if os.path.exists(target_file):
        score_details.append({"item": "检查目标结果文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 flight_dynamics/quaternions.json 存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查目标结果文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件 flight_dynamics/quaternions.json 不存在"})
        result = {"total_score": 0, "details": score_details}
        with open("workplace_score.json", "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        return

    # 2. 结构探针：检查 JSON 合法性
    with open(target_file, "r") as f:
        content = f.read()
        
    json_data = None
    try:
        json_data = json.loads(content)
        score_details.append({"item": "验证 JSON 语法格式", "score": 10, "max_score": 10, "passed": True, "reason": "文件是合法的 JSON"})
        total_score += 10
    except Exception as e:
        score_details.append({"item": "验证 JSON 语法格式", "score": 0, "max_score": 10, "passed": False, "reason": f"解析 JSON 失败: {e}"})

    # 3. LLM 语义探针：判断 Key 命名是否具可读性
    if json_data is not None:
        prompt = "Does the following JSON content clearly express quaternion components using explicit keys like q_w, q_x, q_y, q_z, or have an extremely clear and unambiguous array structure for quaternions?"
        is_clear = llm_judge_content(prompt, content)
        if is_clear:
            score_details.append({"item": "利用大模型检查数据字段表达是否清晰", "score": 10, "max_score": 10, "passed": True, "reason": "大模型判定 JSON 结构中包含清晰的四元数表达或键名"})
            total_score += 10
        else:
            score_details.append({"item": "利用大模型检查数据字段表达是否清晰", "score": 0, "max_score": 10, "passed": False, "reason": "大模型认为数据字段不够直观或缺失相关标记"})
    else:
        score_details.append({"item": "利用大模型检查数据字段表达是否清晰", "score": 0, "max_score": 10, "passed": False, "reason": "JSON无法解析，跳过大模型检测"})

    # 4 & 5. 核心计算探针：防幻觉与精度验证
    expected_data = [
        (0.9990, 0.0100, 0.0200, -0.0400),
        (0.9950, 0.0250, 0.0350, -0.0890),
        (0.9800, 0.0500, 0.0700, -0.1790),
        (0.9500, 0.0900, 0.1200, -0.2700),
        (0.9000, 0.1500, 0.1800, -0.3700)
    ]
    
    if json_data is not None:
        extracted = extract_quaternions(json_data)
        if len(extracted) == 0:
            score_details.append({"item": "防幻觉及数据完整性检测", "score": 0, "max_score": 20, "passed": False, "reason": "未能在 JSON 中找到四元数数据组"})
            score_details.append({"item": "验证四元数数值提取精度", "score": 0, "max_score": 50, "passed": False, "reason": "无数据可校验"})
        else:
            acc_score, matched_flags = match_quaternions(extracted, expected_data)
            
            # 计算幻觉与遗漏扣分
            extra_items = len(extracted) - sum(matched_flags) # 找到了但无法匹配上的伪造数据
            missing_items = len(expected_data) - sum(matched_flags) # 漏找的数据
            
            penalty = min(extra_items * 5, 20)
            hal_score = 20 - penalty - (missing_items * 4)
            hal_score = max(0, hal_score)
            
            if hal_score == 20:
                score_details.append({"item": "防幻觉及数据完整性检测", "score": 20, "max_score": 20, "passed": True, "reason": "精准提取了所有5组数据，且无任何冗余错漏数据"})
                total_score += 20
            else:
                score_details.append({"item": "防幻觉及数据完整性检测", "score": hal_score, "max_score": 20, "passed": False, "reason": f"提取存在漏掉或冗余: 漏掉 {missing_items} 组，多出 {extra_items} 组无法对齐的数据"})
                total_score += hal_score
                
            # 精度分
            score_details.append({"item": "验证四元数数值提取精度", "score": acc_score, "max_score": 50, "passed": acc_score == 50, "reason": f"成功匹配 {sum(matched_flags)}/5 组四元数，每组 10 分"})
            total_score += acc_score
    else:
        score_details.append({"item": "防幻觉及数据完整性检测", "score": 0, "max_score": 20, "passed": False, "reason": "无有效 JSON 供检查"})
        score_details.append({"item": "验证四元数数值提取精度", "score": 0, "max_score": 50, "passed": False, "reason": "无有效 JSON 供检查"})

    result = {"total_score": total_score, "details": score_details}
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
