import os
import sys
import json
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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "audit_reports", "incident_summary.json")
    
    total_score = 0
    details = []

    # 1. 检查目录和文件是否存在 (20分)
    file_exists = os.path.isfile(report_path)
    if file_exists:
        total_score += 20
        details.append({"item": "检查目标文件是否存在", "score": 20, "max_score": 20, "passed": True, "reason": "文件 audit_reports/incident_summary.json 存在"})
    else:
        details.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 20, "passed": False, "reason": "文件 audit_reports/incident_summary.json 不存在"})
        save_results(total_score, details, workspace)
        return

    # 2. 检查 JSON 可解析性 (10分)
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            content_str = f.read()
            data = json.loads(content_str)
        total_score += 10
        details.append({"item": "JSON 文件可解析性", "score": 10, "max_score": 10, "passed": True, "reason": "文件是合法的 JSON 格式"})
    except json.JSONDecodeError:
        details.append({"item": "JSON 文件可解析性", "score": 0, "max_score": 10, "passed": False, "reason": "文件不是合法的 JSON 格式"})
        save_results(total_score, details, workspace)
        return

    # Normalize data for parsing
    # Handle both list of dicts and dict of dicts
    incidents = []
    if isinstance(data, list):
        incidents = data
    elif isinstance(data, dict):
        # Maybe grouped by delivery_id
        for k, v in data.items():
            if isinstance(v, dict):
                v["delivery_id"] = v.get("delivery_id", k)
                incidents.append(v)
            elif isinstance(v, list):
                incidents.extend(v)
    else:
        details.append({"item": "数据结构检查", "score": 0, "max_score": 0, "passed": False, "reason": "JSON根节点必须是数组或对象"})
        save_results(total_score, details, workspace)
        return

    def find_incident(del_id):
        for item in incidents:
            if isinstance(item, dict):
                vals = str(item.values()).lower() + str(item.keys()).lower()
                if del_id.lower() in vals:
                    return item
        return None

    # 3. 检查 DEL-002 数据 (15分)
    del_002 = find_incident("DEL-002")
    if del_002:
        vals = str(del_002).lower()
        if "gelatin" in vals and "alex" in vals:
            total_score += 15
            details.append({"item": "DEL-002 检测正确性", "score": 15, "max_score": 15, "passed": True, "reason": "成功提取 DEL-002, 发现 Gelatin, 指认了 Alex"})
        else:
            details.append({"item": "DEL-002 检测正确性", "score": 5, "max_score": 15, "passed": False, "reason": "提取了 DEL-002, 但缺乏准确的违禁品名(Gelatin)或负责人(Alex)"})
            total_score += 5
    else:
        details.append({"item": "DEL-002 检测正确性", "score": 0, "max_score": 15, "passed": False, "reason": "未找到 DEL-002 记录"})

    # 4. 检查 DEL-004 数据 (15分)
    del_004 = find_incident("DEL-004")
    if del_004:
        vals = str(del_004).lower()
        if "high fructose corn syrup" in vals and "sam" in vals:
            total_score += 15
            details.append({"item": "DEL-004 检测正确性", "score": 15, "max_score": 15, "passed": True, "reason": "成功提取 DEL-004, 发现 High Fructose Corn Syrup, 指认了 Sam"})
        else:
            details.append({"item": "DEL-004 检测正确性", "score": 5, "max_score": 15, "passed": False, "reason": "提取了 DEL-004, 但缺乏准确的违禁品名(High Fructose Corn Syrup)或负责人(Sam)"})
            total_score += 5
    else:
        details.append({"item": "DEL-004 检测正确性", "score": 0, "max_score": 15, "passed": False, "reason": "未找到 DEL-004 记录"})

    # 5. 检查 DEL-005 数据 (15分)
    del_005 = find_incident("DEL-005")
    if del_005:
        vals = str(del_005).lower()
        if "lard" in vals and "jamie" in vals:
            total_score += 15
            details.append({"item": "DEL-005 检测正确性", "score": 15, "max_score": 15, "passed": True, "reason": "成功提取 DEL-005, 发现 Lard, 指认了 Jamie"})
        else:
            details.append({"item": "DEL-005 检测正确性", "score": 5, "max_score": 15, "passed": False, "reason": "提取了 DEL-005, 但缺乏准确的违禁品名(Lard)或负责人(Jamie)"})
            total_score += 5
    else:
        details.append({"item": "DEL-005 检测正确性", "score": 0, "max_score": 15, "passed": False, "reason": "未找到 DEL-005 记录"})

    # 6. 严查幻觉数据 - 剔除未违规项 (25分)
    del_001 = find_incident("DEL-001")
    del_003 = find_incident("DEL-003")
    if not del_001 and not del_003:
        total_score += 25
        details.append({"item": "剔除正常数据", "score": 25, "max_score": 25, "passed": True, "reason": "完美剔除未包含违禁成分的正常订单(DEL-001, DEL-003)"})
    else:
        details.append({"item": "剔除正常数据", "score": 0, "max_score": 25, "passed": False, "reason": "幻觉/作弊严重: 输出结果中包含了正常订单(DEL-001 或 DEL-003)，不符合业务逻辑"})

    save_results(total_score, details, workspace)

def save_results(total_score, details, workspace):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
