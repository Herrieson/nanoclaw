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

def find_count_for_brand(data, brand_name):
    """
    原生且严密的纯代码 JSON 结构化解析探针。
    通过递归应对 Agent 可能创造的各种千奇百怪但合乎逻辑的 JSON Schema（杜绝正则模糊匹配）。
    """
    brand_lower = brand_name.lower().strip()
    
    if isinstance(data, dict):
        # 场景 1: 品牌名作为 Key (例如 {"WoodSpecs": 5} 或 {"WoodSpecs": {"count": 5}})
        for k, v in data.items():
            if k.lower().strip() == brand_lower:
                if isinstance(v, (int, float)):
                    return v
                elif isinstance(v, dict):
                    # 寻找字典内的第一个数值
                    for sub_v in v.values():
                        if isinstance(sub_v, (int, float)):
                            return sub_v
                elif isinstance(v, list) and len(v) > 0 and isinstance(v[0], (int, float)):
                    return v[0]

        # 场景 2: 品牌名作为 Value (例如 {"brand": "WoodSpecs", "quantity": 5})
        is_match = False
        for k, v in data.items():
            if isinstance(v, str) and v.lower().strip() == brand_lower:
                is_match = True
        
        if is_match:
            # 优先寻找特征明显的计数 Key
            for k, v in data.items():
                if isinstance(v, (int, float)) and any(x in k.lower() for x in ['count', 'total', 'quant', 'amount', 'num', 'val']):
                    return v
            # 退化处理：返回该对象里的首个数值
            for k, v in data.items():
                if isinstance(v, (int, float)):
                    return v

        # 递归遍历字典子节点
        for k, v in data.items():
            res = find_count_for_brand(v, brand_name)
            if res is not None:
                return res

    elif isinstance(data, list):
        # 递归遍历列表子节点
        for item in data:
            res = find_count_for_brand(item, brand_name)
            if res is not None:
                return res

    return None

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    score_details = []
    total_score = 0
    
    # 1. 结构验证: 检查输出目录 green_report (10分)
    report_dir = os.path.join(workspace, "green_report")
    dir_exists = os.path.isdir(report_dir)
    if dir_exists:
        score_details.append({"item": "检查结果目录 green_report 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录成功创建"})
        total_score += 10
    else:
        score_details.append({"item": "检查结果目录 green_report 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 green_report 目录"})
        
    # 2. 格式验证: 检查并解析唯一 JSON 文件 (10分)
    json_data = None
    json_content_str = ""
    json_valid = False
    
    if dir_exists:
        files = [f for f in os.listdir(report_dir) if f.endswith('.json')]
        if len(files) == 1:
            file_path = os.path.join(report_dir, files[0])
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json_content_str = f.read()
                    json_data = json.loads(json_content_str)
                json_valid = True
                score_details.append({"item": "检查是否有唯一的合法 JSON 报告文件", "score": 10, "max_score": 10, "passed": True, "reason": f"成功解析 {files[0]}"})
                total_score += 10
            except Exception as e:
                score_details.append({"item": "检查是否有唯一的合法 JSON 报告文件", "score": 0, "max_score": 10, "passed": False, "reason": f"文件不符合 JSON 规范: {e}"})
        else:
            score_details.append({"item": "检查是否有唯一的合法 JSON 报告文件", "score": 0, "max_score": 10, "passed": False, "reason": f"找到 {len(files)} 个 JSON 文件，期望 1 个"})
    else:
         score_details.append({"item": "检查是否有唯一的合法 JSON 报告文件", "score": 0, "max_score": 10, "passed": False, "reason": "依赖的 green_report 目录不存在"})

    # 3. 语义验证: 检查结构是否清晰区分 (20分)
    if json_valid:
        prompt = (
            "You are evaluating a JSON file containing an eye-glasses recycling report. "
            "The user explicitly requested to structure a JSON summary that CLEARLY SEPARATES "
            "the totals for APPROVED partner brands from the totals for UNAPPROVED junk brands. "
            "Analyze the JSON keys and structural grouping. "
            "Does it clearly separate or group the approved brands apart from the unapproved brands?"
        )
        is_separated = llm_judge_content(prompt, json_content_str)
        if is_separated:
            score_details.append({"item": "利用大模型检查 JSON 是否清晰区分合作与非合作品牌", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定结构合理且分离清晰"})
            total_score += 20
        else:
            score_details.append({"item": "利用大模型检查 JSON 是否清晰区分合作与非合作品牌", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定 JSON Schema 混杂了所有数据，未能有效区分类别"})
    else:
        score_details.append({"item": "利用大模型检查 JSON 是否清晰区分合作与非合作品牌", "score": 0, "max_score": 20, "passed": False, "reason": "无合法 JSON 内容供评估"})

    # 4. 精准数值探针验证: 对各个品牌总和的绝对准确性进行验证 (共 60 分)
    brands_to_check = [
        ("WoodSpecs", 5, 8, "Approved"),
        ("OceanPlastics Co.", 1, 7, "Approved"),
        ("LeafFrames", 4, 8, "Approved"),
        ("EcoGaze", 2, 7, "Approved"),
        ("RayBan", 1, 10, "Unapproved"),
        ("FastFashion", 5, 10, "Unapproved"),
        ("CheapoPlastics", 2, 10, "Unapproved")
    ]
    
    if json_valid:
        for brand, expected, max_s, b_type in brands_to_check:
            actual = find_count_for_brand(json_data, brand)
            if actual == expected:
                score_details.append({"item": f"精准解析 {brand} ({b_type}) 的统计总量", "score": max_s, "max_score": max_s, "passed": True, "reason": f"成功在 JSON 任意合法结构中定位到数量: {actual}"})
                total_score += max_s
            else:
                score_details.append({"item": f"精准解析 {brand} ({b_type}) 的统计总量", "score": 0, "max_score": max_s, "passed": False, "reason": f"数量错误或未记录。期望: {expected}, 实际提取: {actual}"})
    else:
        for brand, expected, max_s, b_type in brands_to_check:
            score_details.append({"item": f"精准解析 {brand} ({b_type}) 的统计总量", "score": 0, "max_score": max_s, "passed": False, "reason": "无合法 JSON 供代码解析"})
            
    # 输出结果文件
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
