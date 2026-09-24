import os
import sys
import json
import re
import httpx
from openai import OpenAI

# =====================================================================
# 强制 API 规范初始化
# =====================================================================
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 强制关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """大模型进行非结构化语义判断的统一接口"""
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict data validation assistant. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[Content to Judge]:\n{file_content}"}
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

# =====================================================================
# 辅助函数：递归解析 JSON 中的所有的键和值
# =====================================================================
def extract_values_and_keys(obj):
    values = []
    keys = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            keys.append(str(k))
            res_v, res_k = extract_values_and_keys(v)
            values.extend(res_v)
            keys.extend(res_k)
    elif isinstance(obj, list):
        for item in obj:
            res_v, res_k = extract_values_and_keys(item)
            values.extend(res_v)
            keys.extend(res_k)
    else:
        values.append(obj)
    return values, keys

# =====================================================================
# 核心验证逻辑
# =====================================================================
def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    target_file = os.path.join(workspace, "hike_manifest.json")
    
    # -----------------------------
    # 1. 检查物理文件存在性 (20分)
    # -----------------------------
    if os.path.exists(target_file):
        score_details.append({"item": "检查结果文件是否存在", "score": 20, "max_score": 20, "passed": True, "reason": "文件 hike_manifest.json 存在。"})
        total_score += 20
    else:
        score_details.append({"item": "检查结果文件是否存在", "score": 0, "max_score": 20, "passed": False, "reason": "未找到目标文件 hike_manifest.json。"})
        # 核心文件缺失直接判定结束
        write_score(workspace, total_score, score_details)
        return
        
    # -----------------------------
    # 2. 检查 JSON 格式合法性 (20分)
    # -----------------------------
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        score_details.append({"item": "检查 JSON 格式合法性", "score": 20, "max_score": 20, "passed": True, "reason": "文件是结构完整的合法 JSON 格式。"})
        total_score += 20
    except Exception as e:
        score_details.append({"item": "检查 JSON 格式合法性", "score": 0, "max_score": 20, "passed": False, "reason": f"解析 JSON 结构失败，非合法数据格式: {str(e)}"})
        write_score(workspace, total_score, score_details)
        return

    # 展开所有数值以备检查（严格避免正则模糊匹配 JSON 字符串本身）
    values, keys = extract_values_and_keys(data)
    
    # -----------------------------
    # 3. 检查结构清洁度/防作弊捏造 (10分)
    # -----------------------------
    # 根据题目要求“a clean JSON document”，若写入大量无用键值或堆砌全文，则判定为捏造或废话
    if len(keys) > 8:
        score_details.append({"item": "检查 JSON 结构是否冗余", "score": 0, "max_score": 10, "passed": False, "reason": f"提取到 {len(keys)} 个键，超出合理的极简报告范畴，存在捏造或无意义堆砌嫌疑。"})
    else:
        score_details.append({"item": "检查 JSON 结构是否冗余", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 键值规模合适，文档足够清洁 (Clean)。"})
        total_score += 10
        
    # -----------------------------
    # 4. 精准验证：Trail 名称提取正确性 (20分)
    # -----------------------------
    trail_found = False
    for v in values:
        if isinstance(v, str) and "little bear loop" in v.lower():
            trail_found = True
            break
    
    if trail_found:
        score_details.append({"item": "关键信息验证: Trail 名称", "score": 20, "max_score": 20, "passed": True, "reason": "准确找出了符合 Easy 和 < 3.0 miles 要求的路线 (Little Bear Loop)。"})
        total_score += 20
    else:
        score_details.append({"item": "关键信息验证: Trail 名称", "score": 0, "max_score": 20, "passed": False, "reason": "未能从结果中正确提供路线名称 'Little Bear Loop'，逻辑筛选失败。"})

    # -----------------------------
    # 5. 精准验证：装备总重量聚合与单位转换准确性 (20分)
    # -----------------------------
    # Expected target is 157.5 oz ≈ 4.465 kg. We accept precision between 4.45 and 4.48.
    weight_found = False
    for v in values:
        if isinstance(v, (int, float)):
            if 4.45 <= v <= 4.48:
                weight_found = True
                break
        elif isinstance(v, str):
            # 防止 Agent 把数值连同单位写成字符串，例如 "4.465 kg"
            nums = re.findall(r"[-+]?\d*\.\d+|\d+", v)
            for n in nums:
                if 4.45 <= float(n) <= 4.48:
                    weight_found = True
                    break

    if weight_found:
        score_details.append({"item": "关键计算验证: 装备重量与千克换算", "score": 20, "max_score": 20, "passed": True, "reason": "正确筛选 'Needed' 装备、计算了总重量并正确执行了到千克 (KG) 的单位转换。"})
        total_score += 20
    else:
        score_details.append({"item": "关键计算验证: 装备重量与千克换算", "score": 0, "max_score": 20, "passed": False, "reason": "未找到约 4.465 kg 的数值结果，计算错误或没有转换单位。"})
        
    # -----------------------------
    # 6. LLM 语义检测：键名明确度 (10分)
    # -----------------------------
    # 用户明确要求 explicitly states ... in kilograms
    if trail_found and weight_found and keys:
        keys_str = ", ".join(keys)
        prompt = "Does the following list of JSON keys indicate that the JSON explicitly specifies the name of a trail and the final gear weight in kilograms (kg)? Return YES if it is explicitly clear from the key names, and NO if it is vague or missing the mention of kilograms."
        llm_pass = llm_judge_content(prompt, keys_str)
        if llm_pass:
            score_details.append({"item": "利用大模型检查 JSON 键语意明确度", "score": 10, "max_score": 10, "passed": True, "reason": "大模型判定输出文档的 JSON 键能够明确表明其是包含路线名与千克重量单位。"})
            total_score += 10
        else:
            score_details.append({"item": "利用大模型检查 JSON 键语意明确度", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定输出的 JSON 键不够清晰，无法让人立刻识别出这是对应千克(kg)重量清单。"})
    else:
         score_details.append({"item": "利用大模型检查 JSON 键语意明确度", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 中连关键的值都缺失或为空，跳过 LLM 对键名语义的校验。"})

    write_score(workspace, total_score, score_details)


def write_score(workspace, total_score, score_details):
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "total_score": total_score,
                "details": score_details
            }, 
            f, indent=2, ensure_ascii=False
        )


if __name__ == "__main__":
    verify()
