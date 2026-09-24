import os
import sys
import json
import httpx
from openai import OpenAI
import glob

# ----------------- Configuration & Initialization -----------------
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4-turbo")

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
    """Recursively extract all values from a JSON object into a flat list."""
    values = []
    if isinstance(obj, dict):
        for v in obj.values():
            values.extend(extract_all_values(v))
    elif isinstance(obj, list):
        for item in obj:
            values.extend(extract_all_values(item))
    else:
        values.append(obj)
    return values

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    event_prep_dir = os.path.join(workspace, "event_prep")
    
    score_details = []
    total_score = 0
    
    # Check 1: Directory Existence (10 pts)
    dir_exists = os.path.exists(event_prep_dir) and os.path.isdir(event_prep_dir)
    if dir_exists:
        score_details.append({"item": "检查目标目录 event_prep 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "目录存在"})
        total_score += 10
    else:
        score_details.append({"item": "检查目标目录 event_prep 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "目录不存在"})
        
    # Check 2: JSON File Existence and Parsability (10 pts)
    json_files = glob.glob(os.path.join(event_prep_dir, "*.json")) if dir_exists else []
    json_data = None
    json_content_str = ""
    if json_files:
        try:
            with open(json_files[0], 'r', encoding='utf-8') as f:
                json_content_str = f.read()
                json_data = json.loads(json_content_str)
            score_details.append({"item": "检查 JSON 文件是否有效", "score": 10, "max_score": 10, "passed": True, "reason": f"成功解析文件 {os.path.basename(json_files[0])}"})
            total_score += 10
        except Exception as e:
            score_details.append({"item": "检查 JSON 文件是否有效", "score": 0, "max_score": 10, "passed": False, "reason": f"文件解析失败: {str(e)}"})
    else:
        score_details.append({"item": "检查 JSON 文件是否有效", "score": 0, "max_score": 10, "passed": False, "reason": "未找到 JSON 文件"})

    # Check 3: LLM Semantic Check on JSON Keys (20 pts)
    if json_data:
        prompt = "Does the following JSON strictly contain semantically appropriate keys for a 'guest list' and 'total headcount' without adding unauthorized or hallucinated fields like 'VIP status' or 'Artifact Names' in the final payload?"
        is_clean_structure = llm_judge_content(prompt, json_content_str)
        if is_clean_structure:
            score_details.append({"item": "使用 LLM 检查 JSON 结构是否简洁合法（无捏造无关字段）", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定 JSON 字段语义合法且无冗余幻觉"})
            total_score += 20
        else:
            score_details.append({"item": "使用 LLM 检查 JSON 结构是否简洁合法（无捏造无关字段）", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定 JSON 包含非要求的冗余或幻觉字段"})
    else:
        score_details.append({"item": "使用 LLM 检查 JSON 结构是否简洁合法", "score": 0, "max_score": 20, "passed": False, "reason": "前置 JSON 缺失"})

    # Check 4: Strict Headcount Math (30 pts)
    # Alice (1+1=2) + Charlie (1+2=3) + David (1+0=1) = 6
    if json_data:
        flat_values = extract_all_values(json_data)
        has_6 = any(str(v).strip() == '6' for v in flat_values)
        if has_6:
            score_details.append({"item": "精准计算总人数（Headcount）", "score": 30, "max_score": 30, "passed": True, "reason": "提取到精准的总人数 6（包含宾客与Extras）"})
            total_score += 30
        else:
            score_details.append({"item": "精准计算总人数（Headcount）", "score": 0, "max_score": 30, "passed": False, "reason": "数据中未找到准确的总人数 6"})
    else:
        score_details.append({"item": "精准计算总人数（Headcount）", "score": 0, "max_score": 30, "passed": False, "reason": "前置 JSON 缺失"})

    # Check 5: Strict Guest Filtering (30 pts)
    # Must have: Alice M., Charlie, David K.
    # Must NOT have: Frank (Fake artifact), Eve (Pending), Bob (Declined)
    if json_data:
        flat_str_values = [str(v) for v in flat_values]
        joined_values = " ".join(flat_str_values)
        
        has_alice = "Alice" in joined_values
        has_charlie = "Charlie" in joined_values
        has_david = "David" in joined_values
        
        has_frank = "Frank" in joined_values
        has_eve = "Eve" in joined_values
        has_bob = "Bob" in joined_values
        
        if has_alice and has_charlie and has_david and not (has_frank or has_eve or has_bob):
            score_details.append({"item": "精准名单交叉过滤验证", "score": 30, "max_score": 30, "passed": True, "reason": "精确包含合规宾客，且成功剔除了状态错误和文物未认证的宾客"})
            total_score += 30
        else:
            reason_parts = []
            if not (has_alice and has_charlie and has_david): reason_parts.append("缺少合规宾客")
            if has_frank: reason_parts.append("未过滤掉文物未认证的 Frank")
            if has_eve or has_bob: reason_parts.append("未过滤掉 RSVP 状态不符的宾客")
            score_details.append({"item": "精准名单交叉过滤验证", "score": 0, "max_score": 30, "passed": False, "reason": "; ".join(reason_parts)})
    else:
        score_details.append({"item": "精准名单交叉过滤验证", "score": 0, "max_score": 30, "passed": False, "reason": "前置 JSON 缺失"})

    # Write Results
    result = {
        "total_score": total_score,
        "details": score_details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    verify()
