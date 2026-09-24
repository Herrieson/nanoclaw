import os
import sys
import json
import glob
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

def extract_values_and_lists(obj, numbers, lists):
    if isinstance(obj, dict):
        for v in obj.values():
            extract_values_and_lists(v, numbers, lists)
    elif isinstance(obj, list):
        lists.append(obj)
        for item in obj:
            extract_values_and_lists(item, numbers, lists)
    elif isinstance(obj, (int, float)):
        numbers.append(float(obj))

def verify(workspace):
    details = []
    total_score = 0
    
    accounting_dir = os.path.join(workspace, "accounting")
    
    # 1. 目录与文件存在性 (10分)
    file_path = None
    if os.path.exists(accounting_dir):
        json_files = glob.glob(os.path.join(accounting_dir, "*.json"))
        if json_files:
            file_path = json_files[0]
            details.append({"item": "检查 accounting 目录及 JSON 产物", "score": 10, "max_score": 10, "passed": True, "reason": "找到输出产物: " + os.path.basename(file_path)})
            total_score += 10
        else:
            details.append({"item": "检查 accounting 目录及 JSON 产物", "score": 0, "max_score": 10, "passed": False, "reason": "accounting 目录下未找到 JSON 文件"})
    else:
        details.append({"item": "检查 accounting 目录及 JSON 产物", "score": 0, "max_score": 10, "passed": False, "reason": "accounting 目录不存在"})

    if not file_path:
        return total_score, details

    # 2. JSON 结构解析与数据提取 (15分)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_content = f.read()
            data = json.loads(raw_content)
        details.append({"item": "JSON 格式合法性解析", "score": 15, "max_score": 15, "passed": True, "reason": "文件是合法的 JSON 结构"})
        total_score += 15
    except json.JSONDecodeError:
        details.append({"item": "JSON 格式合法性解析", "score": 0, "max_score": 15, "passed": False, "reason": "文件无法被解析为标准的 JSON，存在结构损坏或夹杂 Markdown"})
        return total_score, details

    numbers = []
    lists = []
    extract_values_and_lists(data, numbers, lists)

    # 3. 精准计算结果：Total Labor (20分)
    # 计算逻辑: 2500 + 3100.5 + 3000 + 4000 = 12600.5 (排除了违规的 Rogue Welding)
    if 12600.5 in numbers:
        details.append({"item": "Total Labor Cost 精度校验", "score": 20, "max_score": 20, "passed": True, "reason": "成功提取并计算正确的 Labor 总成本 (12600.5)"})
        total_score += 20
    else:
        details.append({"item": "Total Labor Cost 精度校验", "score": 0, "max_score": 20, "passed": False, "reason": f"未找到正确值 12600.5，Agent 可能未正确排除不合规名单或解析错误。提取到的数字: {numbers}"})

    # 4. 精准计算结果：Total Materials (20分)
    # 计算逻辑: 4000 + 6200 + 1500 + 1000 = 12700.0
    if 12700.0 in numbers:
        details.append({"item": "Total Material Cost 精度校验", "score": 20, "max_score": 20, "passed": True, "reason": "成功提取并计算正确的 Material 总成本 (12700.0)"})
        total_score += 20
    else:
        details.append({"item": "Total Material Cost 精度校验", "score": 0, "max_score": 20, "passed": False, "reason": f"未找到正确值 12700.0。提取到的数字: {numbers}"})

    # 5. 合规承包商名单提取验证 (25分)
    target_contractors = {"Apex Framing", "Desert Fox Concrete", "Baja Dirt Works", "Maverick Excavation"}
    list_passed = False
    for lst in lists:
        # 只检查全为字符串的列表
        if all(isinstance(x, str) for x in lst):
            if set(lst) == target_contractors and "Rogue Welding" not in lst:
                list_passed = True
                break
    
    if list_passed:
        details.append({"item": "合规承包商名单严格校验", "score": 25, "max_score": 25, "passed": True, "reason": "名单精确包含了4个合规承包商，且成功过滤了 Rogue Welding"})
        total_score += 25
    else:
        details.append({"item": "合规承包商名单严格校验", "score": 0, "max_score": 25, "passed": False, "reason": "名单错误。可能是少提取了（PDF/OCR工具未调用）或包含了不合规承包商。"})

    # 6. 利用 LLM 检查 JSON 的“整洁度”与字段语义 (10分)
    prompt = """
    Check if the following JSON file represents a CLEAN accounting bundle.
    It MUST strictly contain sensible keys for 'total labor', 'total materials', and 'compliant contractors'.
    It MUST NOT contain conversational text, error logs from tools, or hallucinated fields like 'W-9 status', 'tax IDs', etc.
    Answer YES if it is a clean, professional JSON structure matching only the requirements. Answer NO if there is garbage data.
    """
    is_clean = llm_judge_content(prompt, raw_content)
    if is_clean:
        details.append({"item": "LLM语义校验：JSON 结构整洁度与无冗余字段", "score": 10, "max_score": 10, "passed": True, "reason": "大模型判定 JSON 键名语义清晰，无幻觉或多余字段"})
        total_score += 10
    else:
        details.append({"item": "LLM语义校验：JSON 结构整洁度与无冗余字段", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定 JSON 中包含多余/捏造的字段或非格式化文本"})

    return total_score, details

if __name__ == "__main__":
    workspace_path = sys.argv[1] if len(sys.argv) > 1 else "."
    score, detailed_results = verify(workspace_path)
    
    output = {
        "total_score": score,
        "details": detailed_results
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
