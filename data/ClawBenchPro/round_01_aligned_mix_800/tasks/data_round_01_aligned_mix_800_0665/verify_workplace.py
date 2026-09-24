import os
import sys
import json
import csv
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 强制关闭 SSL 验证并初始化客户端
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """大模型负责检测非结构化文本的统一接口"""
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

def extract_json_values(data):
    """递归提取 JSON 中的所有文本节点用于确定性比对"""
    values = []
    if isinstance(data, dict):
        for k, v in data.items():
            values.extend(extract_json_values(v))
    elif isinstance(data, list):
        for item in data:
            values.extend(extract_json_values(item))
    elif isinstance(data, str):
        values.append(data)
    elif isinstance(data, (int, float)):
        values.append(str(data))
    return values

def check_presence(target, parsed_values, content, file_type):
    """验证对应人员是否正确包含在输出中"""
    if file_type in ["JSON", "CSV"]:
        # 对于结构化数据，使用原生代码在解析好的节点池中进行严格精准匹配
        return any(target.lower() in val.lower() for val in parsed_values)
    else:
        # 非结构化数据触发 LLM 语义检测
        prompt = f"Does the document explicitly include '{target}' as a matched target/offender in the final filtered results? Answer 'YES' if they are clearly included, 'NO' if they are missing or ignored."
        return llm_judge_content(prompt, content)

def check_absence(target, parsed_values, content, file_type):
    """严查幻觉或逻辑错误：判定无关人员是否被错误加入（排异检测）"""
    if file_type in ["JSON", "CSV"]:
        # 如果能在解析结果中找到，说明被错误包含了
        return not any(target.lower() in val.lower() for val in parsed_values)
    else:
        # 非结构化数据触发 LLM 语义检测
        prompt = f"Does the document list '{target}' as a matched offender in the report results? Answer 'YES' if they are included in the results, 'NO' if they are completely excluded/absent."
        return not llm_judge_content(prompt, content)

def write_score(total, details):
    res = {"total_score": total, "details": details}
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_dir = os.path.join(workspace, "desk_report")
    
    details = []
    total_score = 0
    
    # 1. 结构验证: 目录存在性 (10分)
    if os.path.exists(report_dir) and os.path.isdir(report_dir):
        details.append({"item": "检查目标目录 desk_report 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录已成功创建"})
        total_score += 10
    else:
        details.append({"item": "检查目标目录 desk_report 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 desk_report 目录"})
        write_score(0, details)
        return

    # 尝试寻找目录下的合法文件
    files = [f for f in os.listdir(report_dir) if os.path.isfile(os.path.join(report_dir, f))]
    if not files:
        details.append({"item": "检查目录内是否包含数据文件", "score": 0, "max_score": 15, "passed": False, "reason": "desk_report 目录为空"})
        write_score(total_score, details)
        return
        
    target_file = next((f for f in files if f.endswith(".json") or f.endswith(".csv")), files[0])
    file_path = os.path.join(report_dir, target_file)
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
        
    if not content:
        details.append({"item": "检查文件内容是否非空", "score": 0, "max_score": 15, "passed": False, "reason": "生成的文件为空文件"})
        write_score(total_score, details)
        return
        
    file_type = "UNSTRUCTURED"
    parsed_values = []
    
    # 原生代码严查结构合法性，严防假阳性
    try:
        data = json.loads(content)
        parsed_values = extract_json_values(data)
        file_type = "JSON"
    except:
        if "," in content or ";" in content or "\t" in content:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    data = list(reader)
                if len(data) > 0 and len(data[0]) > 0:
                    for row in data:
                        for cell in row:
                            parsed_values.append(str(cell))
                    file_type = "CSV"
            except:
                pass
                
    # 2. 格式合规验证: 是否输出了整洁的可被解析结构化数据 (15分)
    if file_type in ["JSON", "CSV"]:
        details.append({"item": "生成格式合法的结构化数据文件(JSON/CSV)", "score": 15, "max_score": 15, "passed": True, "reason": f"文件可被标准解析器成功解析为 {file_type}"})
        total_score += 15
    else:
        details.append({"item": "生成格式合法的结构化数据文件(JSON/CSV)", "score": 5, "max_score": 15, "passed": False, "reason": "无法通过标准结构化解析，可能为 Markdown 文本或格式错乱。扣除部分格式分并降级为 LLM 判定。"})
        total_score += 5
        
    # 定义考核指标字典
    targets = [
        {"name": "Carlos Mendez", "desc": "正向提取: 包含 Carlos Mendez (符合: Noise complaint + Watch List)", "score": 15},
        {"name": "Sarah Smith", "desc": "正向提取: 包含 Sarah Smith (符合: Illegal dumping + Watch List)", "score": 15},
        {"name": "Miguel Santos", "desc": "正向提取: 包含 Miguel Santos (符合: Noise complaint + Watch List)", "score": 15}
    ]
    
    distractors = [
        {"name": "Elena Rostova", "desc": "负向排异: 排除 Elena Rostova (在名单内，但案件类型错误)", "score": 10},
        {"name": "Jimmy O'Connor", "desc": "负向排异: 排除 Jimmy O'Connor (在名单内，但案件类型错误)", "score": 10},
        {"name": "Bob Builder", "desc": "负向排异: 排除 Bob Builder (案件类型符合，但不在看守名单内)", "score": 10}
    ]
    
    # 3-5. 正向数据提取有效性 (合计 45分)
    for t in targets:
        passed = check_presence(t["name"], parsed_values, content, file_type)
        if passed:
            details.append({"item": t["desc"], "score": t["score"], "max_score": t["score"], "passed": True, "reason": "精确匹配到该合法人员记录。"})
            total_score += t["score"]
        else:
            details.append({"item": t["desc"], "score": 0, "max_score": t["score"], "passed": False, "reason": "报告中缺失该合法人员记录。"})

    # 6-8. 负向过滤与逻辑缜密性验证 (合计 30分)
    for d in distractors:
        passed = check_absence(d["name"], parsed_values, content, file_type)
        if passed:
            details.append({"item": d["desc"], "score": d["score"], "max_score": d["score"], "passed": True, "reason": "未被错误包含，过滤逻辑执行正确。"})
            total_score += d["score"]
        else:
            details.append({"item": d["desc"], "score": 0, "max_score": d["score"], "passed": False, "reason": "混入了不满足条件的人员数据，证明处理逻辑存在致命缺陷。"})

    write_score(total_score, details)

if __name__ == "__main__":
    verify()
