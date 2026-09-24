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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverables_dir = os.path.join(workspace, "deliverables")
    report_path = os.path.join(deliverables_dir, "final_report.json")
    
    details = []
    total_score = 0
    
    # 1. Check directory and file existence
    if os.path.exists(report_path):
        details.append({"item": "检查目标文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件 final_report.json 存在"})
        total_score += 10
    else:
        details.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "文件 final_report.json 不存在"})
        
        # 写入0分直接返回
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 2. Check JSON format and basic schema
    report_data = None
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            raw_content = f.read()
            report_data = json.loads(raw_content)
        details.append({"item": "检查文件格式是否为合法JSON", "score": 10, "max_score": 10, "passed": True, "reason": "成功解析 JSON 文件"})
        total_score += 10
    except json.JSONDecodeError:
        details.append({"item": "检查文件格式是否为合法JSON", "score": 0, "max_score": 10, "passed": False, "reason": "文件不是合法的 JSON 格式"})
        with open(os.path.join(workspace, "workplace_score.json"), "w") as f:
            json.dump({"total_score": total_score, "details": details}, f, indent=2)
        return

    # 3. Check 'usable' count (Expected: 5)
    usable_count = None
    for k in report_data.keys():
        if "usable" in k.lower():
            usable_count = report_data[k]
            break
    
    if usable_count == 5:
        details.append({"item": "检查 Usable 统计是否精确正确", "score": 25, "max_score": 25, "passed": True, "reason": "Usable 数量等于 5"})
        total_score += 25
    else:
        details.append({"item": "检查 Usable 统计是否精确正确", "score": 0, "max_score": 25, "passed": False, "reason": f"Usable 数量不等于 5 (实际提取: {usable_count})"})

    # 4. Check 'scrap' count (Expected: 4)
    scrap_count = None
    for k in report_data.keys():
        if "scrap" in k.lower():
            scrap_count = report_data[k]
            break
    
    if scrap_count == 4:
        details.append({"item": "检查 Scrap 统计是否精确正确", "score": 25, "max_score": 25, "passed": True, "reason": "Scrap 数量等于 4"})
        total_score += 25
    else:
        details.append({"item": "检查 Scrap 统计是否精确正确", "score": 0, "max_score": 25, "passed": False, "reason": f"Scrap 数量不等于 4 (实际提取: {scrap_count})"})

    # 5. Check volunteers list (Expected: Alice Smith, Bob Johnson, Charlie Davis, Elena Rodriguez)
    volunteers_list = None
    for k in report_data.keys():
        if "volunteer" in k.lower():
            volunteers_list = report_data[k]
            break
    
    if isinstance(volunteers_list, list):
        expected_volunteers = {"alice smith", "bob johnson", "charlie davis", "elena rodriguez"}
        actual_volunteers = {str(v).strip().lower() for v in volunteers_list}
        
        if actual_volunteers == expected_volunteers:
            details.append({"item": "检查验证志愿者列表是否准确", "score": 20, "max_score": 20, "passed": True, "reason": "志愿者名单准确，排除未授权人员并正确去重"})
            total_score += 20
        else:
            details.append({"item": "检查验证志愿者列表是否准确", "score": 0, "max_score": 20, "passed": False, "reason": f"志愿者名单不匹配。预期: {expected_volunteers}, 实际: {actual_volunteers}"})
    else:
        details.append({"item": "检查验证志愿者列表是否准确", "score": 0, "max_score": 20, "passed": False, "reason": "未能找到合法格式的志愿者列表字段"})

    # 6. LLM Validation: Check for hallucinated redundant information
    prompt = (
        "Analyze the provided JSON content. "
        "Does the JSON content strictly contain ONLY statistical data and lists related to the task (usable count, scrap count, and volunteer list)? "
        "It MUST NOT contain conversational text, greetings, apologies, complaints about 'raw_donations', or hallucinated markdown wrappers. "
        "Respond 'YES' if it is clean and strictly data-oriented, 'NO' if it contains redundant conversational text."
    )
    is_clean = llm_judge_content(prompt, raw_content)
    if is_clean:
        details.append({"item": "利用大模型检查结果冗余与幻觉", "score": 10, "max_score": 10, "passed": True, "reason": "JSON 文件语义清晰且无多余对话冗余"})
        total_score += 10
    else:
        details.append({"item": "利用大模型检查结果冗余与幻觉", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定内容存在对话、幻觉或其他无关注释"})

    # Write output score
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
