import os
import sys
import json
import httpx
import re
from openai import OpenAI

# =====================================================================
# 强制 API 规范：初始化 OpenAI 客户端并强制关闭 SSL 验证
# =====================================================================
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
    """大模型辅助判断非结构化内容及语义的统一接口"""
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

# =====================================================================
# 工具函数：用于从复杂嵌套 JSON 结构中递归提取纯文本与数值，防欺骗
# =====================================================================
def extract_strings(data):
    """递归压平所有键和字符串值，用于精确的实体匹配"""
    res = []
    if isinstance(data, dict):
        for k, v in data.items():
            res.append(str(k))
            res.extend(extract_strings(v))
    elif isinstance(data, list):
        for v in data:
            res.extend(extract_strings(v))
    else:
        res.append(str(data))
    return res

def extract_numbers(data):
    """递归压平并提取所有数值形式的内容，容忍字符串格式的数字"""
    res = []
    if isinstance(data, dict):
        for v in data.values():
            res.extend(extract_numbers(v))
    elif isinstance(data, list):
        for v in data:
            res.extend(extract_numbers(v))
    elif isinstance(data, (int, float)):
        res.append(float(data))
    elif isinstance(data, str):
        # 防护：尝试从字符串内部用正则捕捉数字
        matches = re.findall(r"[-+]?\d*\.\d+|\d+", data)
        res.extend([float(m) for m in matches])
    return res

def write_score(total, details, workspace):
    """统一写入结果标准规范文件"""
    output_path = os.path.join(workspace, "workplace_score.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"total_score": total, "details": details}, f, ensure_ascii=False, indent=2)

# =====================================================================
# 核心验证逻辑
# =====================================================================
def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    file_path = os.path.join(workspace, "desk", "audit.json")
    
    # 1. 结构与文件存在性检测 (10分)
    if os.path.isfile(file_path):
        score_details.append({"item": "检查目标文件 desk/audit.json 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查目标文件 desk/audit.json 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到文件 desk/audit.json"})
        write_score(0, score_details, workspace)
        return

    # 2. JSON 格式合法性检测 (10分)
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    try:
        data = json.loads(content)
        score_details.append({"item": "检查文件内容是否为合法 JSON", "score": 10, "max_score": 10, "passed": True, "reason": "成功解析 JSON"})
        total_score += 10
    except json.JSONDecodeError:
        score_details.append({"item": "检查文件内容是否为合法 JSON", "score": 0, "max_score": 10, "passed": False, "reason": "文件内容不是合法的 JSON 格式，违背要求"})
        write_score(total_score, score_details, workspace)
        return
        
    all_strs = extract_strings(data)
    all_strs_joined = " ".join(all_strs).lower()
    
    # 3. 目标 VIP 名单提取正确性 (20分)
    targets = ["alice walker", "margaret atwood", "toni morrison"]
    missing = [t for t in targets if t not in all_strs_joined]
    if not missing:
        score_details.append({"item": "是否准确包含三位问题 VIP 名字", "score": 20, "max_score": 20, "passed": True, "reason": "所有目标 VIP 名字均出现于结果中"})
        total_score += 20
    else:
        score_details.append({"item": "是否准确包含三位问题 VIP 名字", "score": 0, "max_score": 20, "passed": False, "reason": f"缺失关键目标 VIP: {missing}"})

    # 4. 数据隔离与剔除的严谨度 (20分)
    # 不允许包含非目标人员，否则说明未真正执行逻辑过滤
    excludes = ["bob general", "han kang", "stephen king", "jane doe", "james baldwin"]
    included_excludes = [e for e in excludes if e in all_strs_joined]
    if not included_excludes:
        score_details.append({"item": "是否严格过滤非目标人员及非 VIP 参会者", "score": 20, "max_score": 20, "passed": True, "reason": "未包含任何其他不需要处理的与会者"})
        total_score += 20
    else:
        score_details.append({"item": "是否严格过滤非目标人员及非 VIP 参会者", "score": 0, "max_score": 20, "passed": False, "reason": f"未正确过滤，包含了多余人员: {included_excludes}"})

    # 5. 精确费用计算校验 (30分)
    # 正确总和 = 1050.50 (inv_01) + 320.25 (inv_02) + 89.99 (inv_02) + 40.00 (inv_03) = 1500.74
    all_nums = extract_numbers(data)
    has_target_cost = False
    for num in all_nums:
        if abs(num - 1500.74) < 0.01:
            has_target_cost = True
            break
            
    if has_target_cost:
        score_details.append({"item": "是否通过代码逻辑精确计算出食品和饮料总费用", "score": 30, "max_score": 30, "passed": True, "reason": "在 JSON 中找到了精确计算的数值 1500.74"})
        total_score += 30
    else:
        extracted_display = all_nums[:5] if all_nums else "空"
        score_details.append({"item": "是否通过代码逻辑精确计算出食品和饮料总费用", "score": 0, "max_score": 30, "passed": False, "reason": f"未能在结果中找到正确合计数值 1500.74，提取到的前几个数值为: {extracted_display}"})
        
    # 6. 利用大模型评估字典 Key 设计的语义清晰度 (10分)
    # User Persona 要求 key 必须 clean, logical 且清晰表明意义
    keys = list(data.keys()) if isinstance(data, dict) else []
    if keys:
        keys_str = ", ".join(keys)
        prompt = (
            "We have a JSON object with the following top-level keys: {}. "
            "Based on the context, one or more keys should clearly represent 'total food and beverage cost' and 'list of problematic VIPs'. "
            "Do these keys reasonably and explicitly convey these exact meanings?"
        ).format(keys_str)
        
        is_clear = llm_judge_content(prompt, keys_str)
        if is_clear:
            score_details.append({"item": "大模型验证JSON Keys的语义清晰度", "score": 10, "max_score": 10, "passed": True, "reason": "Key 命名清晰严谨，符合管理者的苛刻要求"})
            total_score += 10
        else:
            score_details.append({"item": "大模型验证JSON Keys的语义清晰度", "score": 0, "max_score": 10, "passed": False, "reason": f"Key 的命名 ({keys_str}) 模糊或者不具备直接说明意义"})
    else:
        score_details.append({"item": "大模型验证JSON Keys的语义清晰度", "score": 0, "max_score": 10, "passed": False, "reason": "结果结构并非字典，未能提供清晰的语义 Key 描述"})
        
    write_score(total_score, score_details, workspace)

if __name__ == "__main__":
    main()
