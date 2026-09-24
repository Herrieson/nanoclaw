import os
import sys
import json
import httpx
import re
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 强制关闭 SSL 验证并初始化 OpenAI 客户端
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

def has_float_value(data, target, tol=1e-3):
    """递归检索 JSON，检查是否存在指定的浮点数值"""
    if isinstance(data, dict):
        return any(has_float_value(v, target, tol) for v in data.values())
    elif isinstance(data, list):
        return any(has_float_value(v, target, tol) for v in data)
    elif isinstance(data, (int, float)) and not isinstance(data, bool):
        return abs(data - target) < tol
    elif isinstance(data, str):
        try:
            return abs(float(data) - target) < tol
        except ValueError:
            return False
    return False

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "export", "stress_report.json")
    
    details = []
    total_score = 0
    
    # 1. 检查物理文件存在性 (15分)
    if os.path.exists(report_path):
        details.append({"item": "检查结果文件 export/stress_report.json 是否存在", "score": 15, "max_score": 15, "passed": True, "reason": "报告文件成功创建"})
        total_score += 15
    else:
        details.append({"item": "检查结果文件 export/stress_report.json 是否存在", "score": 0, "max_score": 15, "passed": False, "reason": "未找到报告文件 export/stress_report.json"})
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)
        return

    # 2. 检查 JSON 语法合法性 (15分)
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            content_str = f.read()
            data = json.loads(content_str)
        details.append({"item": "检查报告文件是否为合法的 JSON 格式", "score": 15, "max_score": 15, "passed": True, "reason": "JSON 解析成功"})
        total_score += 15
    except json.JSONDecodeError:
        details.append({"item": "检查报告文件是否为合法的 JSON 格式", "score": 0, "max_score": 15, "passed": False, "reason": "JSON 语法错误或非标准 JSON 格式"})
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)
        return
        
    # 3. 检查峰值负载的精确数值 (20分)
    # 沙盒内注入的确切最大值为 1250.75
    if has_float_value(data, 1250.75):
        details.append({"item": "检查 JSON 是否精准包含绝对峰值负载的计算结果 (1250.75)", "score": 20, "max_score": 20, "passed": True, "reason": "找到了正确的峰值负载数值，计算无误"})
        total_score += 20
    else:
        details.append({"item": "检查 JSON 是否精准包含绝对峰值负载的计算结果 (1250.75)", "score": 0, "max_score": 20, "passed": False, "reason": "未找到正确的峰值负载数值 1250.75，大概率计算错误或被损坏文件干扰"})

    # 4. 严查传感器 ID 集合是否完全吻合，禁止捏造与遗漏 (30分)
    # 仅包含峰值 TX-007 与 超限 TX-004, TX-009
    found_ids = set(re.findall(r'TX-\d{3}', content_str))
    expected_ids = {"TX-007", "TX-004", "TX-009"}
    if found_ids == expected_ids:
        details.append({"item": "检查提取的传感器 ID 集合是否完全正确且无捏造 (仅包含 TX-007, TX-004, TX-009)", "score": 30, "max_score": 30, "passed": True, "reason": "传感器 ID 列表严密匹配，没有受脏数据污染"})
        total_score += 30
    else:
        missing = expected_ids - found_ids
        extra = found_ids - expected_ids
        reason = f"传感器提取存在瑕疵。缺失: {missing if missing else '无'}, 多余(幻觉/错误过滤): {extra if extra else '无'}"
        details.append({"item": "检查提取的传感器 ID 集合是否完全正确且无捏造 (仅包含 TX-007, TX-004, TX-009)", "score": 0, "max_score": 30, "passed": False, "reason": reason})

    # 5. LLM 非结构化验证: Schema 语义映射及工程师风格命名 (20分)
    prompt_text = (
        "Evaluate the semantics and naming tone of the following JSON output. "
        "Does the JSON clearly and accurately associate the transducer 'TX-007' specifically with the peak load / maximum limit? "
        "Does it correctly list 'TX-004' and 'TX-009' together as the specific transducers that breached the threshold? "
        "Furthermore, are the JSON keys concisely named in a professional engineering style (e.g., 'peak_load', 'breached_sensors'), "
        "avoiding any conversational, chatty, or overly verbose keys?"
    )
    is_semantic_ok = llm_judge_content(prompt_text, content_str)
    if is_semantic_ok:
        details.append({"item": "利用大模型检查 JSON 的 Schema 语义映射关系以及工程师风格规范", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定 Schema 语义分配正确，命名风格符合苛刻工程师设定"})
        total_score += 20
    else:
        details.append({"item": "利用大模型检查 JSON 的 Schema 语义映射关系以及工程师风格规范", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定 Schema 语义错误（如混淆了峰值与超限名单）或存在废话/不专业的字段命名"})

    # 写入最终结果
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
