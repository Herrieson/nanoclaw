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

def extract_all_values(obj):
    """
    Recursively extract all terminal values from a JSON structure
    to strictly check the existence of expected numbers and strings.
    """
    vals = []
    if isinstance(obj, dict):
        for v in obj.values():
            vals.extend(extract_all_values(v))
    elif isinstance(obj, list):
        for v in obj:
            vals.extend(extract_all_values(v))
    else:
        vals.append(obj)
    return vals

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliv_path = os.path.join(workspace, "deliverables")
    
    total_score = 0
    details = []

    # 1. Check Directory Existence
    if os.path.isdir(deliv_path):
        details.append({"item": "检查交付物目录是否创建", "score": 10, "max_score": 10, "passed": True, "reason": "deliverables 目录存在"})
        total_score += 10
    else:
        details.append({"item": "检查交付物目录是否创建", "score": 0, "max_score": 10, "passed": False, "reason": "deliverables 目录未创建"})
        write_score(0, details)
        return

    # 2. Check JSON Report Format & Parsing
    json_files = glob.glob(os.path.join(deliv_path, "*.json"))
    if not json_files:
        details.append({"item": "检查 JSON 报告文件是否存在", "score": 0, "max_score": 15, "passed": False, "reason": "未找到 JSON 文件"})
        # Cascading failures
        details.append({"item": "精确提取与计算：有效总工时", "score": 0, "max_score": 35, "passed": False, "reason": "缺少文件，无法校验"})
        details.append({"item": "精确提取与比对：拒绝名单(Crashers)", "score": 0, "max_score": 30, "passed": False, "reason": "缺少文件，无法校验"})
        details.append({"item": "大模型语义审查：防止捏造与误伤", "score": 0, "max_score": 10, "passed": False, "reason": "缺少文件，无法校验"})
        write_score(total_score, details)
        return

    json_file = json_files[0]
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            content = f.read()
            data = json.loads(content)
        details.append({"item": "检查 JSON 报告格式合法性", "score": 15, "max_score": 15, "passed": True, "reason": "JSON 文件存在且能成功解析为结构化数据"})
        total_score += 15
    except Exception as e:
        details.append({"item": "检查 JSON 报告格式合法性", "score": 0, "max_score": 15, "passed": False, "reason": f"JSON 解析失败：{e}"})
        details.append({"item": "精确提取与计算：有效总工时", "score": 0, "max_score": 35, "passed": False, "reason": "JSON格式破坏，无法提取"})
        details.append({"item": "精确提取与比对：拒绝名单(Crashers)", "score": 0, "max_score": 30, "passed": False, "reason": "JSON格式破坏，无法提取"})
        details.append({"item": "大模型语义审查：防止捏造与误伤", "score": 0, "max_score": 10, "passed": False, "reason": "JSON格式破坏，无法审查"})
        write_score(total_score, details)
        return

    all_values = extract_all_values(data)
    
    # 3. Exact Calculation Check: Total Valid Hours (35 points)
    # The valid total is exactly 18.5 (Sarah 4 + Chloe 1.5+3.5 + Michael 3.5 + Emily 4 + David 2)
    has_valid_total = any(v == 18.5 or str(v) == "18.5" for v in all_values)
    if has_valid_total:
        details.append({"item": "精确提取与计算：有效总工时", "score": 35, "max_score": 35, "passed": True, "reason": "成功在 JSON 中提取出精确的有效总工时(18.5)"})
        total_score += 35
    else:
        details.append({"item": "精确提取与计算：有效总工时", "score": 0, "max_score": 35, "passed": False, "reason": "JSON 数值中缺失 18.5。可能是遗漏 OCR 记录、重复人名未合并或将未授权工时算入。"})

    # 4. Exact Extraction Check: Crashers List (30 points)
    # Both Gary Smith and Melissa Vance must be reported.
    all_str_lower = " ".join([str(v).lower() for v in all_values])
    has_gary = "gary smith" in all_str_lower or "gary" in all_str_lower
    has_melissa = "melissa vance" in all_str_lower or "melissa" in all_str_lower
    
    if has_gary and has_melissa:
        details.append({"item": "精确提取与比对：拒绝名单(Crashers)", "score": 30, "max_score": 30, "passed": True, "reason": "准确找出了 Gary 和 Melissa 两名非法潜入者。"})
        total_score += 30
    else:
        details.append({"item": "精确提取与比对：拒绝名单(Crashers)", "score": 0, "max_score": 30, "passed": False, "reason": f"拒绝名单提取不全。Gary 存在:{has_gary}, Melissa 存在:{has_melissa}。"})

    # 5. LLM Semantic Verification for Hallucinations and False Positives (10 points)
    # Check if Agent hallucinated other names as crashers (like Sarah, Emily, etc.)
    prompt_text = (
        "Here is the finalized church volunteer JSON report. Based on the rules, ONLY 'Gary Smith' and 'Melissa Vance' "
        "(or just Gary/Melissa) are unapproved crashers. "
        "Examine the document's structure and semantics: "
        "Are any approved volunteers (like Sarah, Chloe, Michael, Emily, David) falsely listed as unapproved crashers? "
        "Are there any completely made-up names? "
        "Answer YES if the unapproved list is purely Gary and/or Melissa and no one else is falsely accused. "
        "Answer NO if it falsely accuses approved volunteers or hallucinated non-existent individuals."
    )
    
    no_hallucination = llm_judge_content(prompt_text, content)
    if no_hallucination:
        details.append({"item": "大模型语义审查：防止捏造与误伤", "score": 10, "max_score": 10, "passed": True, "reason": "大模型校验通过，拒绝名单纯净，无幻觉、无无辜者遭到误判"})
        total_score += 10
    else:
        details.append({"item": "大模型语义审查：防止捏造与误伤", "score": 0, "max_score": 10, "passed": False, "reason": "大模型校验未通过，Agent 的报告存在对合规人员的误判或者在结构中捏造了不存在的数据。"})

    write_score(total_score, details)

def write_score(total, details):
    output = {
        "total_score": total,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
