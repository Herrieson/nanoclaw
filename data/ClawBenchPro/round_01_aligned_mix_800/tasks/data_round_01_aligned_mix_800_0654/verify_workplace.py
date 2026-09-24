import os
import sys
import json
import re
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
    
    score_details = []
    total_score = 0
    
    # 1. 检查 deliverables 目录
    if os.path.exists(deliverables_dir) and os.path.isdir(deliverables_dir):
        files = os.listdir(deliverables_dir)
        if len(files) > 0:
            score_details.append({"item": "Deliverables directory and files exist", "score": 10, "max_score": 10, "passed": True, "reason": "Directory exists and contains files."})
            total_score += 10
        else:
            score_details.append({"item": "Deliverables directory and files exist", "score": 0, "max_score": 10, "passed": False, "reason": "Directory exists but is empty."})
    else:
        score_details.append({"item": "Deliverables directory and files exist", "score": 0, "max_score": 10, "passed": False, "reason": "Directory 'deliverables' does not exist."})
        
    # Read all contents from deliverables
    all_content = ""
    if os.path.exists(deliverables_dir):
        for root, _, files in os.walk(deliverables_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        all_content += f.read() + "\n"
                except Exception:
                    pass

    content_lower = all_content.lower()

    # 2. 检查所需零件是否全数列出 (Max 15)
    missing_parts = []
    for part in ["oil filter", "alternator", "spark plugs"]:
        if part in content_lower:
            missing_parts.append(part)
    
    part_score = len(missing_parts) * 5
    if part_score > 0:
        score_details.append({"item": "Identify low inventory parts (< 5)", "score": part_score, "max_score": 15, "passed": part_score == 15, "reason": f"Found parts: {missing_parts}"})
        total_score += part_score
    else:
        score_details.append({"item": "Identify low inventory parts (< 5)", "score": 0, "max_score": 15, "passed": False, "reason": "No valid low inventory parts found."})

    # 3. 严查幻觉/错误零件 (Max 15)
    wrong_parts = []
    for part in ["brake pads", "wiper blades", "battery"]:
        if part in content_lower:
            wrong_parts.append(part)
    
    if len(wrong_parts) == 0:
        score_details.append({"item": "Exclude sufficient inventory parts (>= 5)", "score": 15, "max_score": 15, "passed": True, "reason": "No sufficient parts were mistakenly ordered."})
        total_score += 15
    else:
        penalty = 15 - (len(wrong_parts) * 5)
        score_details.append({"item": "Exclude sufficient inventory parts (>= 5)", "score": penalty, "max_score": 15, "passed": False, "reason": f"Wrongly included sufficient parts: {wrong_parts}"})
        total_score += penalty

    # 4. 严查非法志愿者 (Max 10)
    unapproved = []
    for sketchy in ["sketchy bob", "random joe"]:
        if sketchy in content_lower:
            unapproved.append(sketchy)
    
    if len(unapproved) == 0:
        score_details.append({"item": "Exclude unapproved volunteers", "score": 10, "max_score": 10, "passed": True, "reason": "No unapproved volunteers found in the output."})
        total_score += 10
    else:
        score_details.append({"item": "Exclude unapproved volunteers", "score": 0, "max_score": 10, "passed": False, "reason": f"Found unapproved volunteers: {unapproved}. This is a critical failure."})

    # 5. 检查确定性数值计算 (总工时或分项工时) (Max 20)
    # Total approved hours: 19.5
    # Individuals: Hector 8.0, Luis 5.0, Maria 5.0, Father Thomas 1.5
    numbers = re.findall(r'\d+\.?\d*', all_content)
    numbers_float = [float(n) for n in numbers]
    
    if 19.5 in numbers_float:
        score_details.append({"item": "Accurate calculation of total approved hours", "score": 20, "max_score": 20, "passed": True, "reason": "Found exact total hours (19.5)."})
        total_score += 20
    else:
        # Check individual hours
        individual_score = 0
        if 8.0 in numbers_float or 8 in numbers_float: individual_score += 5
        if 5.0 in numbers_float or 5 in numbers_float: individual_score += 5
        if 1.5 in numbers_float: individual_score += 5
        
        if individual_score > 0:
            score_details.append({"item": "Accurate calculation of total approved hours", "score": individual_score, "max_score": 20, "passed": False, "reason": "Total 19.5 not found, but found some accurate individual hours."})
            total_score += individual_score
        else:
            score_details.append({"item": "Accurate calculation of total approved hours", "score": 0, "max_score": 20, "passed": False, "reason": "Neither total (19.5) nor accurate individual hours found."})

    # 6. LLM 非结构化语义检查：格式是否适合手机阅读并且清晰划分 (Max 30)
    if all_content.strip():
        llm_prompt = "Does the text clearly separate 'Parts to Order' and 'Approved Volunteer Hours' in a simple, mobile-friendly format? It should not be overly dense, just a clean and easy-to-read summary."
        is_mobile_friendly = llm_judge_content(llm_prompt, all_content)
        if is_mobile_friendly:
            score_details.append({"item": "LLM Check: Clear, mobile-friendly formatting", "score": 30, "max_score": 30, "passed": True, "reason": "LLM verified the format is clean and separated appropriately."})
            total_score += 30
        else:
            score_details.append({"item": "LLM Check: Clear, mobile-friendly formatting", "score": 0, "max_score": 30, "passed": False, "reason": "LLM determined the format is messy or not separated clearly."})
    else:
        score_details.append({"item": "LLM Check: Clear, mobile-friendly formatting", "score": 0, "max_score": 30, "passed": False, "reason": "No content to evaluate."})

    # Output results
    result_data = {
        "total_score": total_score,
        "details": score_details
    }
    
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)
        
    print(json.dumps(result_data, indent=2))

if __name__ == "__main__":
    verify()
