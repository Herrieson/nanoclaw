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
    """大模型语义校验统一接口"""
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

def extract_values(obj):
    """递归提取 JSON 中的所有标量值与键名以防数据隐藏嵌套"""
    values = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            values.extend(extract_values(k))
            values.extend(extract_values(v))
    elif isinstance(obj, list):
        for item in obj:
            values.extend(extract_values(item))
    else:
        values.append(obj)
    return values

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    total_score = 0
    results = []

    # 1. 验证目标目录是否存在 (10分)
    dir_path = os.path.join(workspace, "audit_results")
    if os.path.isdir(dir_path):
        results.append({"item": "目录 audit_results 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "成功创建报告目录"})
        total_score += 10
    else:
        results.append({"item": "目录 audit_results 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到指定目录 audit_results"})

    # 2. 验证目标文件是否存在 (10分)
    file_path = os.path.join(workspace, "audit_results", "final_audit.json")
    if os.path.isfile(file_path):
        results.append({"item": "文件 final_audit.json 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "审计报告文件存在"})
        total_score += 10
    else:
        results.append({"item": "文件 final_audit.json 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未生成最终的 json 文件"})

    # 3. 解析验证与 JSON 格式合法性 (10分)
    json_valid = False
    json_content = None
    if os.path.isfile(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                json_content = json.load(f)
            json_valid = True
            results.append({"item": "JSON 格式合法性", "score": 10, "max_score": 10, "passed": True, "reason": "是规范的 JSON 文件"})
            total_score += 10
        except Exception as e:
            results.append({"item": "JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": f"文件并非合法 JSON 格式: {e}"})
    else:
        results.append({"item": "JSON 格式合法性", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失，无法解析"})

    # 4. 精准核心数据验证：逻辑与计算探针 (共50分)
    if json_valid:
        extracted = extract_values(json_content)
        found_185 = False
        found_john_doe = False
        
        for v in extracted:
            if isinstance(v, (int, float)) and v == 185:
                found_185 = True
            elif isinstance(v, str) and v.strip() == "185":
                found_185 = True
            elif isinstance(v, str) and "john doe" in v.lower():
                found_john_doe = True

        # 时长计算验证: 25分
        if found_185:
            results.append({"item": "精确计算校验：总时长 185", "score": 25, "max_score": 25, "passed": True, "reason": "精准计算出时长为 185。说明Agent成功做到了剔除重复项(session 101)且处理了非标数据(30 mins)"})
            total_score += 25
        else:
            results.append({"item": "精确计算校验：总时长 185", "score": 0, "max_score": 25, "passed": False, "reason": "未找到 185 值。Agent可能由于未去重(得到230)或未清洗字符(得到155)导致计算错误。"})

        # 人员过滤验证: 25分
        if found_john_doe:
            results.append({"item": "精准过滤校验：捕获违规者 John Doe", "score": 25, "max_score": 25, "passed": True, "reason": "成功在结果中定位到违规人员 John Doe"})
            total_score += 25
        else:
            results.append({"item": "精准过滤校验：捕获违规者 John Doe", "score": 0, "max_score": 25, "passed": False, "reason": "未能锁定违规人员，数据隔离逻辑失效。"})

        # 5. LLM语义校验与幻觉监控 (20分)
        prompt_text = (
            "Check if the following JSON report meets ALL these strict criteria:\n"
            "1. It explicitly assigns 'John Doe' to a field indicating unauthorized, fake, unapproved, or non-white-listed personnel.\n"
            "2. It explicitly associates the value '185' with the total duration of valid/approved counseling sessions.\n"
            "3. It has a professional audit report structure and tone, and crucially, does NOT falsely accuse any valid, authorized counselors (e.g., Mary O'Connor, James Wilson, Sarah Miller, Robert Brown) of being unauthorized."
        )
        passed_llm = llm_judge_content(prompt_text, json.dumps(json_content, indent=2))
        if passed_llm:
            results.append({"item": "大模型语义与防幻觉验证", "score": 20, "max_score": 20, "passed": True, "reason": "语义映射正确，报告结构规范，且没有误伤合法辅导员"})
            total_score += 20
        else:
            results.append({"item": "大模型语义与防幻觉验证", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定内容存在逻辑错位：'185'/'John Doe' 未与正确语义字段关联，或发生捏造/误伤行为"})
    else:
        results.append({"item": "精确计算校验：总时长 185", "score": 0, "max_score": 25, "passed": False, "reason": "无法读取 JSON"})
        results.append({"item": "精准过滤校验：捕获违规者 John Doe", "score": 0, "max_score": 25, "passed": False, "reason": "无法读取 JSON"})
        results.append({"item": "大模型语义与防幻觉验证", "score": 0, "max_score": 20, "passed": False, "reason": "无法读取 JSON"})

    # 输出规范化验证结果
    output_data = {"total_score": total_score, "details": results}
    score_file = os.path.join(workspace, "workplace_score.json")
    with open(score_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
