import os
import sys
import json
import httpx
from openai import OpenAI

# ----------------------------------------------------------------
# Configuration & Client Setup
# ----------------------------------------------------------------
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

# ----------------------------------------------------------------
# Validation Logic
# ----------------------------------------------------------------
def run_verification():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverable_path = os.path.join(workspace, "deliverables/urgent_field_review.json")
    
    score_details = []
    total_score = 0

    # 1. 检查交付文件是否存在 (10分)
    if os.path.exists(deliverable_path):
        score_details.append({"item": "Deliverable file existence", "score": 10, "max_score": 10, "passed": True, "reason": "Found urgent_field_review.json"})
        total_score += 10
    else:
        score_details.append({"item": "Deliverable file existence", "score": 0, "max_score": 10, "passed": False, "reason": "Missing urgent_field_review.json"})
        # 写入最终结果并退出
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": 0, "details": score_details}, f)
        return

    # 2. JSON 格式合法性与结构检查 (10分)
    try:
        with open(deliverable_path, "r") as f:
            data = json.load(f)
        score_details.append({"item": "JSON Format Validity", "score": 10, "max_score": 10, "passed": True, "reason": "Correctly parsed JSON content"})
        total_score += 10
    except Exception as e:
        score_details.append({"item": "JSON Format Validity", "score": 0, "max_score": 10, "passed": False, "reason": f"JSON parse error: {e}"})
        with open("workplace_score.json", "w") as f:
            json.dump({"total_score": total_score, "details": score_details}, f)
        return

    # 3. 业务逻辑验证：pH 违规项识别 (30分)
    # Target: Grove_South (5.8), Grove_Central (5.2)
    ph_violations = [item for item in data if "Grove_South" in str(item) or "Grove_Central" in str(item)]
    ph_detected = []
    for field in ["Grove_South", "Grove_Central"]:
        found = any(field in str(item) and ("ph" in str(item).lower() or "5.8" in str(item) or "5.2" in str(item)) for item in data)
        if found: ph_detected.append(field)
    
    ph_score = len(ph_detected) * 15
    score_details.append({
        "item": "Low pH Violation Detection",
        "score": ph_score,
        "max_score": 30,
        "passed": ph_score == 30,
        "reason": f"Detected low pH for: {ph_detected}"
    })
    total_score += ph_score

    # 4. 业务逻辑验证：非合规化学品识别 (30分)
    # Target: Grove_East (Nitro-Max), Grove_Central (Quick-Green)
    chem_detected = []
    for field in ["Grove_East", "Grove_Central"]:
        # 必须包含化学品原因或具体的禁用成分（如 Ammonium Nitrate 或 Urea）
        found = any(field in str(item) and ("nitro" in str(item).lower() or "quick" in str(item).lower() or "urea" in str(item).lower() or "nitrate" in str(item).lower()) for item in data)
        if found: chem_detected.append(field)
    
    chem_score = len(chem_detected) * 15
    score_details.append({
        "item": "Chemical Compliance Detection",
        "score": chem_score,
        "max_score": 30,
        "passed": chem_score == 30,
        "reason": f"Detected unapproved chemicals for: {chem_detected}"
    })
    total_score += chem_score

    # 5. LLM 语义验证：违规理由的准确性 (20分)
    # 检查是否准确说明了 Grove_Central 是“双重违规”
    central_violation = next((item for item in data if "Grove_Central" in str(item)), None)
    if central_violation:
        prompt = "Does this JSON snippet correctly state that Grove_Central violated both pH levels (being too low) and chemical compliance (using unapproved ingredients)?"
        is_accurate = llm_judge_content(prompt, json.dumps(central_violation))
        if is_accurate:
            score_details.append({"item": "Dual Violation Explanation Accuracy", "score": 20, "max_score": 20, "passed": True, "reason": "LLM verified the explanation for Grove_Central covers both issues."})
            total_score += 20
        else:
            score_details.append({"item": "Dual Violation Explanation Accuracy", "score": 0, "max_score": 20, "passed": False, "reason": "LLM found the explanation incomplete or incorrect for Grove_Central."})
    else:
        score_details.append({"item": "Dual Violation Explanation Accuracy", "score": 0, "max_score": 20, "passed": False, "reason": "Grove_Central not found in report."})

    # 6. 反向指标：误报检查 (如果多报了 Grove_North 或 Grove_West 则扣分)
    over_reporting = any("Grove_North" in str(item) or "Grove_West" in str(item) for item in data)
    if over_reporting:
        deduction = 20
        total_score = max(0, total_score - deduction)
        score_details.append({"item": "Over-reporting Check", "score": -deduction, "max_score": 0, "passed": False, "reason": "Report includes compliant fields (Grove_North or Grove_West)"})

    # 最终分值归一化处理
    total_score = min(100, max(0, int(total_score)))

    # 输出结果
    result = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open("workplace_score.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    run_verification()
