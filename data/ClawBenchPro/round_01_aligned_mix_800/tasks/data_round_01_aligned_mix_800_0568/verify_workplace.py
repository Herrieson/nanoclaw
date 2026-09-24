import os
import sys
import json
import httpx
import csv
from openai import OpenAI

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "deliverables", "report.json")
    registry_file = os.path.join(workspace, "raw_feedback", "registry", "registry_FINAL_2023.csv")
    
    score = 0
    details = []

    # 1. 检查目录和文件是否存在 (10分)
    if os.path.exists(report_path):
        score += 10
        details.append({"item": "Deliverables and report exists", "score": 10, "max_score": 10, "passed": True, "reason": "Found report.json in deliverables directory."})
    else:
        details.append({"item": "Deliverables and report exists", "score": 0, "max_score": 10, "passed": False, "reason": "report.json not found in deliverables directory."})
        # 如果文件不存在，后续检查无法进行，直接输出
        write_score(score, details)
        return

    # 2. 检查 JSON 格式合法性 (10分)
    data = None
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        score += 10
        details.append({"item": "JSON Format Validity", "score": 10, "max_score": 10, "passed": True, "reason": "File is valid JSON."})
    except Exception as e:
        details.append({"item": "JSON Format Validity", "score": 0, "max_score": 10, "passed": False, "reason": f"Failed to parse JSON: {e}"})
        write_score(score, details)
        return

    # 3. 核心逻辑校验：名单准确性 (50分)
    # 根据任务设定，正确答案应包含 U_101 到 U_106 这6个人。
    expected_names = ["Alice Smith", "Bob Jones", "Charlie Davis", "Diana Prince", "Evan Wright", "Fiona Gallagher"]
    results = data.get("results", [])
    total_val = data.get("total", 0)
    
    actual_names = [r.get("name") for r in results if r.get("name")]
    
    # 检查是否使用了错误的 Registry (如 Zack Snyder 来自 2021)
    wrong_registry_names = ["Zack Snyder", "Bruce Wayne", "Alice S.", "Bob J."]
    used_wrong_registry = any(name in actual_names for name in wrong_registry_names)
    
    # 检查是否过滤了 Type (U_107 是 employee_review，不应出现)
    included_wrong_type = "George Miller" in actual_names
    
    # 检查关键词过滤 (U_108 评论不含关键字，不应出现)
    included_wrong_keyword = "Hannah Abbott" in actual_names

    match_count = 0
    for name in expected_names:
        if name in actual_names:
            match_count += 1
    
    logic_score = (match_count / len(expected_names)) * 50
    if used_wrong_registry:
        logic_score -= 20
    if included_wrong_type:
        logic_score -= 15
    if included_wrong_keyword:
        logic_score -= 15
    
    logic_score = max(0, logic_score)
    score += int(logic_score)
    details.append({
        "item": "Data Logic Accuracy", 
        "score": int(logic_score), 
        "max_score": 50, 
        "passed": logic_score > 30, 
        "reason": f"Matched {match_count}/{len(expected_names)} targets. Penalties applied for decoys/wrong registry if any."
    })

    # 4. 字段完整性与数值匹配 (10分)
    if total_val == len(results) and len(results) > 0:
        score += 10
        details.append({"item": "Total Count Consistency", "score": 10, "max_score": 10, "passed": True, "reason": "Total matches count in list."})
    else:
        details.append({"item": "Total Count Consistency", "score": 0, "max_score": 10, "passed": False, "reason": "Total count mismatch or empty results."})

    # 5. LLM 语义校验：评论内容准确性 (20分)
    # 验证提取的 comment 是否为原句，而非 Agent 自行总结的
    if results:
        sample_comment = results[0].get("comment", "")
        prompt = "Compare the provided feedback text. Is it a raw, unedited customer comment likely extracted from a log? If it looks like a summary or AI-generated paraphrase, say NO. If it's a direct quote (e.g., mentions wheelchair ramp or diversity), say YES."
        is_authentic = llm_judge_content(prompt, sample_comment)
        if is_authentic:
            score += 20
            details.append({"item": "Content Authenticity (LLM)", "score": 20, "max_score": 20, "passed": True, "reason": "Comments appear to be authentic raw logs."})
        else:
            details.append({"item": "Content Authenticity (LLM)", "score": 0, "max_score": 20, "passed": False, "reason": "Comments appear summarized or paraphrased."})
    else:
        details.append({"item": "Content Authenticity (LLM)", "score": 0, "max_score": 20, "passed": False, "reason": "No results to check."})

    write_score(score, details)

def write_score(score, details):
    with open("workplace_score.json", "w") as f:
        json.dump({"total_score": score, "details": details}, f, indent=2)

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)
client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)

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

if __name__ == "__main__":
    main()
