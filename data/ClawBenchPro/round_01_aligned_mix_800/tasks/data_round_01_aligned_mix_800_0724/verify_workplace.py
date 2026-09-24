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

def check_sales_total(data):
    """
    Recursively check if the exact heritage total (43.75) exists.
    """
    if isinstance(data, dict):
        return any(check_sales_total(v) for v in data.values())
    elif isinstance(data, list):
        return any(check_sales_total(item) for item in data)
    elif isinstance(data, (int, float)):
        return abs(float(data) - 43.75) < 1e-5
    elif isinstance(data, str):
        try:
            val = float(data.replace('$', '').strip())
            return abs(val - 43.75) < 1e-5
        except ValueError:
            pass
    return False

def get_all_strings(data):
    """
    Recursively extract all keys and string values to thoroughly check against hallucination.
    """
    strings = []
    if isinstance(data, dict):
        for k, v in data.items():
            strings.append(str(k))
            strings.extend(get_all_strings(v))
    elif isinstance(data, list):
        for item in data:
            strings.extend(get_all_strings(item))
    elif isinstance(data, str):
        strings.append(data)
    return strings

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results_dir = os.path.join(workspace, "results")
    
    score_details = []
    total_score = 0

    # 1. Check if results directory exists
    if os.path.isdir(results_dir):
        score_details.append({"item": "检查 results 目录是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "results 目录已成功创建"})
        total_score += 10
    else:
        score_details.append({"item": "检查 results 目录是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "results 目录不存在"})

    # 2. Check for a valid JSON file inside the directory
    valid_json_data = None
    json_content_str = ""
    
    if os.path.isdir(results_dir):
        # We don't restrict to .json extension because user says "I don't care what you name the file"
        file_paths = []
        for root, _, files in os.walk(results_dir):
            for file in files:
                file_paths.append(os.path.join(root, file))
                
        for fp in file_paths:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    content = f.read()
                    valid_json_data = json.loads(content)
                    json_content_str = content
                    break
            except Exception:
                continue

    if valid_json_data is not None:
        score_details.append({"item": "检查结果是否为合法的 JSON", "score": 15, "max_score": 15, "passed": True, "reason": "成功读取并解析结构化的 JSON 文件"})
        total_score += 15
    else:
        score_details.append({"item": "检查结果是否为合法的 JSON", "score": 0, "max_score": 15, "passed": False, "reason": "未能找到或解析出合法的 JSON 内容"})

    # 3, 4, 5. Validate JSON content structure and logic
    if valid_json_data is not None:
        # 3. Exact Sales Total Verification
        if check_sales_total(valid_json_data):
            score_details.append({"item": "代码级精准核验 Heritage 销售额", "score": 30, "max_score": 30, "passed": True, "reason": "成功提取到准确数值 43.75（已忽略通用类商品）"})
            total_score += 30
        else:
            score_details.append({"item": "代码级精准核验 Heritage 销售额", "score": 0, "max_score": 30, "passed": False, "reason": "未找到精确值 43.75，可能误算了 General 品类，或计算错误"})

        # 4. Strict Array Check for Unauthorized Personnel
        all_strs = get_all_strings(valid_json_data)
        text = " ".join(all_strs).lower()
        
        unapproved = ["frank miller", "grace kelly"]
        approved = ["alice henderson", "bob jenkins", "clara smith", "diane o'connor", "earl thompson"]
        
        has_unapproved = all(u in text for u in unapproved)
        has_approved = any(a in text for a in approved)
        
        if has_unapproved and not has_approved:
            score_details.append({"item": "严格过滤与核对未经授权名单", "score": 30, "max_score": 30, "passed": True, "reason": "精准检出 Frank Miller 和 Grace Kelly，且未混入任何白名单人员（无幻觉）"})
            total_score += 30
        elif has_unapproved and has_approved:
            score_details.append({"item": "严格过滤与核对未经授权名单", "score": 10, "max_score": 30, "passed": False, "reason": "包含未授权人员，但错误地混入了白名单成员，未严格执行集合差集逻辑"})
            total_score += 10
        else:
            score_details.append({"item": "严格过滤与核对未经授权名单", "score": 0, "max_score": 30, "passed": False, "reason": "未找齐未授权人员名单，或完全遗漏"})

        # 5. LLM Tone and Extraneous Content Verification
        prompt_text = (
            "The board president, Mr. Higgins, is extremely traditional and strict. He requested a strict JSON report. "
            "Please check if the given JSON content strictly focuses on the business requirements (unauthorized personnel and heritage sales total), "
            "uses professional/formal key names, and contains NO conversational text, NO emotional comfort, and NO unnecessary chit-chat towards the stressed out person."
        )
        is_formal = llm_judge_content(prompt_text, json_content_str)
        if is_formal:
            score_details.append({"item": "大模型语义判别 JSON 汇报风格与冗余度", "score": 15, "max_score": 15, "passed": True, "reason": "JSON 风格严肃正式，无多余的针对焦虑人物的情感寒暄"})
            total_score += 15
        else:
            score_details.append({"item": "大模型语义判别 JSON 汇报风格与冗余度", "score": 0, "max_score": 15, "passed": False, "reason": "包含了不合适的情感安抚闲聊，或 JSON 键命名极其不正式/包含废话"})
            
    else:
        # Fallback for failing condition 2
        score_details.append({"item": "代码级精准核验 Heritage 销售额", "score": 0, "max_score": 30, "passed": False, "reason": "缺少合法的 JSON 文件作为前置"})
        score_details.append({"item": "严格过滤与核对未经授权名单", "score": 0, "max_score": 30, "passed": False, "reason": "缺少合法的 JSON 文件作为前置"})
        score_details.append({"item": "大模型语义判别 JSON 汇报风格与冗余度", "score": 0, "max_score": 15, "passed": False, "reason": "缺少合法的 JSON 文件作为前置"})

    # Write final output
    output_data = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    verify()
