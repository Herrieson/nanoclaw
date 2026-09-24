import os
import sys
import json
import httpx
from openai import OpenAI

# 强制读取环境变量中的配置
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，强制关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """大模型语义验证函数，用于非结构化或半结构化语义校验"""
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

def check_amount(json_obj, target=2275.75):
    """递归查找所有值，确保精确合计金额的存在 (应对各种JSON结构嵌套)"""
    if isinstance(json_obj, dict):
        return any(check_amount(v, target) for v in json_obj.values())
    elif isinstance(json_obj, list):
        return any(check_amount(v, target) for v in json_obj)
    elif isinstance(json_obj, (int, float)):
        return abs(json_obj - target) < 0.01
    elif isinstance(json_obj, str):
        try:
            # 兼容带有千分位或货币符号的字符串格式
            cleaned = json_obj.replace(',', '').replace('$', '').strip()
            return abs(float(cleaned) - target) < 0.01
        except ValueError:
            return False
    return False

def get_all_strings(json_obj):
    """提取 JSON 中出现的所有字符串（键和值），用于原样字符串的强匹配"""
    strings = []
    if isinstance(json_obj, dict):
        for k, v in json_obj.items():
            strings.append(k)
            strings.extend(get_all_strings(v))
    elif isinstance(json_obj, list):
        for v in json_obj:
            strings.extend(get_all_strings(v))
    elif isinstance(json_obj, str):
        strings.append(json_obj)
    return strings

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_dir = os.path.join(workspace, "deliverables")
    
    details = []
    total_score = 0

    # 【检测项 1】: 目录与文件存在性 (10分)
    json_files = []
    if os.path.isdir(deliverables_dir):
        json_files = [f for f in os.listdir(deliverables_dir) if f.endswith('.json')]
    
    if json_files:
        details.append({"item": "Deliverables目录及JSON文件存在", "score": 10, "max_score": 10, "passed": True, "reason": f"找到了文件: {json_files[0]}"})
        total_score += 10
    else:
        details.append({"item": "Deliverables目录及JSON文件存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 deliverables 目录或任何 JSON 文件"})

    # 【检测项 2】: JSON 文件合法性解析 (10分)
    json_data = None
    json_content = ""
    if json_files:
        json_path = os.path.join(deliverables_dir, json_files[0])
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                json_content = f.read()
                json_data = json.loads(json_content)
            details.append({"item": "JSON格式合法", "score": 10, "max_score": 10, "passed": True, "reason": "代码成功解析了JSON结构"})
            total_score += 10
        except Exception as e:
            details.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON解析失败，格式异常: {e}"})
    else:
        details.append({"item": "JSON格式合法", "score": 0, "max_score": 10, "passed": False, "reason": "无文件可解析"})

    # 【依赖 JSON 解析的后续检测项】
    if json_data is not None:
        # 【检测项 3】: 计算金额精确提取 (40分 - 代码硬核比对)
        if check_amount(json_data, 2275.75):
            details.append({"item": "总金额计算准确度", "score": 40, "max_score": 40, "passed": True, "reason": "使用递归代码成功提取到了精准的合法总金额 2275.75"})
            total_score += 40
        else:
            details.append({"item": "总金额计算准确度", "score": 0, "max_score": 40, "passed": False, "reason": "JSON 的键值中未发现正确的合计金额 2275.75"})

        # 【检测项 4】: 黑名单脏数据字符原样提取 (20分 - 代码硬核比对)
        all_strs = get_all_strings(json_data)
        expected_rogues = ["Shady Steve", "Mike's Lawn Care", "QuickFix LLC"]
        missing = [r for r in expected_rogues if r not in all_strs]
        
        if not missing:
            details.append({"item": "无资质承包商精准提取", "score": 20, "max_score": 20, "passed": True, "reason": "3名无资质承包商均以 CSV 中原样的字符被写入JSON"})
            total_score += 20
        else:
            details.append({"item": "无资质承包商精准提取", "score": 0, "max_score": 20, "passed": False, "reason": f"缺失或拼写被错误修正: {missing}"})

        # 【检测项 5】: 大模型逻辑校验与防幻觉 (20分 - 语义与逻辑检查)
        prompt = (
            "Check if this JSON explicitly and solely classifies 'Shady Steve', \"Mike's Lawn Care\", and 'QuickFix LLC' "
            "as the rogue, unapproved, or unauthorized contractors. It MUST NOT label legitimately approved vendors like "
            "'A1 Plumbing', 'Holy Cross Roofers', or 'st. peter landscaping' as rogue. If there are any hallucinated "
            "vendors, fabricated extra fields, or reversed categories, you must reject it. "
            "Answer YES if the data segregation logic is sound and hallucination-free. Answer NO otherwise."
        )
        if llm_judge_content(prompt, json_content):
            details.append({"item": "分类逻辑有效性与防幻觉(大模型检测)", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定JSON逻辑清晰无误，未产生混淆或幻觉"})
            total_score += 20
        else:
            details.append({"item": "分类逻辑有效性与防幻觉(大模型检测)", "score": 0, "max_score": 20, "passed": False, "reason": "大模型发现JSON逻辑错乱、幻觉捏造或白名单承包商被误判"})
    else:
        # JSON 不存在或解析失败时的兜底
        details.append({"item": "总金额计算准确度", "score": 0, "max_score": 40, "passed": False, "reason": "前置条件失败，无法验证"})
        details.append({"item": "无资质承包商精准提取", "score": 0, "max_score": 20, "passed": False, "reason": "前置条件失败，无法验证"})
        details.append({"item": "分类逻辑有效性与防幻觉(大模型检测)", "score": 0, "max_score": 20, "passed": False, "reason": "前置条件失败，无法验证"})

    # 输出结果文件
    output = {
        "total_score": total_score,
        "details": details
    }
    
    score_file = os.path.join(workspace, "workplace_score.json")
    with open(score_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
        
    print(f"Validation complete. Total Score: {total_score}/100")

if __name__ == "__main__":
    main()
