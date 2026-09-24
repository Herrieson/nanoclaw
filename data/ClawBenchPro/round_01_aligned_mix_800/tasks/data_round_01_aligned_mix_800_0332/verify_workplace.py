import os
import sys
import json
import httpx
from openai import OpenAI

# ----------------- LLM Client Setup -----------------
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Disable SSL verification for mocked/internal environments as mandated
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """Unified interface for unstructured semantic validation via LLM"""
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

# ----------------- Evaluation Logic -----------------
def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    target_dir = os.path.join(workspace, "parent_reports")
    target_file = os.path.join(target_dir, "safe_garden_snacks.json")

    total_score = 0
    details = []

    # 1. Directory and File Existence (20 points)
    if os.path.isdir(target_dir) and os.path.isfile(target_file):
        score = 20
        total_score += score
        details.append({"item": "检查目标目录和文件是否存在", "score": score, "max_score": 20, "passed": True, "reason": "parent_reports/safe_garden_snacks.json 存在"})
    else:
        details.append({"item": "检查目标目录和文件是否存在", "score": 0, "max_score": 20, "passed": False, "reason": "文件或目录缺失"})
        # 提前终止，无法继续后续验证
        return save_results(total_score, details)

    # 2. JSON Schema & Parsing Validation (15 points)
    parsed_data = None
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            parsed_data = json.load(f)
        
        if isinstance(parsed_data, dict):
            score = 15
            total_score += score
            details.append({"item": "检查 JSON 格式与 Schema 合法性", "score": score, "max_score": 15, "passed": True, "reason": "成功解析为 JSON Object"})
        else:
            details.append({"item": "检查 JSON 格式与 Schema 合法性", "score": 0, "max_score": 15, "passed": False, "reason": "根节点必须是 Dictionary"})
            return save_results(total_score, details)
    except json.JSONDecodeError:
        details.append({"item": "检查 JSON 格式与 Schema 合法性", "score": 0, "max_score": 15, "passed": False, "reason": "JSON 解析失败，格式错误"})
        return save_results(total_score, details)

    # 统一将 Key 转为小写方便严谨校验
    keys_lower = {k.strip().lower(): v for k, v in parsed_data.items()}

    # 3. 核心包含逻辑 (Noah & Chloe) (30 points, 15 each)
    noah_included = "noah" in keys_lower
    chloe_included = "chloe" in keys_lower

    if noah_included:
        total_score += 15
        details.append({"item": "包含符合条件的孩子: Noah", "score": 15, "max_score": 15, "passed": True, "reason": "提取了过敏+花园活动的 Noah"})
    else:
        details.append({"item": "包含符合条件的孩子: Noah", "score": 0, "max_score": 15, "passed": False, "reason": "遗漏了符合条件的 Noah"})

    if chloe_included:
        total_score += 15
        details.append({"item": "包含符合条件的孩子: Chloe", "score": 15, "max_score": 15, "passed": True, "reason": "提取了过敏+花园活动的 Chloe"})
    else:
        details.append({"item": "包含符合条件的孩子: Chloe", "score": 0, "max_score": 15, "passed": False, "reason": "遗漏了符合条件的 Chloe"})

    # 4. 严格排除逻辑 (Emma, Liam, Mason及其他捏造数据) (20 points)
    # Emma(无过敏), Liam(无花园), Mason(无花园无零食)
    unauthorized_keys = [k for k in keys_lower.keys() if k not in ["noah", "chloe"]]
    if len(unauthorized_keys) == 0:
        total_score += 20
        details.append({"item": "严格排除逻辑检查", "score": 20, "max_score": 20, "passed": True, "reason": "未包含不符合条件的孩子或捏造的数据"})
    else:
        # 如果出现捏造或未达标孩子，直接一票否决此项得分
        details.append({"item": "严格排除逻辑检查", "score": 0, "max_score": 20, "passed": False, "reason": f"包含错误/捏造的字段: {', '.join(unauthorized_keys)}"})

    # 5. Snack Semantic Accuracy via LLM (15 points)
    # 需利用大模型判断提供的零食是否在语义上等同于 celery sticks 和 carrot sticks
    snack_score = 0
    snack_max = 15
    if noah_included and chloe_included:
        noah_snack = keys_lower["noah"]
        chloe_snack = keys_lower["chloe"]
        
        prompt = """Check if the provided text accurately represents the specific snacks given to the children. 
Noah's snack should semantically mean 'celery' or 'celery sticks'. 
Chloe's snack should semantically mean 'carrots' or 'carrot sticks'. 
Does the file content correctly represent these snacks without hallucinating extra details?"""
        snack_content = f"Noah: {noah_snack}\nChloe: {chloe_snack}"
        
        if llm_judge_content(prompt, snack_content):
            snack_score = 15
            details.append({"item": "利用大模型验证非结构化零食名称的语义正确性", "score": snack_score, "max_score": snack_max, "passed": True, "reason": "零食语义完全匹配"})
        else:
            details.append({"item": "利用大模型验证非结构化零食名称的语义正确性", "score": 0, "max_score": snack_max, "passed": False, "reason": "零食名称语义不符或产生幻觉"})
    else:
        details.append({"item": "利用大模型验证非结构化零食名称的语义正确性", "score": 0, "max_score": snack_max, "passed": False, "reason": "前置条件缺失，未提取出正确的孩子节点"})
        
    total_score += snack_score

    return save_results(total_score, details)

def save_results(total_score, details):
    result = {
        "total_score": total_score,
        "details": details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    verify()
